"""A self-contained 2D ninja campaign built with Python's Tkinter."""

from __future__ import annotations

import tkinter as tk
import math
from time import perf_counter
from dataclasses import dataclass


WIDTH = 960
HEIGHT = 600
GROUND_Y = 500
FIGHTER_HEIGHT = 100
FRAME_MS = 16


@dataclass(frozen=True)
class Level:
    name: str
    boss: str
    boss_color: str
    map_width: int
    boss_health: int
    boss_speed: float
    boss_cooldown: float
    reward: str
    sky: str
    far_hills: str
    near_hills: str
    ground: str
    foliage: str


LEVELS = (
    Level(
        "Whispering Forest", "Bramble Fang", "#4aa878", 2200, 140,
        145, 1.35, "Storm Chakra: energy waves deal more damage",
        "#8bc4d9", "#678da0", "#486b62", "#354f3d", "#527b4c",
    ),
    Level(
        "Red Dune Pass", "Dune Reaver", "#c87948", 2500, 185,
        165, 1.08, "Sky Step: jump once more in midair",
        "#d99875", "#ad7772", "#805653", "#73503a", "#b78350",
    ),
    Level(
        "Frost Moon Keep", "Moon Warden", "#8496d0", 2800, 235,
        185, 0.86, "Phoenix Guard: slowly recover health",
        "#829eb8", "#647d9e", "#4b5d79", "#35495d", "#8aafc1",
    ),
)


@dataclass
class Fighter:
    x: float
    y: float
    color: str
    facing: int
    health: float = 100
    chakra: float = 100
    max_health: int = 100
    velocity_x: float = 0
    velocity_y: float = 0
    jump_count: int = 0
    attack_time: float = 0
    attack_landed: bool = False
    hurt_time: float = 0


@dataclass
class EnergyWave:
    x: float
    y: float
    direction: int
    owner: str
    damage: int
    speed: float


