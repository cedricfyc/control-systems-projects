"""
Account repository — all SQL access for the Account entity lives here.
No business logic should be placed in this layer; that belongs in services/account_service.py.
"""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from banking_app.database.db_connector import get_connection, db_transaction
from banking_app.models.user import User, UserRole
from banking_app.utils.enums import UserStatus


class UserNotFoundError(Exception):
    pass


class UserRepository:
    """
    CRUD operations against the storage backend for User object.
    """

    # ----- CREATE -----

    def create(self, user: User) -> User:
        """
        Creates a User entry inside the database.

        Parameters
        ----------
        user

        Returns
        -------

        """

        with db_transaction() as conn:
            conn.execute(
                """
                INSERT INTO users (
                    user_id, username, password_hash, user_role,
                    customer_id, user_status, created_at, last_login_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(user.user_id),
                    user.username,
                    user.password_hash,
                    user.user_role.value,
                    str(user.customer_id) if not None else None,
                    user.user_status.value,
                    user.created_at.isoformat(),
                    user.last_login_at.isoformat() if user.last_login_at is not None else None
                ),
            )
        return user

    # ----- READ -----

    def get_by_id(self, user_id: UUID) -> User:
        """
        Get a User object by its ID.

        Parameters
        ----------
        user_id

        Returns
        -------

        """
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (str(user_id),)
            ).fetchone()
        finally:
            conn.close()

        if row is None:
            raise UserNotFoundError(f"No user with id {user_id} found.")

        # Retrieve the db entry and convert to User object
        return User.from_db_row(row)


    def list_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """
        Get all users from the database in descending order.

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
                "SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
        finally:
            conn.close()
        return [User.from_db_row(r) for r in rows]


    def exists(self, user_id: Optional[UUID] = None) -> bool:
        """
        Check if a user exists in database by user_id.

        Parameters
        ----------
        user_id

        Returns
        -------

        """
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT 1 FROM users WHERE user_id = ? LIMIT 1",
                (user_id,)
            ).fetchone()

        finally:
            conn.close()
        return row is not None


    def search(
            self,
            user_id: Optional[UUID] = None,
            username: Optional[str] = None,
            user_role: Optional[UserRole] = None,
            user_status: Optional[UserStatus] = None,
            limit: int = 100,
            offset: int = 0,
    ) -> List[User]:
        """
        Flexible multi-criteria search. All filters are optional and combined with AND.
        Balance comparisons cast the stored TEXT column to REAL for numeric ordering.

        Parameters
        ----------
        offset
        limit
        user_id
        username
        user_role
        user_status

        Returns
        -------

        """
        clauses = []
        params: list = []

        if user_id is not None:
            clauses.append("user_id = ?")
            params.append(str(user_id))
        if username is not None:
            clauses.append("username = ?")
            params.append(username)
        if user_role is not None:
            clauses.append("user_role = ?")
            params.append(user_role.value)
        if user_status is not None:
            clauses.append("user_status = ?")
            params.append(user_status.value)

        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        query = f"""
                    SELECT * FROM users
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
        return [User.from_db_row(r) for r in rows]


    def count(self, user_status: Optional[UserStatus] = None) -> int:
        """
        Returns the count according to user status or the total database.

        Args:
            user_status:

        Returns:

        """
        conn = get_connection()
        try:
            if user_status is not None:
                row = conn.execute(
                    "SELECT COUNT(*) AS cnt FROM users WHERE user_status = ?",
                    (user_status.value,)
                ).fetchone()
            else:
                row = conn.execute("SELECT COUNT(*) as cnt FROM users").fetchone()
        finally:
            conn.close()
        return row["cnt"]


    # ----- UPDATE -----

    def update_status(self, user_id: UUID, user_status: UserStatus) -> User:
        """
        Update the user status of the User entry.

        Parameters
        ----------
        user_id
        user_status

        Returns
        -------

        """
        with db_transaction() as conn:
            cursor = conn.execute(
                "UPDATE users SET user = ? WHERE user_id = ?",
                (user_status.value, str(user_id)),
            )
            if cursor.rowcount == 0:
                raise UserNotFoundError(f"No user with id {user_id}")
        return self.get_by_id(user_id)


    def update(self, user: User) -> User:
        """
        Full-row update for a user.

        Parameters
        ----------
        user

        Returns
        -------

        """

        with db_transaction() as conn:
            conn.execute(
                """
                UPDATE customers SET
                    username = ?, password_hash = ?, user_role = ?,
                    custom_id = ?, user_status = ?, created_at = ?, last_login_at = ?
                WHERE user_id = ?
                """,
                (
                    user.username,
                    user.password_hash,
                    user.user_role.value,
                    str(user.customer_id),
                    user.user_status.value,
                    user.created_at.isoformat(),
                    user.last_login_at.isoformat(),
                    str(user.user_id)
                ),
            )

        # Return updated entry
        return self.get_by_id(user.user_id)


    # ---------- DELETE ----------

    def delete(self, user_id: UUID) -> None:
        """
        Hard delete. Prefer update_status(..., UserStatus.DEACTIVATED) for audit purposes.

        Parameters
        ----------
        user_id

        Returns
        -------

        """
        with db_transaction() as conn:
            cursor = conn.execute(
                "DELETE FROM users WHERE user_id = ?", (str(user_id),)
            )
            if cursor.rowcount == 0:
                raise UserNotFoundError(f"No user with id {user_id}")
