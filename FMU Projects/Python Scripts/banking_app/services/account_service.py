from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from banking_app.services.audit_log_service import AuditLogService
from banking_app.services.auth_service import AuthorisationService

from banking_app.models.account import Account
from banking_app.models.audit_log import AuditLog
from banking_app.models.user import User

from banking_app.utils.enums import Permission

from banking_app.repositories.account_repo import AccountRepository
from banking_app.repositories.customer_repo import CustomerRepository

from banking_app.utils.enums import (
    AccountStatus,
    AccountType,
    AuditOutcome,
    AuditAction,
)

"""Account service for both customers and staff"""


class AccountService:
    """
        Business logic for Account operations.

        This service is responsible for:
        - authorization
        - validation
        - applying business rules
        - constructing Account objects
        - coordinating repositories
        - triggering audit events

        It must not contain SQL.
    """

    def __init__(
            self,
            account_repository: AccountRepository,
            customer_repository: CustomerRepository,
            audit_log_service: AuditLogService
    ):
        self.account_repository = account_repository
        self.customer_repository = customer_repository
        self.audit_log_service = audit_log_service

    def create_account(
            self,
            current_user: User,
            customer_id: UUID,
            account_type: AccountType,
            pin_hash: str,
            currency: str = "EUR",
            initial_deposit: Decimal = Decimal("0.00"),
            interest_rate: Optional[Decimal] = None,
            overdraft_limit: Optional[Decimal] = None,
            min_balance: Decimal = Decimal("0.00"),
    ) -> Account:
        """
        Create a new bank account.

        The caller must have CREATE_ACCOUNT permission.

        Parameters
        ----------
        current_user
            User creating account.
        customer_id
            Possible customer ID.
        account_type
            Account type.
        pin_hash
            PIN to be encrypted.
        currency
            Currency of account
        initial_deposit
            Initial deposit to account.
        interest_rate
            Interest rate of account.
        overdraft_limit
            Overdraft limit of account.
        min_balance
            Minimum balance of account.

        Returns
        -------
        Account
            The newly created account.

        Raises
        ------
        AuthorisationError
            If the current user cannot create accounts.
        ValueError
            If any business rule or validation fails.
        """

        # Check if current user has the rights to account creation
        AuthorisationService.require_permission(
            current_user,
            Permission.CREATE_ACCOUNT,
        )

        # Validate inputs

        if initial_deposit < Decimal("0.00"):
            raise ValueError(
                "Initial deposit cannot be negative."
            )

        if min_balance < Decimal("0.00"):
            raise ValueError(
                "Minimum balance cannot be negative."
            )

        if overdraft_limit is not None and overdraft_limit < Decimal("0.00"):
            raise ValueError(
                "Overdraft limit cannot be negative."
            )

        if interest_rate is not None and interest_rate < Decimal("0.00"):
            raise ValueError(
                "Interest rate cannot be negative."
            )

        currency = currency.upper()

        if len(currency) != 3:
            raise ValueError(
                "Currency must be a valid three-letter ISO code."
            )

        # Verify customer
        customer = self.customer_repository.get_by_id(customer_id)

        if customer is None:
            raise ValueError(
                f"Customer '{customer_id}' does not exist."
            )

        # Apply business rules
        if account_type == AccountType.CHECKING:
            if interest_rate is None:
                interest_rate = Decimal("0.00")

        if account_type == AccountType.SAVINGS:
            if interest_rate is None:
                raise ValueError(
                    "Savings accounts require an interest rate."
                )

        # Generate account id and account number
        account_id = uuid4()
        account_number = self._generate_account_number()

        # Initialise the account object
        account = Account(
            account_id=account_id,
            account_number=account_number,
            customer_id=customer_id,
            account_type=account_type,
            balance=initial_deposit,
            currency=currency,
            interest_rate=interest_rate,
            overdraft_limit=overdraft_limit,
            min_balance=min_balance,
            pin_hash=pin_hash,
            account_status=AccountStatus.ACTIVE,
            version=1
        )

        # Persist the account created
        created_account = self.account_repository.create(account)

        # Audit successful operation
        current_audit_log = AuditLog(
            user_id=current_user.user_id,
            audit_action=AuditAction.ACCOUNT_CREATED,
            audit_outcome=AuditOutcome.SUCCESS,
            details=f"Account created for {current_user.username}",
        )
        # Persist the audit created
        self.audit_log_service.log(current_audit_log)

        return created_account



    def _generate_account_number(self) -> str:
        """
        Generate a unique account number.

        The actual implementation should preferably delegate
        uniqueness enforcement to the database as well.

        Returns

        -------

        """
        account_count = self.account_repository.count(None)
        # Get randomised part length e.g. 8 - len(10000) = 3
        # 3 randomised numbers are added with 10000 existing accounts
        randomised_segment_length = 8 - len(str(account_count  + 1000))
        randomised_no = str(uuid4().int)[:randomised_segment_length]

        # Account number can only be numbers 1000+
        # Check database and return incremented count
        return str(randomised_no) + str(account_count + 1000)