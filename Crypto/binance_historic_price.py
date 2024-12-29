import requests
import datetime
import json
import os
import pandas as pd
import numpy as np
import pandas_ta as ta
import matplotlib.pyplot as plt
from signals import generate_signals
import mplcursors  # Import mplcursors for interactive tooltips


isTestEnv = False
exhaustive_logging_enabled = False
testCount = 10
bullishCountThreshold = 130
interval = '1d'
start = '2024-01-01 00:00:00'  # in UTC
end = datetime.datetime.utcnow().strftime('%Y-%m-%d') + ' 00:00:00'  # Set end to today's date in UTC at 00:00:00

startDateTime = datetime.datetime.now()


def extractCryptoPairInfo(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

    cryptoPairInfo = []
    if 'data' in data and isinstance(data['data'], list):
        for item in data['data']:
            if item["q"] == "USDT":
                cryptoPairInfo.append(item['s'])

    return cryptoPairInfo


def get_binance_data_by_requests(ticker, interval, start, end):
    columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades',
               'taker_base_vol', 'taker_quote_vol', 'ignore']
    usecols = ['open', 'high', 'low', 'close', 'volume', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol']
    start = int(datetime.datetime.timestamp(pd.to_datetime(start)) * 1000)
    end_u = int(datetime.datetime.timestamp(pd.to_datetime(end)) * 1000)
    df = pd.DataFrame()
    print(f'Downloading {interval} {ticker} ohlc-data ...', end=' ')
    while True:
        url = f'https://www.binance.com/api/v3/klines?symbol={ticker}&interval={interval}&limit=1000&startTime={start}#&endTime={end_u}'
        data = pd.DataFrame(requests.get(url, headers={'Cache-Control': 'no-cache', "Pragma": "no-cache"}).json(),
                            columns=columns, dtype=np.float64)
        start = int(data.open_time.tolist()[-1]) + 1
        data.index = [pd.to_datetime(x, unit='ms').strftime('%Y-%m-%d %H:%M:%S') for x in data.open_time]
        data = data[usecols]
        df = pd.concat([df, data], axis=0)
        if end in data.index.tolist():
            break
    print('Done.')
    df.index = pd.to_datetime(df.index)
    df = df.loc[:end]
    return df[['open', 'high', 'low', 'close']]


def generateSignalWithBinance(ticker, interval, start, end, all_signals):
    try:
        data = get_binance_data_by_requests(ticker=ticker, interval=interval, start=start, end=end)
        if exhaustive_logging_enabled:
            print(data)

        # Extract closing prices
        closes = data['close']

        rsi_values = ta.rsi(close=closes, length=14)
        if exhaustive_logging_enabled:
            print(f'ticker={ticker} rsi_values : \n{rsi_values}')

        ma_of_rsi_values = ta.sma(close=rsi_values, length=14)
        if exhaustive_logging_enabled:
            print(f'ticker={ticker} ma_of_rsi_values : \n{ma_of_rsi_values}')

        ma_values = ta.sma(close=closes, length=8)
        # ta.cross()
        if exhaustive_logging_enabled:
            print(f'ticker={ticker} ma_values : \n{ma_values}')

        signals = generate_signals(closes, ma_values, rsi_values, ma_of_rsi_values)
        print(f'ticker={ticker} signals : \n{signals}')

        # Collect signals with their corresponding dates
        for index, row in signals.iterrows():
            all_signals.append({'date': index, 'ticker': ticker, 'signal': row['signal']})

    except ConnectionError as connectionError:
        print(f'ticker={ticker} occurred connectionError : {connectionError}')
    except Exception as exp:
        print(f'ticker={ticker} occurred exp : {exp}')


# Specify the path to your JSON file
cryptoCoinsJsonFilePath = '/Users/h0k00sn/Documents/Projects/py/Crypto/resources/cryptoCoins.json'
tickers = extractCryptoPairInfo(cryptoCoinsJsonFilePath)
totalCount = len(tickers)
# Print the extracted CryptoPairInfo
print(f'Extracted total={totalCount} CryptoPairInfo : {tickers}')

all_signals = []
count = 1
for ticker in tickers:
    print(f'\nRunning #{count}/{totalCount} for ticker={ticker} =>')
    generateSignalWithBinance(ticker=ticker, interval=interval, start=start, end=end, all_signals=all_signals)
    count += 1
    if isTestEnv and count > testCount:
        break

# Convert all signals to a DataFrame for easier manipulation
signals_df = pd.DataFrame(all_signals)

# Group by date and aggregate signals
grouped_signals = signals_df.groupby('date').agg(
    tickers=('ticker', lambda x: list(set(x))),  # Get unique tickers as a list
    count=('ticker', 'size')  # Count of tickers
).reset_index()

# Print the grouped signals
print(f'Grouped Signals:\n{grouped_signals}')


current_date = startDateTime.strftime('%Y-%m-%d')
base_directory = '/Users/h0k00sn/Documents/Projects/py/Crypto/resources/crypto-reports'
date_directory = os.path.join(base_directory, current_date)  # Create the full path for the date directory

# Initialize item count
item_count = 0

# Create the date directory if it doesn't exist
if not os.path.exists(date_directory):
    os.makedirs(date_directory)
else:
    # Count the number of items in the existing directory
    item_count = sum(len(files) for _, _, files in os.walk(date_directory))

# Save grouped_signals to a CSV file with current execution time
current_time = startDateTime.strftime('%Y%m%d_%H%M%S')  # Format: YYYYMMDD_HHMMSS
csv_filename = f'crypto_report_{item_count+1}_{current_time}.csv'
full_path = os.path.join(date_directory, csv_filename)  # Combine date directory and filename


grouped_signals.to_csv(full_path, index=False)

print(f'Grouped signals saved to {csv_filename}')


print(f'Plotting signals from {csv_filename}')

# Determine colors based on the count
colors = ['red' if count > bullishCountThreshold else 'blue' for count in grouped_signals['count']]

# Plotting a bar chart
plt.figure(figsize=(12, 6))
bars = plt.bar(grouped_signals['date'], grouped_signals['count'], color=colors, width=0.5)

# Adding titles and labels
plt.title('Bullish Crypto-Coins Data')
plt.xlabel('Date')
plt.ylabel('Count of Bullish Crypto-Coins')
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
plt.grid(axis='y')  # Add grid lines for the y-axis
plt.tight_layout()  # Adjust layout to prevent clipping of tick-labels

# Adding tooltips
mplcursors.cursor(bars, hover=True).connect("add", lambda sel: sel.annotation.set_text(
    f'Date: {grouped_signals["date"].iloc[sel.index]}\nCount: {grouped_signals["count"].iloc[sel.index]}'))


plt.axhline(y=bullishCountThreshold, color='red', linestyle='--', label='Bullish Count Threshold')

plt.show()

print(f'Done plotting signals from {csv_filename}')
