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
app.secret_key = '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'  # Replace with a real secret key

oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key='72321166098-rqs54h296h3pp6clb1h19cn7bp4rp8rn.apps.googleusercontent.com',  # Replace with your Google Client ID
    consumer_secret='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',  # Replace with your Google Client Secret
    request_token_params={
        'scope': 'email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('index'))

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

# ... rest of your code ...

if __name__ == '__main__':
    app.run(debug=True)

