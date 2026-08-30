from banking_app.repositories.account_repo import AccountRepository
from banking_app.repositories.user_repo import UserRepository
from banking_app.models.user import User

from typing import Optional
from uuid import UUID


class AuthenticationService:

    def __init__(self,
                 user_repository: UserRepository,
                 account_repository: AccountRepository):
        self.user_repository = user_repository
        self.account_repository = account_repository


    def login_user(self, username: Optional[str], user_id: Optional[UUID], password_hash: str) -> None:
        pass

    def logout_user(self,  username: Optional[str], user_id: Optional[UUID], password_hash: str) -> None:
        pass