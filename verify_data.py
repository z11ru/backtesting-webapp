import pandas as pd
import matplotlib.pyplot as plt

# Define the stock ticker symbol
ticker_symbol = 'TSLA'  # Example: Apple Inc.
stock_data = pd.read_csv('TSLA_stock_data.csv')

# Plotting the closing price of the stock
stock_data['Close'].plot(figsize=(10, 6))
plt.title(f'Closing Price of {ticker_symbol}')
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.show()