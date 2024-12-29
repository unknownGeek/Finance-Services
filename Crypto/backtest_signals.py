import pandas as pd

capital_per_trade = 10000


def calculate_stop_loss(df, sl_index, candlesCountForSL, is_buy_signal, entry_price, stop_loss_percentage, slBasedOnPercentageEnabled):
    """
    Calculate the stop loss based on the last candlesCountForSL.
    """
    if slBasedOnPercentageEnabled:
        return entry_price * (1 - stop_loss_percentage * 0.01)

    if candlesCountForSL == 0:
        return df['low'][sl_index] if is_buy_signal else df['high'][sl_index]

    # Ensure we have enough candles to calculate the stop loss
    if df is None or df.empty or sl_index < candlesCountForSL:
        return None  # Not enough data to calculate stop loss

    if is_buy_signal:
        # For buy signals, use the lowest price of the last candlesCountForSL candles
        lows = df['low'].iloc[sl_index - candlesCountForSL : sl_index+1]
        return lows.min() if not lows.empty else None  # Return the minimum low as the stop loss
    else:
        # For sell signals, use the highest price of the last candlesCountForSL candles
        highs = df['high'].iloc[sl_index - candlesCountForSL : sl_index+1]
        return highs.max() if not highs.empty else None  # Return the maximum high as the stop loss


def calculate_take_profit(entry_price, stop_loss, is_buy_signal, riskToRewardRatio):
    """
    Calculate the take profit based on the entry price, stop loss, and risk-to-reward ratio.
    """
    if is_buy_signal:
        # TP = entryPrice + (entryPrice - SL) * RRR for buy signals
        return entry_price + (entry_price - stop_loss) * riskToRewardRatio
    else:
        # TP = entryPrice - (SL - entryPrice) * RRR for sell signals
        return entry_price - (stop_loss - entry_price) * riskToRewardRatio


def get_entry_price(df, signal_index):
    """
    Get the entry price from the close price of the signal candle.
    """
    if df is None or df.empty or signal_index < 0 or signal_index >= len(df):
        return None  # Return None if the DataFrame is empty or index is out of bounds
    return df['close'].iloc[signal_index]


def evaluate_trade(df, signal_index, stop_loss, target_price, is_buy_signal, entry_price, quantity):
    """
    Evaluate the trade by checking future candles against stop loss and target price.
    """
    if df is None or df.empty or stop_loss is None or target_price is None:
        return 'INSUFFICIENT_DATA', None, None  # Mark as GREY if data is insufficient

    last_close_price = df['close'].iloc[-1]  # Get the last close price
    last_candle_date = df.index[-1]  # Get the last date in the DataFrame
    sl_value = quantity * (stop_loss - entry_price)# PnL calculation for SL hit
    tp_value = quantity * (target_price - entry_price)# PnL calculation for TP hit

    if not is_buy_signal:
        sl_value *= -1
        tp_value *= -1

    for future_index in range(signal_index + 1, len(df)):
        future_low = df['low'].iloc[future_index]
        future_high = df['high'].iloc[future_index]

        if is_buy_signal:
            # For buy signals, check if the low crosses the stop loss
            if future_low < stop_loss:
                return 'FAIL', df.index[future_index], sl_value
            if future_high >= target_price:
                return 'PASS', df.index[future_index], tp_value
        else:
            # For sell signals, check if the high crosses the stop loss
            if future_high > stop_loss:
                return 'FAIL', df.index[future_index], sl_value
            if future_low <= target_price:
                return 'PASS', df.index[future_index], tp_value

    # If neither SL nor TP is hit, calculate current P&L based on last close price
    if is_buy_signal:
        current_pnl = quantity * (last_close_price - entry_price)
    else:
        current_pnl = quantity * (entry_price - last_close_price)

    return 'OPEN', last_candle_date, current_pnl  # Trade is still open, return current P&L


