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
    
    st.sidebar.header("Conditions")

    use_bollinger_band = st.sidebar.checkbox("Bollinger Band", value=True)
    use_rsi = st.sidebar.checkbox("RSI", value=True)
    max_profit = st.sidebar.number_input("Profit Limit (%)", value=25) / 100  # Convert percentage to decimal
    max_drawdown = st.sidebar.number_input("Drawdown Limit (%)", value=-50) / 100  # Convert percentage to decimal

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
    results = run_test(use_bollinger_band, use_rsi, max_profit, max_drawdown, stock_data)

    # Prepare metrics data
    metrics_data = {
        'Metric': [
            'Final Equity',
            'Peak Equity',
            'Return',
            'Buy & Hold Return',
            'Max. Drawdown',
            'Sharpe Ratio'
        ],
        'Value': [
            f"{results['Equity Final [$]']:.2f}",
            f"{results['Equity Peak [$]']:.2f}",
            f"{results['Return [%]']:.2f}%",
            f"{results['Buy & Hold Return [%]']:.2f}%",
            f"{results['Max. Drawdown [%]']:.2f}%",
            'N/A' if pd.isna(results['Sharpe Ratio']) else f"{results['Sharpe Ratio']:.2f}"
        ]
    }

    metrics_df = pd.DataFrame(metrics_data)

    # Display results
    with left_pane: st.plotly_chart(plot_curve(stock_data, results), use_container_width=True)
    with right_pane:
        if st.button('Optimize Parameters'):
            with st.spinner('Searching parameters... Please wait.'):
                best_params = optimize_parameters(stock_data)
            st.markdown(f"**Optimized Parameters:**\n- SMA Period: {best_params['SMA Period']}\n- Std Dev Multiplier: {best_params['Std Dev Multiplier']}\n- RSI Window: {best_params['RSI Window']}")
            st.write("Please adjust the sliders to these optimized values.")

        st.markdown(metrics_df.style.hide(axis="index").to_html(), unsafe_allow_html=True)

    with st.expander("List of Trades"): st.text(results._trades)
if __name__ == "__main__":
    main()
