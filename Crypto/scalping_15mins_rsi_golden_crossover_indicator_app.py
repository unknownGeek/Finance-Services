import datetime
import json
import pandas as pd
import numpy as np
import pandas_ta as ta
import matplotlib.pyplot as plt
import mplcursors  # Import mplcursors for interactive tooltips
import time  # Import time module to track execution time
import asyncio
import aiohttp
# Create custom legend handles
import matplotlib.patches as mpatches
import pytz
from Crypto.file_saver import create_date_directory, create_run_directory, save_to_csv
from Crypto.signals import generate_both_golden_crossover_signals
from Crypto.backtest_signals import backtest_signals

isTestEnv = False
exhaustive_logging_enabled = False
bullishCountThreshold = 130

# Get the current time in UTC
utc_time = datetime.datetime.now(pytz.utc)
# Convert to IST (Indian Standard Time)
time_ist = utc_time.astimezone(pytz.timezone('Asia/Kolkata'))
# Format the IST time as a string

interval = '15m'
start = '2024-12-27 00:00:00'  # in IST
end = time_ist.strftime('%Y-%m-%d %H:%M:%S')

startDateTime = time_ist

tickersDataMap = {}  # Initialize a dictionary to store data for the ticker
candlesCountForSL = 2
riskToRewardRatio = 2.0
backtest_signals_enabled = True

slBasedOnPercentageEnabled = False

# Define stop loss and take profit percentages
stop_loss_percentage = 2.0  # 2% stop loss


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
    global tickersDataMap
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

    # Localize index to UTC and then convert to IST
    df.index = df.index.tz_localize('UTC').tz_convert('Asia/Kolkata')

    # Store the DataFrame in the global tickersDataMap for the ticker
    tickersDataMap[ticker] = df[['open', 'high', 'low', 'close', 'volume']]  # Store DataFrame directly

    return tickersDataMap[ticker]


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
    if isTestEnv == True:
        tickers = ['LAZIOUSDT']
    totalCount = len(tickers)
    print(f'Extracted total={totalCount} CryptoPairInfo : {tickers}\n')

    all_signals = []

    # Disable SSL verification for the session
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        tasks = [generateSignalWithBinance(session, ticker, interval, start, end, all_signals) for ticker in tickers]
        await asyncio.gather(*tasks)

    signals_df = pd.DataFrame(all_signals)

    execution_time = time.time() - start_time
    print(f'Total execution time: {execution_time:.2f} seconds\n')

    # Check if signals_df is empty
    if signals_df.empty:
        print("No signals were generated. Exiting the script.")
        return  # Exit the function early

    grouped_signals = signals_df.groupby(['date', 'signal']).agg(
        tickers=('ticker', lambda x: list(set(x))),
        count=('ticker', 'size')
    ).reset_index()

    # Print the grouped signals
    print(f'Grouped Signals:\n{grouped_signals}\n')

    date_directory = create_date_directory(startDateTime)  # Pass startDateTime

    # Create a run directory
    run_directory = create_run_directory(date_directory, startDateTime)  # Pass startDateTime

    current_time = startDateTime.strftime('%Y%m%d_%H%M%S')  # Format: YYYYMMDD_HHMMSS

    # Save grouped_signals to a CSV file in the run directory
    crypto_report_filename = f'crypto_report_{current_time}.csv'
    save_to_csv(grouped_signals, run_directory, crypto_report_filename)

    if backtest_signals_enabled:
        backtest_signals_df = backtest_signals(grouped_signals, tickersDataMap, candlesCountForSL, riskToRewardRatio, stop_loss_percentage, slBasedOnPercentageEnabled)
        print(f'backtest_signals_df :\n{backtest_signals_df}\n')
        backtest_report_filename = f'backtest_report_{current_time}.csv'
        save_to_csv(backtest_signals_df, run_directory, backtest_report_filename)

    print(f'Plotting signals from {crypto_report_filename}\n')

    # Create a new column for color based on signals
    # Prioritize green for BUY signals, red for SELL signals
    grouped_signals['color'] = \
        np.where(grouped_signals['count'] > 0, np.where(grouped_signals['signal'] == 'BUY', 'green', 'red'), 'grey')

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

    print(f'Done plotting signals from {crypto_report_filename}\n')


if __name__ == "__main__":
    asyncio.run(main())
