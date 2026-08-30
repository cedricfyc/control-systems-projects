from banking_app.repositories.user_repo import UserRepository
from banking_app.services.customer_service import CustomerService

from banking_app.models.customer import Customer
from banking_app.models.user import User, PermissionChecker
from banking_app.models.user_role import UserRole

from banking_app.utils.enums import UserStatus
from banking_app.utils.enums import Permission

from uuid import UUID
from typing import Optional, List

"""
User service is for the internal workings of the banking application.
User roles are declared based on the username and password. The customer
service is linked to the user service as long as the login is non-staff
Staff do not need customer IDs, but need user IDs for auditing and
authentication. Customers have both user ID and customer ID. Customer
accounts are created by the staff who have to authenticate themselves first.

Everyone starts as a GUEST. Then, they can become any assigned ROLE within
the system. A system admin exists by default within the system. It is the all
powerful admin 007.
"""


class UserService:

    def __init__(self, current_user: User, user_repository: UserRepository):
        self.current_user = current_user
        self.user_repository = user_repository
        self.permission_checker = PermissionChecker()

    # -----------------------------------------------------------
    #                          CREATE
    # -----------------------------------------------------------

    def register_user(self,
                      username: str,
                      password_hash: str,
                      user_role: UserRole,
                      customer_id: Optional[UUID] = None,
                      ) -> Optional[User]:

        # Insert error checking, e.g. username uniqueness, etc.
        # INCOMPLETE

        # Check for permission first
        if PermissionChecker.require_permission(
                self.current_user,
                Permission.CREATE_USER):

            created_user = User(
                username=username,
                password_hash=password_hash,
                user_role=user_role,
                customer_id=customer_id if user_role is UserRole.CUSTOMER else None,
            )
            self.user_repository.create(created_user)

            return created_user

        else:
            return None

    # -----------------------------------------------------------
    #                          READ
    # -----------------------------------------------------------

    def get_user_details(self,
                         user_id: Optional[UUID],
                         username: Optional[str]) -> User:
        pass

    def search_user(self,
            user_id: Optional[UUID] = None,
            username: Optional[str] = None,
            user_role: Optional[UserRole] = None,
            user_status: Optional[UserStatus] = None,
            limit: int = 100,
            offset: int = 0) -> List [User]:
        pass

    # -----------------------------------------------------------
    #                          UPDATE
    # -----------------------------------------------------------

    def change_password(self,
                        user_id: Optional[UUID],
                        username: Optional[str],
                        password_hash: str):
        pass

    def change_user_status(self,
                           user_id: Optional[UUID],
                           username: Optional[str]) -> User:
        pass



    # -----------------------------------------------------------
    #                          DELETE
    # -----------------------------------------------------------

    def delete_user(self, user_id: Optional[UUID]):
        # Staff with sufficient rights can delete the user profile
        pass