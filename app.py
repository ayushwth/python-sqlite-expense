# from flask import Flask, render_template, request, redirect, url_for
# import sqlite3
# import os
# import pandas as pd
# import numpy as np
# from analysis.data_processing import get_expense_data, insert_dataframe
# from analysis.visualizations import create_plots

# app = Flask(__name__)
# DB_NAME = 'finance.db'

# # Ensure DB exists with correct table
# def init_db():
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS expenses (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             date TEXT NOT NULL,
#             category TEXT NOT NULL,
#             amount REAL NOT NULL,
#             notes TEXT
#         )
#     ''')
#     conn.commit()
#     conn.close()

# init_db()

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     # Add manual entry or CSV upload
#     if request.method == 'POST':
#         # CSV upload (file input named 'file')
#         if 'file' in request.files and request.files['file'].filename != '':
#             file = request.files['file']
#             if file.filename.endswith('.csv'):
#                 try:
#                     df = pd.read_csv(file)
#                 except Exception as e:
#                     return f"Error reading CSV: {e}", 400

#                 # Required columns: date, category, amount, notes (notes optional)
#                 # Normalize column names to lower-case
#                 df.columns = [c.strip().lower() for c in df.columns]

#                 # If amount column is not numeric attempt conversion
#                 if 'amount' not in df.columns or 'date' not in df.columns or 'category' not in df.columns:
#                     return "CSV must include columns: date, category, amount (notes optional)", 400

#                 # Keep only needed columns, add notes if missing
#                 if 'notes' not in df.columns:
#                     df['notes'] = ''

#                 # Ensure date formatting (leave as-is; DB stores text)
#                 df = df[['date', 'category', 'amount', 'notes']]

#                 # Insert into DB safely
#                 try:
#                     insert_dataframe(DB_NAME, df)
#                 except Exception as e:
#                     return f"Error inserting CSV to DB: {e}", 500

#         else:
#             # Manual form fields
#             date = request.form.get('date')
#             category = request.form.get('category', '').strip()
#             amount = request.form.get('amount', '').strip()
#             notes = request.form.get('notes', '').strip()

#             if not date or not category or amount == '':
#                 return "Date, category and amount are required", 400

#             try:
#                 amount_val = float(amount)
#             except:
#                 return "Amount must be a number", 400

#             conn = sqlite3.connect(DB_NAME)
#             c = conn.cursor()
#             c.execute(
#                 "INSERT INTO expenses (date, category, amount, notes) VALUES (?, ?, ?, ?)",
#                 (date, category, amount_val, notes)
#             )
#             conn.commit()
#             conn.close()

#         return redirect(url_for('dashboard'))

#     return render_template('index.html')

# @app.route('/dashboard')
# def dashboard():
#     # optional category filter via query param
#     selected_category = request.args.get('category', default=None, type=str)
#     df = get_expense_data(DB_NAME)

#     # if df empty keep consistent types
#     if df.empty:
#         df_records = []
#         columns = ['id', 'date', 'category', 'amount', 'notes']
#         categories = []
#     else:
#         # filter if requested
#         if selected_category:
#             df = df[df['category'] == selected_category]

#         # ensure correct types and sorting
#         df['date'] = pd.to_datetime(df['date'], errors='coerce')
#         df = df.sort_values('date')

#         # For templates
#         df_records = df.to_dict(orient='records')
#         columns = ['id', 'date', 'category', 'amount', 'notes']
#         categories = sorted(get_expense_data(DB_NAME)['category'].dropna().unique().tolist())

#     plots_html = create_plots(df)

#     return render_template('dashboard.html',
#                            records=df_records,
#                            columns=columns,
#                            plots=plots_html,
#                            categories=categories,
#                            selected_category=selected_category)

# @app.route('/delete/<int:expense_id>', methods=['POST'])
# def delete_expense(expense_id):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
#     conn.commit()
#     conn.close()
#     return redirect(url_for('dashboard'))

# @app.route('/delete_all', methods=['POST'])
# def delete_all():
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute("DELETE FROM expenses")
#     conn.commit()
#     conn.close()
#     return redirect(url_for('dashboard'))

# @app.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
# def edit_expense(expense_id):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()

#     if request.method == 'POST':
#         date = request.form.get('date')
#         category = request.form.get('category', '').strip()
#         amount = request.form.get('amount', '').strip()
#         notes = request.form.get('notes', '').strip()

#         if not date or not category or amount == '':
#             conn.close()
#             return "Date, category and amount required", 400

#         try:
#             amount_val = float(amount)
#         except:
#             conn.close()
#             return "Amount must be a number", 400

#         c.execute("""
#             UPDATE expenses
#             SET date=?, category=?, amount=?, notes=?
#             WHERE id=?
#         """, (date, category, amount_val, notes, expense_id))
#         conn.commit()
#         conn.close()
#         return redirect(url_for('dashboard'))

#     c.execute("SELECT * FROM expenses WHERE id=?", (expense_id,))
#     row = c.fetchone()
#     conn.close()
#     if not row:
#         return "Expense not found", 404
#     return render_template('edit.html', row=row)

# @app.route('/summary')
# def summary():
#     df = get_expense_data(DB_NAME)
#     if df.empty:
#         table_html = "<p>No data available</p>"
#     else:
#         df['date'] = pd.to_datetime(df['date'], errors='coerce')
#         df['month'] = df['date'].dt.to_period('M')
#         monthly = df.groupby('month')['amount'].sum().reset_index()
#         monthly['month'] = monthly['month'].astype(str)
#         table_html = monthly.to_html(index=False, classes='table table-striped')

#     return render_template('summary.html', table=table_html)

# if __name__ == '__main__':
#     # ensure folder for DB exists (project root)
#     app.run(debug=True)

# from flask import Flask, render_template, request, redirect, url_for
# import sqlite3
# import pandas as pd
# import numpy as np
# from analysis.data_processing import get_expense_data, insert_dataframe
# from analysis.visualizations import create_plots

# # ------------------------------
# # Flask App Setup
# # ------------------------------
# app = Flask(__name__)
# DB_NAME = 'finance.db'  # SQLite DB file name

# # ------------------------------
# # Database Initialization
# # Ensures the 'expenses' table exists
# # ------------------------------
# def init_db():
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS expenses (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             date TEXT NOT NULL,
#             category TEXT NOT NULL,
#             amount REAL NOT NULL,
#             notes TEXT
#         )
#     ''')
#     conn.commit()
#     conn.close()

# init_db()

# # ------------------------------
# # Route: Index / Add Expense
# # Handles manual form submission & CSV uploads
# # ------------------------------
# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         # --- CSV Upload Handling ---
#         if 'file' in request.files and request.files['file'].filename != '':
#             file = request.files['file']
#             if file.filename.endswith('.csv'):
#                 try:
#                     df = pd.read_csv(file)
#                 except Exception as e:
#                     return f"Error reading CSV: {e}", 400

#                 # Normalize column names to lower-case
#                 df.columns = [c.strip().lower() for c in df.columns]

#                 # Check for required columns
#                 if 'amount' not in df.columns or 'date' not in df.columns or 'category' not in df.columns:
#                     return "CSV must include columns: date, category, amount (notes optional)", 400

#                 # Add missing notes column
#                 if 'notes' not in df.columns:
#                     df['notes'] = ''

#                 # Keep only needed columns
#                 df = df[['date', 'category', 'amount', 'notes']]

#                 # Insert into DB
#                 try:
#                     insert_dataframe(DB_NAME, df)
#                 except Exception as e:
#                     return f"Error inserting CSV to DB: {e}", 500

#         else:
#             # --- Manual Entry Handling ---
#             date = request.form.get('date')
#             category = request.form.get('category', '').strip()
#             amount = request.form.get('amount', '').strip()
#             notes = request.form.get('notes', '').strip()

#             # Validation
#             if not date or not category or amount == '':
#                 return "Date, category and amount are required", 400

#             try:
#                 amount_val = float(amount)
#             except:
#                 return "Amount must be a number", 400

#             # Insert into DB
#             conn = sqlite3.connect(DB_NAME)
#             c = conn.cursor()
#             c.execute(
#                 "INSERT INTO expenses (date, category, amount, notes) VALUES (?, ?, ?, ?)",
#                 (date, category, amount_val, notes)
#             )
#             conn.commit()
#             conn.close()

#         return redirect(url_for('dashboard'))

#     # GET request => render the Add Expense page
#     return render_template('index.html')

# # ------------------------------
# # Route: Dashboard
# # Shows expenses table + charts
# # Optional category filter via query param
# # ------------------------------
# @app.route('/dashboard')
# def dashboard():
#     selected_category = request.args.get('category', default=None, type=str)
#     df = get_expense_data(DB_NAME)

#     if df.empty:
#         df_records = []
#         columns = ['id', 'date', 'category', 'amount', 'notes']
#         categories = []
#     else:
#         # Filter by category if selected
#         if selected_category:
#             df = df[df['category'] == selected_category]

#         # Convert date column to datetime & sort
#         df['date'] = pd.to_datetime(df['date'], errors='coerce')
#         df = df.sort_values('date')

#         # Prepare data for template
#         df_records = df.to_dict(orient='records')
#         columns = ['id', 'date', 'category', 'amount', 'notes']

#         # All unique categories for filter dropdown
#         categories = sorted(get_expense_data(DB_NAME)['category'].dropna().unique().tolist())

#     # Generate plots HTML (via Plotly)
#     plots_html = create_plots(df)

#     return render_template(
#         'dashboard.html',
#         records=df_records,
#         columns=columns,
#         plots=plots_html,
#         categories=categories,
#         selected_category=selected_category
#     )

# # ------------------------------
# # Route: Delete single expense
# # ------------------------------
# @app.route('/delete/<int:expense_id>', methods=['POST'])
# def delete_expense(expense_id):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
#     conn.commit()
#     conn.close()
#     return redirect(url_for('dashboard'))

# # ------------------------------
# # Route: Delete all expenses
# # ------------------------------
# @app.route('/delete_all', methods=['POST'])
# def delete_all():
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute("DELETE FROM expenses")
#     conn.commit()
#     conn.close()
#     return redirect(url_for('dashboard'))

# # ------------------------------
# # Route: Edit an expense
# # GET => show form
# # POST => update expense
# # ------------------------------
# @app.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
# def edit_expense(expense_id):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()

#     if request.method == 'POST':
#         date = request.form.get('date')
#         category = request.form.get('category', '').strip()
#         amount = request.form.get('amount', '').strip()
#         notes = request.form.get('notes', '').strip()

#         # Validation
#         if not date or not category or amount == '':
#             conn.close()
#             return "Date, category and amount required", 400

#         try:
#             amount_val = float(amount)
#         except:
#             conn.close()
#             return "Amount must be a number", 400

#         # Update DB
#         c.execute("""
#             UPDATE expenses
#             SET date=?, category=?, amount=?, notes=?
#             WHERE id=?
#         """, (date, category, amount_val, notes, expense_id))
#         conn.commit()
#         conn.close()
#         return redirect(url_for('dashboard'))

#     # GET => fetch current expense
#     c.execute("SELECT * FROM expenses WHERE id=?", (expense_id,))
#     row = c.fetchone()
#     conn.close()
#     if not row:
#         return "Expense not found", 404

#     return render_template('edit.html', row=row)

# # ------------------------------
# # Route: Monthly Summary
# # ------------------------------
# @app.route('/summary')
# def summary():
#     df = get_expense_data(DB_NAME)
#     if df.empty:
#         table_html = "<p>No data available</p>"
#     else:
#         df['date'] = pd.to_datetime(df['date'], errors='coerce')
#         df['month'] = df['date'].dt.to_period('M')
#         monthly = df.groupby('month')['amount'].sum().reset_index()
#         monthly['month'] = monthly['month'].astype(str)

#         # Use Bootstrap classes for consistent look
#         table_html = monthly.to_html(index=False, classes='table table-striped text-center')

#     return render_template('summary.html', table=table_html)

# # ------------------------------
# # Main entry point
# # ------------------------------
# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import pandas as pd
from analysis.data_processing import init_db, get_expense_data, insert_dataframe
from analysis.visualizations import create_plots

app = Flask(__name__)
DB_NAME = 'finance.db'

# Initialize DB
init_db(DB_NAME)

# ------------------ INDEX / ADD ------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # CSV upload
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
                df.columns = [c.strip().lower() for c in df.columns]
                if 'notes' not in df.columns:
                    df['notes'] = ''
                df = df[['date','category','amount','notes']]
                insert_dataframe(DB_NAME, df)
        else:
            # Manual add
            date = request.form.get('date')
            category = request.form.get('category').strip()
            amount = float(request.form.get('amount'))
            notes = request.form.get('notes','').strip()
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("INSERT INTO expenses (date, category, amount, notes) VALUES (?,?,?,?)",
                      (date, category, amount, notes))
            conn.commit()
            conn.close()
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# ------------------ DASHBOARD ------------------
@app.route('/dashboard')
def dashboard():
    selected_category = request.args.get('category', None)
    df = get_expense_data(DB_NAME)
    if selected_category:
        df = df[df['category']==selected_category]

    df = df.sort_values('date')
    records = df.to_dict(orient='records')
    categories = sorted(get_expense_data(DB_NAME)['category'].dropna().unique().tolist())
    plots = create_plots(df)

    return render_template('dashboard.html', records=records, categories=categories,
                           selected_category=selected_category, plots=plots)

# ------------------ DELETE ------------------
@app.route('/delete/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id=?",(expense_id,))
    conn.commit(); conn.close()
    return redirect(url_for('dashboard'))

@app.route('/delete_all', methods=['POST'])
def delete_all():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM expenses")
    conn.commit(); conn.close()
    return redirect(url_for('dashboard'))

# ------------------ EDIT ------------------
@app.route('/edit/<int:expense_id>', methods=['GET','POST'])
def edit_expense(expense_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if request.method=='POST':
        date = request.form.get('date')
        category = request.form.get('category')
        amount = float(request.form.get('amount'))
        notes = request.form.get('notes','')
        c.execute("UPDATE expenses SET date=?, category=?, amount=?, notes=? WHERE id=?",
                  (date,category,amount,notes,expense_id))
        conn.commit(); conn.close()
        return redirect(url_for('dashboard'))
    c.execute("SELECT * FROM expenses WHERE id=?",(expense_id,))
    row = c.fetchone()
    conn.close()
    return render_template('edit.html', row=row)

# ------------------ SUMMARY ------------------
@app.route('/summary')
def summary():
    df = get_expense_data(DB_NAME)
    if df.empty:
        table_html = "<p>No data</p>"
    else:
        df['month'] = df['date'].dt.to_period('M')
        monthly = df.groupby('month')['amount'].sum().reset_index()
        monthly['month'] = monthly['month'].astype(str)
        table_html = monthly.to_html(index=False, classes='table table-striped text-center')
    return render_template('summary.html', table=table_html)

if __name__=='__main__':
    app.run(debug=True)
