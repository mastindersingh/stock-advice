from flask import Flask, render_template, request, redirect, url_for
import os
import pandas as pd
import yfinance as yf
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from datetime import datetime
import base64
from io import BytesIO

# Set MPLCONFIGDIR to a writable directory
os.environ['MPLCONFIGDIR'] = '/tmp'

app = Flask(__name__)

csv_file = 'stock_purchases.csv'

# Function to read stock purchases from CSV
def read_stock_purchases():
    try:
        return pd.read_csv(csv_file)
    except FileNotFoundError:
        return pd.DataFrame(columns=['Ticker', 'BuyDate', 'BuyPrice', 'Quantity'])

# Function to write stock purchases to CSV
def write_stock_purchases(df):
    df.to_csv(csv_file, index=False)

# Function to fetch stock data
def fetch_stock_data(stock_purchases):
    stock_data = {}
    end_date = datetime.now()

    for _, row in stock_purchases.iterrows():
        ticker = row['Ticker']
        buy_date = pd.to_datetime(row['BuyDate'])
        buy_price = float(row['BuyPrice'])
        quantity = int(row['Quantity'])

        try:
            tickerData = yf.Ticker(ticker)
            data = tickerData.history(start=buy_date, end=end_date)
            current_price = data['Close'].iloc[-1]
            percentage_change = ((current_price - buy_price) / buy_price) * 100
            performance = "Up" if current_price > buy_price else "Down"

            # Generate graph
            plt.figure(figsize=(10, 4))
            plt.plot(data['Close'])
            plt.title(f"{ticker} Stock Price")
            plt.xlabel("Date")
            plt.ylabel("Price")
            graph = get_graph()

            stock_data[ticker] = {
                'data': data,
                'buy_date': buy_date.date(),
                'buy_price': buy_price,
                'quantity': quantity,
                'current_price': current_price,
                'performance': performance,
                'percentage_change': percentage_change,
                'graph': graph
            }
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")

    return stock_data

# Function to get graph image
def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

# Route for the main page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ticker = request.form.get('ticker')
        buy_date = request.form.get('buy_date')
        buy_price = request.form.get('buy_price')
        quantity = request.form.get('quantity')

        new_data = pd.DataFrame([[ticker, buy_date, buy_price, quantity]], columns=['Ticker', 'BuyDate', 'BuyPrice', 'Quantity'])
        df = read_stock_purchases()
        df = pd.concat([df, new_data], ignore_index=True)
        write_stock_purchases(df)

        return redirect(url_for('index'))

    stock_data = fetch_stock_data(read_stock_purchases())
    return render_template('stocks.html', stock_data=stock_data)

if __name__ == '__main__':
    app.run(debug=True)

