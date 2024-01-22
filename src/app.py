# Streamlit app code structure
import streamlit as st
from process import *

import pandas as pd
import numpy as np
import os

# Load and process stock data
@st.cache_data
def load_data(symbol):
    current_dir = os.path.dirname(__file__)
    data_dir = os.path.join(current_dir, '..', 'data')
    file_name = f'{symbol}_stock_data.csv'
    path = os.path.join(data_dir, file_name)
    try:
        stock_data = pd.read_csv(path, parse_dates=True, index_col='Date')
    except FileNotFoundError:
        st.error(f"File not found: {path}")
        return None
    return stock_data

# Streamlit app
def main():
    st.title("Trading Strategy Backtesting")

    # Sidebar for input parameters
    ticker_symbol = st.sidebar.selectbox("Ticker Symbol",
                                         ["AAPL", "AMZN", "GOOG", "META", "MSFT", "NVDA", "TSLA"])
    strategy = st.sidebar.selectbox("Trading Strategy",
                                    ["Mean Reversion - Bollinger",
                                     "Mean Reversion - RSI",
                                     "Bollinger-RSI Hybrid",
                                     "Pretrained Timeseries ML Model"])

    st.sidebar.header("Parameters")

    sma_period = st.sidebar.slider("SMA Period (Days)", 5, 50, 20)
    rsi_window = st.sidebar.slider("RSI Window (Days)", 5, 30, 14)
    std_dev_multiplier = st.sidebar.slider("Std Dev Multiplier", 1.0, 3.0, 2.0, step=0.25)

    # Load stock data
    stock_data = load_data(ticker_symbol)

    # Calculate indicators based on input parameters
    stock_data['SMA'] = stock_data['Close'].rolling(window=sma_period).mean()
    stock_data['STD'] = stock_data['Close'].rolling(window=sma_period).std()
    stock_data['Upper_Band'] = stock_data['SMA'] + (stock_data['STD'] * std_dev_multiplier)
    stock_data['Lower_Band'] = stock_data['SMA'] - (stock_data['STD'] * std_dev_multiplier)
    stock_data['RSI'] = rsi(stock_data['Close'].to_numpy(), rsi_window)

    # Display Equity Curve and Indicators
    st.plotly_chart(equity_curve(stock_data))
    with st.expander("RSI Calculation"): st.code(rsi_code, language='python')

    # Run backtesting
    results = run_test(stock_data)

    # Display results

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'], mode='lines', name='Close Price'))

    # Loop through the trades and add entry/exit markers
    for _, trade in results._trades.iterrows():
        # Entry marker
        fig.add_trace(go.Scatter(x=[trade['EntryTime']], y=[trade['EntryPrice']],
                                mode='markers', marker=dict(color='green', size=10, symbol='triangle-up'),
                                name='Entry'))
        
        # Exit marker
        fig.add_trace(go.Scatter(x=[trade['ExitTime']], y=[trade['ExitPrice']],
                                mode='markers', marker=dict(color='red', size=10, symbol='triangle-down'),
                                name='Exit'))

    # Update layout
    fig.update_layout(title='Trades on Price Chart', xaxis_title='Date', yaxis_title='Price')

    # Display in Streamlit
    st.plotly_chart(fig)

    st.text(results)

if __name__ == "__main__":
    main()
