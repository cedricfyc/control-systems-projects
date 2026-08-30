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

    # -----------------------------------------------------------
    #                          CREATE
    # -----------------------------------------------------------


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

    # -----------------------------------------------------------
    #                          READ
    # -----------------------------------------------------------

    def get_all_audit_logs(self):
        pass

    def get_audit_logs_by_id(self):
        pass

    def search_audit_logs(self):
        pass

    def get_all_audit_logs_by_outcome(self):
        pass

    # -----------------------------------------------------------
    #                          UPDATE
    # -----------------------------------------------------------

    def update_audit_log(self, audit_log: AuditLog) -> AuditLog:
        pass

    # -----------------------------------------------------------
    #                          DELETE
    # -----------------------------------------------------------