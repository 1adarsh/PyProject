"""A cozy, animated PDF reader.

Install the packages in requirements.txt, then run this file with Python.
"""

from __future__ import annotations

import io
import math
import os
import tkinter as tk
import time
from tkinter import filedialog, messagebox, simpledialog

import pymupdf as fitz
from PIL import Image, ImageTk


PLUM = "#281539"
PANEL = "#3B2052"
PANEL_LIGHT = "#512D6B"
LILAC = "#D7A9F2"
PINK = "#F28FC7"
PALE_PINK = "#F9D8EC"
TEXT = "#FFF4FF"
MUTED = "#D6C0E3"


class CozyPDFReader:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Moonberry Reader")
        self.root.geometry("1120x780")
        self.root.minsize(760, 560)
        self.root.configure(bg=PLUM)

        self.document: fitz.Document | None = None
        self.document_path: str | None = None
        self.page_index = 0
        self.zoom = 1.0
        self.bookmarks: set[int] = set()
        self.page_image: ImageTk.PhotoImage | None = None
        self.render_after_id: str | None = None
        self.page_number = tk.StringVar(value="1")
        self.zoom_label = tk.StringVar(value="Fit")
        self.status_text = tk.StringVar(value="Pick a PDF and settle in.")

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self._build_header()
        self._build_reader()
        self._build_footer()

        self.root.bind("<Left>", lambda _event: self.show_page(self.page_index - 1))
        self.root.bind("<Right>", lambda _event: self.show_page(self.page_index + 1))
        self.root.bind("<Control-o>", lambda _event: self.open_dialog())
        self.root.bind("<Control-plus>", lambda _event: self.change_zoom(1.15))
        self.root.bind("<Control-equal>", lambda _event: self.change_zoom(1.15))
        self.root.bind("<Control-minus>", lambda _event: self.change_zoom(1 / 1.15))
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self._animate_sparkles()

    def _build_header(self) -> None:
        header = tk.Frame(self.root, bg=PLUM, padx=28, pady=17)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        mark = tk.Label(
            header,
            text="♥",
            bg=PLUM,
            fg=PINK,
            font=("TkDefaultFont", 27, "bold"),
        )
        mark.grid(row=0, column=0, rowspan=2, padx=(0, 13))

        tk.Label(
            header,
            text="Moonberry Reader",
            bg=PLUM,
            fg=TEXT,
            font=("TkDefaultFont", 19, "bold"),
        ).grid(row=0, column=1, sticky="sw")
        self.file_label = tk.Label(
            header,
            text="Your little reading nook",
            bg=PLUM,
            fg=MUTED,
            font=("TkDefaultFont", 10),
            anchor="w",
        )
        self.file_label.grid(row=1, column=1, sticky="nw", pady=(2, 0))

        self.sparkle_canvas = tk.Canvas(
            header,
            width=105,
            height=48,
            bg=PLUM,
            highlightthickness=0,
        )
        self.sparkle_canvas.grid(row=0, column=2, rowspan=2, padx=(8, 18))
        self.sparkle_ids = [
            self.sparkle_canvas.create_text(
                20, 22, text="✦", fill=PINK, font=("TkDefaultFont", 15, "bold")
            ),
            self.sparkle_canvas.create_text(
                54, 30, text="♥", fill=LILAC, font=("TkDefaultFont", 13, "bold")
            ),
            self.sparkle_canvas.create_text(
                83, 17, text="✧", fill=PALE_PINK, font=("TkDefaultFont", 17, "bold")
            ),
        ]

        self._button(
            header,
            "Open a PDF",
            self.open_dialog,
            bg=PINK,
            fg=PLUM,
            active_bg=PALE_PINK,
            padx=18,
        ).grid(row=0, column=3, rowspan=2, sticky="e")

    def _build_reader(self) -> None:
        shell = tk.Frame(self.root, bg=PANEL, padx=18, pady=14)
        shell.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 12))
        shell.grid_columnconfigure(0, weight=1)
        shell.grid_rowconfigure(1, weight=1)

        toolbar = tk.Frame(shell, bg=PANEL)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        toolbar.grid_columnconfigure(3, weight=1)

        self._button(
            toolbar, "‹  Previous", lambda: self.show_page(self.page_index - 1)
        ).grid(row=0, column=0, padx=(0, 10))
        self._button(
            toolbar, "Next  ›", lambda: self.show_page(self.page_index + 1)
        ).grid(row=0, column=1, padx=(0, 12))

        page_controls = tk.Frame(toolbar, bg=PANEL)
        page_controls.grid(row=0, column=2)
        tk.Label(
            page_controls,
            text="Page",
            bg=PANEL,
            fg=MUTED,
            font=("TkDefaultFont", 10),
        ).pack(side="left", padx=(0, 7))
        self.page_entry = tk.Entry(
            page_controls,
            textvariable=self.page_number,
            width=5,
            justify="center",
            bg=PANEL_LIGHT,
            fg=TEXT,
            insertbackground=TEXT,
            selectbackground=PINK,
            selectforeground=PLUM,
            relief="flat",
            font=("TkDefaultFont", 10, "bold"),
        )
        self.page_entry.pack(side="left", ipady=6)
        self.page_entry.bind("<Return>", self._go_to_page)
        self.total_pages_label = tk.Label(
            page_controls,
            text="of —",
            bg=PANEL,
            fg=MUTED,
            font=("TkDefaultFont", 10),
        )
        self.total_pages_label.pack(side="left", padx=(7, 0))

        right_controls = tk.Frame(toolbar, bg=PANEL)
        right_controls.grid(row=0, column=4, sticky="e")
        self._button(right_controls, "−", lambda: self.change_zoom(1 / 1.15)).pack(
            side="left", padx=(0, 5)
        )
        tk.Label(
            right_controls,
            textvariable=self.zoom_label,
            width=5,
            bg=PANEL,
            fg=PALE_PINK,
            font=("TkDefaultFont", 9, "bold"),
        ).pack(side="left")
        self._button(right_controls, "+", lambda: self.change_zoom(1.15)).pack(
            side="left", padx=(5, 12)
        )
        self.bookmark_button = self._button(
            right_controls, "♡  Save page", self.toggle_bookmark
        )
        self.bookmark_button.pack(side="left")

        self.canvas = tk.Canvas(
            shell,
            bg=PLUM,
            highlightthickness=0,
            borderwidth=0,
            xscrollincrement=24,
            yscrollincrement=24,
        )
        self.canvas.grid(row=1, column=0, sticky="nsew")
        self.vertical_scrollbar = tk.Scrollbar(
            shell,
            orient="vertical",
            command=self.canvas.yview,
            bg=PANEL_LIGHT,
            troughcolor=PANEL,
            activebackground=PINK,
            highlightthickness=0,
            relief="flat",
        )
        self.vertical_scrollbar.grid(row=1, column=1, sticky="ns", padx=(8, 0))
        self.horizontal_scrollbar = tk.Scrollbar(
            shell,
            orient="horizontal",
            command=self.canvas.xview,
            bg=PANEL_LIGHT,
            troughcolor=PANEL,
            activebackground=PINK,
            highlightthickness=0,
            relief="flat",
        )
        self.horizontal_scrollbar.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        self.canvas.configure(
            xscrollcommand=self.horizontal_scrollbar.set,
            yscrollcommand=self.vertical_scrollbar.set,
        )
        self.canvas.bind("<Configure>", self._schedule_render)
        self.canvas.bind("<MouseWheel>", self._mouse_wheel)
        self.canvas.bind("<Button-4>", lambda _event: self.canvas.yview_scroll(-3, "units"))
        self.canvas.bind("<Button-5>", lambda _event: self.canvas.yview_scroll(3, "units"))
        self.canvas.bind(
            "<Shift-MouseWheel>",
            lambda event: self.canvas.xview_scroll(-1 if event.delta > 0 else 1, "units"),
        )
        self._draw_welcome()

    def _build_footer(self) -> None:
        footer = tk.Frame(self.root, bg=PLUM, padx=29)
        footer.grid(row=2, column=0, sticky="ew", pady=(0, 18))
        footer.grid_columnconfigure(0, weight=1)

        self.progress_canvas = tk.Canvas(
            footer,
            height=7,
            bg=PANEL,
            highlightthickness=0,
            borderwidth=0,
        )
        self.progress_canvas.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.progress_canvas.bind("<Configure>", self._update_progress)

        tk.Label(
            footer,
            textvariable=self.status_text,
            bg=PLUM,
            fg=MUTED,
            font=("TkDefaultFont", 9),
            anchor="w",
        ).grid(row=1, column=0, sticky="w")

    @staticmethod
    def _button(
        parent: tk.Widget,
        label: str,
        command: object,
        *,
        bg: str = PANEL_LIGHT,
        fg: str = TEXT,
        active_bg: str = LILAC,
        padx: int = 12,
    ) -> tk.Button:
        return tk.Button(
            parent,
            text=label,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=active_bg,
            activeforeground=PLUM,
            relief="flat",
            borderwidth=0,
            padx=padx,
            pady=8,
            cursor="hand2",
            font=("TkDefaultFont", 9, "bold"),
        )

    def _animate_sparkles(self) -> None:
        phase = time.monotonic()
        for index, item in enumerate(self.sparkle_ids):
            x = (20, 54, 83)[index] + math.sin(phase * 1.8 + index) * 3
            y = (22, 30, 17)[index] + math.cos(phase * 1.6 + index) * 4
            self.sparkle_canvas.coords(item, x, y)
        self.root.after(80, self._animate_sparkles)

    def _draw_welcome(self) -> None:
        self.canvas.delete("all")
        width = max(600, self.canvas.winfo_width())
        height = max(360, self.canvas.winfo_height())
        center_x = width // 2
        center_y = height // 2
        self.canvas.configure(scrollregion=(0, 0, width, height))
        self.canvas.create_text(
            center_x,
            center_y - 20,
            text="A cozy little corner for your next chapter",
            fill=PALE_PINK,
            font=("TkDefaultFont", 17, "bold"),
        )
        self.canvas.create_text(
            center_x,
            center_y + 25,
            text="Open a PDF to begin  ♥",
            fill=LILAC,
            font=("TkDefaultFont", 11),
        )

    def open_dialog(self) -> None:
        path = filedialog.askopenfilename(
            parent=self.root,
            title="Choose a PDF for your reading nook",
            filetypes=(("PDF files", "*.pdf"), ("All files", "*.*")),
        )
        if path:
            self.open_document(path)

    def open_document(self, path: str) -> None:
        try:
            candidate = fitz.open(path)
        except (fitz.FileDataError, OSError, RuntimeError) as error:
            messagebox.showerror(
                "Couldn't open that PDF",
                f"Moonberry Reader couldn't open this file:\n{error}",
                parent=self.root,
            )
            return

        if candidate.needs_pass:
            password = simpledialog.askstring(
                "Password-protected PDF",
                "Enter the password to open this PDF:",
                parent=self.root,
                show="•",
            )
            if password is None:
                candidate.close()
                return
            try:
                authenticated = candidate.authenticate(password)
            except RuntimeError as error:
                candidate.close()
                messagebox.showerror(
                    "Couldn't unlock that PDF", str(error), parent=self.root
                )
                return
            if not authenticated:
                candidate.close()
                messagebox.showerror(
                    "Couldn't unlock that PDF",
                    "That password didn't unlock the document.",
                    parent=self.root,
                )
                return

        if candidate.page_count == 0:
            candidate.close()
            messagebox.showerror(
                "Empty PDF",
                "This PDF doesn't contain any pages to read.",
                parent=self.root,
            )
            return

        previous_document = self.document
        self.document = candidate
        self.document_path = path
        self.page_index = 0
        self.zoom = 1.0
        self.bookmarks.clear()
        if previous_document is not None:
            previous_document.close()

        self.file_label.configure(text=os.path.basename(path))
        self.total_pages_label.configure(text=f"of {candidate.page_count}")
        self.zoom_label.set("Fit")
        self.status_text.set("Take your time. You're right where you need to be.")
        self.show_page(0)

    def show_page(self, page_index: int) -> None:
        if self.document is None:
            return
        page_index = max(0, min(page_index, self.document.page_count - 1))
        self.page_index = page_index
        self.page_number.set(str(page_index + 1))
        self._update_bookmark_button()
        self._update_progress()
        self._render_page()

    def _go_to_page(self, _event: tk.Event[tk.Misc]) -> None:
        if self.document is None:
            return
        try:
            requested_page = int(self.page_number.get())
        except ValueError:
            self.page_number.set(str(self.page_index + 1))
            self.status_text.set("Enter a page number to hop there.")
            return
        if not 1 <= requested_page <= self.document.page_count:
            self.page_number.set(str(self.page_index + 1))
            self.status_text.set(
                f"Choose a page from 1 to {self.document.page_count}."
            )
            return
        self.show_page(requested_page - 1)

    def change_zoom(self, factor: float) -> None:
        if self.document is None:
            return
        self.zoom = max(0.4, min(self.zoom * factor, 4.0))
        self.zoom_label.set(f"{round(self.zoom * 100)}%")
        self._render_page()

    def toggle_bookmark(self) -> None:
        if self.document is None:
            return
        if self.page_index in self.bookmarks:
            self.bookmarks.remove(self.page_index)
        else:
            self.bookmarks.add(self.page_index)
        self._update_bookmark_button()

    def _update_bookmark_button(self) -> None:
        if self.page_index in self.bookmarks:
            self.bookmark_button.configure(
                text="♥  Saved", bg=PINK, fg=PLUM, activebackground=PALE_PINK
            )
        else:
            self.bookmark_button.configure(
                text="♡  Save page",
                bg=PANEL_LIGHT,
                fg=TEXT,
                activebackground=LILAC,
            )

    def _schedule_render(self, _event: tk.Event[tk.Misc] | None = None) -> None:
        if self.document is None:
            self._draw_welcome()
            return
        if self.render_after_id is not None:
            self.root.after_cancel(self.render_after_id)
        self.render_after_id = self.root.after(100, self._render_page)

    def _render_page(self) -> None:
        self.render_after_id = None
        if self.document is None:
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width < 40 or canvas_height < 40:
            self._schedule_render()
            return

        try:
            page = self.document.load_page(self.page_index)
            fit_scale = min(
                (canvas_width - 48) / page.rect.width,
                (canvas_height - 48) / page.rect.height,
            )
            scale = max(0.1, fit_scale * self.zoom)
            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(scale, scale),
                colorspace=fitz.csRGB,
                alpha=False,
            )
            image = Image.open(io.BytesIO(pixmap.tobytes("png"))).convert("RGB")
        except (fitz.FileDataError, OSError, RuntimeError, ValueError) as error:
            self.status_text.set(f"Couldn't render this page: {error}")
            messagebox.showerror(
                "Couldn't render this page",
                f"Moonberry Reader couldn't display page {self.page_index + 1}:\n{error}",
                parent=self.root,
            )
            return

        self.page_image = ImageTk.PhotoImage(image, master=self.root)
        region_width = max(canvas_width, image.width)
        region_height = max(canvas_height, image.height)
        x = (region_width - image.width) // 2
        y = (region_height - image.height) // 2
        self.canvas.delete("all")
        self.canvas.configure(scrollregion=(0, 0, region_width, region_height))
        self.canvas.create_image(x, y, image=self.page_image, anchor="nw")
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

    def _update_progress(self, _event: tk.Event[tk.Misc] | None = None) -> None:
        self.progress_canvas.delete("all")
        width = self.progress_canvas.winfo_width()
        height = self.progress_canvas.winfo_height()
        if width <= 1:
            return
        self.progress_canvas.create_rectangle(
            0, 0, width, height, fill=PANEL, outline=""
        )
        if self.document is not None:
            progress = (self.page_index + 1) / self.document.page_count
            self.progress_canvas.create_rectangle(
                0, 0, width * progress, height, fill=PINK, outline=""
            )

    def _mouse_wheel(self, event: tk.Event[tk.Misc]) -> None:
        direction = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(direction * 3, "units")

    def close(self) -> None:
        if self.render_after_id is not None:
            self.root.after_cancel(self.render_after_id)
        if self.document is not None:
            self.document.close()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    CozyPDFReader(root)
    root.mainloop()


if __name__ == "__main__":
    main()
