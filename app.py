from flask import Flask, render_template, request, redirect, url_for, session
from flask_oauthlib.client import OAuth
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
from datetime import datetime
import base64
import os
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'bApG1HXBfOeC5JhRj_tvKA'  # Replace with your real secret key

# Example hardcoded credentials
users = {
    'user1@yahoo.com': 'password1',
    'user2': 'password2'
}

# Google OAuth Setup
oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key='72321166098-rqs54h296h3pp6clb1h19cn7bp4rp8rn.apps.googleusercontent.com',  # Your Google Client ID
    consumer_secret='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',  # Your Google Client Secret
    request_token_params={'scope': 'email'},
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users and users[username] == password:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials.")

    return render_template('login.html')

@app.route('/google-login')
def google_login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    session.pop('email', None)
    session.pop('subscribed', None)
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/login/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    user_info = google.get('userinfo')
    session['email'] = user_info.data['email']
    return redirect(url_for('subscribe'))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        subscription_code = request.form.get('subscription_code')
        if check_subscription_code(subscription_code):
            session['subscribed'] = True
            return redirect(url_for('index'))
        else:
            return render_template('subscribe.html', error="Invalid subscription code.")
    return render_template('subscribe.html')

def check_subscription_code(code):
    try:
        file_path = 'subscription_codes.csv'
        print(f"Reading file from: {os.path.abspath(file_path)}")  # Print the absolute file path

        codes_df = pd.read_csv(file_path)
        print("Contents of the file:")  # Debug: Print the DataFrame to check its contents
        print(codes_df)

        # Ensure the code is checked as a string
        code = str(code)
        return code in codes_df['code'].astype(str).values
    except FileNotFoundError:
        print("File not found.")
        return False
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'logged_in' not in session and 'email' not in session:
        return redirect(url_for('login'))

    # Check if the user is subscribed
    if not session.get('subscribed', False):
        return redirect(url_for('subscribe'))

    # If the user is subscribed, display the stock data
    if request.method == 'POST':
        # Your existing POST request handling code
        pass

    stock_data = fetch_stock_data(read_stock_purchases())
    return render_template('stocks.html', stock_data=stock_data)

def read_stock_purchases():
    try:
        return pd.read_csv('stock_purchases.csv')
    except FileNotFoundError:
        return pd.DataFrame(columns=['Ticker', 'BuyDate', 'BuyPrice', 'Quantity'])

def write_stock_purchases(new_data):
    try:
        existing_data = pd.read_csv('stock_purchases.csv')
        combined_data = pd.concat([existing_data, new_data], ignore_index=True)
        combined_data.to_csv('stock_purchases.csv', index=False)
    except FileNotFoundError:
        new_data.to_csv('stock_purchases.csv', index=False)

def fetch_stock_data(stock_purchases):
    stock_data = {}
    for ticker, group in stock_purchases.groupby('Ticker'):
        total_quantity = group['Quantity'].sum()
        weighted_avg_price = (group['BuyPrice'] * group['Quantity']).sum() / total_quantity
        tickerData = yf.Ticker(ticker)
        data = tickerData.history(period="max")
        current_price = data['Close'].iloc[-1]
        percentage_change = ((current_price - weighted_avg_price) / weighted_avg_price) * 100
        performance = "Up" if current_price > weighted_avg_price else "Down"

        plt.figure(figsize=(10, 4))
        plt.plot(data['Close'])
        plt.title(f"{ticker} Stock Price")
        plt.xlabel("Date")
        plt.ylabel("Price")
        graph = get_graph()

        stock_data[ticker] = {
            'data': data,
            'earliest_buy_date': group['BuyDate'].min(),
            'weighted_avg_price': weighted_avg_price,
            'total_quantity': total_quantity,
            'current_price': current_price,
            'performance': performance,
            'percentage_change': percentage_change,
            'graph': graph
        }

    return stock_data

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def test_check_subscription_code():
    test_code = "12345"  # Replace with a test code
    result = check_subscription_code(test_code)
    print(f"Test Code: {test_code}, Result: {result}")


