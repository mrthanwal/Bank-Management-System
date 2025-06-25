import sqlite3

def init_db():
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # ACCOUNTS TABLE
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        account_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        balance REAL DEFAULT 0,
        account_type TEXT CHECK(account_type IN ('Savings', 'Current')) NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    ''')

    # TRANSACTIONS TABLE
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL,
        type TEXT CHECK(type IN ('deposit', 'withdraw', 'FD','transfer_d','transfer_w')) NOT NULL,
        amount REAL NOT NULL,
        performed_by TEXT NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (account_id) REFERENCES accounts(account_id)
    )
    ''')

    # FIXED DEPOSITS TABLE
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fd (
        fd_id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        interest_rate REAL NOT NULL,
        duration_days INTEGER NOT NULL,
        start_date TEXT NOT NULL,
        FOREIGN KEY (account_id) REFERENCES accounts(account_id)
    )
    ''')

    # ADMINS TABLE
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT,
        role TEXT CHECK(role IN ('clerk', 'manager')) NOT NULL
    )
    ''')

    # LOANS TABLE
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS loans (
        loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        interest_rate REAL NOT NULL,
        duration_months INTEGER NOT NULL,
        approved_by TEXT NOT NULL,
        approved_date TEXT NOT NULL,
        FOREIGN KEY (account_id) REFERENCES accounts(account_id)
    )
    ''')

    # CLOSED ACCOUNTS TABLE
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS closed_accounts (
        account_id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        closed_at TEXT DEFAULT CURRENT_TIMESTAMP,
        reason TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")

if __name__ == '__main__':
    init_db()
