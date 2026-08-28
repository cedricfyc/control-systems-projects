from __future__ import annotations

from banking_app.models.audit_log import AuditLog
from banking_app.repositories.audit_log_repo import AuditLogRepository


class AuditLogService:
    """
    Service responsible for creating and retrieving audit logs.

    Business services should use this service rather than creating
    AuditLog objects or interacting with the audit repository directly.
    """

    def __init__(self, audit_log_repository: AuditLogRepository):
        self.audit_log_repository = audit_log_repository

    def log(self, audit_log: AuditLog):
        """
        Service-level functionality to create an audit log

        Parameters
        ----------
        audit_log

        Returns
        -------

        """
        # Convert audit logs to primitive dict format
        # Create persistent repo to store the log
        return self.audit_log_repository.create(audit_log)

    def get_audit_logs(self):
        pass