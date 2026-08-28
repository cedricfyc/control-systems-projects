"""
Card model for the Banking CLI application.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from banking_app.utils.enums import CardType, CardStatus


@dataclass
class Card:
    """
    Card model class.
    """
    card_id: UUID
    account_id: UUID
    account_number: str
    card_type: CardType
    card_status: CardStatus
    expiry_date: date
    cvv_hash: str


    def to_dict(self) -> dict:
        """
        Serialize the account to a dict of primitive types (for DB storage / display).

        Returns
        -------

        """

        return {
            "card_id": str(self.card_id),
            "account_id": str(self.account_id),
            "account_number": self.account_number,
            "card_type": self.card_type.value,
            "card_status": self.card_status.value,
            "expiry_date": self.expiry_date.isoformat(),
            "cvv_hash": self.cvv_hash,
        }


    @staticmethod
    def from_db_row(row: dict) -> Card:
        """
        Reconstruct a Card from a DB row.

        Parameters
        ----------
        row

        Returns
        -------

        """
        return Card(
            card_id=UUID(row["card_id"]),
            account_id=UUID(row["account_id"]),
            account_number=row["account_number"],
            card_type=CardType(row["card_type"]),
            card_status=CardStatus(row["card_status"]),
            expiry_date=date.fromisoformat((row["expiry_date"])),
            cvv_hash=row["cvv_hash"],
        )