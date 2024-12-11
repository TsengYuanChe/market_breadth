import pandas as pd
import backtrader as bt
import matplotlib.pyplot as plt

# 讀取市場寬度資料
file_path = '2023-01-01_market_breadth_analysis.csv'
results_df = pd.read_csv(file_path)

# 假設 'Date' 列是字符串格式，我們將其轉換為 datetime 格式
results_df['Date'] = pd.to_datetime(results_df['Date'])

# 去除前 60 筆資料，因為它們無法計算 60MA
results_df = results_df.iloc[60:]

class MarketBreadthData(bt.feeds.PandasData):
    # 定義 total_percentage 作為額外的線
    lines = ('total_percentage',)
    
    # 在此設置 params，確保其它欄位都設為 -1
    params = (
        ('datetime', None),  # 已經有 Date 作為索引
        ('open', -1),        # 沒有開盤價格，設置為 -1
        ('high', -1),        # 沒有最高價格，設置為 -1
        ('low', -1),         # 沒有最低價格，設置為 -1
        ('close', -1),       # 沒有收盤價格，設置為 -1
        ('volume', -1),      # 沒有交易量，設置為 -1
        ('openinterest', -1) # 沒有開盤未平倉合約，設置為 -1
    )
    
data_feed = MarketBreadthData(dataname=results_df)

# 檢查資料加載是否成功
print(data_feed.lines)