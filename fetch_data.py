import pandas as pd
import yfinance as yf

# Define the stock ticker symbol
ticker_symbol = 'TSLA'  # Example: Apple Inc.

# Fetch historical data
stock_data = yf.download(ticker_symbol, start='2008-01-01', end='2024-01-01')
file_name = f'{ticker_symbol}_stock_data.csv'
stock_data.to_csv(file_name, index=True)

print(stock_data.head())  # Print first few rows of the data