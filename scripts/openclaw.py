#!/usr/bin/env python3
"""OpenClaw — AIOS Lab Assistant.

CLI tool for managing the AIOS lab from your Dev PC.
All commands SSH into the server and return results.

Usage:
  openclaw                → Interactive menu mode
  openclaw status         → Health report
  openclaw ps             → Docker container list
  openclaw logs <service> → Docker logs
  openclaw deploy         → git add + commit + push
  openclaw backup         → Run backup
  openclaw vault init     → Initialize Vault
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime

SERVER = os.environ.get("AIOS_SERVER", "ai@10.0.0.100")
SSH_OPTS = "-o StrictHostKeyChecking=no -o BatchMode=yes"


def ssh(cmd):
    full = f'ssh {SSH_OPTS} {SERVER} "{cmd}"'
    result = subprocess.run(full, shell=True, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        print(f"Error: {result.stderr.strip()}")
    return result.stdout.strip()


def cmd_status():
    print("\n" + "=" * 60)
    print("  AIOS LAB — System Health")
    print("=" * 60 + "\n")
    print(ssh("python3 /aios/scripts/health-check.py --brief"))
    print()


def cmd_ps():
    print("\n" + "=" * 60)
    print("  AIOS LAB — Running Containers")
    print("=" * 60 + "\n")
    out = ssh("docker ps --format 'table {{.Names}}\t{{.Status}}'")
    print(out)
    print()


def cmd_logs(service):
    if not service:
        service = input("Service name (e.g. hermes, traefik): ").strip()
    if not service:
        return
    print(f"\n--- Logs for {service} ---\n")
    print(ssh(f"docker logs aios-{service} --tail 30 2>&1 || docker logs {service} --tail 30 2>&1"))
    print()


def cmd_deploy():
    msg = input("Commit message: ").strip() or f"update {datetime.now().isoformat()}"
    print(ssh(f"cd /aios && git add -A && git commit -m '{msg}' && git push"))
    print("\n[GitOps] Deploy triggered — check in 30s\n")


def cmd_backup():
    print(ssh("python3 /aios/scripts/backup.py"))
    print()


def cmd_vault_init():
    print("\nInitializing Vault...\n")
    print(ssh("docker exec aios-vault vault operator init 2>&1"))
    print("\nSAVE THESE UNSEAL KEYS AND ROOT TOKEN.\n")


def cmd_restart(service):
    if not service:
        service = input("Service name: ").strip()
    if not service:
        return
    print(ssh(f"docker restart aios-{service} 2>/dev/null || docker restart {service}"))
    print(f"Restarted {service}\n")


def interactive():
    while True:
        print("\n" + "=" * 60)
        print("  OpenClaw — AIOS Lab Assistant")
        print("=" * 60)
        print("  [1] Status         Health report")
        print("  [2] PS             Running containers")
        print("  [3] Logs           Show service logs")
        print("  [4] Deploy         Git push + auto-deploy")
        print("  [5] Backup         Run backup")
        print("  [6] Vault Init     Initialize HashiCorp Vault")
        print("  [7] Restart        Restart a service")
        print("  [0] Exit")
        print("=" * 60)

        choice = input("Select: ").strip()
        if choice == "1":
            cmd_status()
        elif choice == "2":
            cmd_ps()
        elif choice == "3":
            cmd_logs(None)
        elif choice == "4":
            cmd_deploy()
        elif choice == "5":
            cmd_backup()
        elif choice == "6":
            cmd_vault_init()
        elif choice == "7":
            cmd_restart(None)
        elif choice == "0":
            print("Exiting. Lab is running 24/7.\n")
            break


def main():
    parser = argparse.ArgumentParser(description="OpenClaw — AIOS Lab Assistant")
    parser.add_argument("command", nargs="?", default="menu",
                        choices=["menu", "status", "ps", "logs", "deploy",
                                 "backup", "vault", "restart"])
    parser.add_argument("arg", nargs="?", help="Additional argument (service name, etc.)")
    args = parser.parse_args()

    commands = {
        "menu": lambda: interactive(),
        "status": lambda: cmd_status(),
        "ps": lambda: cmd_ps(),
        "logs": lambda: cmd_logs(args.arg),
        "deploy": lambda: cmd_deploy(),
        "backup": lambda: cmd_backup(),
        "vault": lambda: cmd_vault_init(),
        "restart": lambda: cmd_restart(args.arg),
    }

    if args.command in commands:
        commands[args.command]()
    else:
        interactive()


if __name__ == "__main__":
    main()
