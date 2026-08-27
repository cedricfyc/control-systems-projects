"""
Audit log model for the Banking CLI application.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timezone, datetime
from typing import Optional
from uuid import UUID, uuid4

from banking_app.utils.enums import AuditAction, AuditOutcome


@dataclass
class AuditLog:

    user_id: UUID
    audit_action: AuditAction
    audit_outcome: AuditOutcome
    ip_address: Optional[str] = None
    details: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    log_id: UUID = field(default_factory=uuid4)

    def to_dict(self) -> dict:
        """Serialize the account to a dict of primitive types (for DB storage / display)."""
        return {
            "user_id": str(self.user_id),
            "audit_action": self.audit_action.value,
            "audit_outcome": self.audit_outcome.value,
            "ip_address": self.ip_address,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "log_id": str(self.log_id),
            }


    @staticmethod
    def from_db_row(row: dict) -> "AuditLog":
        """Reconstruct an Customer from a DB row (dict-like: sqlite3.Row, psycopg2 DictRow, etc.)."""
        return AuditLog(
            user_id=UUID(row["user_id"]),
            audit_action=AuditAction(row["audit_action"]),
            audit_outcome=AuditOutcome(row["audit_outcome"]),
            ip_address=row["ip_address"],
            details=row["details"],
            timestamp=row["timestamp"].fromisoformat(),
            log_id=UUID(row["log_id"]),
        )
