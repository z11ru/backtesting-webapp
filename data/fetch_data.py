import yfinance as yf

symbols = {'TSLA', 'MSFT', 'AAPL', 'NVDA', 'META', 'GOOG', 'AMZN'}

for symbol in symbols:
    stock_data = yf.download(symbol, start='2020-01-01', end='2024-01-01')
    file_name = f'{symbol}_stock_data.csv'
    stock_data.to_csv(file_name, index=True)