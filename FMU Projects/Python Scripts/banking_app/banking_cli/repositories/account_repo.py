"""
Account repository — all SQL access for the Account entity lives here.
No business logic should be placed in this layer; that belongs in services/account_service.py.
"""

from __future__ import annotations

from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from ..database.db_connector import get_connection, db_transaction
from ..models.account import Account, AccountStatus, AccountType


class AccountNotFoundError(Exception):
    pass


class OptimisticLockError(Exception):
    """Raised when an update fails due to a stale version (concurrent modification)."""
    pass

class AccountRepository:

    """
    CRUD operations against the storage backend for Account object.
    """

    # ----- CREATE -----

    def create(self, account: Account) -> Account:
        """
        Creates an Account entry inside the database.

        Parameters
        ----------
        account

        Returns
        -------

        """

        with db_transaction() as conn:
            conn.execute(
                """
                INSERT INTO accounts (
                    account_id, account_number, customer_id, account_type,
                    balance, currency, interest_rate, overdraft_limit,
                    min_balance, pin_hash, status, created_at, version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(account.account_id),
                    account.account_number,
                    str(account.customer_id),
                    account.account_type.value,
                    str(account.balance),
                    account.currency,
                    str(account.interest_rate) if account.interest_rate is not None else None,
                    str(account.overdraft_limit) if account.overdraft_limit is not None else None,
                    str(account.min_balance),
                    account.pin_hash,
                    account.account_status.value,
                    account.created_at.isoformat(),
                    account.version,
                ),
            )
        return account

    # ----- READ -----

    def get_by_id(self, account_id: UUID) -> Account:
        """
        Get an Account by its ID from database.

        Parameters
        ----------
        account_id

        Returns
        -------

        """
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM accounts WHERE account_id = ?", (str(account_id),)
            ).fetchone()
        finally:
            conn.close()

        if row is None:
            raise AccountNotFoundError(f"No account with id {account_id} found.")

        # Retrieve db entry and convert to Account object
        return Account.from_db_row(row)


    def get_by_account_number(self, account_number: str) -> Account:
        """
        Get an Account by its number from database.

        Parameters
        ----------
        account_number

        Returns
        -------

        """
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM accounts WHERE account_number = ?", (account_number,)
            ).fetchone()
        finally:
            conn.close()

        if row is None:
            raise AccountNotFoundError(f"No account with number {account_number}")
        return Account.from_db_row(row)


    def get_all_by_customer(self, customer_id: UUID) -> List[Account]:
        """
        Get an Account by its customer ID from database.

        Parameters
        ----------
        customer_id

        Returns
        -------

        """
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM accounts WHERE customer_id = ? ORDER BY created_at DESC",
                (str(customer_id),),
            ).fetchall()
        finally:
            conn.close()
        return [Account.from_db_row(r) for r in rows]


    def list_all(self, limit: int = 100, offset: int = 0) -> List[Account]:
        """
        Get all accounts from the database in descending order.

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
        return [Account.from_db_row(r) for r in rows]


    def exists(self, account_number: str) -> bool:
        """
        Check if an account exists in database by account_number or customer_id.

        Parameters
        ----------
        customer_id
        account_number

        Returns
        -------

        """
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT 1 FROM accounts WHERE account_number = ? LIMIT 1",
                (account_number,)
            ).fetchone()
        finally:
            conn.close()
        return row is not None

    def search(
            self,
            customer_id: Optional[UUID] = None,
            account_type: Optional[AccountType] = None,
            account_status: Optional[AccountStatus] = None,
            min_balance: Optional[int] = None,
            max_balance: Optional[int] = None,
            currency: Optional[str] = None,
            limit: int = 100,
            offset: int = 0,
    ) -> List[Account]:
        """
        Flexible multi-criteria search. Flexible multi-criteria search. All filters are optional and combined with AND.
        Balance comparisons cast the stored TEXT column to REAL for numeric ordering.

        Parameters
        ----------
        customer_id
        account_type
        account_status
        min_balance
        max_balance
        currency
        limit
        offset

        Returns
        -------

        """

        clauses = []
        params: list = []

        if customer_id is not None:
            clauses.append("customer_id = ?")
            params.append(str(customer_id))
        if account_type is not None:
            clauses.append("account_type = ?")
            params.append(account_type.value)
        if account_status is not None:
            clauses.append("status = ?")
            params.append(account_status.value)
        if currency is not None:
            clauses.append("currency = ?")
            params.append(currency)
        if min_balance is not None:
            clauses.append("CAST(balance AS REAL) >= ?")
            params.append(float(min_balance))
        if max_balance is not None:
            clauses.append("CAST(balance AS REAL) <= ?")
            params.append(float(max_balance))

        # Construct the SQL Query to find the relevant accounts.
        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        query = f"""
                    SELECT * FROM accounts
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

        # Convert found rows to accounts
        return [Account.from_db_row(r) for r in rows]


    def count(self, status: Optional[AccountStatus] = None) -> int:
        """
        Returns the number of accounts matching the given status.

        Parameters
        ----------
        status

        Returns
        -------

        """
        conn = get_connection()
        try:
            if status is not None:
                row = conn.execute(
                    "SELECT COUNT(*) AS cnt FROM accounts WHERE status = ?", (status.value,)
                ).fetchone()
            else:
                row = conn.execute("SELECT COUNT(*) AS cnt FROM accounts").fetchone()
        finally:
            conn.close()
        return row["cnt"]


    # ----- UPDATE -----

    def update_balance(self, account_id: UUID, new_balance: Decimal, expected_version: int) -> Account:
        """
        Optimistic-locking balance update. Fails if `version` has moved on since it was read,
        which indicates a concurrent modification.
        """
        with db_transaction() as conn:
            cursor = conn.execute(
                """
                UPDATE accounts
                SET balance = ?, version = version + 1
                WHERE account_id = ? AND version = ?
                """,
                (str(new_balance), str(account_id), expected_version),
            )
            if cursor.rowcount == 0:
                raise OptimisticLockError(
                    f"Update failed for account {account_id}: version mismatch or account not found"
                )
        return self.get_by_id(account_id)


    def update_status(self, account_id: UUID, status: AccountStatus) -> Account:
        """
        Updates the status of an account within the SQL database.

        Parameters
        ----------
        account_id
        status

        Returns
        -------

        """
        with db_transaction() as conn:
            cursor = conn.execute(
                "UPDATE accounts SET status = ?, version = version + 1 WHERE account_id = ?",
                (status.value, str(account_id)),
            )
            if cursor.rowcount == 0:
                raise AccountNotFoundError(f"No account with id {account_id}")
        return self.get_by_id(account_id)

    def update(self, account: Account) -> Account:
        """
        Full-row update. Increments version; raises on stale version.
        """
        with db_transaction() as conn:
            cursor = conn.execute(
                """
                UPDATE accounts SET
                    account_number = ?, account_type = ?, balance = ?, currency = ?,
                    interest_rate = ?, overdraft_limit = ?, min_balance = ?,
                    pin_hash = ?, status = ?, version = version + 1
                WHERE account_id = ? AND version = ?
                """,
                (
                    account.account_number,
                    account.account_type.value,
                    str(account.balance),
                    account.currency,
                    str(account.interest_rate) if account.interest_rate is not None else None,
                    str(account.overdraft_limit) if account.overdraft_limit is not None else None,
                    str(account.min_balance),
                    account.pin_hash,
                    account.account_status.value,
                    str(account.account_id),
                    account.version,
                ),
            )
            if cursor.rowcount == 0:
                raise OptimisticLockError(
                    f"Update failed for account {account.account_id}: version mismatch or not found"
                )

        # Return updated entry
        return self.get_by_id(account.account_id)

    # ---------- DELETE ----------

    def delete(self, account_id: UUID) -> None:
        """
        Hard delete. Prefer update_status(..., CustomerStatus.CLOSED) for audit purposes.

        Parameters
        ----------
        account_id

        Returns
        -------

        """
        with db_transaction() as conn:
            cursor = conn.execute(
                "DELETE FROM accounts WHERE account_id = ?", (str(account_id),)
            )
            if cursor.rowcount == 0:
                raise AccountNotFoundError(f"No account with id {account_id}")