import yfinance as yf
import pandas as pd
from collections import deque
import numpy as np
from keras.models import Sequential
from keras.layers import *
from datetime import datetime, timedelta


def predict_1(stock):
    df = yf.download(stock, period='MAX', actions=False)
    df = df.drop(columns=['Open', 'High', 'Low', 'Close', 'Volume'])
    df = df.rename(columns={'Adj Close': 'T'})
    df = df.reset_index()
    df = df[:-1]

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
    pred = lstm.predict(x_test)
    future = 30
    newpreds = []
    pred_fut = pred
    newpred = pred_fut[-1]
    time_fut = date_test
    x_fut_test = x_test[-1]
    day = datetime.today()
    day = day.replace(hour=0, minute=0, second=0, microsecond=0)
    for i in range(future):
        x_fut_test = np.append(x_fut_test, newpred)
        x_fut_test = np.delete(x_fut_test, 0)
        x_fut_test = np.reshape(x_fut_test, (1, x.shape[1], 1))
        newpred = lstm.predict(x_fut_test)
        newpreds.append(newpred)
        pred_fut = np.append(pred_fut, newpred)
        day = day + timedelta(days=1)
        time_fut = np.append(time_fut, pd.Timestamp(day))
    newpreds = np.array(newpreds)
    newpreds = np.reshape(newpreds, (len(newpreds), 1))
    index = p_80
    df4 = df3.copy()
    for i in range(len(df4) - index - 11):
        a = df3.loc[index + i, ['T']]
        b = float(pred[i])
        a = a.iloc[0]
        df4.loc[index + i + 1, ['T']] = a + b
    day = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    today = day
    graph_x = [day]
    graph_y = [df4.loc[len(df4) - 1, ['T']]]
    for i in range(future):
        y = graph_y[-1]
        day = day + timedelta(days=1)
        while day.weekday() > 4:
            day = day + timedelta(days=1)
        graph_x.append(day)
        graph_y.append(y + float(newpreds[i]))
    return (graph_x, graph_y, today)


def predict_2(stock):
    pass
