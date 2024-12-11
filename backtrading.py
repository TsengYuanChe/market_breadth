import yfinance as yf
import pandas as pd
import backtrader as bt
import matplotlib.pyplot as plt

# 下載道瓊指數（DJI）資料
symbol_dji = "^DJI"  # 道瓊指數
start_date = "2023-01-01"
end_date = "2023-12-31"

# 下載道瓊指數的資料
dji_data = yf.download(symbol_dji, start=start_date, end=end_date)

# 檢查道瓊指數資料
print(dji_data.head())

# 讀取你之前計算的 market breadth 資料（這裡假設你的資料已經計算好）
file_path = '2023-01-01_market_breadth_analysis.csv'
results_df = pd.read_csv(file_path)

# 假設 'Date' 列是字符串格式，將其轉換為 datetime 格式
results_df['Date'] = pd.to_datetime(results_df['Date'])

# 去除前 60 筆資料，因為它們無法計算 60MA
results_df = results_df.iloc[60:]

# 設置 'Date' 列為索引
results_df.set_index('Date', inplace=True)

# 將道瓊指數的資料重設索引，確保索引層級一致
dji_data.reset_index(inplace=True)

# 合併道瓊指數資料和 market breadth 資料
# 這樣你就可以將 'total_percentage' 和道瓊指數的資料結合到一起
merged_data = pd.merge(dji_data[['Date', 'Open', 'Close']], results_df[['Total Percentage']], on='Date', how='inner')

# 檢查合併後的資料
print(merged_data.head())

# 定義資料源
class MarketBreadthData(bt.feeds.PandasData):
    lines = ('total_percentage',)  # 將 total_percentage 設為額外的線

    params = (
        ('datetime', None),  # 已經有 Date 作為索引
        ('open', -1),        # 使用道瓊指數的開盤價格
        ('high', -1),        # 無需此欄位，設置為 -1
        ('low', -1),         # 無需此欄位，設置為 -1
        ('close', -1),       # 使用道瓊指數的收盤價格
        ('volume', -1),      # 無需此欄位，設置為 -1
        ('openinterest', -1) # 無需此欄位，設置為 -1
    )

# 載入合併後的資料
data_feed = MarketBreadthData(dataname=merged_data)

# 定義策略
class MarketBreadthStrategy(bt.Strategy):
    params = (
        ('buy_threshold', 500),  # 這裡的 buy_threshold 代表當 total_percentage 超過某個閾值時買入
        ('sell_threshold', 300)  # 當 total_percentage 小於某個閾值時賣出
    )

    def __init__(self):
        self.total_percentage = self.data.total_percentage

    def next(self):
        # 根據 total_percentage 做出買賣決策
        if self.total_percentage[0] > self.params.buy_threshold:
            if not self.position:  # 沒有持倉時才買入
                self.buy()
        elif self.total_percentage[0] < self.params.sell_threshold:
            if self.position:  # 有持倉時才賣出
                self.sell()

# 創建回測引擎
cerebro = bt.Cerebro()

# 添加資料
cerebro.adddata(data_feed)

# 添加策略
cerebro.addstrategy(MarketBreadthStrategy)

# 設置初始資金
cerebro.broker.set_cash(10000)

# 設置佣金
cerebro.broker.set_commission(commission=0.001)

# 設置每個交易的價差
cerebro.broker.set_slippage_perc(0.01)

# 設置資金管理
cerebro.addsizer(bt.sizers.FixedSize, stake=10)

# 運行回測
cerebro.run()

# 顯示最終資金
print(f'Final Portfolio Value: {cerebro.broker.getvalue()}')

# 顯示圖表
cerebro.plot()