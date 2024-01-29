import streamlit as st
from process import *

import pandas as pd
import numpy as np
import os

# Load and process stock data
@st.cache_data
def load_data(symbol, start_date, end_date):
    current_dir = os.path.dirname(__file__)
    data_dir = os.path.join(current_dir, '..', 'data')
    file_name = f'{symbol}_stock_data.csv'
    path = os.path.join(data_dir, file_name)
    try:
        stock_data = pd.read_csv(path, parse_dates=['Date'])
        # Filter the data based on the start and end dates
        mask = (stock_data['Date'] >= pd.to_datetime(start_date)) & (stock_data['Date'] <= pd.to_datetime(end_date))
        return stock_data.loc[mask]
    except FileNotFoundError:
        st.error(f"File not found: {path}")
        return pd.DataFrame()

# Streamlit app
def main():
    st.set_page_config(layout="wide")

    ## SIDEBAR ##

    st.sidebar.header("Symbol")

    ticker_symbol = st.sidebar.selectbox("Ticker Symbol",
                                         ["AAPL", "AMZN", "GOOG", "META", "MSFT", "NVDA", "TSLA"])
    
    start_date = st.sidebar.date_input("Start Date",
                                       value=pd.to_datetime('2022-01-01'),
                                       min_value=pd.to_datetime('2010-01-01'),
                                       max_value=pd.to_datetime('2024-01-01'))
    
    end_date = st.sidebar.date_input("End Date",
                                     value=pd.to_datetime('2024-01-01'),
                                     min_value=start_date,
                                     max_value=pd.to_datetime('2024-01-01'))
    
    st.sidebar.header("Entry Conditions")

    entry_use_support_line = st.sidebar.checkbox("Support/Resistance", key='entry1')
    entry_use_bollinger_band = st.sidebar.checkbox("Bollinger Band", key='entry2')
    entry_use_rsi = st.sidebar.checkbox("RSI", key='entry3')
    entry_use_MACD = st.sidebar.checkbox("MACD", key='entry4')
    entry_use_oscillator = st.sidebar.checkbox("Stochastic Oscillator", key='entry5')

    st.sidebar.header("Exit Conditions")

    exit_use_support_line = st.sidebar.checkbox("Support/Resistance", key='exit1')
    exit_use_bollinger_band = st.sidebar.checkbox("Bollinger Band", key='exit2')
    exit_use_rsi = st.sidebar.checkbox("RSI", key='exit3')
    exit_use_MACD = st.sidebar.checkbox("MACD", key='exit4')
    exit_use_oscillator = st.sidebar.checkbox("Stochastic Oscillator", key='exit5')
    exit_use_max_profit = st.sidebar.checkbox("Profit Limit", key='exit6')
    exit_use_max_drawdown = st.sidebar.checkbox("Drawdown Limit", key='exit7')

    html_content = """
    <style>
        .small-text {
            font-size: 12px; /* Adjust the size as needed */
            font-family: Arial, sans-serif; /* Set the Arial font */
        }
        a {
            color: inherit; /* Optional: ensures link color matches text color */
            text-decoration: none; /* Optional: no underline */
        }
    </style>
    <div class="small-text">
        Henry Zhao | 
        <a href="https://github.com/z11ru" target="_blank">github</a> | 
        <a href="https://linkedin.com/in/hrzhao" target="_blank">linkedin</a>
    </div>
    """

    st.sidebar.markdown(html_content, unsafe_allow_html=True)

    ## MAIN PAGE ##

    st.subheader("Trading Strategy Backtesting: " + ticker_symbol)
    left_pane, right_pane = st.columns([3,1])

    with right_pane:
        st.subheader("Parameters")

        sma_period = st.slider("SMA Period (Days)", 5, 50, 20)
        rsi_window = st.slider("RSI Window (Days)", 5, 30, 14)
        std_dev_multiplier = st.slider("Std Dev Multiplier", 1.0, 3.0, 2.0, step=0.25)

    # Load stock data
    stock_data = load_data(ticker_symbol, start_date, end_date)

    # Calculate indicators based on input parameters
    stock_data['SMA'] = stock_data['Close'].rolling(window=sma_period).mean()
    stock_data['STD'] = stock_data['Close'].rolling(window=sma_period).std()
    stock_data['Upper_Band'] = stock_data['SMA'] + (stock_data['STD'] * std_dev_multiplier)
    stock_data['Lower_Band'] = stock_data['SMA'] - (stock_data['STD'] * std_dev_multiplier)
    stock_data['RSI'] = rsi(stock_data['Close'].to_numpy(), rsi_window)

    # Run backtesting
    results = run_test(stock_data)

    with left_pane: st.plotly_chart(bollinger_curve(stock_data, results), use_container_width=True)
    with right_pane:
        if st.button('Optimize Parameters'):
            with st.spinner('Searching parameters... Please wait.'):
                best_params = optimize_parameters(stock_data)
            st.markdown(f"**Optimized Parameters:**\n- SMA Period: {best_params['SMA Period']}\n- Std Dev Multiplier: {best_params['Std Dev Multiplier']}\n- RSI Window: {best_params['RSI Window']}")
            st.write("Please adjust the sliders to these optimized values.")

        with st.expander("Backtesting results"): st.text(results)

    with st.expander("List of Trades"): st.text(results._trades)
if __name__ == "__main__":
    main()
