# analysis/visualizations.py
import plotly.express as px
import pandas as pd

def create_plots(df):
    """Return combined HTML of pie, bar, and cumulative line charts"""
    if df.empty:
        return "<p>No data to display charts.</p>"

    df = df.copy()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    html_output = ""

    # Pie chart: category
    try:
        cat = df.groupby('category', dropna=True)['amount'].sum().reset_index()
        fig_pie = px.pie(cat, names='category', values='amount', title='Expenses by Category')
        html_output += fig_pie.to_html(full_html=False)
    except:
        html_output += "<p>Unable to create pie chart</p>"

    # Bar chart: monthly
    try:
        df['month'] = df['date'].dt.to_period('M')
        monthly = df.groupby('month')['amount'].sum().reset_index()
        monthly['month'] = monthly['month'].astype(str)
        fig_bar = px.bar(monthly, x='month', y='amount', title='Monthly Expenses')
        html_output += fig_bar.to_html(full_html=False)
    except:
        html_output += "<p>Unable to create monthly bar chart</p>"

    # Line chart: cumulative
    try:
        df_sorted = df.sort_values('date')
        df_sorted['cumulative'] = df_sorted['amount'].cumsum()
        fig_line = px.line(df_sorted, x='date', y='cumulative', title='Cumulative Expenses Over Time')
        html_output += fig_line.to_html(full_html=False)
    except:
        html_output += "<p>Unable to create cumulative chart</p>"

    return html_output
