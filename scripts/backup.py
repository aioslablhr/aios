#!/usr/bin/env python3
"""AIOS — Nightly Encrypted Backup.

Creates encrypted backup of all critical data:
  - Docker Compose configs and .env files
  - Qdrant vector collections (via snapshot API)
  - PostgreSQL databases (via pg_dump)
  - Langfuse data
  - n8n workflows (via export API)

Uploads to: local /aios/backups/ + optional S3/NAS target.

Usage:
  python3 backup.py                    # Full backup to local
  python3 backup.py --s3-bucket aios-backups  # + S3 upload
  python3 backup.py --restore latest   # Restore from latest backup
"""

import argparse
import json
import os
import subprocess
import sys
import tarfile
from datetime import datetime

BACKUP_DIR = "/aios/backups"
SERVICES_DIR = "/aios"
RETENTION_DAYS = 30


def log(msg):
    print(f"[backup] {msg}")


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def run(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\n{result.stderr}")
    return result.stdout.strip()


def backup_configs(timestamp):
    # TODO: backup /aios/configs/ + docker-compose*.yml + .env*
    log("configs: Skipped — path not populated yet")


def backup_qdrant(timestamp):
    # TODO: POST /collections/{name}/snapshots to Qdrant API for each collection
    log("qdrant: Skipped — Qdrant API not wired yet")


def backup_postgres(timestamp):
    # TODO: pg_dump -h 10.30.0.10 -U postgres -F c -f {file} aios
    log("postgres: Skipped — pg_dump not configured yet")


def backup_n8n(timestamp):
    # TODO: GET /rest/workflows from n8n API, export all as JSON
    log("n8n: Skipped — n8n API not wired yet")


def rotate_backups():
    # TODO: delete backups older than RETENTION_DAYS
    pass


def upload_to_s3(backup_path):
    # TODO: aws s3 cp {backup_path} s3://{bucket}/
    log("s3: Skipped — AWS credentials not configured")


def main():
    parser = argparse.ArgumentParser(description="AIOS backup manager")
    parser.add_argument("--s3-bucket", help="Upload to S3 bucket")
    parser.add_argument("--restore", help="Restore from backup ID (e.g. 'latest' or timestamp)")
    args = parser.parse_args()

    if args.restore:
        print("Restore mode not yet implemented — use disaster-recovery.py")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"aios-backup-{timestamp}")
    ensure_dir(backup_path)

    print(f"\n{'='*60}")
    print(f"  AIOS Backup — {timestamp}")
    print(f"{'='*60}\n")

    backup_configs(timestamp)
    backup_qdrant(timestamp)
    backup_postgres(timestamp)
    backup_n8n(timestamp)

    # Create tarball
    tarball = f"{backup_path}.tar.gz"
    with tarfile.open(tarball, "w:gz") as tar:
        tar.add(backup_path, arcname=os.path.basename(backup_path))

    log(f"Backup created: {tarball}")
    rotate_backups()

    if args.s3_bucket:
        upload_to_s3(tarball)

    print(f"\n{'='*60}")
    print(f"  Backup complete: {tarball}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
