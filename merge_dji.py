import yfinance as yf
import pandas as pd

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

# 確保資料的日期對齊
dji_data.index = pd.to_datetime(dji_data.index)

# 找出共同的日期範圍
common_dates = results_df.index.intersection(dji_data.index)

# 根據共同的日期範圍選擇資料
dji_data = dji_data.loc[common_dates]
results_df = results_df.loc[common_dates]

# 將日期從索引中移除並設為列
dji_data.reset_index(inplace=True)
results_df.reset_index(inplace=True)

# 合併道瓊指數資料和 market breadth 資料
df = pd.DataFrame({
    'Date': dji_data['Date'],  # 將日期列作為第一欄
    'total_percentage': results_df['Total Percentage'].values,  # 加入 total_percentage
    'close': dji_data['Close'].values.flatten(),  # 加入道瓊的收盤價
    'open': dji_data['Open'].values.flatten(),    # 加入道瓊的開盤價
    'high': dji_data['High'].values.flatten(),    # 加入道瓊的最高價
    'low': dji_data['Low'].values.flatten(),      # 加入道瓊的最低價
    'volume': dji_data['Volume'].values.flatten() # 加入道瓊的成交量
})

# 刪除 'total_percentage' 為 0 的行
df = df[df['total_percentage'] != 0]

# 檢查合併後的資料
print(df.head())

# 儲存合併後的資料為新的 CSV 文件
df.to_csv('dji_market_breadth_combined.csv', index=False)

# 顯示結果
print("資料已成功合併並保存為 'dji_market_breadth_combined.csv'")