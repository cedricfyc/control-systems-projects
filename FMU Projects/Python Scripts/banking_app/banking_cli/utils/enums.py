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


class UserRole(str, Enum):
    """
    Enumeration for user role.
    """
    CUSTOMER = "CUSTOMER"
    TELLER = "TELLER"
    ADMIN = "ADMIN"