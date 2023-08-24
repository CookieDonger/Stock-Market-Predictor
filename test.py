import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from keras.models import load_model

stocks = ['AAPL', 'MSFT', 'AMZN', 'NVDA', 'TSLA', 'GOOGL', 'META', 'GOOG', 'BRK-B', 'UNH']


def day1return(t1, t2):
    return t2 - t1


for stock in stocks:
    df = yf.download(stock, period='11d').reset_index().drop(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])

    df2 = df.shift(1)
    df2['T + 1'] = df.loc[1:, 'Adj Close']
    df2 = df2.drop(0)

    df2['R'] = df2.apply(lambda row: day1return(row['Adj Close'], row['T + 1']), axis=1)
    x_fut_test = df2['R'].to_numpy()
    x_fut_test = np.reshape(x_fut_test, (1, 10, 1))
    price = df2.iloc[9]['T + 1']

    today = datetime.today()

    model = load_model(f'models/{stock}1.keras')
    newpred = model.predict(x_fut_test)

    days, prices = [today.strftime('%Y-%m-%d')], [price]

    future = 30

    for i in range(future):
        x_fut_test = np.append(x_fut_test, newpred)
        x_fut_test = np.delete(x_fut_test, 0)
        newpred = model.predict(x_fut_test)
        price = price + newpred
        prices.append(price)
        day = today + timedelta(days=1)
        days.append(day.strftime('%Y-%m-%d'))


def predict_2(stock):
    pass
