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
    phone_number     TEXT NOT NULL,
    street           TEXT,
    city             TEXT NOT NULL,
    zip              TEXT,
    state            TEXT,
    country          TEXT NOT NULL,
    created_at       TEXT NOT NULL,
    customer_status  TEXT NOT NULL,
    kyc_verified     INTEGER NOT NULL DEFAULT 0
);  

CREATE INDEX IF NOT EXISTS idx_customers_customer_id
    ON customers(customer_id);
    
CREATE INDEX IF NOT EXISTS idx_customers_customer_status
    ON customers(customer_status);

CREATE TABLE IF NOT EXISTS accounts (
    account_id       TEXT PRIMARY KEY,
    account_number   TEXT UNIQUE NOT NULL,
    customer_id      TEXT NOT NULL,
    FOREIGN KEY (customer_id) 
        REFERENCES customers(customer_id)),
    account_type     TEXT NOT NULL,
    balance          TEXT NOT NULL,
    currency         TEXT NOT NULL,
    interest_rate    TEXT,
    overdraft_limit  TEXT,
    min_balance      TEXT NOT NULL,
    pin_hash         TEXT NOT NULL,
    account_status   TEXT NOT NULL,
    created_at       TEXT NOT NULL,
    version          INTEGER NOT NULL DEFAULT 0
);    

CREATE INDEX IF NOT EXISTS idx_accounts_customer_id
    ON accounts(customer_id);
    
CREATE INDEX IF NOT EXISTS idx_accounts_status
    ON accounts(account_status);
    
CREATE INDEX IF NOT EXISTS idx_accounts_account_type
    ON accounts(account_type);
    


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
def transaction():
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