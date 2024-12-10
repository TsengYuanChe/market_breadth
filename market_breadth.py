import yfinance as yf
import pandas as pd
import datetime

# 讀取 S&P 500 成分股資料
sp500_df = pd.read_csv('sp500_companies.csv')
sp500_df = sp500_df[['Security', 'GICS Sector', 'Symbol']]

start_date = '2023-01-01'  # yyyy-mm-dd
end_date = datetime.datetime.today().strftime('%Y-%m-%d')

tickers = sp500_df['Symbol'].tolist()
stocks_data = {}

for ticker in tickers:
    try:
        stocks_data[ticker] = yf.download(ticker, start=start_date, end=end_date)
        print(f'{ticker} data is downloaded')
    except (yf.YFPricesMissingError, yf.YFTzMissingError):
        print(f"警告: 股票 {ticker} 資料下載失敗，可能已除名或無資料。")

columns = ['Date', 'Total Percentage'] + [f'{sector} Percentage' for sector in sp500_df['GICS Sector'].unique()]
results_df = pd.DataFrame(columns=columns)

dates = pd.date_range(start=start_date, end=end_date, freq='B')
total_days = len(dates)
print(f'Overall {total_days} dates must be completed')
for date in dates:  # freq='B' 保證是開盤日
    date_str = date.strftime('%Y-%m-%d')
    sector_percentage = {sector: {'above_60ma': 0, 'total': 0} for sector in sp500_df['GICS Sector'].unique()}

    total_above_60ma = 0
    total_companies = 0
    
    for ticker in tickers:
        if ticker not in stocks_data:
            continue

        stock_data = stocks_data[ticker].loc[:date]  # 取該股票在該日期之前的資料
        
        if stock_data.empty:  # 如果沒有資料，跳過
            continue
        
        stock_data = stock_data.reset_index()
        stock_data_close = stock_data['Close']
            
        if len(stock_data) >= 60:
            # 計算60日移動平均
            stock_data['60MA'] = stock_data['Close'].rolling(window=60).mean()

            # 確保 60MA 並非 NaN
            if pd.notna(stock_data['60MA'].iloc[-1]):  
                # 提取最後的數值
                close_value = stock_data['Close'].iloc[-1].values[0]  # 已是單一數值
                ma_value = stock_data['60MA'].iloc[-1]  # 已是單一數值
                
                # 判斷股價是否高於 60MA
                is_above_60ma = close_value > ma_value
            else:
                is_above_60ma = False
        else:
            is_above_60ma = False
            
        sector = sp500_df.loc[sp500_df['Symbol'] == ticker, 'GICS Sector'].values[0]
        
        sector_percentage[sector]['total'] += 1
        if is_above_60ma:
            sector_percentage[sector]['above_60ma'] += 1
            
    sector_percentages = {
        sector: (values['above_60ma'] / values['total']) * 100 if values['total'] > 0 else 0
        for sector, values in sector_percentage.items()
    }
    total_percentage = sum(sector_percentages.values())
    
    row = {'Date': date_str, 'Total Percentage': total_percentage}
    
    for sector in sp500_df['GICS Sector'].unique():
        row[f'{sector} Percentage'] = sector_percentages.get(sector, 0)
    
    results_df = pd.concat([results_df, pd.DataFrame([row])], ignore_index=True)
    total_days -= 1
    print(f'Completed date: {date}| Ramaining days: {total_days}')

outputpath = f'{start_date}_market_breadth_analysis.csv'
results_df.to_csv(f'{outputpath}', index=False)
print(f"The result is located at {outputpath}")
