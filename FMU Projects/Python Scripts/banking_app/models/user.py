from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from banking_app.utils.enums import Permission, UserStatus
from banking_app.models.user_role import UserRole, get_permissions_for_role

from banking_app.utils.exceptions import AuthorisationError


@dataclass
class User:
    """
    Represents an authenticated application user.

    A User represents login/authorization identity.
    Customer represents the banking customer.
    """

    user_id: UUID
    username: str
    password_hash: str
    user_role: UserRole
    customer_id: Optional[UUID] = None
    user_status: UserStatus = UserStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_login_at: Optional[datetime] = None

    def has_permission(self, permission: Permission) -> bool:
        """Check whether this user has a specific permission."""
        return permission in get_permissions_for_role(self.user_role)

    def require_permission(self, permission: Permission) -> None:
        """
        Raise an exception if the user doesn't have the permission.
        """
        if not self.has_permission(permission):
            raise AuthorisationError(
                f"User '{self.username}' with role '{self.user_role.value}' "
                f"does not have permission '{permission.value}'."
            )

    def is_customer(self) -> bool:
        """
        Determine whether the user is a customer.
        Customers can only access their own data.

        Returns
        -------

        """
        return self.user_role == UserRole.CUSTOMER

    def is_staff(self) -> bool:
        """
        Check if the user is staff or not.
        Staff users have varying levels of access to data.

        Returns
        -------

        """
        return self.user_role in {
            UserRole.TELLER,
            UserRole.MANAGER,
            UserRole.ADMIN,
            UserRole.AUDITOR,
        }

    def can_access_customer(self, customer_id: UUID) -> bool:
        """
        Determine whether the user can access a customer's data.

        Customers can only access their own data.
        Staff can access any customer depending on their role.
        """
        if self.user_role == UserRole.CUSTOMER:
            return self.customer_id == customer_id

        return self.has_permission(Permission.VIEW_ANY_CUSTOMER)


    @staticmethod
    def from_db_row(row: dict) -> "User":
        """Reconstruct an Account from a DB row (dict-like: sqlite3.Row, psycopg2 DictRow, etc.)."""
        return User(
            user_id=UUID(row["user_id"]),
            username=row["username"],
            password_hash=row["password_hash"],
            user_role=UserRole(row["user_role"]),
            customer_id=UUID(row["customer_id"]),
            user_status=UserStatus(row["user_status"]),
            created_at=row["created_at"].fromisoformat(),
            last_login_at=row["last_login_at"].fromisoformat(),
        )