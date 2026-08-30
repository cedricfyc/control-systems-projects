"""
Database connection handling
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path


DB_PATH = Path(__file__).parent / "database.db"

SCHEMA = """

CREATE TABLE IF NOT EXISTS customers (
    customer_id      TEXT PRIMARY KEY,
    first_name       TEXT NOT NULL,
    middle_name      TEXT,
    last_name        TEXT NOT NULL,
    date_of_birth    TEXT NOT NULL,
    national_id      TEXT NOT NULL,
    email            TEXT,
    phone_number     TEXT,
    address_street   TEXT,
    address_city     TEXT,
    address_zip      TEXT,
    address_state    TEXT,
    address_country  TEXT,
    created_at       TEXT NOT NULL,
    customer_status  TEXT NOT NULL,
    kyc_verified     INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_customers_customer_status
    ON customers(customer_status);


CREATE TABLE IF NOT EXISTS users (
    user_id        TEXT PRIMARY KEY,
    customer_id    TEXT,
    username       TEXT NOT NULL UNIQUE,
    password_hash  TEXT NOT NULL,
    user_role      TEXT NOT NULL,
    user_status    TEXT NOT NULL,
    created_at     TEXT NOT NULL,
    last_login_at  TEXT
);

CREATE INDEX IF NOT EXISTS idx_users_customer_id
    ON users(customer_id);


CREATE TABLE IF NOT EXISTS accounts (
    account_id       TEXT PRIMARY KEY,
    account_number   TEXT UNIQUE NOT NULL,
    customer_id      TEXT NOT NULL,
    account_type     TEXT NOT NULL,
    balance          TEXT NOT NULL,
    currency         TEXT NOT NULL,
    interest_rate    TEXT,
    overdraft_limit  TEXT,
    min_balance      TEXT NOT NULL,
    pin_hash         TEXT NOT NULL,
    account_status   TEXT NOT NULL,
    created_at       TEXT NOT NULL,
    version          INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);

CREATE INDEX IF NOT EXISTS idx_accounts_customer_id
    ON accounts(customer_id);

CREATE INDEX IF NOT EXISTS idx_accounts_status
    ON accounts(account_status);

CREATE INDEX IF NOT EXISTS idx_accounts_account_type
    ON accounts(account_type);


CREATE TABLE IF NOT EXISTS transactions (
    transaction_id          TEXT PRIMARY KEY,
    account_id              TEXT NOT NULL,
    transaction_type        TEXT NOT NULL,
    amount                  TEXT NOT NULL,
    balance_after           TEXT NOT NULL,
    timestamp               TEXT NOT NULL,
    transaction_status      TEXT NOT NULL,
    reference_id            TEXT NOT NULL,
    description             TEXT,
    counterparty_account_id TEXT,
    FOREIGN KEY (account_id)
        REFERENCES accounts(account_id),
    FOREIGN KEY (counterparty_account_id)
        REFERENCES accounts(account_id)
);

CREATE INDEX IF NOT EXISTS idx_transactions_account_id
    ON transactions(account_id);

CREATE INDEX IF NOT EXISTS idx_transactions_reference_id
    ON transactions(reference_id);


CREATE TABLE IF NOT EXISTS audit_logs (
    log_id         TEXT PRIMARY KEY,
    user_id        TEXT NOT NULL,
    audit_action   TEXT NOT NULL,
    audit_outcome  TEXT NOT NULL,
    ip_address     TEXT,
    details        TEXT,
    timestamp      TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id
    ON audit_logs(user_id);
    
    
CREATE TABLE IF NOT EXISTS cards (
    card_id             TEXT PRIMARY KEY,
    account_id          TEXT NOT NULL UNIQUE,
    account_number      TEXT NOT NULL,
    card_type           TEXT NOT NULL,
    card_status         TEXT NOT NULL,
    expiry_date         TEXT NOT NULL,
    cvv_hash            TEXT NOT NULL
    FOREIGN KEY (account_id)
        REFERENCES accounts(account_id),
);

CREATE INDEX IF NOT EXISTS idx_cards_card_id
    ON cards(card_id);

"""


def get_connection() -> sqlite3.Connection:
    """
    Return a connection with row factory set
    so that rows behave like dicts
    Returns
    -------

    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """
    Create tables if they do not already exist
    Returns
    -------

    """
    with get_connection() as conn:
        # execute script within sqlite
        conn.executescript(SCHEMA)


@contextmanager
def db_transaction():
    """
    Context manager for an atomic block of work.
    Commits on success, rolls back on any exception.

    Usage:
        with transaction() as conn:
            conn.execute(...)
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()