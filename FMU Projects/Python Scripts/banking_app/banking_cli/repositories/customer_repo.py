"""
Account repository — all SQL access for the Account entity lives here.
No business logic should be placed in this layer; that belongs in services/account_service.py.
"""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from ..database.db_connector import get_connection, db_transaction
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

        with db_transaction() as conn:
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
                "SELECT * FROM customers WHERE customer_id = ?  ORDER BY created_at DESC",
                (last_name,)
            ).fetchall()
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
            last_name: Optional[str] = None,
            address_country: Optional[str] = None,
            customer_status: Optional[CustomerStatus] = None,
            limit: int = 100,
            offset: int = 0,
    ) -> List[Customer]:
        """
        Flexible multi-criteria search. All filters are optional and combined with AND.
        Balance comparisons cast the stored TEXT column to REAL for numeric ordering.

        Parameters
        ----------
        offset
        limit
        customer_id
        last_name
        address_country
        customer_status

        Returns
        -------

        """
        clauses = []
        params: list = []

        if customer_id is not None:
            clauses.append("customer_id = ?")
            params.append(str(customer_id))
        if last_name is not None:
            clauses.append("last_name = ?")
            params.append(last_name)
        if address_country is not None:
            clauses.append("address_country = ?")
            params.append(address_country)
        if customer_status is not None:
            clauses.append("customer_status = ?")
            params.append(customer_status.value)

        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        query = f"""
                    SELECT * FROM customers
                    {where_sql}
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """
        params.extend([limit, offset])

        conn = get_connection()
        try:
            rows = conn.execute(query, params).fetchall()
        finally:
            conn.close()
        return [Customer.from_db_row(r) for r in rows]


    def count(self, customer_status: Optional[CustomerStatus] = None) -> int:
        conn = get_connection()
        try:
            if customer_status is not None:
                row = conn.execute(
                    "SELECT COUNT(*) AS cnt FROM customers WHERE customer_status = ?",
                    (customer_status.value,)
                ).fetchone()
            else:
                row = conn.execute("SELECT COUNT(*) as cnt FROM customers").fetchone()
        finally:
            conn.close()
        return row["cnt"]


    # ----- UPDATE -----

    def update_status(self, customer_id: UUID, customer_status: CustomerStatus) -> Customer:
        """
        Update the customer status of the Customer entry.

        Parameters
        ----------
        customer_id
        customer_status

        Returns
        -------

        """
        with db_transaction() as conn:
            cursor = conn.execute(
                "UPDATE customers SET customer = ? WHERE customer_id = ?",
                (customer_status.value, str(customer_id)),
            )
            if cursor.rowcount == 0:
                raise CustomerNotFoundError(f"No customer with id {customer_id}")
        return self.get_by_id(customer_id)


    def update(self, customer: Customer) -> Customer:
        """
        Full-row update for a customer.

        Parameters
        ----------
        customer

        Returns
        -------

        """

        with db_transaction() as conn:
            conn.execute(
                """
                UPDATE customers SET
                    first_name = ?, middle_name = ?, last_name = ?,
                    date_of_birth = ?, national_id = ?, email = ?,
                    phone_number = ?, address_street = ?, address_city = ?,
                    address_zip = ?, address_state = ?, address_country = ?,
                    customer_status = ?, kyc_verified = ?
                WHERE customer_id = ?
                """,
                (
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
                    customer.customer_status.value,
                    customer.kyc_verified,
                    str(customer.customer_id)
                ),
            )

        # Return updated entry
        return self.get_by_id(customer.customer_id)


    # ---------- DELETE ----------

    def delete(self, customer_id: UUID) -> None:
        """
        Hard delete. Prefer update_status(..., CustomerStatus.CLOSED) for audit purposes.

        Parameters
        ----------
        customer_id

        Returns
        -------

        """
        with db_transaction() as conn:
            cursor = conn.execute(
                "DELETE FROM customers WHERE customer_id = ?", (str(customer_id),)
            )
            if cursor.rowcount == 0:
                raise CustomerNotFoundError(f"No customer with id {customer_id}")
