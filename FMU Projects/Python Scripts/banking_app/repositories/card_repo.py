"""
Audit logs repository — all SQL access for the Account entity lives here.
No business logic should be placed in this layer; that belongs in services/account_service.py.
"""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from banking_app.database.db_connector import get_connection, db_transaction
from banking_app.models.card import Card
from banking_app.utils.enums import CardStatus, CardType


class CardNotFoundError(Exception):
    pass


class CardRepository:
    """
    CRUD operations against the storage backend for Card object.
    """

    # ----- CREATE -----

    def create(self, card: Card) -> Card:
        """
        Creates a Card entry inside the database.

        Parameters
        ----------
        card
            Card object to store in database

        Returns
        -------
        Card
            Card within database
        """

        with db_transaction() as conn:
            conn.execute(
                """
                INSERT INTO cards (
                    card_id, account_id, account_number,
                    card_type, card_status, expiry_date, cvv_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(card.card_id),
                    str(card.account_id),
                    card.account_number,
                    card.card_type.value,
                    card.card_status.value,
                    card.expiry_date.isoformat(),
                    card.cvv_hash,
                ),
            )
        return card

    # ----- READ -----

    def get_by_id(self, card_id: UUID) -> Optional[Card]:
        """
        Get a Card object by its id.

        Parameters
        ----------
        card_id

        Returns
        -------

        """

        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM cards WHERE card_id = ?",
                (card_id,)
            ).fetchone()
        finally:
            conn.close()

        if row is None:
            raise CardNotFoundError(f"No audit log with id {card_id} found.")

        # Retrieve db entry and convert to Card object
        return Card.from_db_row(row)


    def list_all(self, limit: int = 100, offset: int = 0) -> List[Card]:
        """
        Get all cards from the database in descending order.

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
                "SELECT * FROM cards ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
        finally:
            conn.close()
        return [Card.from_db_row(r) for r in rows]


    def search(
            self,
            card_id: Optional[UUID] = None,
            account_id: Optional[UUID] = None,
            account_number: Optional[str] = None,
            card_type: Optional[CardType] = None,
            card_status: Optional[CardStatus] = None,
            limit: int = 100,
            offset: int = 0,
    ) -> List[Card]:
        """
        Flexible multi-criteria search. Flexible multi-criteria search. All filters are optional and combined with AND.
        Balance comparisons cast the stored TEXT column to REAL for numeric ordering.

        Parameters
        ----------
        card_id
            ID of card
        account_id
            ID of account holding card
        account_number
            Number of account holding card
        card_type
            Card type
        card_status
            Card status
        limit
            Extent of display
        offset
            Space between results

        Returns
        -------

        """

        clauses = []
        params: list = []

        if card_id is not None:
            clauses.append("card_id = ?")
            params.append(str(card_id))
        if account_id is not None:
            clauses.append("account_id = ?")
            params.append(str(account_id))
        if account_number is not None:
            clauses.append("account_number = ?")
            params.append(account_number)
        if card_type is not None:
            clauses.append("card_type = ?")
            params.append(card_type.value)
        if card_status is not None:
            clauses.append("card_status = ?")
            params.append(card_status.value)

        # Construct the SQL Query to find the relevant accounts.
        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        query = f"""
                    SELECT * FROM cards
                    {where_sql}
                    ORDER BY card_status DESC
                    LIMIT ? OFFSET ?
                """
        params.extend([limit, offset])

        conn = get_connection()
        try:
            rows = conn.execute(query, params).fetchall()
        finally:
            conn.close()

        # Convert found rows to accounts
        return [Card.from_db_row(r) for r in rows]


    def count_by_status(self, card_status: Optional[CardStatus] = None) -> int:
        """
        Returns the number of accounts matching the given status.

        Parameters
        ----------
        card_status
            Card status

        Returns
        -------

        """
        conn = get_connection()
        try:
            if card_status is not None:
                row = conn.execute(
                    "SELECT COUNT(*) AS cnt FROM cards WHERE card_status = ?",
                    (card_status.value,)
                ).fetchone()
            else:
                row = conn.execute("SELECT COUNT(*) AS cnt FROM cards").fetchone()
        finally:
            conn.close()
        return row["cnt"]


    # ----- UPDATE -----

    def update_status(self, card_id: UUID, card_status: CardStatus) -> Card:
        """
        Updates the card status of an account within the SQL database.

        Parameters
        ----------
        card_id
        card_status

        Returns
        -------

        """
        with db_transaction() as conn:
            cursor = conn.execute(
                "UPDATE cards SET card_status = ?",
                (card_status.value, str(card_id)),
            )
            if cursor.rowcount == 0:
                raise CardNotFoundError(f"No cards with id {card_id}")
        return self.get_by_id(card_id)

    def update(self, card: Card) -> Card:
        """
        Full-row update. Increments version; raises on stale version.
        """
        with db_transaction() as conn:
            conn.execute(
                """
                UPDATE cards SET
                    account_id = ?, account_number = ?, card_type = ?,
                    card_status = ?, expiry_date = ?, cvv_hash = ?
                WHERE card_id = ?
                """,
                (
                    str(card.card_id),
                    str(card.account_id),
                    card.account_number,
                    card.card_type.value,
                    card.card_status.value,
                    card.expiry_date.isoformat(),
                    card.cvv_hash,
                ),
            )

        # Return updated entry
        return self.get_by_id(card.card_id)


    # ---------- DELETE ----------

    def delete(self, card_id: UUID) -> None:
        """
        Hard delete. Prefer update_outcome for audit purposes.

        Parameters
        ----------
        card_id

        Returns
        -------

        """
        with db_transaction() as conn:
            cursor = conn.execute(
                "DELETE FROM cards WHERE card_id = ?", (str(card_id),)
            )
            if cursor.rowcount == 0:
                raise CardNotFoundError(f"No card with id {card_id}")