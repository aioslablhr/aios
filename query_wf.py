"""Query and update workflow_configurations for Ext 105 and 102."""
import json, asyncio, sys
sys.path.insert(0, '/app/api')
from api.db.database import get_async_session
from api.db.models import WorkflowDefinitionModel
from sqlalchemy import select

async def main():
    async with get_async_session() as session:
        result = await session.execute(
            select(WorkflowDefinitionModel).where(WorkflowDefinitionModel.id.in_([1, 3]))
        )
        for wf in result.scalars().all():
            cfg = wf.workflow_configurations or {}
            print(f"ID: {wf.id}, Name: {wf.name}")
            print(f"  Company: {cfg.get('company', 'NOT SET')}")
            sp = cfg.get('system_prompt', '')
            print(f"  System prompt ({len(sp)} chars): {sp[:300]}...")
            print(f"  Keys: {list(cfg.keys())}")
            print()

if __name__ == '__main__':
    asyncio.run(main())
