import yfinance as yf
import pandas as pd
import datetime

# 讀取 S&P 500 成分股資料
sp500_df = pd.read_csv('sp500_companies.csv')
sp500_df = sp500_df[['Security', 'GICS Sector', 'Symbol']]

start_date = '2023-01-01'  # yyyy-mm-dd
end_date = datetime.datetime.today().strftime('%Y-%m-%d')

tickers = ['AAPL']
stocks_data = {}

# 下載股票資料，無需設定 group_by
for ticker in tickers:
    try:
        # 默認使用 group_by=None，返回每支股票的資料
        stocks_data[ticker] = yf.download(ticker, start=start_date, end=end_date)
    except (yf.YFPricesMissingError, yf.YFTzMissingError):
        print(f"警告: 股票 {ticker} 資料下載失敗，可能已除名或無資料。")

# 初始化 DataFrame 用於儲存結果
columns = ['Date', 'Total Percentage'] + [f'{sector} Percentage' for sector in sp500_df['GICS Sector'].unique()]
results_df = pd.DataFrame(columns=columns)

# 逐日計算各部門的百分比
for date in pd.date_range(start=start_date, end=end_date, freq='B'):  # freq='B' 保證是開盤日
    date_str = date.strftime('%Y-%m-%d')
    sector_percentage = {sector: {'above_60ma': 0, 'total': 0} for sector in sp500_df['GICS Sector'].unique()}

    total_above_60ma = 0
    total_companies = 0
    
    # 按部門分類，並計算每個部門的股價高於 60MA 的百分比
    for ticker in tickers:
        if ticker not in stocks_data:
            continue

        stock_data = stocks_data[ticker].loc[:date]  # 取該股票在該日期之前的資料
        
        if stock_data.empty:  # 如果沒有資料，跳過
            continue
        
        stock_data = stock_data.reset_index()

        # 確保 'Close' 欄位存在
        if 'Close' not in stock_data.columns:
            print(f"警告: 股票 {ticker} 缺少 'Close' 欄位，跳過該股票。")
            continue

        # 檢查資料是否足夠 (至少 60 天)
        if len(stock_data) >= 60:
            stock_data['60MA'] = stock_data['Close'].rolling(window=60).mean()
            
            # 判斷股價是否高於 60MA
            is_above_60ma = stock_data['Close'].iloc[-1] > stock_data['60MA'].iloc[-1]
        else:
            # 如果資料不足 60 天，則跳過這一天的計算
            is_above_60ma = False
        
        # 取得該股票所屬的部門
        sector = sp500_df.loc[sp500_df['Symbol'] == ticker, 'GICS Sector'].values[0]
        
        # 統計部門資料
        sector_percentage[sector]['total'] += 1
        if is_above_60ma:
            sector_percentage[sector]['above_60ma'] += 1

        # 總計
        total_companies += 1
        if is_above_60ma:
            total_above_60ma += 1

    # 計算每個部門的百分比
    sector_percentages = {
        sector: (values['above_60ma'] / values['total']) * 100 if values['total'] > 0 else 0
        for sector, values in sector_percentage.items()
    }
    
    # 構造結果並添加到 DataFrame
    row = {'Date': date_str, 'Total Percentage': (total_above_60ma / total_companies) * 100 if total_companies > 0 else 0}
    
    for sector in sp500_df['GICS Sector'].unique():
        row[f'{sector} Percentage'] = sector_percentages.get(sector, 0)
    
    results_df = pd.concat([results_df, pd.DataFrame([row])], ignore_index=True)

# 顯示結果
print(results_df)

# 儲存結果到 CSV 文件
results_df.to_csv(f'{start_date}_market_breadth_analysis.csv', index=False)