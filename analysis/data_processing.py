import sqlite3
import pandas as pd

def get_expense_data(db_name):
    conn = sqlite3.connect(db_name)
    try:
        df = pd.read_sql_query('SELECT * FROM expenses', conn)
    except Exception:
        df = pd.DataFrame(columns=['id', 'date', 'category', 'amount', 'notes'])
    conn.close()

    # if no rows return empty df with expected columns
    if df.empty:
        return pd.DataFrame(columns=['id', 'date', 'category', 'amount', 'notes'])

    # Normalize: ensure columns exist and correct types
    if 'amount' in df.columns:
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)

    # Keep only relevant columns in case
    df = df[['id', 'date', 'category', 'amount', 'notes']]

    return df

def insert_dataframe(db_name, df):
    """
    Insert a pandas DataFrame (with columns date, category, amount, notes) into the expenses table.
    Uses sqlite3 connection and pandas.to_sql for simplicity.
    """
    # convert columns to expected order and names
    df = df.rename(columns=lambda x: x.strip().lower())
    # ensure necessary columns present
    if 'date' not in df.columns or 'category' not in df.columns or 'amount' not in df.columns:
        raise ValueError("DataFrame must contain 'date','category','amount' columns")

    # keep only required columns, supply notes if missing
    df = df[['date', 'category', 'amount', 'notes']]
    conn = sqlite3.connect(db_name)
    df.to_sql('expenses', conn, if_exists='append', index=False)
    conn.close()
