"""
Transaction model for the Banking CLI application.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from banking_app.utils.enums import TransactionType, TransactionStatus


# Dataclass for transaction
@dataclass
class Transaction:
    account_id: UUID
    transaction_type: TransactionType
    amount: Decimal
    balance_after: Decimal
    reference_id: str
    transaction_id: UUID = field(default_factory=uuid4)
    description: Optional[str] = None
    counterparty_account_id: Optional[UUID] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    transaction_status: TransactionStatus = TransactionStatus.PENDING


    def to_dict(self) -> dict:
        """
        Serialise the transaction to a dict of primitive types (for DB storage / display)
        Parameters
        ----------
        self

        Returns
        -------

        """
        return {
            "transaction_id": str(self.transaction_id),
            "account_id": str(self.account_id),
            "transaction_type": self.transaction_type.value,
            "amount": str(self.amount),
            "balance_after": str(self.balance_after),
            "timestamp": self.timestamp.isoformat(),
            "transaction_status": self.transaction_status.value,
            "reference_id": self.reference_id,
            "description": self.description,
            "counterparty_account_id": str(self.counterparty_account_id) if not None else None,
        }

    @staticmethod
    def from_db_row(row: dict) -> "Transaction":
        """Reconstruct a Transaction from a DB row (dict-like: sqlite3.Row, psycopg2 DictRow, etc.)."""
        return Transaction(
            transaction_id=UUID(row["transaction_id"]),
            account_id=UUID(row["account_id"]),
            amount=Decimal(row["amount"]),
            balance_after=Decimal(row["balance_after"]),
            reference_id=row["reference_id"],
            description=row["description"],
            counterparty_account_id=UUID(row["counterparty_account_id"]) if not None else None,
            timestamp=datetime.fromisoformat(row["timestamp"]),
            transaction_status=TransactionStatus(row["transaction_status"]),
            transaction_type=TransactionType(row["transaction_type"]),
        )