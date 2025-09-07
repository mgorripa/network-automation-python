#!/usr/bin/env python3
"""
backup.py
---------
Take pre-change backups of each device's running configuration.
Saves output of `show configuration commands` into the backups/ folder.

I run this before any deployment so I always have a known-good config
I can roll back to if needed.
"""

import sys
from datetime import datetime
from common import load_inventory, connect, BACKUP_DIR


def backup_device(name: str, host: str) -> str:
    conn = connect(host)
    try:
        output = conn.send_command("show configuration commands", use_textfsm=False)
        stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        filename = BACKUP_DIR / f"{name}.{stamp}.show"
        filename.write_text(output)
        return str(filename)
    finally:
        conn.disconnect()


def main():
    devices = load_inventory()
    for name, vars in devices.items():
        host = vars["host"]
        try:
            path = backup_device(name, host)
            print(f"[{name}] backup saved to {path}")
        except Exception as e:
            print(f"[{name}] backup failed: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
