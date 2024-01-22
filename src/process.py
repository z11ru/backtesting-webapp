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

def equity_curve(ticker_symbol, stock_data):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05,
                        row_heights=[0.7, 0.3])

    # Bollinger Bands Plot (First Subplot)
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'], mode='lines', name='Close Price', line=dict(color='blue', width=0.75), opacity=1), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['SMA'], mode='lines', name='SMA', line=dict(color='light blue', width=0.75), opacity=1), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Upper_Band'], mode='lines', name='Upper Bollinger Band', line=dict(color='red', width=0.75), opacity=1), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Lower_Band'], mode='lines', name='Lower Bollinger Band', line=dict(color='orange', width=0.75), opacity=1), row=1, col=1)

    # RSI Plot (Second Subplot)
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['RSI'], mode='lines', name='RSI', line=dict(color='purple', width=1), opacity=0.6), row=2, col=1)

    # Adding Overbought and Oversold lines
    fig.add_hline(y=70, line=dict(color='blue', dash='dash', width=0.75), row=2, col=1)
    fig.add_hline(y=30, line=dict(color='blue', dash='dash', width=0.75), row=2, col=1)

    # Update y-axis range for RSI plot
    fig.update_yaxes(range=[0, 100], row=2, col=1)

    # Update layout
    fig.update_layout(title=ticker_symbol + " Indicators", height = 800, showlegend=False)

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

def optimize_parameters(stock_data):

    strategy = HybridStrategy

    sma_periods = range(5, 50, 1)  # For example, from 5 to 50 in steps of 5
    std_dev_multipliers = [1, 2, 3]  # Standard deviation multipliers
    rsi_windows = range(10, 30, 1)  # RSI window periods

    best_sharpe = -float('inf')
    best_params = {}

    for sma_period in sma_periods:
        for std_dev_multiplier in std_dev_multipliers:
            for rsi_window in rsi_windows:
                # Calculate Bollinger Bands and RSI for the current set of parameters
                stock_data['SMA'] = stock_data['Close'].rolling(window=sma_period).mean()
                stock_data['STD'] = stock_data['Close'].rolling(window=sma_period).std()
                stock_data['Upper_Band'] = stock_data['SMA'] + (stock_data['STD'] * std_dev_multiplier)
                stock_data['Lower_Band'] = stock_data['SMA'] - (stock_data['STD'] * std_dev_multiplier)
                stock_data['RSI'] = rsi(stock_data['Close'].to_numpy(), rsi_window)

                # Run backtest
                bt = Backtest(stock_data, strategy, cash=10000, commission=.002)
                stats = bt.run()

                # Check if this combination has the best Sharpe ratio
                if stats['Sharpe Ratio'] > best_sharpe:
                    best_sharpe = stats['Sharpe Ratio']
                    best_params = {
                        'SMA Period': sma_period,
                        'Std Dev Multiplier': std_dev_multiplier,
                        'RSI Window': rsi_window,
                        'Sharpe Ratio': best_sharpe
                    }
    
    return best_params