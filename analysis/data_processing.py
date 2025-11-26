# analysis/data_processing.py
import sqlite3
import pandas as pd

def init_db(db_name='finance.db'):
    """Create the expenses table if it doesn't exist"""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_expense_data(db_name='finance.db'):
    """Fetch all expense data as a DataFrame"""
    conn = sqlite3.connect(db_name)
    try:
        df = pd.read_sql_query("SELECT * FROM expenses", conn)
    except Exception:
        df = pd.DataFrame(columns=['id', 'date', 'category', 'amount', 'notes'])
    conn.close()

    if df.empty:
        return pd.DataFrame(columns=['id', 'date', 'category', 'amount', 'notes'])

    # Ensure correct types
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Ensure all columns exist
    for col in ['id', 'date', 'category', 'amount', 'notes']:
        if col not in df.columns:
            df[col] = None

    return df[['id', 'date', 'category', 'amount', 'notes']]

def insert_dataframe(db_name, df):
    """Insert a DataFrame into the expenses table"""
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Ensure required columns
    if 'date' not in df.columns or 'category' not in df.columns or 'amount' not in df.columns:
        raise ValueError("DataFrame must have 'date','category','amount'")
    
    if 'notes' not in df.columns:
        df['notes'] = ''

    df = df[['date', 'category', 'amount', 'notes']]

    conn = sqlite3.connect(db_name)
    df.to_sql('expenses', conn, if_exists='append', index=False)
    conn.close()
