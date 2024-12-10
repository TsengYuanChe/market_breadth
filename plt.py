import pandas as pd
import matplotlib.pyplot as plt

# 讀取 CSV 文件
file_path = '2023-01-01_market_breadth_analysis.csv'
results_df = pd.read_csv(file_path)

# 假設 'Date' 列是字符串格式，我們將其轉換為 datetime 格式
results_df['Date'] = pd.to_datetime(results_df['Date'])

# 去除前 60 筆資料，因為它們無法計算 60MA
results_df = results_df.iloc[60:]

# 設定 y 軸的範圍，假設產業數為 11
industries_count = 11
y_max = industries_count * 100  # y軸的最大值

# 設定圖表
fig, ax = plt.subplots(figsize=(15, 6))

# 繪製 total_percentage 的線
ax.plot(results_df['Date'], results_df['Total Percentage'], label='Total Percentage', color='black', linewidth=2)

# 設定背景顏色
for i in range(1, len(results_df)):
    total_percentage = results_df['Total Percentage'].iloc[i]
    
    # 根據 total_percentage 的值設置背景顏色
    if total_percentage < 300:
        ax.axvspan(results_df['Date'].iloc[i-1], results_df['Date'].iloc[i], color='blue', alpha=0.3)  # 紅色背景
    elif 300 <= total_percentage < 500:
        ax.axvspan(results_df['Date'].iloc[i-1], results_df['Date'].iloc[i], color='yellow', alpha=0.3)  # 黃色背景
    elif 500 <= total_percentage < 800:
        ax.axvspan(results_df['Date'].iloc[i-1], results_df['Date'].iloc[i], color='green', alpha=0.3)  # 藍色背景
    else:
        ax.axvspan(results_df['Date'].iloc[i-1], results_df['Date'].iloc[i], color='red', alpha=0.3)
        
# 設定圖表標籤和標題
ax.set_xlabel('Date')
ax.set_ylabel('Total Percentage')
ax.set_title('Total Percentage with Industry Backgrounds')

# 顯示圖表
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()