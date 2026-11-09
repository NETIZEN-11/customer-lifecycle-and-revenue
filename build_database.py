"""
build_database.py
Initializes and populates the SQLite analytical database (retail_analytics.db)
from preprocessed CSVs in data/ and executes schema indexes and validation.
"""
import os
import sqlite3
import time
import pandas as pd

DB_PATH = "retail_analytics.db"
LFS_BACKUP_PATH = "retail_analytics.db.lfs"

DATA_DIR = "data"
TRANSACTIONS_CSV = os.path.join(DATA_DIR, "transactions.csv")
ORDERS_CSV = os.path.join(DATA_DIR, "orders.csv")
CUSTOMERS_CSV = os.path.join(DATA_DIR, "customers.csv")

def is_lfs_pointer(path):
    if not os.path.exists(path):
        return False
    try:
        with open(path, "rb") as f:
            header = f.read(50)
            return b"git-lfs" in header
    except Exception:
        return False

def setup_database():
    print("=" * 80)
    print("RETAIL ANALYTICS DATABASE BUILDER")
    print("=" * 80)

    # 1. Handle LFS pointer file or existing corrupt file
    if os.path.exists(DB_PATH):
        if is_lfs_pointer(DB_PATH):
            print(f"ℹ️  '{DB_PATH}' is a Git LFS pointer text file.")
            if not os.path.exists(LFS_BACKUP_PATH):
                print(f"   Backing up Git LFS pointer to '{LFS_BACKUP_PATH}'...")
                os.rename(DB_PATH, LFS_BACKUP_PATH)
            else:
                os.remove(DB_PATH)
            print(f"   Removed placeholder; creating real SQLite database.")
        else:
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table';")
                count = cursor.fetchone()[0]
                if count >= 3:
                    print(f"✅ '{DB_PATH}' already exists and contains {count} tables.")
                    validate_database(conn)
                    conn.close()
                    return
                conn.close()
            except sqlite3.DatabaseError:
                print(f"⚠️ '{DB_PATH}' is corrupted or not a valid database. Rebuilding...")
                os.remove(DB_PATH)

    start_time = time.time()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable SQLite speed optimizations
    cursor.execute("PRAGMA synchronous = OFF;")
    cursor.execute("PRAGMA journal_mode = MEMORY;")
    cursor.execute("PRAGMA cache_size = 100000;")

    # 2. Import Customers
    print("\n📥 Importing customers table...")
    c_start = time.time()
    df_customers = pd.read_csv(CUSTOMERS_CSV)
    df_customers.to_sql("customers", conn, if_exists="replace", index=False)
    print(f"   Loaded {len(df_customers):,} rows into 'customers' ({time.time() - c_start:.2f}s)")

    # 3. Import Orders
    print("\n📥 Importing orders table...")
    o_start = time.time()
    df_orders = pd.read_csv(ORDERS_CSV)
    df_orders.to_sql("orders", conn, if_exists="replace", index=False)
    print(f"   Loaded {len(df_orders):,} rows into 'orders' ({time.time() - o_start:.2f}s)")

    # 4. Import Transactions (chunked for memory efficiency)
    print("\n📥 Importing transactions table (790k+ rows)...")
    t_start = time.time()
    chunk_size = 100000
    first_chunk = True
    total_tx = 0
    for chunk in pd.read_csv(TRANSACTIONS_CSV, chunksize=chunk_size):
        chunk.to_sql("transactions", conn, if_exists="replace" if first_chunk else "append", index=False)
        first_chunk = False
        total_tx += len(chunk)
        print(f"   Loaded {total_tx:,} transactions...")
    print(f"   Finished loading {total_tx:,} rows into 'transactions' ({time.time() - t_start:.2f}s)")

    # 5. Create Indexes
    print("\n⚡ Creating performance indexes (from sql/schema_setup.sql)...")
    idx_start = time.time()
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_tx_customer    ON transactions(customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_tx_invoice     ON transactions(invoice);",
        "CREATE INDEX IF NOT EXISTS idx_tx_yearmonth   ON transactions(invoice_yearmonth);",
        "CREATE INDEX IF NOT EXISTS idx_tx_date        ON transactions(invoice_date_only);",
        "CREATE INDEX IF NOT EXISTS idx_tx_country     ON transactions(country);",
        "CREATE INDEX IF NOT EXISTS idx_tx_stock       ON transactions(stock_code);",
        "CREATE INDEX IF NOT EXISTS idx_ord_customer   ON orders(customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_ord_invoice    ON orders(invoice);",
        "CREATE INDEX IF NOT EXISTS idx_ord_yearmonth  ON orders(invoice_yearmonth);",
        "CREATE INDEX IF NOT EXISTS idx_cust_customer  ON customers(customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_cust_country   ON customers(country);"
    ]
    for idx_sql in indexes:
        cursor.execute(idx_sql)
    conn.commit()
    print(f"   11 indexes created successfully ({time.time() - idx_start:.2f}s)")

    # 6. Validate
    validate_database(conn)
    conn.close()
    print(f"\n🎉 Database successfully built in {time.time() - start_time:.2f}s!")

def validate_database(conn):
    print("\n🔍 Validating Database Integrity & Cross-Table Consistency...")
    cursor = conn.cursor()

    # Table row counts
    print("-" * 60)
    print("Table Row Counts:")
    print("-" * 60)
    query_counts = """
    SELECT 'transactions' AS table_name, COUNT(*) AS row_count FROM transactions
    UNION ALL
    SELECT 'orders',                      COUNT(*) FROM orders
    UNION ALL
    SELECT 'customers',                   COUNT(*) FROM customers;
    """
    for table_name, count in cursor.execute(query_counts).fetchall():
        print(f"  • {table_name:<15} : {count:>10,} rows")

    # Revenue cross-check
    print("-" * 60)
    print("Revenue Reconciliation Cross-Check:")
    print("-" * 60)
    query_rev = """
    SELECT 'transactions' AS source, ROUND(SUM(CAST(revenue AS REAL)), 2) AS total_revenue FROM transactions
    UNION ALL
    SELECT 'orders',                  ROUND(SUM(CAST(order_revenue AS REAL)), 2) FROM orders
    UNION ALL
    SELECT 'customers',               ROUND(SUM(CAST(lifetime_revenue AS REAL)), 2) FROM customers;
    """
    for source, rev in cursor.execute(query_rev).fetchall():
        print(f"  • {source:<15} : £{rev:>15,.2f}")
    print("-" * 60)

if __name__ == "__main__":
    setup_database()

