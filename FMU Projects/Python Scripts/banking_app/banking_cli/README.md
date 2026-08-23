# Banking CLI Application

A command-line interface (CLI) application for managing banking operations — customers, accounts, transactions, and cards — built with a layered architecture for maintainability, testability, and safe handling of financial data.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Data Models](#data-models)
- [Enumerations](#enumerations)
- [Services](#services)
- [Exceptions](#exceptions)
- [Design Decisions](#design-decisions)
- [Setup](#setup)
- [Usage](#usage)
- [Roadmap](#roadmap)
- [Contributing](#contributing)

---

## Overview

The Banking CLI is a terminal-based application that simulates core banking functionality: customer onboarding, account management, deposits, withdrawals, transfers, and transaction history/reporting. It is designed with a clear separation between data models, persistence, and business logic so that the underlying storage (file-based, SQLite, PostgreSQL, etc.) can be swapped without affecting business rules.

**Goals:**
- Correctness and safety when handling monetary values
- Clear audit trail for every account-affecting action
- Extensible architecture (new account types, new transaction types, new interfaces)
- No business logic in the presentation (CLI) layer

---

## Features

- [ ] Customer registration & KYC status tracking
- [ ] Account creation (Checking, Savings, Fixed Deposit, Loan)
- [ ] Deposits, withdrawals, and transfers between accounts
- [ ] PIN/password-based authentication
- [ ] Transaction history with filtering (date range, type, status)
- [ ] Statement export (CSV)
- [ ] Interest calculation for savings/fixed deposit accounts
- [ ] Account freeze/unfreeze and closure
- [ ] Card issuance and management (optional module)
- [ ] Full audit logging of sensitive actions

> Check items off as they're implemented, or replace this with a real status table.

---

## Architecture

The application follows a **layered architecture**:

```
Presentation (CLI)
        │
        ▼
   Services (business logic)
        │
        ▼
 Repositories (data access)
        │
        ▼
   Database / Storage
```

| Layer             | Responsibility                                                                            |
|-------------------|-------------------------------------------------------------------------------------------|
| **CLI (main.py)** | Menu rendering, input capture, calling services, displaying output. No business rules.    |
| **Services**      | Business rules: validation, balance checks, interest calculation, transfer orchestration. |
| **Repositories**  | CRUD operations against the storage backend. No business logic.                           |
| **Models**        | Plain data structures shared across all layers.                                           |
| **Database**      | Connection handling and schema.                                                           |

This separation means the storage layer (e.g., SQLite → PostgreSQL) or the interface (CLI → REST API) can be replaced independently.

---

## Project Structure

```
banking_cli/
├── main.py                    # Entry point, CLI loop/menu
├── config.py                  # Constants, settings, fees, limits
├── models/
│   ├── account.py
│   ├── customer.py
│   ├── transaction.py
│   └── card.py
├── services/
│   ├── auth_service.py
│   ├── account_service.py
│   ├── transaction_service.py
│   └── report_service.py
├── repositories/
│   ├── account_repository.py
│   ├── customer_repository.py
│   └── transaction_repository.py
├── database/
│   ├── db_connector.py
│   └── schema.sql
├── utils/
│   ├── validators.py
│   ├── logger.py
│   └── exceptions.py
└── tests/
```

---

## Data Models

All monetary values use `Decimal` (never `float`) to avoid floating-point rounding errors. All primary keys use `UUID` to avoid collisions and avoid leaking sequential record counts.

### Customer

| Field           | Type                   | Notes                                        |
|-----------------|------------------------|----------------------------------------------|
| `customer_id`   | `UUID`                 | Primary key                                  |
| `first_name`    | `str`                  |                                              |
| `last_name`     | `str`                  |                                              |
| `date_of_birth` | `date`                 |                                              |
| `email`         | `str`                  | Validated format                             |
| `phone_number`  | `str`                  | Stored as string (leading zeros, formatting) |
| `address`       | `Address` (nested)     | street, city, state, zip, country            |
| `national_id`   | `str`                  | Encrypted at rest                            |
| `created_at`    | `datetime`             | UTC                                          |
| `status`        | `Enum(CustomerStatus)` | ACTIVE, SUSPENDED, CLOSED                    |
| `kyc_verified`  | `bool`                 |                                              |

### Account

| Field             | Type                  | Notes                                  |
|-------------------|-----------------------|----------------------------------------|
| `account_id`      | `UUID`                | Primary key                            |
| `account_number`  | `str`                 | Human-facing identifier                |
| `customer_id`     | `UUID` (FK)           |                                        |
| `account_type`    | `Enum(AccountType)`   | CHECKING, SAVINGS, FIXED_DEPOSIT, LOAN |
| `balance`         | `Decimal`             | Never `float`                          |
| `currency`        | `str` (ISO 4217)      | e.g. "USD", "EUR"                      |
| `interest_rate`   | `Decimal`             | Nullable                               |
| `status`          | `Enum(AccountStatus)` | ACTIVE, FROZEN, CLOSED, DORMANT        |
| `created_at`      | `datetime`            | UTC                                    |
| `overdraft_limit` | `Decimal`             | Nullable                               |
| `min_balance`     | `Decimal`             |                                        |
| `pin_hash`        | `str`                 | Hashed, never plaintext                |
| `version`         | `int`                 | Optimistic concurrency control         |

### Transaction

| Field                     | Type                      | Notes                                                         |
|---------------------------|---------------------------|---------------------------------------------------------------|
| `transaction_id`          | `UUID`                    | Primary key                                                   |
| `account_id`              | `UUID` (FK)               |                                                               |
| `type`                    | `Enum(TransactionType)`   | DEPOSIT, WITHDRAWAL, TRANSFER_IN, TRANSFER_OUT, FEE, INTEREST |
| `amount`                  | `Decimal`                 | Always positive; sign inferred from type                      |
| `balance_after`           | `Decimal`                 | Snapshot for audit trail                                      |
| `timestamp`               | `datetime`                | UTC                                                           |
| `status`                  | `Enum(TransactionStatus)` | PENDING, COMPLETED, FAILED, REVERSED                          |
| `reference_id`            | `str`                     | Links paired transfer transactions                            |
| `description`             | `Optional[str]`           |                                                               |
| `counterparty_account_id` | `Optional[UUID]`          | Set for transfers                                             |

### Card *(optional module)*

| Field         | Type               | Notes                     |
|---------------|--------------------|---------------------------|
| `card_id`     | `UUID`             | Primary key               |
| `account_id`  | `UUID` (FK)        |                           |
| `card_number` | `str`              | Masked on display         |
| `expiry_date` | `date`             |                           |
| `cvv_hash`    | `str`              | Never stored in plaintext |
| `card_type`   | `Enum(CardType)`   | DEBIT, CREDIT             |
| `status`      | `Enum(CardStatus)` | ACTIVE, BLOCKED, EXPIRED  |

### AuditLog

| Field        | Type            | Notes                                  |
|--------------|-----------------|----------------------------------------|
| `log_id`     | `UUID`          | Primary key                            |
| `actor_id`   | `UUID`          | Who performed the action               |
| `action`     | `str` / `Enum`  | LOGIN, TRANSFER, PASSWORD_CHANGE, etc. |
| `timestamp`  | `datetime`      | UTC                                    |
| `ip_address` | `Optional[str]` | If a remote/API layer is added         |
| `success`    | `bool`          |                                        |
| `details`    | `dict` / `JSON` | Additional context                     |

---

## Enumerations

| Enum                | Values                                                        |
|---------------------|---------------------------------------------------------------|
| `AccountType`       | CHECKING, SAVINGS, FIXED_DEPOSIT, LOAN                        |
| `AccountStatus`     | ACTIVE, FROZEN, CLOSED, DORMANT                               |
| `TransactionType`   | DEPOSIT, WITHDRAWAL, TRANSFER_IN, TRANSFER_OUT, FEE, INTEREST |
| `TransactionStatus` | PENDING, COMPLETED, FAILED, REVERSED                          |
| `CustomerStatus`    | ACTIVE, SUSPENDED, CLOSED                                     |
| `CardType`          | DEBIT, CREDIT                                                 |
| `CardStatus`        | ACTIVE, BLOCKED, EXPIRED                                      |
| `UserRole`          | CUSTOMER, TELLER, ADMIN                                       |

---

## Services

| Service              | Responsibility                                                                                          |
|----------------------|---------------------------------------------------------------------------------------------------------|
| `AuthService`        | Login, PIN/password verification, session/token management                                              |
| `AccountService`     | Create/close accounts, balance inquiry, freeze/unfreeze                                                 |
| `TransactionService` | Deposit, withdraw, transfer (atomic operations); enforces min balance, overdraft, and daily limit rules |
| `ReportService`      | Statement generation, transaction history filtering, CSV export                                         |

Repositories (`AccountRepository`, `CustomerRepository`, `TransactionRepository`) perform CRUD only — no business logic — which keeps the storage backend swappable.

---

## Exceptions

Defined in `utils/exceptions.py`:

- `InsufficientFundsError`
- `AccountNotFoundError`
- `AccountFrozenError`
- `InvalidPinError`
- `DuplicateTransactionError`
- `AuthenticationError`

Services raise these; the CLI layer catches them and displays user-friendly messages.

---

## Design Decisions

**Money handling**
Use `Decimal` for all monetary fields. Alternatively, store amounts as integer minor units (cents) if avoiding `Decimal` entirely is preferred — both are valid, common banking patterns. `float` is never used for currency due to rounding errors.

**Identifiers**
Internal primary keys use `UUID`. Each account additionally has a human-facing `account_number` (formatted string), kept separate from the internal ID.

**Sensitive data**
PINs, passwords, and CVVs are stored only as hashes (e.g., bcrypt/argon2), never in plaintext. National ID/SSN fields are encrypted at rest and masked on display.

**Timestamps**
All timestamps are timezone-aware `datetime` values stored in UTC, never naive datetimes or raw strings.

**Concurrency**
Accounts include a `version` field for optimistic concurrency control, preventing race conditions on simultaneous balance updates.

**Configuration**
Interest rates, fees, and transaction limits live in `config.py` (or an external config file), not hardcoded in business logic.

---

## Setup

```bash
# Clone the repository
git clone <repo-url>
cd banking_cli

# Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python database/init_db.py

# Run the application
python main.py
```

---

## Usage

```
$ python main.py

=== Banking CLI ===
1. Login
2. Register New Customer
3. Exit
> 1

Enter account number: 
Enter PIN: 

=== Main Menu ===
1. View Balance
2. Deposit
3. Withdraw
4. Transfer
5. Transaction History
6. Logout
>
```

*(Replace with actual menu flow once implemented.)*

---

## Roadmap

- [ ] Multi-currency support with exchange rate service
- [ ] Loan account amortization schedule
- [ ] REST API layer alongside CLI
- [ ] Two-factor authentication
- [ ] Automated interest posting (scheduled job)

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit changes with clear messages
4. Open a pull request

Please ensure new code includes corresponding tests under `tests/` and does not introduce `float` usage for monetary values.