"""
Transaction repository — all SQL access for the Account entity lives here.
No business logic should be placed in this layer; that belongs in services/account_service.py.
"""


from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from banking_app.database.db_connector import get_connection, db_transaction
from banking_app.models.transaction import Transaction, TransactionType, TransactionStatus


class TransactionNotFoundError(Exception):
    pass


class TransactionRepository:
    """
    CRUD operations against the storage backend for Customer object.
    """

    # ----- CREATE -----
    def create(self, transaction: Transaction) -> Transaction:
        """
        Creates a Transaction entry inside the database.

        Parameters
        ----------
        transaction

        Returns
        -------

        """
        with db_transaction() as conn:
            conn.execute(
                """
                INSERT INTO transactions (
                    transaction_id, account_id, transaction_type, 
                    amount, balance_after, reference_id, description
                    counterparty_account_id, timestamp, transaction_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(transaction.transaction_id),
                    str(transaction.account_id),
                    transaction.transaction_type.value,
                    str(transaction.amount),
                    str(transaction.balance_after),
                    transaction.reference_id,
                    transaction.description,
                    str(transaction.counterparty_account_id) if not None else None,
                    transaction.timestamp.isoformat(),
                    transaction.transaction_status.value,
                ),
            )
        return transaction

    # ----- READ -----

    def get_by_id(self, transaction_id: UUID) -> Optional[Transaction]:
        """
        Get a Transaction entry inside the database by its
        transaction id.

        Parameters
        ----------
        transaction_id

        Returns
        -------

        """
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM transactions WHERE transaction_id = ?",
                (str(transaction_id),)
            ).fetchone()

        finally:
            conn.close()

        if row is None:
            raise TransactionNotFoundError(f"No transaction with id {transaction_id} found.")

        return Transaction.from_db_row(row)


    def get_all_by_account_number(self, account_number: str) -> List[Transaction]:
        """
        Get a Transaction by its number from database.

        Parameters
        ----------
        account_number

        Returns
        -------

        """
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM transactions WHERE account_number = ? ORDER BY created_at DESC",
                (account_number,)
            ).fetchall()
        finally:
            conn.close()

        return [Transaction.from_db_row(r) for r in rows]


    def get_all_by_status(self, transaction_status: TransactionStatus) -> List[Transaction]:
        """
        Get Transactions by their status from the database.

        Parameters
        ----------
        transaction_status

        Returns
        -------

        """
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM transactions WHERE transaction_status = ?  ORDER BY created_at DESC",
                (transaction_status,)
            ).fetchall()
        finally:
            conn.close()

        return [Transaction.from_db_row(r) for r in rows]

    def list_all(
            self,
            datestamp: date,
            limit: int = 100,
            offset: int = 0,
    ) -> List[Transaction]:
        """
        Get transactions for a given date in descending order.

        Parameters
        ----------
        datestamp
            The date to retrieve transactions for.
        limit
            Maximum number of transactions to return.
        offset
            Number of transactions to skip.

        Returns
        -------
        List[Transaction]
            Transactions occurring on the given date.
        """
        conn = get_connection()
        try:
            rows = conn.execute(
                """
                SELECT *
                FROM transactions
                WHERE DATE(timestamp) = ?
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
                """,
                (datestamp.isoformat(), limit, offset),
            ).fetchall()
        finally:
            conn.close()

        return [Transaction.from_db_row(r) for r in rows]


    def exists(self, transaction_id: str) -> bool:
        """
        Check if a transaction exists in database by account_number or customer_id.

        Parameters
        ----------
        transaction_id

        Returns
        -------

        """
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT 1 FROM transactions WHERE transaction_id = ? LIMIT 1",
                (transaction_id,)
            ).fetchone()
        finally:
            conn.close()
        return row is not None


    def search(
            self,
            transaction_id: Optional[UUID] = None,
            transaction_type: Optional[TransactionType] = None,
            transaction_status: Optional[TransactionStatus] = None,
            amount: Optional[Decimal] = None,
            balance_after: Optional[Decimal] = None,
            reference_id: Optional[str] = None,
            limit: int = 100,
            offset: int = 0,
    ) -> List[Transaction]:
        """
        Flexible multi-criteria search. Flexible multi-criteria search. All filters are optional and combined with AND.
        Balance comparisons cast the stored TEXT column to REAL for numeric ordering.

        Parameters
        ----------
        transaction_id
        transaction_type
        transaction_status
        amount
        balance_after
        reference_id
        limit
        offset

        Returns
        -------

        """
        clauses = []
        params: list = []

        if transaction_id is not None:
            clauses.append("transaction_id = ?")
            params.append(str(transaction_id))
        if transaction_type is not None:
            clauses.append("transaction_type = ?")
            params.append(transaction_type.value)
        if transaction_status is not None:
            clauses.append("transaction_status = ?")
            params.append(transaction_status.value)
        if amount is not None:
            clauses.append("amount = ?")
            params.append(float(amount))
        if balance_after is not None:
            clauses.append("balance_after = ?")
            params.append(float(balance_after))
        if reference_id is not None:
            clauses.append("reference_id = ?")
            params.append(reference_id)

        # Construct the SQL Query to find the relevant accounts.
        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        query = f"""
                    SELECT * FROM transactions
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

        # Convert found rows to transactions
        return [Transaction.from_db_row(r) for r in rows]


    def count(self, transaction_status: Optional[TransactionStatus] = None) -> int:
        conn = get_connection()
        try:
            # If status is given, filter by status and return count
            if transaction_status is not None:
                row = conn.execute(
                    "SELECT COUNT(*) AS cnt FROM transactions WHERE status = ?",
                    (transaction_status.value,)
                ).fetchone()
            # Else return total count
            else:
                row = conn.execute("SELECT COUNT(*) AS cnt FROM transactions").fetchone()
        finally:
            conn.close()
        return row["cnt"]

    # ----- UPDATE -----

    def update_status(self, transaction_id: UUID,
                      transaction_status: TransactionStatus) -> Transaction:
        with db_transaction() as conn:
            cursor = conn.execute(
                "UPDATE transactions SET transaction_status = ? WHERE transaction_id = ?",
                (transaction_status.value, str(transaction_id)),
            )
            if cursor.rowcount == 0:
                raise TransactionNotFoundError(f"No account with id {transaction_id}")
        return self.get_by_id(transaction_id)


    def update(self, transaction: Transaction) -> Transaction:
        """Full-row update. Increments version; raises on stale version."""
        with db_transaction() as conn:
            conn.execute(
                """
                UPDATE accounts SET
                    transaction_status, transaction_type = ?, amount = ?, balance_after = ?,
                    reference_id = ?, description = ?, counterparty_account_id = ?
                WHERE transaction_id = ?
                """,
                (
                    transaction.transaction_status.value,
                    transaction.transaction_type.value,
                    str(transaction.amount),
                    str(transaction.balance_after),
                    transaction.reference_id,
                    transaction.description,
                    str(transaction.counterparty_account_id),
                ),
            )

        return self.get_by_id(transaction.transaction_id)

    # ---------- DELETE ----------

    def delete(self, transaction_id: UUID) -> None:
        """
        Hard delete.
        """
        with db_transaction() as conn:
            cursor = conn.execute(
                "DELETE FROM transactions WHERE transaction_id = ?", (str(transaction_id),)
            )
            if cursor.rowcount == 0:
                raise TransactionNotFoundError(f"No transaction with id {transaction_id}")