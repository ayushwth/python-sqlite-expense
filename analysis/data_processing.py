import sqlite3
import pandas as pd

def get_expense_data(db_name):
    conn = sqlite3.connect(db_name)
    try:
        df = pd.read_sql_query('SELECT * FROM expenses', conn)
    except Exception:
        df = pd.DataFrame(columns=['id', 'date', 'category', 'amount', 'notes'])
    conn.close()

    if df.empty:
        return pd.DataFrame(columns=['id', 'date', 'category', 'amount', 'notes'])

    # Ensure amount column is numeric
    if 'amount' in df.columns:
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)

    # Ensure all required columns exist
    for col in ['id', 'date', 'category', 'amount', 'notes']:
        if col not in df.columns:
            if col == 'id':
                df[col] = range(1, len(df) + 1)
            else:
                df[col] = ""

    df = df[['id', 'date', 'category', 'amount', 'notes']]
    return df

def insert_dataframe(db_name, df):
    """
    Insert a pandas DataFrame into the expenses table.
    """
    df = df.rename(columns=lambda x: x.strip().lower())

    if 'date' not in df.columns or 'category' not in df.columns or 'amount' not in df.columns:
        raise ValueError("DataFrame must contain 'date','category','amount' columns")

    if 'notes' not in df.columns:
        df['notes'] = ""

    df = df[['date', 'category', 'amount', 'notes']]
    conn = sqlite3.connect(db_name)
    df.to_sql('expenses', conn, if_exists='append', index=False)
    conn.close()
