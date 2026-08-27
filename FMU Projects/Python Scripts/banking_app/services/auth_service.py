from uuid import UUID

from banking_app.utils.enums import Permission
from banking_app.models.user import User
from banking_app.utils.exceptions import AuthorisationError


class AuthorisationService:
    """
    Handles application authorisation.
    """

    @staticmethod
    def has_permission(user: User, permission: Permission) -> bool:
        """
        Makes the user method static

        Parameters
        ----------
        user
        permission

        Returns
        -------

        """
        return user.has_permission(permission)


    @staticmethod
    def require_permission(user: User, permission: Permission) -> None:
        """
        Checks for permission of the user and outputs authorisation status.

        Parameters
        ----------
        user
        permission

        Returns
        -------

        """

        if not user.has_permission(permission):
            raise AuthorisationError(
                f"User '{user.username}' with role "
                f"'{user.role.value}' lacks permission "
                f"'{permission.value}'."
            )


    @staticmethod
    def require_customer_access(user: User, target_customer_id: UUID) -> bool:
        """
        Checks if user has access to customer data.
        If customer with the right id, allow access.

        Parameters
        ----------
        user
        target_customer_id

        Returns
        -------

        """

        # Case of customer
        if user.role == user.role.CUSTOMER:
            if user.customer_id != target_customer_id:
                raise AuthorisationError(
                    "Customers can only have access to their own data."
                )
            return True

        # Case of staff roles
        if not user.has_permission(Permission.VIEW_ANY_CUSTOMER):
            raise AuthorisationError(
                "User is not authorized to access customer data."
            )
        # Staff has access
        else:
            return True