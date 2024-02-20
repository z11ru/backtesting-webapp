import pandas as pd
import numpy as np

from backtesting import Backtest, Strategy
from backtesting.lib import crossover

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

def plot_curve(stock_data, results):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05,
                        row_heights=[0.7, 0.3])

    # Bollinger Bands Plot (First Subplot)
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'], mode='lines', name='Close Price', line=dict(color='blue', width=0.75), opacity=1), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['SMA'], mode='lines', name='SMA', line=dict(color='light blue', width=0.75), opacity=1), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Upper_Band'], mode='lines', name='Upper Bollinger Band', line=dict(color='red', width=0.75), opacity=1), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Lower_Band'], mode='lines', name='Lower Bollinger Band', line=dict(color='orange', width=0.75), opacity=1), row=1, col=1)

    for _, trade in results._trades.iterrows():
        color = 'green' if trade['PnL'] > 0 else 'red'
        entry_symbol = 'triangle-up' if trade['Size'] > 0 else 'triangle-down'
        exit_symbol = 'triangle-down' if trade['Size'] > 0 else 'triangle-up'

        # Add entry point
        fig.add_trace(go.Scatter(x=[trade['EntryTime']], y=[trade['EntryPrice']],
                                 mode='markers', marker=dict(color='orange', size=13, symbol=entry_symbol),
                                 name='Entry Point'))

        # Add exit point
        fig.add_trace(go.Scatter(x=[trade['ExitTime']], y=[trade['ExitPrice']],
                                 mode='markers', marker=dict(color=color, size=13, symbol=exit_symbol),
                                 name='Exit Point'))

        # Add dashed line between entry and exit
        fig.add_trace(go.Scatter(x=[trade['EntryTime'], trade['ExitTime']], 
                                 y=[trade['EntryPrice'], trade['ExitPrice']],
                                 mode='lines', line=dict(color=color, dash='dash'), 
                                 name='Trade Line'))

    # RSI Plot (Second Subplot)
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['RSI'], mode='lines', name='RSI', line=dict(color='orange', width=1), opacity=0.6), row=2, col=1)

    # Adding Overbought and Oversold lines
    fig.add_hline(y=70, line=dict(color='blue', dash='dash', width=0.75), row=2, col=1)
    fig.add_hline(y=30, line=dict(color='blue', dash='dash', width=0.75), row=2, col=1)

    # Update y-axis range for RSI plot
    fig.update_yaxes(range=[0, 100], row=2, col=1)

    # Update layout
    fig.update_layout(title='Results', height = 800, showlegend=False)

    return fig

class HybridStrategy(Strategy):
    use_rsi = True
    use_bollinger = True
    profit_limit = None
    drawdown_limit = None

    @classmethod
    def set_parameters(cls, use_rsi, use_bollinger, profit_limit, drawdown_limit):
        cls.use_rsi = use_rsi
        cls.use_bollinger = use_bollinger
        cls.profit_limit = profit_limit
        cls.drawdown_limit = drawdown_limit

    def init(self, use_rsi=True, use_bollinger=True, profit_limit=None, drawdown_limit=None):
        # Technical indicators
        self.upper_band = self.I(lambda x: x['Upper_Band'], self.data.df)
        self.lower_band = self.I(lambda x: x['Lower_Band'], self.data.df)
        self.rsi = self.I(lambda x: x['RSI'], self.data.df)

        # User selections
        self.use_rsi = use_rsi
        self.use_bollinger = use_bollinger

        # Profit/drawdown limits
        self.profit_limit = profit_limit
        self.drawdown_limit = drawdown_limit

        # Conditions state
        self.bollinger_condition_met = False
        self.rsi_condition_met = False

        # Entry price for calculating profit/drawdown
        self.entry_price = None

    def next(self):
        if self.position:
            # Calculate current profit or drawdown
            current_profit_drawdown = self.position.pl

            # Check for profit or drawdown limit to close the position
            if (self.profit_limit and current_profit_drawdown >= self.profit_limit) or \
            (self.drawdown_limit and current_profit_drawdown <= -self.drawdown_limit):
                self.position.close()
                self.entry_price = None
                return  # Exit this iteration to avoid opening a new position immediately

        # Entry conditions based on user selection
        enter_long = False
        enter_short = False

        if self.use_bollinger:
            if crossover(self.data.Close, self.lower_band):
                enter_long = True
            elif crossover(self.upper_band, self.data.Close):
                enter_short = True

        if self.use_rsi:
            if self.rsi[-1] < 30:
                enter_long = True
            elif self.rsi[-1] > 70:
                enter_short = True

        # Execute trades based on conditions
        if enter_long and not self.position.is_long:
            self.buy()
        elif enter_short and not self.position.is_short:
            self.sell()

def run_test(bollinger, rsi, profit, drawdown, stock_data):
    # Set strategy parameters before running the backtest
    HybridStrategy.set_parameters(rsi, bollinger, profit, drawdown)
    bt = Backtest(stock_data, HybridStrategy, cash=10000, exclusive_orders=True)
    stats = bt.run()
    return stats

def optimize_parameters(stock_data):
    strategy = HybridStrategy
    sma_periods = range(5, 50, 1)
    std_dev_multipliers = [1, 2, 3]
    rsi_windows = range(10, 30, 1)

    best_sharpe = -float('inf')
    best_params = {}

    # Pre-calculate RSI for all windows
    rsi_values = {window: rsi(stock_data['Close'].to_numpy(), window) for window in rsi_windows}

    for sma_period in sma_periods:
        # Calculate SMA and STD once for each sma_period
        stock_data['SMA'] = stock_data['Close'].rolling(window=sma_period).mean()
        stock_data['STD'] = stock_data['Close'].rolling(window=sma_period).std()

        for std_dev_multiplier in std_dev_multipliers:
            stock_data['Upper_Band'] = stock_data['SMA'] + (stock_data['STD'] * std_dev_multiplier)
            stock_data['Lower_Band'] = stock_data['SMA'] - (stock_data['STD'] * std_dev_multiplier)

            for rsi_window in rsi_windows:
                stock_data['RSI'] = rsi_values[rsi_window]

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