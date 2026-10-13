"""
JSON to SQLite Data Migrator for JARVIS / Liseth
Safely imports existing data from legacy JSON files into SQLite without any data loss.
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.database import AsyncSessionLocal, init_db
from app.core.models import (
    AppSetting,
    AuditEntry,
    ChatMessage,
    ScheduledTask,
    TokenUsage,
    UploadedFile,
    UserProfile,
)

logger = logging.getLogger("jarvis.migrator")


async def run_migration_if_needed() -> dict:
    """
    Checks for legacy JSON files in data/ and imports their records into SQLite
    if the database tables are empty.
    Returns migration statistics.
    """
    await init_db()
    stats = {
        "migrated": False,
        "user_profile": False,
        "chat_messages": 0,
        "tasks": 0,
        "audit_logs": 0,
        "token_usage": False,
        "files": 0,
        "settings": 0,
    }

    data_dir = settings.DATA_DIR
    liseth_db_path = data_dir / "liseth_db.json"
    token_usage_path = data_dir / "token_usage.json"
    scheduled_tasks_path = data_dir / "scheduled_tasks.json"
    audit_log_path = data_dir / "audit_log.json"

    async with AsyncSessionLocal() as session:
        # 1. Check & Migrate User Profile & Chat History from liseth_db.json
        if liseth_db_path.exists():
            try:
                with open(liseth_db_path, "r", encoding="utf-8") as f:
                    liseth_db = json.load(f)

                # Migrate User Profile
                user_data = liseth_db.get("user")
                if user_data:
                    existing_user = await session.get(UserProfile, 1)
                    if not existing_user:
                        user = UserProfile(
                            id=1,
                            name=user_data.get("name", "Santiago"),
                            nickname=user_data.get("nickname", "Santi"),
                            memory_facts=user_data.get("memoryFacts", []),
                            preferences=user_data.get("preferences", {}),
                        )
                        session.add(user)
                        stats["user_profile"] = True

                # Migrate Chat History
                chat_history = liseth_db.get("chat_history", [])
                if chat_history:
                    # Check if messages already exist
                    res = await session.execute(select(ChatMessage).limit(1))
                    if res.scalars().first() is None:
                        for item in chat_history:
                            msg = ChatMessage(
                                session_id="default",
                                role=item.get("role", "user"),
                                parts=item.get("parts", [{"text": ""}]),
                            )
                            session.add(msg)
                            stats["chat_messages"] += 1

                # Migrate Settings: config, google, productivity, whatsapp_module
                for setting_key in ["config", "google", "productivity", "whatsapp_module"]:
                    val = liseth_db.get(setting_key)
                    if val is not None:
                        existing = await session.get(AppSetting, setting_key)
                        if not existing:
                            session.add(AppSetting(key=setting_key, value=val))
                            stats["settings"] += 1

                # Migrate Files
                files = liseth_db.get("files", [])
                if files:
                    for f_item in files:
                        fid = str(f_item.get("id"))
                        existing_file = await session.get(UploadedFile, fid)
                        if not existing_file:
                            new_file = UploadedFile(
                                id=fid,
                                name=f_item.get("name", "archivo"),
                                original_name=f_item.get("originalName", f_item.get("name", "archivo")),
                                size=f_item.get("size", 0),
                                file_type=f_item.get("type", "application/octet-stream"),
                                url=f_item.get("url", f"/api/files/{fid}"),
                                file_path=str(settings.UPLOADS_DIR / f_item.get("name", "archivo")),
                            )
                            session.add(new_file)
                            stats["files"] += 1

            except Exception as e:
                logger.error(f"Error migrando liseth_db.json: {e}")

        # 2. Check & Migrate Token Usage
        if token_usage_path.exists():
            try:
                with open(token_usage_path, "r", encoding="utf-8") as f:
                    tu_data = json.load(f)

                existing_tu = await session.get(TokenUsage, 1)
                if not existing_tu:
                    tu_stats = tu_data.get("stats", {})
                    tu_limits = tu_data.get("limits", {})
                    tu = TokenUsage(
                        id=1,
                        prompt_tokens=tu_stats.get("totalPromptTokens", 0),
                        candidates_tokens=tu_stats.get("totalCandidatesTokens", 0),
                        total_tokens=tu_stats.get("totalTokens", 0),
                        daily_limit=tu_limits.get("dailyTokenLimit", settings.DAILY_TOKEN_LIMIT),
                        alert_threshold_pct=tu_limits.get("alertThresholdPct", settings.ALERT_THRESHOLD_PCT),
                        last_reset_date=tu_stats.get("lastResetDate"),
                    )
                    session.add(tu)
                    stats["token_usage"] = True
            except Exception as e:
                logger.error(f"Error migrando token_usage.json: {e}")

        # 3. Check & Migrate Scheduled Tasks
        if scheduled_tasks_path.exists():
            try:
                with open(scheduled_tasks_path, "r", encoding="utf-8") as f:
                    tasks_list = json.load(f)

                if isinstance(tasks_list, list):
                    for t in tasks_list:
                        tid = str(t.get("id"))
                        existing_task = await session.get(ScheduledTask, tid)
                        if not existing_task:
                            task = ScheduledTask(
                                id=tid,
                                title=t.get("title", "Tarea programada"),
                                type=t.get("type", "reminder"),
                                schedule=t.get("schedule", "daily"),
                                time_of_day=t.get("timeOfDay"),
                                enabled=t.get("enabled", True),
                                last_run=str(t.get("lastRun")) if t.get("lastRun") else None,
                                next_run=str(t.get("nextRun")) if t.get("nextRun") else None,
                                params=t.get("params", {}),
                            )
                            session.add(task)
                            stats["tasks"] += 1
            except Exception as e:
                logger.error(f"Error migrando scheduled_tasks.json: {e}")

        # 4. Check & Migrate Audit Logs
        if audit_log_path.exists():
            try:
                with open(audit_log_path, "r", encoding="utf-8") as f:
                    logs_list = json.load(f)

                if isinstance(logs_list, list):
                    for item in logs_list:
                        aid = str(item.get("id"))
                        existing_audit = await session.get(AuditEntry, aid)
                        if not existing_audit:
                            entry = AuditEntry(
                                id=aid,
                                timestamp=str(item.get("timestamp", datetime.now(timezone.utc).isoformat())),
                                action=item.get("action", "unknown"),
                                category=item.get("category", "system"),
                                status=item.get("status", "executed"),
                                sensitive=item.get("sensitive", False),
                                details=item.get("details", {}),
                            )
                            session.add(entry)
                            stats["audit_logs"] += 1
            except Exception as e:
                logger.error(f"Error migrando audit_log.json: {e}")

        await session.commit()
        stats["migrated"] = True

    return stats
