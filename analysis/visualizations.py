import plotly.express as px
import pandas as pd

def create_plots(df):
    # df expected with date (datetime or str), category, amount
    if df is None or df.empty:
        return "<p>No data to show charts.</p>"

    # ensure date is datetime
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # 1. Pie chart: expenses by category
    try:
        cat = df.groupby('category', dropna=True)['amount'].sum().reset_index()
        fig1 = px.pie(cat, names='category', values='amount', title='Expenses by Category')
        pie_html = fig1.to_html(full_html=False)
    except Exception:
        pie_html = "<p>Unable to create pie chart.</p>"

    # 2. Monthly totals bar chart
    try:
        df['month'] = df['date'].dt.to_period('M')
        monthly = df.groupby('month')['amount'].sum().reset_index()
        monthly['month'] = monthly['month'].astype(str)
        fig2 = px.bar(monthly, x='month', y='amount', title='Monthly Expenses')
        bar_html = fig2.to_html(full_html=False)
    except Exception:
        bar_html = "<p>Unable to create monthly bar chart.</p>"

    # 3. Cumulative over time
    try:
        df_sorted = df.sort_values('date')
        df_sorted['cumulative'] = df_sorted['amount'].cumsum()
        fig3 = px.line(df_sorted, x='date', y='cumulative', title='Cumulative Expenses Over Time')
        line_html = fig3.to_html(full_html=False)
    except Exception:
        line_html = "<p>Unable to create cumulative chart.</p>"

    return pie_html + bar_html + line_html
