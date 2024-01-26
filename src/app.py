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
    return stock_data[stock_data.index >= '2022-01-01']

# Streamlit app
def main():
    st.set_page_config(layout="wide")

    st.title("Trading Strategy Backtesting")

    # Sidebar for input parameters
    st.sidebar.header("Symbol and Strategy")

    ticker_symbol = st.sidebar.selectbox("Ticker Symbol",
                                         ["AAPL", "AMZN", "GOOG", "META", "MSFT", "NVDA", "TSLA"])
    strategy = st.sidebar.selectbox("Trading Strategy",
                                    ["Bollinger-RSI Hybrid",
                                     "Pretrained Timeseries ML Model"])

    st.sidebar.header("Parameters")

    sma_period = st.sidebar.slider("SMA Period (Days)", 5, 50, 20)
    rsi_window = st.sidebar.slider("RSI Window (Days)", 5, 30, 14)
    std_dev_multiplier = st.sidebar.slider("Std Dev Multiplier", 1.0, 3.0, 2.0, step=0.25)

    st.sidebar.text("Henry Zhao | github.com/z11ru \nlinkedin.com/in/hrzhao")

    st.subheader(ticker_symbol + " - " + strategy)
    # Load stock data
    stock_data = load_data(ticker_symbol)

    # Calculate indicators based on input parameters
    stock_data['SMA'] = stock_data['Close'].rolling(window=sma_period).mean()
    stock_data['STD'] = stock_data['Close'].rolling(window=sma_period).std()
    stock_data['Upper_Band'] = stock_data['SMA'] + (stock_data['STD'] * std_dev_multiplier)
    stock_data['Lower_Band'] = stock_data['SMA'] - (stock_data['STD'] * std_dev_multiplier)
    stock_data['RSI'] = rsi(stock_data['Close'].to_numpy(), rsi_window)

    # Run backtesting
    results = run_test(stock_data)

    # Display results
    st.plotly_chart(bollinger_curve(results, stock_data, results), use_container_width=True)

    if st.button('Optimize Parameters'):
        with st.spinner('Searching parameters... Please wait.'):
            best_params = optimize_parameters(stock_data)

        # Display the optimized parameters
        st.markdown(f"**Optimized Parameters:**\n- SMA Period: {best_params['SMA Period']}\n- Std Dev Multiplier: {best_params['Std Dev Multiplier']}\n- RSI Window: {best_params['RSI Window']}")

        # Display a note asking user to adjust sliders
        st.write("Please adjust the sliders to these optimized values.")

    with st.expander("RSI Calculation"): st.code(rsi_code, language='python')

    with st.expander("Backtesting results"): st.text(results)

    with st.expander("List of Trades"): st.text(results._trades)

if __name__ == "__main__":
    main()
