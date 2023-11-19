from flask import Flask, render_template, request, redirect, url_for, session
from flask_oauthlib.client import OAuth
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
from datetime import datetime
import base64
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a real secret key

# Google OAuth Setup
oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key='72321166098-rqs54h296h3pp6clb1h19cn7bp4rp8rn.apps.googleusercontent.com',
    consumer_secret='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',
    request_token_params={'scope': 'email'},
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/google-login')
def google_login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    session.pop('email', None)
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
    return redirect(url_for('index'))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'email' not in session:
        return redirect(url_for('login'))


    # ... [previous code] ...


    # Redirect to subscription page after successful login
    return redirect(url_for('subscribe'))

@app.route('/subscribe')
def subscribe():
    return render_template('subscribe.html')




    if request.method == 'POST':
        ticker = request.form.get('ticker')
        buy_date = request.form.get('buy_date')
        buy_price = request.form.get('buy_price')
        quantity = request.form.get('quantity')

        new_data = pd.DataFrame([[ticker, buy_date, buy_price, quantity]], columns=['Ticker', 'BuyDate', 'BuyPrice', 'Quantity'])
        write_stock_purchases(new_data)

        return redirect(url_for('index'))

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

if __name__ == '__main__':
    app.run(debug=True)

