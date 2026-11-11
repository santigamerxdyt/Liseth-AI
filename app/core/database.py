"""
Database connection and session management for JARVIS / Liseth.
Uses SQLite with aiosqlite and WAL mode for high performance.
"""
from typing import AsyncGenerator
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.config import settings
from app.core.models import Base

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False, "timeout": 15.0} if "sqlite" in settings.DATABASE_URL else {},
)

if "sqlite" in settings.DATABASE_URL:
    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragmas(dbapi_conn, connection_record) -> None:
        """Guarantees high-performance & safe SQLite PRAGMAs on every pooled connection."""
        cursor = dbapi_conn.cursor()
        try:
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
            cursor.execute("PRAGMA busy_timeout=5000;")
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.execute("PRAGMA temp_store=MEMORY;")
            cursor.execute("PRAGMA cache_size=-32000;")
        finally:
            cursor.close()

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

_PERFORMANCE_INDEX_DDL = (
    "CREATE INDEX IF NOT EXISTS idx_chat_messages_session_ts ON chat_messages (session_id, timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_audit_entries_status_ts ON audit_entries (status, timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_saas_conv_user_archived_upd ON saas_conversations (user_id, is_archived, updated_at);",
    "CREATE INDEX IF NOT EXISTS idx_saas_msg_conv_created ON saas_messages (conversation_id, created_at);",
    "CREATE INDEX IF NOT EXISTS idx_saas_usage_user_created ON saas_usage_records (user_id, created_at);",
    "CREATE INDEX IF NOT EXISTS idx_saas_audit_created ON saas_audit_logs (created_at);",
    "CREATE INDEX IF NOT EXISTS idx_saas_invoices_user_issued ON saas_invoices (user_id, issued_at);",
    "CREATE INDEX IF NOT EXISTS idx_saas_payments_user_created ON saas_payments (user_id, created_at);",
    "CREATE INDEX IF NOT EXISTS idx_ref_rel_referrer_status ON referral_relationships (referrer_user_id, status);",
    "CREATE INDEX IF NOT EXISTS idx_ref_rewards_user_status_prio ON referral_rewards (user_id, status, priority_order, created_at);",
    "CREATE INDEX IF NOT EXISTS idx_ref_coupons_user_status ON referral_coupons (user_id, status, priority_order, created_at);",
    "CREATE INDEX IF NOT EXISTS idx_nfc_tags_uid_status ON nfc_registered_tags (uid, status);",
    "CREATE INDEX IF NOT EXISTS idx_nfc_tags_owner_cat ON nfc_registered_tags (owner_user_id, category);",
    "CREATE INDEX IF NOT EXISTS idx_nfc_dynlinks_code_active ON nfc_dynamic_links (short_code, is_active);",
    "CREATE INDEX IF NOT EXISTS idx_nfc_filetrans_token ON nfc_file_transfers (access_token, status);",
    "CREATE INDEX IF NOT EXISTS idx_nfc_audit_tag_event ON nfc_audit_logs (tag_id, event_type, created_at);",
    "CREATE INDEX IF NOT EXISTS idx_ai_tokopt_user_created ON ai_token_optimization_logs (user_id, created_at);",
)


async def init_db() -> None:
    """
    Initializes database tables, enables SQLite WAL mode, and ensures composite performance indexes.
    """
    async with engine.begin() as conn:
        # Enable WAL mode for SQLite
        if "sqlite" in settings.DATABASE_URL:
            await conn.exec_driver_sql("PRAGMA journal_mode=WAL;")
            await conn.exec_driver_sql("PRAGMA synchronous=NORMAL;")
            await conn.exec_driver_sql("PRAGMA busy_timeout=5000;")
        # Create all tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)
        if "sqlite" in settings.DATABASE_URL:
            for ddl in _PERFORMANCE_INDEX_DDL:
                await conn.exec_driver_sql(ddl)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency yielding an async database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
