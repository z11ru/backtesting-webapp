from backtesting import Backtest, Strategy
from backtesting.lib import crossover

import pandas as pd
import numpy as np
import plotly as plt

def rsi(array, window):
    deltas = np.diff(array)
    seed = deltas[:window+1]
    up = seed[seed >= 0].sum()/window
    down = -seed[seed < 0].sum()/window
    rs = up/down
    rsi = np.zeros_like(array)
    rsi[:window] = 100. - 100./(1. + rs)

    for i in range(window, len(array)):
        delta = deltas[i - 1]

        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up*(window - 1) + upval)/window
        down = (down*(window - 1) + downval)/window

        rs = up/down
        rsi[i] = 100. - 100./(1. + rs)

    return rsi

path = 'stock_data/TSLA_stock_data.csv'
stock_data = pd.read_csv(path, parse_dates=True, index_col='Date')
stock_data = stock_data[stock_data.index >= '2022-01-01']

sma_period = 20
rsi_window = 14

stock_data['SMA'] = stock_data['Close'].rolling(window=sma_period).mean()
stock_data['STD'] = stock_data['Close'].rolling(window=sma_period).std()
stock_data['Upper_Band'] = stock_data['SMA'] + (stock_data['STD'] * 2)
stock_data['Lower_Band'] = stock_data['SMA'] - (stock_data['STD'] * 2)
stock_data['RSI'] = rsi(stock_data['Close'].to_numpy(), rsi_window)