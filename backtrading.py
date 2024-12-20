import backtrader as bt
import matplotlib.pyplot as plt
import pandas as pd

# 創建自定義的資料源類
class MarketBreadthData(bt.feeds.GenericCSVData):
    lines = ('total_percentage',)
    
    params = (
        ('datetime', 0),  # 日期列
        ('open', 1),       # 開盤價
        ('high', 2),       # 最高價
        ('low', 3),        # 最低價
        ('close', 4),      # 收盤價
        ('volume', 5),     # 成交量
        ('openinterest', -1),  # 開盤未平倉合約（不需要）
        ('total_percentage', 6),  # 市場寬度百分比
    )
    def _loadline(self, linetokens):
        dt = linetokens[0]
        # 將日期轉換為包含時間的格式 (默認時間為 00:00:00)
        dt = dt + " 00:00:00"  # 將時間設為 00:00:00
        dt = pd.to_datetime(dt)
        self.datetime[0] = bt.date2num(dt)

# 載入資料
data_feed = MarketBreadthData(dataname='dji_market_breadth_combined.csv')

# 定義策略
class MarketBreadthStrategy(bt.Strategy):
    params = (
        ('buy_threshold', 500),  # 這裡的 buy_threshold 代表當 total_percentage 超過某個閾值時買入
        ('sell_threshold', 300)  # 當 total_percentage 小於某個閾值時賣出
    )

    def __init__(self):
        self.total_percentage = self.data.total_percentage
        self.buy_dates = []  # 用來儲存每次買入的日期和價格
        self.sell_dates = []  # 用來儲存每次賣出的日期和價格

    def next(self):
        # 根據 total_percentage 做出買賣決策
        if self.total_percentage[0] > self.params.buy_threshold:
            if not self.position:  # 沒有持倉時才買入
                self.buy()
                self.buy_dates.append((self.data.datetime.date(0), self.data.close[0]))  # 記錄買入日期和價格
        elif self.total_percentage[0] < self.params.sell_threshold:
            if self.position:  # 有持倉時才賣出
                self.sell()
                self.sell_dates.append((self.data.datetime.date(0), self.data.close[0]))  # 記錄賣出日期和價格

# 創建回測引擎
cerebro = bt.Cerebro()

# 添加資料
cerebro.adddata(data_feed)

# 添加策略
cerebro.addstrategy(MarketBreadthStrategy)

# 設置初始資金
cerebro.broker.set_cash(10000)

# 設置佣金
cerebro.broker.setcommission(commission=0.001)  # 設置佣金

# 設置每個交易的價差
cerebro.broker.set_slippage_perc(0.01)

# 設置資金管理
cerebro.addsizer(bt.sizers.FixedSize, stake=10)

# 運行回測
cerebro.run()

# 顯示最終資金
print(f'Final Portfolio Value: {cerebro.broker.getvalue()}')

# 獲取策略實例
strategy = cerebro.strats

print(strategy)
