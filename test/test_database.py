"""
Unit tests for app.core.database and migrator.
"""
import asyncio
import pytest
from sqlalchemy import select
from app.core.database import AsyncSessionLocal, init_db
from app.core.migrator import run_migration_if_needed
from app.core.models import (
    AppSetting,
    AuditEntry,
    ChatMessage,
    ScheduledTask,
    TokenUsage,
    UploadedFile,
    UserProfile,
)


def test_database_init_and_crud():
    async def _run():
        await init_db()

        async with AsyncSessionLocal() as session:
            # Create user profile
            user = UserProfile(
                id=999,
                name="Santiago Test",
                nickname="Santi",
                memory_facts=["Le gusta la IA", "Trabaja en desarrollo"],
            )
            session.add(user)
            await session.commit()

            # Read
            fetched = await session.get(UserProfile, 999)
            assert fetched is not None
            assert fetched.name == "Santiago Test"
            assert len(fetched.memory_facts) == 2

            # Create message
            msg = ChatMessage(
                session_id="test_session",
                role="user",
                parts=[{"text": "Hola Liseth"}],
            )
            session.add(msg)
            await session.commit()

            # Query messages
            res = await session.execute(
                select(ChatMessage).where(ChatMessage.session_id == "test_session")
            )
            messages = res.scalars().all()
            assert len(messages) >= 1
            assert messages[0].parts[0]["text"] == "Hola Liseth"

            # Cleanup
            await session.delete(fetched)
            await session.delete(msg)
            await session.commit()

    asyncio.run(_run())


def test_migration_from_json():
    async def _run():
        stats = await run_migration_if_needed()
        assert isinstance(stats, dict)
        assert "migrated" in stats

        async with AsyncSessionLocal() as session:
            # Verify user profile was populated
            user = await session.get(UserProfile, 1)
            assert user is not None
            assert user.name is not None

            # Verify chat messages exist
            res = await session.execute(select(ChatMessage))
            msgs = res.scalars().all()
            assert len(msgs) > 0

            # Verify token usage exists
            tu = await session.get(TokenUsage, 1)
            assert tu is not None

    asyncio.run(_run())
