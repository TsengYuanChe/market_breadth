import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup

# 獲取 S&P 500 成分股與其 GICS 部門資料
url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
tables = pd.read_html(url)
sp500_df = tables[0]

sp500_df = sp500_df[['Security', 'GICS Sector', 'GICS Sub-Industry', 'Symbol']]

print(sp500_df.head())

sp500_df.to_csv('sp500_companies.csv', index=False)