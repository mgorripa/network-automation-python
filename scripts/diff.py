#!/usr/bin/env python3
"""Unified diff plus the exact delta lines that would be applied."""

import pathlib
import sys
import difflib
from colorama import Fore, Style, init
from common import load_inventory, connect, OUT_DIR

init()

def main():
    devices = load_inventory()
    any_changes = False

    for name, v in devices.items():
        intended_p = OUT_DIR / f"{name}.set"
        if not intended_p.exists():
            print(f"[{name}] No generated config in {intended_p}. Run deploy_async.py --generate-only.")
            continue

        intended = [l.rstrip("\n") for l in intended_p.read_text().splitlines()]
        conn = connect(v["host"])
        try:
            running_txt = conn.send_command("show configuration commands", use_textfsm=False)
        finally:
            conn.disconnect()
        running = [l.rstrip("\n") for l in running_txt.splitlines()]

        diff = list(difflib.unified_diff(running, intended, fromfile="running", tofile="intended", lineterm=""))
        print(f"\n=== {name} ===")
        if not diff:
            print("No differences.")
            continue

        any_changes = True
        for line in diff:
            if line.startswith("+") and not line.startswith("+++"):
                print(Fore.GREEN + line + Style.RESET_ALL)
            elif line.startswith("-") and not line.startswith("---"):
                print(Fore.RED + line + Style.RESET_ALL)
            else:
                print(line)

        # Show delta that would be pushed
        running_set = set(running)
        delta = [l for l in intended if l and not l.startswith("#") and l not in running_set]
        if delta:
            print("\nDelta to apply (set-lines not present on device):")
            for l in delta:
                print(Fore.GREEN + f"+ {l}" + Style.RESET_ALL)
    return 0 if not any_changes else 1

if __name__ == "__main__":
    sys.exit(main())
