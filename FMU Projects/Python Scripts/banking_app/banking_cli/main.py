from uuid import uuid4
from decimal import Decimal

from banking_app.database.db_connector import init_db

from banking_app.models.user import User
from banking_app.models.customer import Customer
from banking_app.models.user_role import UserRole

from banking_app.repositories.account_repo import AccountRepository
from banking_app.repositories.audit_log_repo import AuditLogRepository
from banking_app.repositories.customer_repo import CustomerRepository

from banking_app.services.account_service import AccountService
from banking_app.services.audit_service import AuditLogService

from datetime import date

from banking_app.utils.enums import AccountType


def main():
    init_db()

    account_repository = AccountRepository()
    customer_repository = CustomerRepository()
    audit_log_repo = AuditLogRepository()
    audit_log_service = AuditLogService(audit_log_repo)
    customer_id = uuid4()
    current_customer = Customer(
        customer_id=customer_id,
        first_name="Cedric",
        last_name="Fong",
        middle_name="",
        date_of_birth=date(2023, 9, 23),
        national_id="Mauritius"
    )
    customer_repository.create(
        current_customer
    )

    current_user = User(
        user_id=uuid4(),
        username="Cedric",
        password_hash="asdasd",
        role=UserRole.ADMIN,
    )

    account_service = AccountService(
        account_repository,
        customer_repository,
        audit_log_service,
    )

    account_service.create_account(
        account_type=AccountType.SAVINGS,
        customer_id=customer_id,
        pin_hash="hello world",
        current_user=current_user,
        interest_rate=Decimal("0.69")
    )

if __name__ == "__main__":
    main()