def backtest_signal(ticker, date, signal, df, candlesCountForSL, riskToRewardRatio, stop_loss_percentage, slBasedOnPercentageEnabled):
    """
    Backtest a single signal for a given ticker.
    """
    empty_backtest_df = {
        'date': date,
        'ticker': ticker,
        'signal': signal,
        'entry_price': None,
        'stop_loss': None,
        'target_price': None,
        'trade_status': 'GREY',  # Mark as GREY due to insufficient data
        'close_time': None,
        'pnl': 0.0
    }
    if df is None or df.empty or date not in df.index:
        return empty_backtest_df

    signal_index = df.index.get_loc(date)

    # Check if there are enough candles to calculate stop loss
    if not slBasedOnPercentageEnabled and signal_index < candlesCountForSL:
        return empty_backtest_df

    entry_price = get_entry_price(df, signal_index)
    if entry_price is None:
        return empty_backtest_df

    # Define the SL index
    sl_index = signal_index  # The index of the signal candle

    is_buy_signal = signal == 'BUY'  # Determine if the signal is a buy or sell
    stop_loss = calculate_stop_loss(df, sl_index, candlesCountForSL, is_buy_signal, entry_price, stop_loss_percentage, slBasedOnPercentageEnabled)
    if stop_loss is None:
        return empty_backtest_df

    # Calculate quantity based on $1000 capital
    quantity = capital_per_trade / entry_price

    # Calculate target price using the new risk-to-reward ratio
    target_price = calculate_take_profit(entry_price, stop_loss, is_buy_signal, riskToRewardRatio)

    trade_status, close_time, pnl = evaluate_trade(df, signal_index, stop_loss, target_price, is_buy_signal, entry_price, quantity)

    return {
        'date': date,
        'ticker': ticker,
        'signal': signal,
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'target_price': target_price,
        'trade_status': trade_status,
        'close_time': close_time,  # Capture close time for both PASS and FAIL
        'pnl': pnl
    }


def backtest_signals(grouped_signals, tickersDataMap, candlesCountForSL, riskToRewardRatio, stop_loss_percentage, slBasedOnPercentageEnabled):
    """
    Backtest all signals in grouped_signals using tickersDataMap.
    """
    results = []
    total_pnl = 0.0

    for index, row in grouped_signals.iterrows():
        date = row['date']
        signal = row['signal']
        tickers = row['tickers']

        for ticker in tickers:
            if ticker in tickersDataMap:
                df = tickersDataMap[ticker]
                result = backtest_signal(ticker, date, signal, df, candlesCountForSL, riskToRewardRatio, stop_loss_percentage, slBasedOnPercentageEnabled)
                results.append(result)
                total_pnl += result['pnl']

    backtest_signals_df = pd.DataFrame(results)

    # Sort the DataFrame by 'date' and 'signal'
    backtest_signals_df = backtest_signals_df.sort_values(by=['date', 'ticker'])

    # Example counts based on signal types in backtest_signals_df
    # pass_count = backtest_signals_df[backtest_signals_df['trade_status'] == 'PASS'].count()['trade_status']
    # fail_count = backtest_signals_df[backtest_signals_df['trade_status'] == 'FAIL'].count()['trade_status']
    # pending_count = backtest_signals_df[backtest_signals_df['trade_status'] == 'OPEN'].count()['trade_status']
    # grey_count = backtest_signals_df[backtest_signals_df['trade_status'] == 'INSUFFICIENT_DATA'].count()['trade_status']

    pass_count = backtest_signals_df[backtest_signals_df['pnl'] > 0.0].count()['trade_status']
    fail_count = backtest_signals_df[backtest_signals_df['pnl'] < 0.0].count()['trade_status']
    pending_count = backtest_signals_df[backtest_signals_df['pnl'] == 0.0].count()['trade_status']
    grey_count = backtest_signals_df[backtest_signals_df['trade_status'] == 'INSUFFICIENT_DATA'].count()['trade_status']
    # Total signals
    total_signals = len(backtest_signals_df)

    # Calculate percentages
    pass_percentage = (pass_count / total_signals) * 100 if total_signals > 0 else 0
    fail_percentage = (fail_count / total_signals) * 100 if total_signals > 0 else 0
    pending_percentage = (pending_count / total_signals) * 100 if total_signals > 0 else 0
    grey_percentage = (grey_count / total_signals) * 100 if total_signals > 0 else 0

    # Calculate PnL
    PnL = (2 * pass_count) - fail_count
    PnL_percentage = (PnL / total_signals) * 100 if total_signals > 0 else 0

    # Calculate max profit and max loss
    max_profit = backtest_signals_df['pnl'].max()
    max_loss = backtest_signals_df['pnl'].min()

    print(f"Metrics for candlesCountForSL={candlesCountForSL} riskToRewardRatio={riskToRewardRatio} :")
    print(f"Count of PASS Trades: {pass_count} ({pass_percentage:.2f}%)")
    print(f"Count of FAIL Trades : {fail_count} ({fail_percentage:.2f}%)")
    print(f"Count of OPEN Trades: {pending_count} ({pending_percentage:.2f}%)")
    print(f"Count of INSUFFICIENT_DATA: {grey_count} ({grey_percentage:.2f}%)")
    print(f"Max Profit per Trade: ${max_profit:.2f}")
    print(f"Max Loss per Trade: ${max_loss:.2f}")
    print(f"Profit and Loss (PnL): {PnL} ({PnL_percentage:.2f}%)")
    print(f"Actual Total PnL: ${total_pnl:.2f} on capital_per_trade = ${capital_per_trade} with {total_pnl*100/capital_per_trade:.2f}%")

    return backtest_signals_df  # Return results as a DataFrame for easier analysis
