#!/usr/bin/env python3
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Folders relative to repo root
ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
BACKUP_DIR = ROOT / "backups"

load_dotenv(ROOT / ".env")
log_days = int(os.getenv("LOG_RETENTION_DAYS", "14"))
bkp_days = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))

def purge_older_than(folder: Path, days: int):
    if not folder.exists():
        return 0
    cutoff = datetime.now() - timedelta(days=days)
    removed = 0
    for p in folder.iterdir():
        try:
            mtime = datetime.fromtimestamp(p.stat().st_mtime)
            if mtime < cutoff:
                p.unlink()
                removed += 1
        except Exception:
            pass
    return removed

def main():
    rl = purge_older_than(LOG_DIR, log_days)
    rb = purge_older_than(BACKUP_DIR, bkp_days)
    print(f"Purged {rl} log files (> {log_days}d) and {rb} backups (> {bkp_days}d).")

if __name__ == "__main__":
    main()
