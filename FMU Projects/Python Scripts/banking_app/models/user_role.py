from enum import Enum
from typing import FrozenSet

from banking_app.utils.enums import Permission


class UserRole(str, Enum):
    """Predefined roles in the banking system."""

    GUEST = "guest"
    CUSTOMER = "customer"
    TELLER = "teller"
    MANAGER = "manager"
    ADMIN = "admin"
    AUDITOR = "auditor"


ROLE_PERMISSIONS: dict[UserRole, FrozenSet[Permission]] = {
    UserRole.GUEST: frozenset({
        # GUEST -> CUSTOMER or STAFF after login
        # Authentication
        Permission.LOGIN,
    }),

    UserRole.CUSTOMER: frozenset({
        # Authentication
        Permission.LOGIN,
        Permission.LOGOUT,
        Permission.CHANGE_PASSWORD,

        # Own customer/account/card information
        Permission.VIEW_OWN_CUSTOMER,
        Permission.VIEW_OWN_ACCOUNT,
        Permission.VIEW_OWN_CARD,

        # Money movement
        Permission.DEPOSIT,
        Permission.WITHDRAW,
        Permission.CREATE_TRANSFER,

        # Own card operations
        Permission.ACTIVATE_CARD,
        Permission.BLOCK_CARD,
        Permission.UNBLOCK_CARD,
    }),

    UserRole.TELLER: frozenset({
        # Authentication
        Permission.LOGIN,
        Permission.LOGOUT,
        Permission.CHANGE_PASSWORD,

        # Accounts
        Permission.VIEW_ANY_ACCOUNT,
        Permission.CREATE_ACCOUNT,
        Permission.UPDATE_ACCOUNT,
        Permission.CLOSE_ACCOUNT,
        Permission.FREEZE_ACCOUNT,
        Permission.UNFREEZE_ACCOUNT,

        # Customers
        Permission.VIEW_ANY_CUSTOMER,
        Permission.CREATE_CUSTOMER,
        Permission.UPDATE_CUSTOMER,

        # Money movement
        Permission.DEPOSIT,
        Permission.WITHDRAW,
        Permission.CREATE_TRANSFER,
        Permission.CANCEL_TRANSFER,

        # Cards
        Permission.VIEW_ANY_CARD,
        Permission.ISSUE_CARD,
        Permission.ACTIVATE_CARD,
        Permission.BLOCK_CARD,
        Permission.UNBLOCK_CARD,
        Permission.REPLACE_CARD,
        Permission.CANCEL_CARD,
    }),

    UserRole.MANAGER: frozenset({
        # Authentication
        Permission.LOGIN,
        Permission.LOGOUT,
        Permission.CHANGE_PASSWORD,

        # Accounts
        Permission.VIEW_ANY_ACCOUNT,
        Permission.CREATE_ACCOUNT,
        Permission.UPDATE_ACCOUNT,
        Permission.CLOSE_ACCOUNT,
        Permission.FREEZE_ACCOUNT,
        Permission.UNFREEZE_ACCOUNT,

        # Customers
        Permission.VIEW_ANY_CUSTOMER,
        Permission.CREATE_CUSTOMER,
        Permission.UPDATE_CUSTOMER,
        Permission.DELETE_CUSTOMER,

        # Money movement
        Permission.DEPOSIT,
        Permission.WITHDRAW,
        Permission.CREATE_TRANSFER,
        Permission.CANCEL_TRANSFER,

        # Cards
        Permission.VIEW_ANY_CARD,
        Permission.ISSUE_CARD,
        Permission.ACTIVATE_CARD,
        Permission.BLOCK_CARD,
        Permission.UNBLOCK_CARD,
        Permission.REPLACE_CARD,
        Permission.CANCEL_CARD,

        # User administration
        Permission.VIEW_USERS,
        Permission.CREATE_USER,
        Permission.UPDATE_USER,

        # Audit
        Permission.VIEW_AUDIT_LOG,
    }),

    UserRole.ADMIN: frozenset({
        # Authentication
        Permission.LOGIN,
        Permission.LOGOUT,
        Permission.CHANGE_PASSWORD,

        # Accounts
        Permission.VIEW_ANY_ACCOUNT,
        Permission.CREATE_ACCOUNT,
        Permission.UPDATE_ACCOUNT,
        Permission.CLOSE_ACCOUNT,
        Permission.FREEZE_ACCOUNT,
        Permission.UNFREEZE_ACCOUNT,

        # Customers
        Permission.VIEW_ANY_CUSTOMER,
        Permission.CREATE_CUSTOMER,
        Permission.UPDATE_CUSTOMER,
        Permission.DELETE_CUSTOMER,

        # Money movement
        Permission.DEPOSIT,
        Permission.WITHDRAW,
        Permission.CREATE_TRANSFER,
        Permission.CANCEL_TRANSFER,

        # Cards
        Permission.VIEW_ANY_CARD,
        Permission.ISSUE_CARD,
        Permission.ACTIVATE_CARD,
        Permission.BLOCK_CARD,
        Permission.UNBLOCK_CARD,
        Permission.REPLACE_CARD,
        Permission.CANCEL_CARD,

        # User administration
        Permission.VIEW_USERS,
        Permission.CREATE_USER,
        Permission.UPDATE_USER,
        Permission.DELETE_USER,
        Permission.GRANT_PERMISSION,
        Permission.REVOKE_PERMISSION,

        # System administration
        Permission.CHANGE_SETTINGS,

        # Audit
        Permission.VIEW_AUDIT_LOG,
        Permission.EXPORT_AUDIT_LOG,
    }),

    UserRole.AUDITOR: frozenset({
        # Authentication
        Permission.LOGIN,
        Permission.LOGOUT,
        Permission.CHANGE_PASSWORD,

        # Read-only access
        Permission.VIEW_ANY_ACCOUNT,
        Permission.VIEW_ANY_CUSTOMER,
        Permission.VIEW_ANY_CARD,
        Permission.VIEW_USERS,

        # Audit
        Permission.VIEW_AUDIT_LOG,
        Permission.EXPORT_AUDIT_LOG,
    }),
}


def get_permissions_for_role(role: UserRole) -> FrozenSet[Permission]:
    """Return the fixed permissions assigned to a role."""
    return ROLE_PERMISSIONS[role]