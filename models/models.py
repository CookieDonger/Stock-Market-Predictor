import yfinance as yf
from collections import deque
import numpy as np
from keras.models import Sequential
from keras.layers import *

stocks = ['AAPL', 'MSFT', 'AMZN', 'NVDA', 'TSLA', 'GOOGL', 'META', 'GOOG', 'BRK-B', 'UNH']

for stock in stocks:
    df = yf.download(stock, period='MAX', actions=False)
    df = df.drop(columns=['Open', 'High', 'Low', 'Close', 'Volume'])
    df = df.rename(columns={'Adj Close': 'T'})
    df = df.reset_index()

    df2 = df.copy()
    df3 = df.copy()
    df2 = df2.shift(1)
    df2['T + 1'] = df.loc[1:, 'T']
    df2 = df2.drop(0)
    df2['R'] = df2.apply(lambda row: row['T + 1'] - row['T'], axis=1)
    df2 = df2.reset_index()
    df2 = df2.drop(columns=['T', 'T + 1', 'index'])
    n = 10
    indexes = [i for i in range(n)]
    df = df2
    df2 = df2.drop(indexes)
    column = deque(df2.loc[:,'R'])
    for i in range(n):
        column.pop()
        column.appendleft(df.loc[n - i - 1, 'R'])
        df2[f'R - {i + 1}'] = column
    df_as_np = df2.to_numpy()
    time, y, x = np.split(df_as_np, [1, 2], axis=1)
    x = np.array(x)
    y = np.array(y)
    x = np.reshape(x, (x.shape[0], x.shape[1], 1))
    p_80 = int(.8 * x.shape[0])
    x = x.astype(np.float32)
    y = y.astype(np.float32)
    x_train, y_train, date_train = x[:p_80], y[:p_80], time[:p_80]
    x_test, y_test, date_test = x[p_80:], y[p_80:], time[p_80:]
    lstm = Sequential([
        Input((10, 1)),
        LSTM(50, return_sequences=True),
        Dropout(0.1),
        LSTM(50, return_sequences=True),
        Dropout(0.1),
        LSTM(50),
        Dense(1, activation='linear')
    ])
    lstm.compile(optimizer='adam', loss='mse')
    lstm.fit(x_train, y_train, epochs=100, shuffle=True, batch_size=10)
    lstm.save(stock + '1.keras')