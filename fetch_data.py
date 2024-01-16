import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

symbols = {'TSLA', 'MSFT', 'AAPL', 'NVDA', 'META', 'GOOG', 'AMZN'}

for symbol in symbols:
    stock_data = yf.download(symbol, start='2020-01-01', end='2024-01-01')
    file_name = f'{symbol}_stock_data.csv'
    stock_data.to_csv(file_name, index=True)

print(stock_data.head())

stock_data = pd.read_csv('AAPL_stock_data.csv')

stock_data['Close'].plot(figsize=(10, 6))
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.show()