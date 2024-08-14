The following .py files contain the backtesting code for the TRADEBOT data for various trading strategies involving different indicators like RSI, MACD, DMI, etc.,

The backtesting code is almost similar for all strategies, with changes only based on the indicator type used. 

Also, financial data for stocks, crypto or forex data can be downloaded from the 'yfinance' library for which the above strategies can be applied across different time frames (5min, daily).

              df = yf.download(stock, period="60d", interval="5m")
                   replace 'stock' with the ticker-name of the financial asset
