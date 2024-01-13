import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

ticker_symbol = 'TSLA'

stock_data = yf.download(ticker_symbol, start='2008-01-01', end='2024-01-01')
file_name = f'{ticker_symbol}_stock_data.csv'
stock_data.to_csv(file_name, index=True)

print(stock_data.head())

ticker_symbol = 'TSLA'
stock_data = pd.read_csv('TSLA_stock_data.csv')

stock_data['Close'].plot(figsize=(10, 6))
plt.title(f'Closing Price of {ticker_symbol}')
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.show()