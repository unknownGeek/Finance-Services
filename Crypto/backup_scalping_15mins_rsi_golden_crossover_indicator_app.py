import datetime
import json
import os
import pandas as pd
import numpy as np
import pandas_ta as ta
import matplotlib.pyplot as plt
from signals import generate_golden_crossover_signals, generate_both_golden_crossover_signals
import mplcursors  # Import mplcursors for interactive tooltips
import time  # Import time module to track execution time
import asyncio
import aiohttp
# Create custom legend handles
import matplotlib.patches as mpatches
import pytz

isTestEnv = False
exhaustive_logging_enabled = False
testCount = 1
bullishCountThreshold = 130


# Get the current time in UTC
utc_time = datetime.datetime.now(pytz.utc)
# Convert to IST (Indian Standard Time)
time_ist = utc_time.astimezone(pytz.timezone('Asia/Kolkata'))
# Format the IST time as a string

interval = '5m'
start = '2024-12-27 00:00:00'  # in IST
end = time_ist.strftime('%Y-%m-%d %H:%M:%S')

startDateTime = time_ist


def extractCryptoPairInfo(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

    cryptoPairInfo = []
    if 'data' in data and isinstance(data['data'], list):
        for item in data['data']:
            if item["q"] == "USDT":
                cryptoPairInfo.append(item['s'])

    return cryptoPairInfo


async def fetch_binance_data(session, ticker, interval, start, end):
    columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades',
               'taker_base_vol', 'taker_quote_vol', 'ignore']
    usecols = ['open', 'high', 'low', 'close', 'volume', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol']
    start_timestamp = int(datetime.datetime.timestamp(pd.to_datetime(start)) * 1000)
    end_timestamp = int(datetime.datetime.timestamp(pd.to_datetime(end)) * 1000)
    df = pd.DataFrame()

    print(f'Downloading {interval} {ticker} ohlc-data ...', end=' \n')
    invokeCount = 1
    while True:
        url = f'https://www.binance.com/api/v3/klines?symbol={ticker}&interval={interval}&limit=1000&startTime={start_timestamp}&endTime={end_timestamp}'
        print(f'Iteration={invokeCount} => Invoking Binance klines api url={url}\n')
        invokeCount += 1
        async with session.get(url) as response:
            data = await response.json()
            if not data:
                print(f"No data returned for {ticker} in the specified time range[{start_timestamp}, {end_timestamp}].")
                break

            data = pd.DataFrame(data, columns=columns, dtype=np.float64)
            start_timestamp = int(data.open_time.tolist()[-1]) + 1
            data.index = [pd.to_datetime(x, unit='ms').strftime('%Y-%m-%d %H:%M:%S') for x in data.open_time]
            data = data[usecols]
            df = pd.concat([df, data], axis=0)
            if end in data.index.tolist():
                break
    print(f'Done for {ticker}.\n')
    df.index = pd.to_datetime(df.index)
    df = df.loc[:end]
    return df[['open', 'high', 'low', 'close']]


async def generateSignalWithBinance(session, ticker, interval, start, end, all_signals):
    try:
        data = await fetch_binance_data(session, ticker, interval, start, end)
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
        if exhaustive_logging_enabled:
            print(f'ticker={ticker} ma_values : \n{ma_values}')

        signals = generate_both_golden_crossover_signals(data, closes, ma_values, rsi_values, ma_of_rsi_values)
        print(f'ticker={ticker} signals : \n{signals}')

        # Collect signals with their corresponding dates
        for index, row in signals.iterrows():
            all_signals.append({'date': index, 'ticker': ticker, 'signal': row['signal']})

    except ConnectionError as connectionError:
        print(f'ticker={ticker} occurred connectionError : {connectionError}')
    except Exception as e:
        print(f'ticker={ticker} occurred an error: {e}')



async def main():
    # Start time tracking
    start_time = time.time()

    # Specify the path to your JSON file
    cryptoCoinsJsonFilePath = '/Users/h0k00sn/Documents/Projects/py/Crypto/resources/cryptoCoins.json'
    tickers = extractCryptoPairInfo(cryptoCoinsJsonFilePath)
    # tickers = ['BTCUSDT']
    totalCount = len(tickers)
    print(f'Extracted total={totalCount} CryptoPairInfo : {tickers}\n')

    all_signals = []

    # Disable SSL verification for the session
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        tasks = [generateSignalWithBinance(session, ticker, interval, start, end, all_signals) for ticker in tickers]
        await asyncio.gather(*tasks)

    signals_df = pd.DataFrame(all_signals)
    grouped_signals = signals_df.groupby(['date', 'signal']).agg(
        tickers=('ticker', lambda x: list(set(x))),
        count=('ticker', 'size')
    ).reset_index()

    grouped_signals['date'] = pd.to_datetime(grouped_signals['date']).dt.tz_localize('UTC').dt.tz_convert(
        'Asia/Kolkata')

    execution_time = time.time() - start_time
    print(f'Total execution time: {execution_time:.2f} seconds\n')

    # Print the grouped signals
    print(f'Grouped Signals:\n{grouped_signals}\n')

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
    csv_filename = f'crypto_report_{item_count + 1}_{current_time}.csv'
    full_path = os.path.join(date_directory, csv_filename)  # Combine date directory and filename

    grouped_signals.to_csv(full_path, index=False)

    print(f'Grouped signals saved to {csv_filename}\n')

    print(f'Plotting signals from {csv_filename}\n')


    # Create a new column for color based on signals
    # Prioritize green for BUY signals, red for SELL signals
    grouped_signals['color'] = \
        np.where(grouped_signals['count'] > 0, np.where(grouped_signals['signal'] == 'BUY', 'green', 'red'), 'grey')


    # Determine colors based on the count
    colors = ['red' if count > bullishCountThreshold else 'blue' for count in grouped_signals['count']]

    # Plotting a bar chart
    plt.figure(figsize=(12, 6))

    # Set bar width
    bar_width = 0.5
    x = np.arange(len(grouped_signals['date']))  # X positions for each date

    # Plot a single bar for each date
    bars = plt.bar(x, grouped_signals['count'],
                   width=bar_width, color=grouped_signals['color'], label='Signals')

    # Adding titles and labels
    plt.title('Crypto Signals : Bullish/Bearish Crypto Data')
    plt.xlabel('Date (IST)')
    plt.ylabel('Count of Signals')
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.grid(axis='y')  # Add grid lines for the y-axis
    plt.tight_layout()  # Adjust layout to prevent clipping of tick-labels

    # Create legend handles
    green_patch = mpatches.Patch(color='green', label='Buy Signals')
    red_patch = mpatches.Patch(color='red', label='Sell Signals')
    grey_patch = mpatches.Patch(color='grey', label='Both Signals')

    # Add the legend to the plot
    plt.legend(handles=[green_patch, red_patch, grey_patch])

    # Adding interactive tooltips with mplcursors
    mplcursors.cursor(bars, hover=True).connect("add", lambda sel: sel.annotation.set_text(
        f'Date: {grouped_signals["date"].dt.strftime("%Y-%m-%d %H:%M:%S").iloc[sel.index]}\n'
        f'Count: {grouped_signals["count"].iloc[sel.index]}\n'
        f'Signal: {grouped_signals["signal"].iloc[sel.index]}'
    ))
    # plt.axhline(y=bullishCountThreshold, color='red', linestyle='--', label='Bullish Count Threshold')

    # Save the plot to a file
    # plt.savefig('signal_count_plot.png')  # Save as PNG file

    plt.show()

    print(f'Done plotting signals from {csv_filename}\n')


if __name__ == "__main__":
    asyncio.run(main())
