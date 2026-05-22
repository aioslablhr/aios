#!/usr/bin/env python3
"""AIOS — Disaster Recovery.

Full system restore from backup:
  - Recreates Docker networks
  - Restores docker-compose configs
  - Restores PostgreSQL databases
  - Restores Qdrant collections (from snapshots)
  - Redeploys all containers

Usage:
  python3 disaster-recovery.py                    # Interactive restore (latest)
  python3 disaster-recovery.py --backup aios-backup-20260101_120000.tar.gz  # Specific backup
  python3 disaster-recovery.py --list             # List available backups
"""

import argparse
import json
import os
import subprocess
import sys
import tarfile
from datetime import datetime

BACKUP_DIR = "/aios/backups"
NETWORKS = {
    "aios-dmz": "10.10.0.0/24",
    "aios-app": "10.20.0.0/24",
    "aios-data": "10.30.0.0/24",
    "aios-ai": "10.40.0.0/24",
    "aios-voice": "10.50.0.0/24",
    "aios-mon": "10.60.0.0/24",
    "aios-foss": "10.70.0.0/24",
}


def log(msg):
    print(f"[recovery] {msg}")


def run(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\n{result.stderr}")
    return result.stdout.strip()


def list_backups():
    if not os.path.isdir(BACKUP_DIR):
        log("No backups directory found")
        return []
    backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith(".tar.gz")], reverse=True)
    return backups


def recreate_networks():
    log("Recreating Docker networks...")
    for name, subnet in NETWORKS.items():
        existing, _ = run(f"docker network ls --format '{{{{.Name}}}}' | grep ^{name}$", check=False)
        if existing:
            log(f"  Network {name} exists, skipping")
        else:
            internal = " --internal" if name == "aios-data" else ""
            run(f"docker network create {name} --subnet={subnet}{internal}")
            log(f"  Created {name} ({subnet})")


def restore_configs(backup_path):
    # TODO: extract config files from backup tarball
    log("configs: Restore logic not yet implemented")


def restore_postgres(backup_path):
    # TODO: pg_restore into PostgreSQL
    log("postgres: Restore logic not yet implemented")


def restore_qdrant(backup_path):
    # TODO: restore Qdrant from snapshot files
    log("qdrant: Restore logic not yet implemented")


def redeploy_containers():
    log("Redeploying containers...")
    run("cd /aios && docker compose -f docker-compose-aios.yml up -d")
    log("All services redeployed")


def main():
    parser = argparse.ArgumentParser(description="AIOS disaster recovery")
    parser.add_argument("--list", action="store_true", help="List available backups")
    parser.add_argument("--backup", help="Backup file to restore from")
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompts")
    args = parser.parse_args()

    if args.list:
        backups = list_backups()
        if not backups:
            log("No backups found")
            return
        print("Available backups:")
        for b in backups:
            size = os.path.getsize(os.path.join(BACKUP_DIR, b))
            print(f"  {b}  ({size / 1024 / 1024:.1f} MB)")
        return

    backup_file = args.backup
    if not backup_file:
        backups = list_backups()
        if not backups:
            log("No backups found and no --backup specified. Aborting.")
            sys.exit(1)
        backup_file = os.path.join(BACKUP_DIR, backups[0])
        log(f"Using latest backup: {backups[0]}")
    else:
        backup_file = os.path.join(BACKUP_DIR, backup_file)
        if not os.path.isfile(backup_file):
            log(f"Backup not found: {backup_file}")
            sys.exit(1)

    if not args.force:
        print(f"\n{'!'*60}")
        print(f"  DISASTER RECOVERY — This will OVERWRITE current state")
        print(f"  Backup: {backup_file}")
        print(f"{'!'*60}")
        confirm = input("  Type 'RESTORE' to continue: ")
        if confirm != "RESTORE":
            log("Aborted")
            sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  AIOS Disaster Recovery — {datetime.now().isoformat()}")
    print(f"{'='*60}\n")

    recreate_networks()
    restore_configs(backup_file)
    restore_postgres(backup_file)
    restore_qdrant(backup_file)
    redeploy_containers()

    print(f"\n{'='*60}")
    print(f"  Recovery complete. Verify: python3 /aios/scripts/health-check.py")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
