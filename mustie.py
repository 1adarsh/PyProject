"""A harmless, text-only malware behavior simulator for security learning.

This program does not modify files, access the network, change system settings,
or create persistence. It only prints a fictional sequence of events.
"""

from __future__ import annotations

import argparse
import time


EVENTS = (
    ("STARTUP", "A fictional sample starts in the current process."),
    ("DISCOVERY", "It would normally inspect its environment; nothing is inspected here."),
    ("PERSISTENCE", "A persistence attempt is represented, but no system setting is changed."),
    ("NETWORK", "A command-and-control beacon is represented; no connection is made."),
    ("PAYLOAD", "A payload action is represented; no files or data are touched."),
    ("DETECTION", "A defender flags the suspicious behavior and stops the simulation."),
)


def run_simulation(delay: float = 0.0) -> None:
    """Print fictional malware-like events without performing them."""
    print("SAFE SIMULATION ONLY — no system or network actions will be performed.")
    for label, description in EVENTS:
        print(f"[{label}] {description}")
        if delay:
            time.sleep(delay)
    print("Simulation complete.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Print a harmless, text-only sequence of fictional malware behaviors."
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="seconds to pause between events (default: 0)",
    )
    args = parser.parse_args()
    if not 0 <= args.delay <= 5:
        parser.error("--delay must be between 0 and 5 seconds")
    run_simulation(args.delay)


if __name__ == "__main__":
    main()