class NinjaCampaign:
    """Side-scrolling 2D ninja game with three bosses and earned powers."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Ninja Duel: Shinobi Legends")
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(
            root, width=WIDTH, height=HEIGHT, bg=LEVELS[0].sky,
            highlightthickness=0,
        )
        self.canvas.pack()

        self.keys: set[str] = set()
        self.waves: list[EnergyWave] = []
        self.level_index = 0
        self.level = LEVELS[0]
        self.powers: list[str] = []
        self.player = Fighter(160, GROUND_Y - FIGHTER_HEIGHT, "#f08a35", 1)
        self.boss = self.create_boss()
        self.boss_cooldown = self.level.boss_cooldown
        self.boss_jump_cooldown = 1.8
        self.announcement_time = 3.0
        self.camera_x = 0.0
        self.game_over = False
        self.victory = False
        self.elapsed = 0.0
        self.last_frame = perf_counter()

        self.root.bind_all("<KeyPress>", self.on_key_down)
        self.root.bind_all("<KeyRelease>", self.on_key_up)
        self.draw()
        self.update()

    def create_boss(self) -> Fighter:
        level = LEVELS[self.level_index]
        return Fighter(
            level.map_width * 0.67,
            GROUND_Y - FIGHTER_HEIGHT,
            level.boss_color,
            -1,
            health=level.boss_health,
            max_health=level.boss_health,
        )

    def on_key_down(self, event: tk.Event) -> None:
        key = event.keysym.lower()
        if key in self.keys:
            return
        self.keys.add(key)
        if key in ("space", "w", "up"):
            self.jump(self.player, player=True)
        elif key in ("j", "z"):
            self.start_attack(self.player)
        elif key in ("k", "x"):
            self.throw_wave(self.player, "player")
        elif key == "r" and self.game_over:
            self.restart()

    def on_key_up(self, event: tk.Event) -> None:
        key = event.keysym.lower()
        self.keys.discard(key)
        if key in ("space", "w", "up") and self.player.velocity_y < -180:
            self.player.velocity_y = -180

    @staticmethod
    def start_attack(fighter: Fighter) -> None:
        if fighter.attack_time <= 0:
            fighter.attack_time = 0.30
            fighter.attack_landed = False

    def jump(self, fighter: Fighter, player: bool = False) -> None:
        max_jumps = 2 if player and self.level_index >= 1 else 1
        if fighter.jump_count < max_jumps:
            fighter.velocity_y = -610 if fighter.jump_count == 0 else -500
            fighter.jump_count += 1

    def throw_wave(self, fighter: Fighter, owner: str) -> None:
        if fighter.chakra < 25 or self.game_over:
            return
        fighter.chakra -= 25
        if owner == "player":
            damage = 24 if any(power.startswith("Storm Chakra") for power in self.powers) else 16
            speed = 520
        else:
            damage = 12 + 3 * self.level_index
            speed = 430 + 35 * self.level_index
        self.waves.append(EnergyWave(
            fighter.x + fighter.facing * 38,
            fighter.y + 43,
            fighter.facing,
            owner,
            damage,
            speed,
        ))

    def restart(self) -> None:
        self.level_index = 0
        self.level = LEVELS[0]
        self.powers.clear()
        self.player = Fighter(160, GROUND_Y - FIGHTER_HEIGHT, "#f08a35", 1)
        self.boss = self.create_boss()
        self.boss_cooldown = self.level.boss_cooldown
        self.boss_jump_cooldown = 1.8
        self.announcement_time = 3.0
        self.camera_x = 0
        self.waves.clear()
        self.game_over = False
        self.victory = False
        self.last_frame = perf_counter()

    def update(self) -> None:
        now = perf_counter()
        dt = min(now - self.last_frame, 0.04)
        self.last_frame = now
        self.elapsed += dt
        if not self.game_over:
            self.update_player(dt)
            self.update_boss(dt)
            self.update_waves(dt)
            self.update_resources(dt)
            self.announcement_time = max(0, self.announcement_time - dt)
            target_camera = self.player.x - WIDTH * 0.38
            self.camera_x = max(
                0,
                min(self.level.map_width - WIDTH, target_camera),
            )
            if self.boss.health <= 0:
                self.complete_level()
            elif self.player.health <= 0:
                self.game_over = True
        self.draw()
        self.root.after(FRAME_MS, self.update)

    def update_player(self, dt: float) -> None:
        player = self.player
        right = "d" in self.keys or "right" in self.keys
        left = "a" in self.keys or "left" in self.keys
        direction = int(right) - int(left)
        if direction:
            player.velocity_x = max(-315, min(315, player.velocity_x + direction * 1900 * dt))
        else:
            friction = 2100 * dt
            if abs(player.velocity_x) <= friction:
                player.velocity_x = 0
            else:
                player.velocity_x -= math.copysign(friction, player.velocity_x)
        player.x += player.velocity_x * dt
        player.x = max(38, min(self.level.map_width - 38, player.x))
        if player.x in (38, self.level.map_width - 38):
            player.velocity_x = 0
        if direction:
            player.facing = direction
        self.apply_gravity(player, dt, jump_held=bool({"space", "w", "up"} & self.keys))
        self.update_attack(player, self.boss, dt)
        player.hurt_time = max(0, player.hurt_time - dt)

    def update_boss(self, dt: float) -> None:
        boss = self.boss
        distance = self.player.x - boss.x
        boss.facing = 1 if distance > 0 else -1
        if abs(distance) > 86:
            boss.velocity_x += boss.facing * 950 * dt
            boss.velocity_x = max(
                -self.level.boss_speed,
                min(self.level.boss_speed, boss.velocity_x),
            )
        else:
            friction = 1800 * dt
            if abs(boss.velocity_x) <= friction:
                boss.velocity_x = 0
            else:
                boss.velocity_x -= math.copysign(friction, boss.velocity_x)
        boss.x += boss.velocity_x * dt
        boss.x = max(38, min(self.level.map_width - 38, boss.x))
        if boss.x in (38, self.level.map_width - 38):
            boss.velocity_x = 0
        self.apply_gravity(boss, dt)
        self.update_attack(boss, self.player, dt)
        boss.hurt_time = max(0, boss.hurt_time - dt)

        self.boss_jump_cooldown -= dt
        if self.boss_jump_cooldown <= 0:
            if abs(distance) > 130 and boss.jump_count == 0:
                self.jump(boss)
            self.boss_jump_cooldown = max(1.1, self.level.boss_cooldown * 1.8)

        self.boss_cooldown -= dt
        if self.boss_cooldown <= 0:
            if abs(distance) < 118:
                self.start_attack(boss)
                self.boss_cooldown = self.level.boss_cooldown
            elif abs(distance) < 620 and boss.chakra >= 25:
                self.throw_wave(boss, "boss")
                self.boss_cooldown = self.level.boss_cooldown * 1.5
            else:
                self.boss_cooldown = 0.4

    @staticmethod
    def apply_gravity(fighter: Fighter, dt: float, jump_held: bool = False) -> None:
        gravity = 930 if jump_held and fighter.velocity_y < 0 else 1450
        fighter.velocity_y += gravity * dt
        fighter.y += fighter.velocity_y * dt
        floor_y = GROUND_Y - FIGHTER_HEIGHT
        if fighter.y >= floor_y:
            fighter.y = floor_y
            fighter.velocity_y = 0
            fighter.jump_count = 0

    def update_attack(self, attacker: Fighter, target: Fighter, dt: float) -> None:
        if attacker.attack_time <= 0:
            return
        attacker.attack_time = max(0, attacker.attack_time - dt)
        if (
            not attacker.attack_landed
            and attacker.attack_time < 0.19
            and abs(attacker.x - target.x) < 108
            and abs(attacker.y - target.y) < 82
            and attacker.facing * (target.x - attacker.x) > 0
        ):
            target.health = max(0, target.health - 10)
            target.hurt_time = 0.2
            attacker.attack_landed = True

    def update_waves(self, dt: float) -> None:
        remaining: list[EnergyWave] = []
        for wave in self.waves:
            wave.x += wave.direction * wave.speed * dt
            target = self.boss if wave.owner == "player" else self.player
            if (
                abs(wave.x - target.x) < 36
                and abs(wave.y - (target.y + 45)) < 48
            ):
                target.health = max(0, target.health - wave.damage)
                target.hurt_time = 0.22
            elif 0 <= wave.x <= self.level.map_width:
                remaining.append(wave)
        self.waves = remaining

    def update_resources(self, dt: float) -> None:
        self.player.chakra = min(100, self.player.chakra + 8 * dt)
        self.boss.chakra = min(100, self.boss.chakra + 6 * dt)
        if self.level_index >= 2:
            self.player.health = min(self.player.max_health, self.player.health + dt)

    def complete_level(self) -> None:
        self.powers.append(self.level.reward)
        if self.level_index == len(LEVELS) - 1:
            self.game_over = True
            self.victory = True
            return
        self.level_index += 1
        self.level = LEVELS[self.level_index]
        self.player.x = 160
        self.player.y = GROUND_Y - FIGHTER_HEIGHT
        self.player.velocity_y = 0
        self.player.jump_count = 0
        self.player.health = min(self.player.max_health, self.player.health + 30)
        self.player.chakra = 100
        self.boss = self.create_boss()
        self.boss_cooldown = self.level.boss_cooldown
        self.boss_jump_cooldown = 1.5
        self.waves.clear()
        self.camera_x = 0
        self.announcement_time = 3.5

    def draw(self) -> None:
        self.canvas.delete("all")
        self.draw_background()
        self.draw_hud()
        self.draw_fighter(self.player, "HERO", True)
        self.draw_fighter(self.boss, self.level.boss.upper(), False)
        for wave in self.waves:
            self.draw_wave(wave)
        if self.announcement_time > 0 and not self.game_over:
            self.draw_announcement()
        if self.game_over:
            self.draw_game_over()

    def draw_background(self) -> None:
        canvas = self.canvas
        canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=self.level.sky, outline="")
        if self.level_index == 2:
            canvas.create_oval(720, 65, 830, 175, fill="#e7e8d4", outline="")
        else:
            canvas.create_oval(740, 65, 830, 155, fill="#f7d58f", outline="")

        self.draw_hills(self.level.far_hills, 300, 0.16, 180)
        self.draw_hills(self.level.near_hills, 365, 0.32, 140)
        canvas.create_rectangle(0, GROUND_Y, WIDTH, HEIGHT,
                                fill=self.level.ground, outline="")
        canvas.create_rectangle(0, GROUND_Y, WIDTH, GROUND_Y + 8,
                                fill=self.level.foliage, outline="")

        start = int(self.camera_x // 90) * 90
        for world_x in range(start, int(self.camera_x + WIDTH) + 100, 90):
            x = world_x - self.camera_x
            canvas.create_line(x, GROUND_Y + 22, x + 25, GROUND_Y + 22,
                               fill=self.level.foliage, width=3)

        if self.level_index == 0:
            self.draw_forest_details()
        elif self.level_index == 1:
            self.draw_desert_details()
        else:
            self.draw_keep_details()

    def draw_hills(self, tint: str, baseline: int, factor: float,
                   spacing: int) -> None:
        offset = (self.camera_x * factor) % spacing
        for index, x in enumerate(range(-spacing, WIDTH + spacing * 2, spacing)):
            left = x - offset
            peak = baseline - (index * 47 % 90) - 40
            self.canvas.create_polygon(
                left, baseline, left + spacing / 2, peak,
                left + spacing, baseline,
                fill=tint, outline="",
            )

    def draw_forest_details(self) -> None:
        start = int(self.camera_x // 250) * 250
        for world_x in range(start - 250, int(self.camera_x + WIDTH) + 250, 250):
            x = world_x - self.camera_x
            height = 130 + (world_x // 250 % 3) * 22
            self.canvas.create_rectangle(
                x - 9, GROUND_Y - height, x + 9, GROUND_Y,
                fill="#5b463b", outline="",
            )
            for tier in range(3):
                top = GROUND_Y - height + tier * 36
                self.canvas.create_polygon(
                    x - 55 + tier * 8, top + 48,
                    x, top - 30,
                    x + 55 - tier * 8, top + 48,
                    fill=("#285947", "#326b4f", "#397655")[tier],
                    outline="",
                )

    def draw_desert_details(self) -> None:
        start = int(self.camera_x // 360) * 360
        for world_x in range(start - 360, int(self.camera_x + WIDTH) + 360, 360):
            x = world_x - self.camera_x
            self.canvas.create_oval(
                x - 38, GROUND_Y - 45, x + 44, GROUND_Y + 4,
                fill="#b88958", outline="",
            )
            self.canvas.create_polygon(
                x - 28, GROUND_Y - 24, x + 4, GROUND_Y - 93,
                x + 28, GROUND_Y - 20,
                fill="#d6b47d", outline="",
            )

    def draw_keep_details(self) -> None:
        start = int(self.camera_x // 390) * 390
        for world_x in range(start - 390, int(self.camera_x + WIDTH) + 390, 390):
            x = world_x - self.camera_x
            self.canvas.create_rectangle(
                x - 31, GROUND_Y - 145, x + 31, GROUND_Y,
                fill="#667c94", outline="#b6c7d2", width=2,
            )
            self.canvas.create_polygon(
                x - 47, GROUND_Y - 145, x, GROUND_Y - 205,
                x + 47, GROUND_Y - 145,
                fill="#879daf", outline="#c3d0d9", width=2,
            )
            self.canvas.create_line(x, GROUND_Y - 136, x, GROUND_Y - 35,
                                   fill="#c6e1ec", width=3)

    def draw_hud(self) -> None:
        canvas = self.canvas
        canvas.create_text(38, 22, text="HERO", fill="white",
                           font=("TkDefaultFont", 11, "bold"), anchor="w")
        canvas.create_text(WIDTH - 38, 22, text=self.level.boss.upper(),
                           fill="white", font=("TkDefaultFont", 11, "bold"),
                           anchor="e")
        self.draw_bar(38, 34, 330, 18, self.player.health / self.player.max_health,
                      "#e8564f")
        self.draw_bar(WIDTH - 38, 34, WIDTH - 330, 18,
                      self.boss.health / self.boss.max_health, "#e8564f")
        self.draw_bar(38, 59, 245, 9, self.player.chakra / 100, "#54c8e9")

        title = f"LEVEL {self.level_index + 1}/{len(LEVELS)}  •  {self.level.name}"
        canvas.create_text(WIDTH / 2, 26, text=title, fill="#fff0ba",
                           font=("TkDefaultFont", 12, "bold"))
        canvas.create_text(
            WIDTH / 2, 54,
            text="A/D MOVE     SPACE JUMP     J STRIKE     K ENERGY WAVE",
            fill="#f2f5f5", font=("TkDefaultFont", 9, "bold"),
        )
        power_names = ", ".join(power.split(":")[0] for power in self.powers)
        canvas.create_text(
            WIDTH / 2, 74,
            text=f"POWERS: {power_names or 'none yet'}",
            fill="#c8efff", font=("TkDefaultFont", 9),
        )

    def draw_bar(self, x1: int, y1: int, x2: int, height: int,
                 fraction: float, tint: str) -> None:
        left, right = min(x1, x2), max(x1, x2)
        self.canvas.create_rectangle(left, y1, right, y1 + height,
                                     fill="#293442", outline="#d8e1e8")
        filled = (right - left) * max(0, min(1, fraction))
        if x1 <= x2:
            self.canvas.create_rectangle(left, y1, left + filled, y1 + height,
                                         fill=tint, outline="")
        else:
            self.canvas.create_rectangle(right - filled, y1, right, y1 + height,
                                         fill=tint, outline="")

    def draw_fighter(self, fighter: Fighter, label: str, hero: bool) -> None:
        x = fighter.x - self.camera_x
        if not -80 <= x <= WIDTH + 80:
            return
        y = fighter.y
        direction = fighter.facing
        tint = "#fff0d4" if fighter.hurt_time > 0 else fighter.color
        canvas = self.canvas
        trim = "#ffd166" if hero else "#72e8d0"
        dark = "#222b3b"
        skin = "#f2c6a4"
        airborne = y < GROUND_Y - FIGHTER_HEIGHT - 2
        moving = abs(fighter.velocity_x) > 18
        running = moving and not airborne and fighter.attack_time <= 0
        phase = self.elapsed * (15 if hero else 11)
        stride = 10 * math.sin(phase) if running else 0
        hop = math.sin(self.elapsed * 3.2) * 1.5 if not moving and not airborne else 0
        lean = max(-5, min(5, fighter.velocity_x / 60))
        body_x = x + lean
        body_y = y + (3 if airborne and fighter.velocity_y < 0 else 0) + hop
        head_y = body_y + (20 if airborne else 22)
        outline = "#111a28"

        height_above_ground = max(0, GROUND_Y - FIGHTER_HEIGHT - y)
        shadow_scale = max(0.35, 1 - height_above_ground / 300)
        canvas.create_oval(
            x - 27 * shadow_scale, GROUND_Y - 7 - 5 * shadow_scale,
            x + 27 * shadow_scale, GROUND_Y - 7 + 5 * shadow_scale,
            fill="#1c2d2b", outline="",
        )

        if airborne:
            for trail in range(3):
                trail_x = body_x - direction * (25 + trail * 11)
                canvas.create_line(
                    trail_x, body_y + 47 + trail * 8,
                    trail_x - direction * 12, body_y + 55 + trail * 8,
                    fill=("#f9d77e", "#f3b95d", "#e99452")[trail],
                    width=3 - trail,
                )

        canvas.create_polygon(
            body_x - 17, body_y + 60,
            body_x + 17, body_y + 60,
            body_x + 18 + stride * 0.25, body_y + (81 if airborne else 72),
            body_x + 4 + stride * 0.25, body_y + (77 if airborne else 83),
            body_x - 5 - stride * 0.25, body_y + (84 if airborne else 78),
            body_x - 19 - stride * 0.25, body_y + (76 if airborne else 72),
            fill=dark, outline=outline, width=2,
        )
        for leg_x, swing, side in (
            (body_x - 9, stride, -1),
            (body_x + 9, -stride, 1),
        ):
            hip_y = body_y + 69
            knee_x = leg_x + swing * 0.55 + (side * 5 if airborne else 0)
            knee_y = body_y + (83 if airborne else 86)
            foot_x = knee_x + swing * 0.45 + (direction * 7 if airborne else direction * 2)
            foot_y = body_y + (70 if airborne else 98)
            canvas.create_line(leg_x, hip_y, knee_x, knee_y,
                               fill=dark, width=12, capstyle=tk.ROUND)
            canvas.create_line(knee_x, knee_y, foot_x, foot_y,
                               fill="#394052", width=10, capstyle=tk.ROUND)
            canvas.create_line(foot_x - 2, foot_y, foot_x + direction * 13, foot_y,
                               fill=trim, width=7, capstyle=tk.ROUND)
            canvas.create_oval(knee_x - 4, knee_y - 4, knee_x + 4, knee_y + 4,
                               fill="#596072", outline="")

        canvas.create_polygon(
            body_x - 19, body_y + 35,
            body_x - 15, body_y + 31,
            body_x + 14, body_y + 31,
            body_x + 21, body_y + 61,
            body_x + 8, body_y + 72,
            body_x, body_y + 66,
            body_x - 11, body_y + 72,
            body_x - 23, body_y + 60,
            fill=tint, outline=outline, width=2,
        )
        canvas.create_polygon(
            body_x - 15, body_y + 39,
            body_x + 13, body_y + 39,
            body_x + 17, body_y + 59,
            body_x, body_y + 66,
            body_x - 18, body_y + 58,
            fill="", outline="#ffffff", width=1,
        )
        canvas.create_rectangle(body_x - 20, body_y + 56, body_x + 20, body_y + 64,
                                fill=dark, outline="")
        canvas.create_line(body_x - 19, body_y + 59, body_x + 19, body_y + 59,
                           fill=trim, width=4)
        canvas.create_oval(body_x - 3, body_y + 57, body_x + 4, body_y + 65,
                           fill="#f3d28b", outline=outline)

        # Long headband tails and scarf react to movement and leap direction.
        flutter = math.sin(self.elapsed * 12) * (4 if moving or airborne else 1.5)
        tail_x = body_x - direction * 18
        canvas.create_polygon(
            tail_x, body_y + 13,
            tail_x - direction * 32, body_y + 5 + flutter,
            tail_x - direction * 27, body_y + 18 + flutter,
            fill=trim, outline=outline, width=1,
        )
        canvas.create_polygon(
            body_x - direction * 14, body_y + 36,
            body_x - direction * (35 + abs(fighter.velocity_x) * 0.035),
            body_y + 29 + flutter,
            body_x - direction * 29, body_y + 44 + flutter,
            fill="#f2f0df", outline=outline, width=1,
        )

        back_shoulder = (body_x - direction * 12, body_y + 43)
        back_elbow = (body_x - direction * 22 - stride * 0.35, body_y + 57)
        back_hand = (body_x - direction * 16 - stride * 0.5, body_y + 52)
        canvas.create_line(*back_shoulder, *back_elbow, *back_hand,
                           fill=dark, width=9, capstyle=tk.ROUND, joinstyle=tk.ROUND)
        canvas.create_oval(back_hand[0] - 5, back_hand[1] - 5,
                           back_hand[0] + 5, back_hand[1] + 5,
                           fill=skin, outline=outline)

        head_width = 17
        canvas.create_oval(body_x - head_width, head_y - 19,
                           body_x + head_width, head_y + 19,
                           fill=skin, outline=outline, width=2)
        canvas.create_polygon(
            body_x - 18, head_y - 7,
            body_x - 20, head_y - 17,
            body_x - 8, head_y - 15,
            body_x - 8, head_y - 24,
            body_x + 1, head_y - 18,
            body_x + 10, head_y - 25,
            body_x + 12, head_y - 17,
            body_x + 21, head_y - 14,
            body_x + 15, head_y - 3,
            body_x + 5, head_y - 8,
            body_x - 4, head_y - 4,
            fill="#20283a", outline=outline, width=1,
        )
        canvas.create_polygon(
            body_x - 13, head_y - 11,
            body_x - 2, head_y - 17,
            body_x + 13, head_y - 11,
            body_x + 17, head_y - 3,
            body_x - 9, head_y - 5,
            fill="#303b54", outline="",
        )
        band_y = head_y - 2
        canvas.create_line(body_x - 16, band_y, body_x + 15, band_y - 1,
                           fill=trim, width=5)
        canvas.create_rectangle(body_x - 4, band_y - 4, body_x + 8, band_y + 3,
                                fill="#e0e4df", outline=outline)
        canvas.create_line(body_x - 1, band_y, body_x + 5, band_y,
                           fill="#576475", width=1)
        near_eye_x = body_x + direction * 9
        far_eye_x = body_x - direction * 1
        eye_y = head_y + 5
        canvas.create_line(near_eye_x - 4, eye_y - 5, near_eye_x + 4, eye_y - 7,
                           fill=outline, width=2)
        canvas.create_oval(near_eye_x - 3, eye_y - 2, near_eye_x + 3, eye_y + 4,
                           fill="#fff9e9", outline=outline)
        canvas.create_oval(near_eye_x, eye_y - 1, near_eye_x + direction * 2,
                           eye_y + 3, fill="#27334c", outline="")
        canvas.create_line(body_x - 2, eye_y - 3, body_x + 3, eye_y - 4,
                           fill="#624b4b", width=1)
        canvas.create_line(body_x + direction * 10, head_y + 12,
                           body_x + direction * 14, head_y + 11,
                           fill="#bd796f", width=1)

        shoulder_x = body_x + direction * 13
        shoulder_y = body_y + 42
        if fighter.attack_time > 0:
            elbow_x = body_x + direction * 32
            elbow_y = body_y + 43
            hand_x = body_x + direction * 65
            hand_y = body_y + 42 + math.sin(fighter.attack_time * 25) * 2
        elif airborne:
            elbow_x = body_x + direction * 27
            elbow_y = body_y + 28
            hand_x = body_x + direction * 37
            hand_y = body_y + 18
        else:
            elbow_x = body_x + direction * (23 + stride * 0.35)
            elbow_y = body_y + 51 - stride * 0.18
            hand_x = body_x + direction * (29 + stride * 0.5)
            hand_y = body_y + 48 - stride * 0.25
        canvas.create_line(shoulder_x, shoulder_y, elbow_x, elbow_y,
                           hand_x, hand_y, fill=tint, width=11,
                           capstyle=tk.ROUND, joinstyle=tk.ROUND)
        canvas.create_line(shoulder_x, shoulder_y, elbow_x, elbow_y,
                           fill="#ffffff", width=2, capstyle=tk.ROUND)
        canvas.create_oval(hand_x - 7, hand_y - 7, hand_x + 7, hand_y + 7,
                           fill=skin, outline=outline, width=1)
        canvas.create_text(x, y - 16, text=label, fill="#fffdf5",
                           font=("TkDefaultFont", 9, "bold"),
                           stipple="gray50")
        canvas.create_text(x, y - 17, text=label, fill="white",
                           font=("TkDefaultFont", 9, "bold"))

    def draw_wave(self, wave: EnergyWave) -> None:
        x = wave.x - self.camera_x
        tint = "#69e4ff" if wave.owner == "player" else "#bf8aff"
        self.canvas.create_oval(x - 18, wave.y - 18, x + 18, wave.y + 18,
                                fill=tint, outline="#f8ffff", width=2)
        self.canvas.create_oval(x - 9, wave.y - 9, x + 9, wave.y + 9,
                                fill="#ffffff", outline="")

    def draw_announcement(self) -> None:
        self.canvas.create_rectangle(210, 208, WIDTH - 210, 290,
                                     fill="#172235", outline="#f4d38d", width=2)
        self.canvas.create_text(
            WIDTH / 2, 235,
            text=f"LEVEL {self.level_index + 1}: {self.level.name}",
            fill="#f4d38d", font=("TkDefaultFont", 17, "bold"),
        )
        if self.powers:
            self.canvas.create_text(
                WIDTH / 2, 264, text=f"POWER EARNED: {self.powers[-1]}",
                fill="white", font=("TkDefaultFont", 10),
            )

    def draw_game_over(self) -> None:
        canvas = self.canvas
        canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#111a29",
                                stipple="gray50", outline="")
        message = "CAMPAIGN COMPLETE!" if self.victory else "DEFEAT!"
        subtext = "All bosses defeated! Press R to play again" if self.victory else "Press R to retry"
        canvas.create_text(WIDTH / 2, HEIGHT / 2 - 25, text=message,
                           fill="#f5d28b", font=("TkDefaultFont", 34, "bold"))
        canvas.create_text(WIDTH / 2, HEIGHT / 2 + 27, text=subtext,
                           fill="white", font=("TkDefaultFont", 15))


def main() -> None:
    root = tk.Tk()
    NinjaCampaign(root)
    root.mainloop()


if __name__ == "__main__":
    main()
