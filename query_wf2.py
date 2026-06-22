"""Query workflow_configurations for Ext 105 and 102."""
import json, asyncio, sys, os
sys.path.insert(0, '/app/api')
os.environ['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'postgresql+asyncpg://aios:aios_secret_2026@10.30.0.10:5432/dograh')

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(os.environ['DATABASE_URL'])

async def main():
    async with AsyncSession(engine) as session:
        result = await session.execute(
            text("SELECT id, name, workflow_configurations FROM workflow_definitions WHERE id IN (1, 3)")
        )
        for row in result.fetchall():
            wf_id, name, cfg_json = row
            cfg = cfg_json or {}
            print(f"ID: {wf_id}, Name: {name}")
            print(f"  Company: {cfg.get('company', 'NOT SET')}")
            sp = cfg.get('system_prompt', '')
            print(f"  System prompt ({len(sp)} chars): {sp[:200]}...")
            print(f"  Keys: {list(cfg.keys())}")
            print()

if __name__ == '__main__':
    asyncio.run(main())
