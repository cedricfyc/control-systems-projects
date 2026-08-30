"""
Audit logs repository — all SQL access for the Account entity lives here.
No business logic should be placed in this layer; that belongs in services/account_service.py.
"""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from banking_app.database.db_connector import get_connection, db_transaction
from banking_app.models.audit_log import AuditLog
from banking_app.utils.enums import AuditAction, AuditOutcome


class AuditLogNotFoundError(Exception):
    pass


class AuditLogRepository:
    """
    CRUD operations against the storage backend for AuditLog object.
    """

    # ----- CREATE -----

    def create(self, audit_log: AuditLog) -> AuditLog:
        """
        Creates an AuditLog entry inside the database.

        Parameters
        ----------
        audit_log

        Returns
        -------

        """

        with db_transaction() as conn:
            conn.execute(
                """
                INSERT INTO audit_logs (
                    user_id, audit_action, audit_outcome,
                    ip_address, details, timestamp, log_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(audit_log.user_id),
                    audit_log.audit_action.value,
                    audit_log.audit_outcome.value,
                    audit_log.ip_address,
                    audit_log.details,
                    audit_log.timestamp.isoformat(),
                    str(audit_log.log_id),
                ),
            )
        return audit_log

    # ----- READ -----

    def get_by_id(self, log_id: UUID) -> AuditLog:
        """
        Get an AuditLog object by its id.

        Parameters
        ----------
        log_id

        Returns
        -------

        """

        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM audit_logs WHERE log_id = ?",
                (log_id,)
            ).fetchone()
        finally:
            conn.close()

        if row is None:
            raise AuditLogNotFoundError(f"No audit log with id {log_id} found.")

        # Retrieve db entry and convert to AuditLog object
        return AuditLog.from_db_row(row)


    def get_all_by_outcome(self, audit_outcome: AuditOutcome) -> List[AuditLog]:
        """
        Get a list of AuditLog objects by their outcome.

        Parameters
        ----------
        audit_outcome
            Outcome of audit log
        Returns
        -------

        """

        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM audit_logs ORDER BY timestamp DESC WHERE audit_outcome = ?",
                (audit_outcome.value,)
            ).fetchone()
        finally:
            conn.close()

        if rows is None:
            raise AuditLogNotFoundError(f"No audit log with outcome {audit_outcome.value} found.")

        # Retrieve db entry and convert to AuditLog object
        return [AuditLog.from_db_row(r) for r in rows]


    def get_all_by_action(self, audit_action: AuditAction) -> List[AuditLog]:
        """
        Get a list of AuditLog objects by their outcome.

        Parameters
        ----------
        audit_action
            Action documented by audit log
        Returns
        -------

        """

        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM audit_logs ORDER BY timestamp DESC WHERE audit_action = ?",
                (audit_action.value,)
            ).fetchone()
        finally:
            conn.close()

        if rows is None:
            raise AuditLogNotFoundError(f"No audit log with action {audit_action.value} found.")

        # Retrieve db entry and convert to AuditLog object
        return [AuditLog.from_db_row(r) for r in rows]


    def list_all(self, limit: int = 100, offset: int = 0) -> List[AuditLog]:
        """
        Get all audit logs from the database in descending order.

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
                "SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
        finally:
            conn.close()
        return [AuditLog.from_db_row(r) for r in rows]


    def search(
            self,
            log_id: Optional[UUID] = None,
            user_id: Optional[UUID] = None,
            audit_action: Optional[AuditAction] = None,
            audit_outcome: Optional[AuditOutcome] = None,
            ip_address: Optional[int] = None,
            limit: int = 100,
            offset: int = 0,
    ) -> List[AuditLog]:
        """
        Flexible multi-criteria search. Flexible multi-criteria search. All filters are optional and combined with AND.
        Balance comparisons cast the stored TEXT column to REAL for numeric ordering.

        Parameters
        ----------
        log_id
            ID of audit log
        user_id
            ID of user
        audit_action
            Action of audit log
        audit_outcome
            Outcome of audit log
        ip_address
            IP address of user (optional)
        limit
            Extent of display
        offset
            Space between results

        Returns
        -------

        """

        clauses = []
        params: list = []

        if log_id is not None:
            clauses.append("log_id = ?")
            params.append(str(log_id))
        if user_id is not None:
            clauses.append("user_id = ?")
            params.append(str(user_id))
        if audit_action is not None:
            clauses.append("audit_action = ?")
            params.append(audit_action.value)
        if audit_outcome is not None:
            clauses.append("audit_outcome = ?")
            params.append(audit_outcome.value)
        if ip_address is not None:
            clauses.append("ip_address = ?")
            params.append(ip_address)

        # Construct the SQL Query to find the relevant accounts.
        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        query = f"""
                    SELECT * FROM audit_logs
                    {where_sql}
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                """
        params.extend([limit, offset])

        conn = get_connection()
        try:
            rows = conn.execute(query, params).fetchall()
        finally:
            conn.close()

        # Convert found rows to accounts
        return [AuditLog.from_db_row(r) for r in rows]


    def count(self, audit_outcome: Optional[AuditOutcome] = None) -> int:
        """
        Returns the number of accounts matching the given status.

        Parameters
        ----------
        audit_outcome
            Outcome of the audit

        Returns
        -------

        """
        conn = get_connection()
        try:
            if audit_outcome is not None:
                row = conn.execute(
                    "SELECT COUNT(*) AS cnt FROM audit_logs WHERE audit_outcome = ?",
                    (audit_outcome.value,)
                ).fetchone()
            else:
                row = conn.execute("SELECT COUNT(*) AS cnt FROM audit_logs").fetchone()
        finally:
            conn.close()
        return row["cnt"]


    # ----- UPDATE -----

    def update_outcome(self, log_id: UUID, audit_outcome: AuditOutcome) -> AuditLog:
        """
        Updates the audit_outcome of an account within the SQL database.

        Parameters
        ----------
        log_id
        audit_outcome

        Returns
        -------

        """
        with db_transaction() as conn:
            cursor = conn.execute(
                "UPDATE audit_logs SET audit_outcome = ?",
                (audit_outcome.value, str(log_id)),
            )
            if cursor.rowcount == 0:
                raise AuditLogNotFoundError(f"No audit logs with id {log_id}")
        return self.get_by_id(log_id)

    def update(self, audit_log: AuditLog) -> AuditLog:
        """
        Full-row update. Increments version; raises on stale version.
        """
        with db_transaction() as conn:
            conn.execute(
                """
                UPDATE audit_logs SET
                    user_id = ?, audit_action = ?, audit_outcome = ?,
                    ip_address = ?, details = ?, timestamp = ?
                WHERE log_id = ?
                """,
                (
                    str(audit_log.user_id),
                    audit_log.audit_action.value,
                    audit_log.audit_outcome.value,
                    audit_log.ip_address,
                    audit_log.details,
                    audit_log.timestamp.isoformat(),
                    str(audit_log.log_id),
                ),
            )

        # Return updated entry
        return self.get_by_id(audit_log.log_id)


    # ---------- DELETE ----------

    def delete(self, log_id: UUID) -> None:
        """
        Hard delete. Prefer update_outcome for audit purposes.

        Parameters
        ----------
        log_id

        Returns
        -------

        """
        with db_transaction() as conn:
            cursor = conn.execute(
                "DELETE FROM audit_logs WHERE log_id = ?", (str(log_id),)
            )
            if cursor.rowcount == 0:
                raise AuditLogNotFoundError(f"No audit logs with id {log_id}")