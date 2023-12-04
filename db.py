import psycopg2
import pandas as pd

def get_db_connection():
    return psycopg2.connect(
        host="ep-royal-thunder-45099107.us-east-1.postgres.vercel-storage.com",
        database="verceldb",
        user="default",
        password="QhYas0zXyE7A",
        port="5432"
    )

def read_stock_purchases():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ticker, buy_date, buy_price, quantity FROM stock_purchases")
    stock_purchases = cursor.fetchall()
    conn.close()
    return pd.DataFrame(stock_purchases, columns=['Ticker', 'BuyDate', 'BuyPrice', 'Quantity'])

def write_stock_purchases(new_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    for _, row in new_data.iterrows():
        cursor.execute(
            "INSERT INTO stock_purchases (ticker, buy_date, buy_price, quantity) VALUES (%s, %s, %s, %s)",
            (row['Ticker'], row['BuyDate'], row['BuyPrice'], row['Quantity'])
        )
    conn.commit()
    conn.close()

