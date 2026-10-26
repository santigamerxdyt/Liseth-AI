"""
SQLAlchemy ORM models for JARVIS / Liseth SQLite database.
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, default=1)
    name = Column(String(100), default="Santiago")
    nickname = Column(String(100), default="Santi")
    created_at = Column(DateTime, default=utcnow)
    memory_facts = Column(JSON, default=list)
    preferences = Column(JSON, default=dict)
    pin_salt = Column(String(64), nullable=True)
    pin_hash = Column(String(128), nullable=True)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), default="default", index=True)
    role = Column(String(30), nullable=False)  # 'user', 'model', 'system'
    parts = Column(JSON, nullable=False)  # [{ "text": "..." }]
    timestamp = Column(DateTime, default=utcnow)
    meta_info = Column(JSON, default=dict)


class ScheduledTask(Base):
    __tablename__ = "scheduled_tasks"

    id = Column(String(100), primary_key=True)
    title = Column(String(200), nullable=False)
    type = Column(String(50), nullable=False)  # 'reminder', 'report', 'digest', 'check'
    schedule = Column(String(50), nullable=False)  # 'daily', 'interval', 'cron', etc.
    time_of_day = Column(String(20), nullable=True)
    enabled = Column(Boolean, default=True)
    last_run = Column(String(50), nullable=True)
    next_run = Column(String(50), nullable=True)
    params = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)


class AuditEntry(Base):
    __tablename__ = "audit_entries"

    id = Column(String(100), primary_key=True)
    timestamp = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    status = Column(String(30), nullable=False)  # 'pending', 'approved', 'rejected', 'executed'
    sensitive = Column(Boolean, default=False)
    details = Column(JSON, default=dict)


class TokenUsage(Base):
    __tablename__ = "token_usage"

    id = Column(Integer, primary_key=True, default=1)
    prompt_tokens = Column(Integer, default=0)
    candidates_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    daily_limit = Column(Integer, default=100000)
    alert_threshold_pct = Column(Integer, default=80)
    last_reset_date = Column(String(20), nullable=True)
    last_updated = Column(DateTime, default=utcnow)


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(String(100), primary_key=True)
    name = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    size = Column(Integer, default=0)
    file_type = Column(String(100), default="application/octet-stream")
    uploaded_at = Column(DateTime, default=utcnow)
    url = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)


class AppSetting(Base):
    __tablename__ = "app_settings"

    key = Column(String(100), primary_key=True)
    value = Column(JSON, nullable=False)


class NfcTransaction(Base):
    __tablename__ = "nfc_transactions"

    id = Column(String(100), primary_key=True)
    created_at = Column(DateTime, default=utcnow)
    type = Column(String(50), nullable=False)  # 'payment', 'vcard', 'text', 'url', 'token'
    direction = Column(String(20), default="outgoing")  # 'outgoing' (emitted/beamed) or 'incoming' (read/received)
    amount = Column(Float, nullable=True)
    currency = Column(String(10), default="COP")
    recipient = Column(String(200), nullable=True)
    sender = Column(String(200), nullable=True)
    concept = Column(String(255), nullable=True)
    status = Column(String(30), default="completed")  # 'completed', 'pending', 'simulated'
    payload = Column(JSON, default=dict)


class DigitalInvoice(Base):
    __tablename__ = "digital_invoices"

    id = Column(String(100), primary_key=True)  # e.g. FAC-2026-0001
    created_at = Column(DateTime, default=utcnow)
    issuer_name = Column(String(200), default="Santiago Huerfano Lopez")
    issuer_nit = Column(String(50), default="1000000000-1")
    client_name = Column(String(200), nullable=False)
    client_id = Column(String(50), default="222222222222")
    currency = Column(String(10), default="COP")
    items = Column(JSON, default=list)
    subtotal = Column(Float, default=0.0)
    tax_iva = Column(Float, default=0.0)
    retention = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    payment_method = Column(String(50), default="Bre-B Contactless")
    cufe_hash = Column(String(128), nullable=False)
    qr_payload = Column(Text, nullable=True)
    nfc_tx_id = Column(String(100), nullable=True)
    status = Column(String(30), default="issued")


class NfcSecurityKey(Base):
    __tablename__ = "nfc_security_keys"

    id = Column(String(100), primary_key=True)
    label = Column(String(150), default="Credencial de Santiago")
    created_at = Column(DateTime, default=utcnow)
    last_used = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    secret_hash = Column(String(128), nullable=True)
    permissions = Column(JSON, default=list)


