#!/usr/bin/env python3
"""AIOS — New Client Onboarding Automation.

Creates all per-client resources across the stack:
  Keycloak org, Qdrant collection, Supabase schema,
  Bifrost virtual key, Langfuse project, n8n workflow.

Usage:
  python3 new-client.py \\
    --client-id clinic-abc \\
    --industry clinic \\
    --language urdu \\
    --model qwen-2.5-7b \\
    --budget 50 \\
    --agent-name Sarah \\
    --whatsapp +923001234567
"""

import argparse
import json
import os
import sys
from datetime import datetime

SERVICES = {
    "keycloak": {"host": "10.20.0.40", "port": 8080},
    "qdrant": {"host": "10.30.0.20", "port": 6333},
    "supabase": {"host": "10.30.0.10", "port": 8000},
    "bifrost": {"host": "10.40.0.10", "port": 4000},
    "langfuse": {"host": "10.60.0.10", "port": 3000},
    "n8n": {"host": "10.20.0.10", "port": 5678},
}


def log(step, msg):
    print(f"[{step:>12}] {msg}")


def run_step(name, fn, *args):
    log(name, f"Starting...")
    try:
        fn(*args)
        log(name, "OK")
    except Exception as e:
        log(name, f"FAILED — {e}")
        sys.exit(1)


def create_keycloak_org(client_id):
    # TODO: POST to Keycloak Admin API
    # POST /admin/realms/aios/organizations
    # Body: {"name": client_id, "displayName": f"Client {client_id}"}
    log("keycloak", f"Skipped — Keycloak admin API not wired yet")


def create_qdrant_collection(client_id):
    # TODO: PUT to Qdrant REST API
    # PUT /collections/{client_id}-knowledge
    # Body: {"vectors": {"size": 1536, "distance": "Cosine"}}
    log("qdrant", f"Skipped — Qdrant API not wired yet")


def create_supabase_schema(client_id):
    # TODO: Execute via Supabase management SQL endpoint
    # CREATE SCHEMA IF NOT EXISTS {client_id};
    # ALTER SCHEMA {client_id} OWNER TO postgres;
    log("supabase", f"Skipped — Supabase API not wired yet")


def create_bifrost_key(client_id, model, budget):
    # TODO: POST to Bifrost admin API
    # POST /api/keys
    # Body: {"name": client_id, "model": model, "monthly_budget": budget}
    log("bifrost", f"Skipped — Bifrost API not wired yet")


def create_langfuse_project(client_id):
    # TODO: POST to Langfuse management API
    # POST /api/public/projects
    # Body: {"name": client_id}
    log("langfuse", f"Skipped — Langfuse API not wired yet")


def clone_n8n_workflow(client_id, industry, agent_name, whatsapp):
    # TODO: POST to n8n REST API
    # POST /rest/workflows
    # Body: template JSON with client_id injected as variables
    log("n8n", f"Skipped — n8n API not wired yet")


def main():
    parser = argparse.ArgumentParser(description="Onboard a new AIOS client")
    parser.add_argument("--client-id", required=True, help="Unique client identifier")
    parser.add_argument("--industry", default="general", help="Industry template")
    parser.add_argument("--language", default="en", help="Primary language")
    parser.add_argument("--model", default="qwen-2.5-7b", help="Default LLM model")
    parser.add_argument("--budget", type=int, default=50, help="Monthly budget (USD)")
    parser.add_argument("--agent-name", default="AI Agent", help="Agent display name")
    parser.add_argument("--whatsapp", help="Client WhatsApp number")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  AIOS Client Onboarding — {args.client_id}")
    print(f"  Industry: {args.industry} | Lang: {args.language} | Model: {args.model}")
    print(f"{'='*60}\n")

    run_step("Keycloak org", create_keycloak_org, args.client_id)
    run_step("Qdrant coll.", create_qdrant_collection, args.client_id)
    run_step("Supabase sch.", create_supabase_schema, args.client_id)
    run_step("Bifrost key", create_bifrost_key, args.client_id, args.model, args.budget)
    run_step("Langfuse proj", create_langfuse_project, args.client_id)
    run_step("n8n workflow", clone_n8n_workflow, args.client_id, args.industry, args.agent_name, args.whatsapp)

    print(f"\n{'='*60}")
    print(f"  Client {args.client_id} onboarded successfully")
    print(f"  Next: configure prompts in Langfuse + upload knowledge docs")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
