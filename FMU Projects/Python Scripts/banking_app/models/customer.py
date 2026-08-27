"""
Customer model for the Banking CLI application.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, date
from typing import Optional
from uuid import UUID

from banking_app.utils.enums import CustomerStatus


# Dataclass for address
@dataclass
class Address:
    city: str
    country: str
    state: Optional[str] = None
    street: Optional[str] = None
    zip: Optional[str] = None


# Automatically creates constructor with the required fields/properties
# for the given variables and data types.
@dataclass
class Customer:
    customer_id: UUID
    first_name: str
    middle_name: str
    last_name: str
    date_of_birth: date
    national_id: str
    email: Optional[str] = None
    phone_number: Optional[str] = None

    # Custom address object
    address: Optional[Address] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    customer_status: CustomerStatus = CustomerStatus.ACTIVE
    kyc_verified: bool = field(default=False)


    def to_dict(self) -> dict:
        """Serialize the account to a dict of primitive types (for DB storage / display)."""
        return {
            "customer_id": str(self.customer_id),
            "first_name": self.first_name,
            "middle_name": self.middle_name,
            "last_name": self.last_name,
            "date_of_birth": self.date_of_birth.isoformat(),
            "national_id": self.national_id,
            "email": self.email,
            "phone_number": self.phone_number,

            # Address is broken down into individual str
            "address_street": self.address.street,
            "address_city": self.address.city,
            "address_state": self.address.state,
            "address_country": self.address.country,
            "address_zip": self.address.zip,

            "created_at": self.created_at.isoformat(),
            "customer_status": self.customer_status.value,
            "kyc_verified": self.kyc_verified,
            }


    @staticmethod
    def from_db_row(row: dict) -> "Customer":
        """Reconstruct an Customer from a DB row (dict-like: sqlite3.Row, psycopg2 DictRow, etc.)."""
        return Customer(
            customer_id=UUID(row["customer_id"]),
            first_name=row["first_name"],
            middle_name=row["middle_name"],
            last_name=row["last_name"],
            date_of_birth=date.fromisoformat(row["date_of_birth"]),
            national_id=row["national_id"],
            email=row["email"],
            phone_number=row["phone_number"],

            # Create address object
            address=Address(street = row["address_street"],
                            city = row["address_city"],
                            state = row["address_state"],
                            country = row["address_country"],
                            zip = row["address_zip"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            customer_status=CustomerStatus(row["customer_status"]),
            kyc_verified=row["kyc_verified"],
        )