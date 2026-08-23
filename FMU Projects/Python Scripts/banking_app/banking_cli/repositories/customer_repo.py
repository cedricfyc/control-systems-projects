"""
Account repository — all SQL access for the Account entity lives here.
No business logic should be placed in this layer; that belongs in services/account_service.py.
"""

from __future__ import annotations

from typing import List, Optional
from datetime import date, datetime
from uuid import UUID

from ..database.db_connector import get_connection, transaction
from ..models.customer import Customer, CustomerStatus


class CustomerNotFoundError(Exception):
    pass


class CustomerRepository:
    """
    CRUD operations against the storage backend for Customer object.
    """

    # ----- CREATE -----

    def create(self, customer: Customer) -> Customer:
        """
        Creates a Customer entry inside the database.

        Parameters
        ----------
        customer

        Returns
        -------

        """

        with transaction() as conn:
            conn.execute(
                """
                INSERT INTO customers (
                    customer_id, first_name, middle_name, last_name, date_of_birth,
                    national_id, email, phone_number, address_street, address_city,
                    address_zip, address_state, address_country, created_at,
                    customer_status, kyc_verified
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(customer.customer_id),
                    customer.first_name,
                    customer.middle_name,
                    customer.last_name,
                    customer.date_of_birth.isoformat(),
                    customer.national_id,
                    customer.email,
                    customer.phone_number,
                    customer.address.street,
                    customer.address.city,
                    customer.address.zip,
                    customer.address.state,
                    customer.address.country,
                    customer.created_at.isoformat(),
                    customer.customer_status.value,
                    customer.kyc_verified
                ),
            )
        return customer

    # ----- READ -----

    def get_by_id(self, customer_id: UUID) -> Customer:
        """
        Get a Customer object by its ID.

        Parameters
        ----------
        customer_id

        Returns
        -------

        """
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM customers WHERE customer_id = ?", (str(customer_id),)
            ).fetchone()
        finally:
            conn.close()

        if row is None:
            raise CustomerNotFoundError(f"No customer with id {customer_id} found.")

        # Retrieve the db entry and convert to Customer object
        return Customer.from_db_row(row)


    def get_all_by_last_name(self, last_name: str) -> List[Customer]:
        """
        Get all Customers inside the database with a matching last name.

        Parameters
        ----------
        last_name

        Returns
        -------

        """
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM customers WHERE customer_id = ?", (last_name,)
            ).fetchone()
        finally:
            conn.close()


        # Retrieve the db entry and convert to Customer object
        return [Customer.from_db_row(r) for r in rows]


    def list_all(self, limit: int = 100, offset: int = 0) -> List[Customer]:
        """
        Get all customers from the database in descending order.

        Parameters
        ----------
        limit
        offset

        Returns
        -------

        """
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM accounts ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
        finally:
            conn.close()
        return [Customer.from_db_row(r) for r in rows]


    def exists(self, customer_id: Optional[UUID] = None) -> bool:
        """
        Check if a customer exists in database by customer_id.

        Parameters
        ----------
        customer_id

        Returns
        -------

        """
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT 1 FROM customers WHERE customer_id = ? LIMIT 1",
                (customer_id,)
            ).fetchone()

        finally:
            conn.close()
        return row is not None


    def search(
            self,
            customer_id: Optional[UUID] = None,
            first_name: Optional[str] = None,
            middle_name: Optional[str] = None,
            last_name: Optional[str] = None,
            address_country: Optional[str] = None,
            customer_status: Optional[CustomerStatus] = None,
    ):
        """
        Flexible

        Parameters
        ----------
        customer_id
        first_name
        middle_name
        last_name
        address_country
        customer_status

        Returns
        -------

        """
        pass