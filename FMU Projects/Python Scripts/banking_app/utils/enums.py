from enum import Enum


class AccountType(str, Enum):
    """
    Enumeration for account type
    """
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"
    FIXED_DEPOSIT = "FIXED_DEPOSIT"
    LOAN = "LOAN"


class AccountStatus(str, Enum):
    """
    Enumeration for account status
    """
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    FIXED_DEPOSIT = "FIXED_DEPOSIT"
    LOAN = "LOAN"


class TransactionType(str, Enum):
    """
    Enumeration for transaction type.
    """
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER_IN = "TRANSFER_IN"
    TRANSFER_OUT = "TRANSFER_OUT"
    FEE = "FEE"
    INTEREST = "INTEREST"


class TransactionStatus(str, Enum):
    """
    Enumeration for transaction status.
    """
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REVERSED = "REVERSED"


class CustomerStatus(str, Enum):
    """
    Enumeration for customer status.
    """
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    CLOSED = "CLOSED"


class CardType(str, Enum):
    """
    Enumeration for card type.
    """
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class CardStatus(str, Enum):
    """
    Enumeration for card status.
    """
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    EXPIRED = "EXPIRED"


class UserStatus(str, Enum):
    """
    Enumeration for user status
    """
    ACTIVE = "ACTIVE"
    DEACTIVATED = "DEACTIVATED"
    TERMINATED = "TERMINATED"


class AuditAction(str, Enum):
    """
    Enumeration for audit actions.
    """
    # Authentication / session
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGED = "password_changed"

    # Accounts
    ACCOUNT_CREATED = "account_created"
    ACCOUNT_UPDATED = "account_updated"
    ACCOUNT_CLOSED = "account_closed"
    ACCOUNT_FROZEN = "account_frozen"
    ACCOUNT_UNFROZEN = "account_unfrozen"

    # Customers / users
    CUSTOMER_CREATED = "customer_created"
    CUSTOMER_UPDATED = "customer_updated"
    CUSTOMER_DELETED = "customer_deleted"

    # Money movement
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER_CREATED = "transfer_created"
    TRANSFER_CANCELLED = "transfer_cancelled"

    # Cards
    CARD_ISSUED = "card_issued"
    CARD_ACTIVATED = "card_activated"
    CARD_BLOCKED = "card_blocked"
    CARD_UNBLOCKED = "card_unblocked"
    CARD_REPLACED = "card_replaced"
    CARD_CANCELLED = "card_cancelled"

    # Administrative
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"
    SETTINGS_CHANGED = "settings_changed"

    # Audit / compliance
    AUDIT_LOG_VIEWED = "audit_log_viewed"
    AUDIT_LOG_EXPORTED = "audit_log_exported"


class AuditOutcome(str, Enum):
    """
    Enumeration for audit outcome.
    """
    SUCCESS = "success"
    FAILURE = "failure"
    DENIED = "denied"


class Permission(str, Enum):
    """Permissions that can be granted to a user role."""

    # Authentication / own profile
    LOGIN = "login"
    LOGOUT = "logout"
    CHANGE_PASSWORD = "change_password"

    # Accounts
    VIEW_OWN_ACCOUNT = "view_own_account"
    VIEW_ANY_ACCOUNT = "view_any_account"
    CREATE_ACCOUNT = "create_account"
    UPDATE_ACCOUNT = "update_account"
    CLOSE_ACCOUNT = "close_account"
    FREEZE_ACCOUNT = "freeze_account"
    UNFREEZE_ACCOUNT = "unfreeze_account"

    # Customers
    VIEW_OWN_CUSTOMER = "view_own_customer"
    VIEW_ANY_CUSTOMER = "view_any_customer"
    CREATE_CUSTOMER = "create_customer"
    UPDATE_CUSTOMER = "update_customer"
    DELETE_CUSTOMER = "delete_customer"

    # Money movement
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    CREATE_TRANSFER = "create_transfer"
    CANCEL_TRANSFER = "cancel_transfer"

    # Cards
    VIEW_OWN_CARD = "view_own_card"
    VIEW_ANY_CARD = "view_any_card"
    ISSUE_CARD = "issue_card"
    ACTIVATE_CARD = "activate_card"
    BLOCK_CARD = "block_card"
    UNBLOCK_CARD = "unblock_card"
    REPLACE_CARD = "replace_card"
    CANCEL_CARD = "cancel_card"

    # User / role administration
    VIEW_USERS = "view_users"
    CREATE_USER = "create_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    GRANT_PERMISSION = "grant_permission"
    REVOKE_PERMISSION = "revoke_permission"

    # System administration
    CHANGE_SETTINGS = "change_settings"

    # Audit / compliance
    VIEW_AUDIT_LOG = "view_audit_log"
    EXPORT_AUDIT_LOG = "export_audit_log"