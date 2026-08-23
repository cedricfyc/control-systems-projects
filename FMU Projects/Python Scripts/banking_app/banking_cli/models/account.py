"""
Account model for the banking CLI
"""

from __future__ import annotations

from ..utils.enums import AccountType, AccountStatus

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class Account:
    """
    Class for account model.
    """
    customer_id: UUID
    account_number: str
    account_type: AccountType
    account_status: AccountStatus = AccountStatus.ACTIVE
    currency:str = "EUR"
    balance: Decimal = Decimal("0.00")
    interest_rate: Optional[Decimal] = None
    overdraft_limit: Optional[Decimal] = None
    min_balance: Decimal = Decimal("0.00")
    pin_hash: str = ""
    account_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 0


    def to_dict(self) -> dict:
        """Serialize the account to a dict of primitive types (for DB storage / display)."""
        return {
            "account_id": str(self.account_id),
            "account_number": self.account_number,
            "customer_id": str(self.customer_id),
            "account_type": self.account_type.value,
            "balance": str(self.balance),
            "currency": self.currency,
            "interest_rate": str(self.interest_rate) if self.interest_rate is not None else None,
            "overdraft_limit": str(self.overdraft_limit) if self.overdraft_limit is not None else None,
            "min_balance": str(self.min_balance),
            "pin_hash": self.pin_hash,
            "account_status": self.account_status.value,
            "created_at": self.created_at.isoformat(),
            "version": self.version,
        }

    @staticmethod
    def from_db_row(rows: dict) -> "Account":
        """Reconstruct an Account from a DB row (dict-like: sqlite3.Row, psycopg2 DictRow, etc.)."""
        return Account(
            account_id=UUID(rows["account_id"]),
            account_number=rows["account_number"],
            customer_id=UUID(rows["customer_id"]),
            account_type=AccountType(rows["account_type"]),
            balance=Decimal(rows["balance"]),
            currency=rows["currency"],
            interest_rate=Decimal(rows["interest_rate"]) if rows["interest_rate"] is not None else None,
            overdraft_limit=Decimal(rows["overdraft_limit"]) if rows["overdraft_limit"] is not None else None,
            min_balance=Decimal(rows["min_balance"]),
            pin_hash=rows["pin_hash"],
            account_status=AccountStatus(rows["status"]),
            created_at=datetime.fromisoformat(rows["created_at"]),
            version=rows["version"],
        )