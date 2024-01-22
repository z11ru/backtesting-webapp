from backtesting import Backtest, Strategy
from backtesting.lib import crossover

import pandas as pd
import numpy as np
import plotly as plt
import plotly.graph_objs as go
from plotly.subplots import make_subplots

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

rsi_code = '''
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
        '''

def equity_curve(stock_data):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.1, subplot_titles=('Bollinger Bands', 'Relative Strength Index (RSI)'),
                        row_heights=[0.6, 0.4])

    # Bollinger Bands Plot (First Subplot)
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'], mode='lines', name='Close Price', opacity=1), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['SMA'], mode='lines', name='SMA', opacity=1), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Upper_Band'], mode='lines', name='Upper Bollinger Band', opacity=1), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Lower_Band'], mode='lines', name='Lower Bollinger Band', opacity=1), row=1, col=1)

    # RSI Plot (Second Subplot)
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['RSI'], mode='lines', name='RSI', line=dict(color='purple', width=1.5), opacity=0.6), row=2, col=1)

    # Adding Overbought and Oversold lines
    fig.add_hline(y=70, line=dict(color='blue', dash='dash'), row=2, col=1)
    fig.add_hline(y=30, line=dict(color='blue', dash='dash'), row=2, col=1)

    # Update y-axis range for RSI plot
    fig.update_yaxes(range=[0, 100], row=2, col=1)

    # Update layout
    fig.update_layout(height=600, width=800, title_text="Stock Analysis", showlegend=True)

    return fig

class HybridStrategy(Strategy):
    def init(self):
        self.upper_band = self.I(lambda x: x['Upper_Band'], self.data.df)
        self.lower_band = self.I(lambda x: x['Lower_Band'], self.data.df)
        self.rsi = self.I(lambda x: x['RSI'], self.data.df)

    def next(self):
        if crossover(self.data.Close, self.lower_band) and self.rsi[-1] < 30:
            self.buy()

        elif crossover(self.upper_band, self.data.Close) and self.rsi[-1] > 70:
            self.sell()

def run_test(stock_data):
    bt = Backtest(stock_data, HybridStrategy, cash=10000, commission=.002, exclusive_orders=True)
    stats = bt.run()
    return stats