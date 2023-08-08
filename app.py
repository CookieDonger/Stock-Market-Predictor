import yfinance as yf
import pandas as pd
from datetime import date, datetime, timedelta
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib. dates as mandates
from sklearn import *
from keras import *
from sklearn.preprocessing import MinMaxScaler
import joblib
from matplotlib import pyplot as plt
from flask import Flask, request, jsonify, render_template
app = Flask(__name__)


@app.route('/')
def home():
    data = yf.download(tickers=['MSFT'], period='max', interval ='1d')
    y = data['Adj Close'].fillna(method='ffill')
    y = y.values.reshape(-1, 1)

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler = scaler.fit(y)
    y = scaler.transform(y)

    n_lookback = 60
    n_forecast = 30

    mdl = joblib.load('yahoo_daily_model.joblib')

    X_ = y[- n_lookback:]  # last available input sequence
    X_ = X_.reshape(1, n_lookback, 1)

    Y_ = mdl.predict(X_).reshape(-1, 1)
    Y_ = scaler.inverse_transform(Y_)

    df_past = data[['Adj Close']].tail(365).reset_index()
    df_past.rename(columns={'index': 'Date', 'Adj Close': 'Actual'}, inplace=True)
    df_past['Date'] = pd.to_datetime(df_past['Date'])
    df_past['Forecast'] = np.nan
    df_past['Forecast'].iloc[-1] = df_past['Actual'].iloc[-1]

    df_future = pd.DataFrame(columns=['Date', 'Actual', 'Forecast'])
    df_future['Date'] = pd.date_range(start=df_past['Date'].iloc[-1] + pd.Timedelta(days=1), periods=n_forecast)
    df_future['Forecast'] = Y_.flatten()
    df_future['Actual'] = np.nan

    results = df_past.append(df_future).set_index('Date')

    # plot the results


    plt.plot(results)
    plt.title("MSFT Projection")
    plt.xlabel('Time')
    plt.ylabel('USD')
    plt.xticks(rotation = 30)
    # results.plot(title='MSFT')
    plt.savefig('static/MSFT_plot.png')
    return render_template('index.html')
if __name__ == "__main__":
    app.run(debug=True)