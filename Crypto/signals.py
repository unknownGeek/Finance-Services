import pandas as pd

rsiMaxValForLong = 55
rsiMAMaxValForLong = 52
validCandleMult = 1.5
rsiMinValForShort = 62
rsiMAMinValForShort = 62


def generate_signals(closes, ma_values, rsi_values, ma_of_rsi_values):
    """
    Generate buy signals based on price/MA crossover
    """
    # Initialize a Series with None values
    signals = pd.Series(index=closes.index, dtype='object')

    for i in range(1, len(closes)):
        # Check for None or NaN values in the required series
        if i < 1 or pd.isna(ma_values[i]) or pd.isna(ma_values[i - 1]) or \
                pd.isna(rsi_values[i]) or pd.isna(rsi_values[i - 1]) or \
                pd.isna(ma_of_rsi_values[i]) or pd.isna(ma_of_rsi_values[i - 1]):
            signals[i] = None
            continue

        isPriceCrossingSma = float(closes[i]) > ma_values[i] and float(closes[i - 1]) <= ma_values[i - 1]
        isRsiCrossingSmaOfRsi = float(rsi_values[i]) > ma_of_rsi_values[i] and float(rsi_values[i - 1]) <= \
                                ma_of_rsi_values[i - 1]

        # Generate buy signal when price crosses above MA
        # if isPriceCrossingSma and isRsiCrossingSmaOfRsi:
        if isPriceCrossingSma:
            signals[i] = 'BUY'
        else:
            signals[i] = None

    # Create a DataFrame with closes and signals
    result_df = pd.DataFrame({'close': closes, 'signal': signals})

    # Filter the DataFrame to return only rows where signal is not None
    filtered_df = result_df[result_df['signal'].notna()]

    return filtered_df


def generate_golden_crossover_signals(opens, closes, ma_values, rsi_values, ma_of_rsi_values):
    """
    Generate buy signals based on price/MA crossover
    """
    # Initialize a Series with None values
    signals = pd.Series(index=closes.index, dtype='object')

    for i in range(1, len(closes)):
        # Check for None or NaN values in the required series
        if i < 1 or pd.isna(ma_values[i]) or pd.isna(ma_values[i - 1]) or \
                pd.isna(rsi_values[i]) or pd.isna(rsi_values[i - 1]) or \
                pd.isna(ma_of_rsi_values[i]) or pd.isna(ma_of_rsi_values[i - 1]):
            signals[i] = None
            continue

        candleBodySize = abs(float(closes[i]) - float(opens[i]))
        if candleBodySize == 0.0:
            signals[i] = None
            continue

        percentCrossingAboveDiff = (float(closes[i]) - ma_values[i]) * 100 / candleBodySize
        percentCrossingBelowDiff = (float(ma_values[i]) - opens[i]) * 100 / candleBodySize

        isPriceCrossingValid = percentCrossingAboveDiff > 25 and percentCrossingBelowDiff > 25

        isPriceCrossingSma = float(closes[i]) > ma_values[i] and float(closes[i - 1]) <= ma_values[i - 1]
        isRsiCrossingSmaOfRsi = float(rsi_values[i]) > ma_of_rsi_values[i] and float(rsi_values[i - 1]) <= \
                                ma_of_rsi_values[i - 1]
        isRsiBelowMaxValForLong = rsi_values[i] < rsiMaxValForLong
        isRsiMABelowMaxValForLong = ma_of_rsi_values[i] < rsiMAMaxValForLong
        greenCandle = closes[i] > opens[i]
        isPriceIncreasing = closes[i - 1] < closes[i]
        isPrevCandleFarFromSma = ma_values[i - 1] > max(opens[i - 1], closes[i - 1])
        isGreenCandleCrossingSma = opens[i] < ma_values[i] < closes[i]
        isSmaDecreasing = True

        if i > 3:
            isSmaDecreasing = ma_values[i - 3] > ma_values[i - 2] > ma_values[i - 1] > ma_values[i]

        # Generate buy signal when price crosses above MA
        # if isPriceCrossingSma and isRsiCrossingSmaOfRsi:
        if isPriceCrossingSma and isRsiCrossingSmaOfRsi and isRsiBelowMaxValForLong and \
                isRsiMABelowMaxValForLong and isPriceIncreasing and isSmaDecreasing and \
                greenCandle and isPrevCandleFarFromSma and isGreenCandleCrossingSma and isPriceCrossingValid:
            signals[i] = 'BUY'
        else:
            signals[i] = None

    # Create a DataFrame with closes and signals
    result_df = pd.DataFrame({'close': closes, 'signal': signals})

    # Filter the DataFrame to return only rows where signal is not None
    filtered_df = result_df[result_df['signal'].notna()]

    return filtered_df


def generate_both_golden_crossover_signals(data, closes, ma_values, rsi_values, ma_of_rsi_values):
    """
    Generate buy signals based on price/MA crossover
    """
    # Initialize a Series with None values
    signals = pd.Series(index=closes.index, dtype='object')

    for i in range(1, len(closes)):
        # Check for None or NaN values in the required series
        if i < 1 or pd.isna(ma_values[i]) or pd.isna(ma_values[i - 1]) or \
                pd.isna(rsi_values[i]) or pd.isna(rsi_values[i - 1]) or \
                pd.isna(ma_of_rsi_values[i]) or pd.isna(ma_of_rsi_values[i - 1]):
            signals[i] = None
            continue

        candleBodySize = abs(float(closes[i]) - float(data['open'][i]))
        if candleBodySize == 0.0:
            signals[i] = None
            continue
        # Generate buy signal when price crosses above MA
        # if isPriceCrossingSma and isRsiCrossingSmaOfRsi:
        if is_it_a_buy_signal(i, data, closes, ma_values, rsi_values, ma_of_rsi_values, candleBodySize):
            signals[i] = 'BUY'
        elif is_it_a_sell_signal(i, data, closes, ma_values, rsi_values, ma_of_rsi_values, candleBodySize):
            signals[i] = 'SELL'
        else:
            signals[i] = None

    # Create a DataFrame with closes and signals
    result_df = pd.DataFrame({'close': closes, 'signal': signals})

    # Filter the DataFrame to return only rows where signal is not None
    filtered_df = result_df[result_df['signal'].notna()]

    return filtered_df


def is_it_a_buy_signal(i, data, closes, ma_values, rsi_values, ma_of_rsi_values, candleBodySize):
    # Extract open, low, high prices
    opens = data['open']
    highs = data['high']
    lows = data['low']

    percentCrossingAboveDiff = (float(closes[i]) - ma_values[i]) * 100 / candleBodySize
    percentCrossingBelowDiff = (float(ma_values[i]) - opens[i]) * 100 / candleBodySize

    isPriceCrossingValid = percentCrossingAboveDiff > 25 and percentCrossingBelowDiff > 25

    isPriceCrossingSma = float(closes[i]) > ma_values[i] and float(closes[i - 1]) <= ma_values[i - 1]
    isRsiCrossingSmaOfRsi = float(rsi_values[i]) > ma_of_rsi_values[i] and \
                            float(rsi_values[i - 1]) <= ma_of_rsi_values[i - 1]
    isRsiBelowMaxValForLong = rsi_values[i] < rsiMaxValForLong
    isRsiMABelowMaxValForLong = ma_of_rsi_values[i] < rsiMAMaxValForLong
    greenCandle = closes[i] > opens[i]
    isPriceIncreasing = closes[i - 1] < closes[i]
    isPrevCandleFarFromSma = ma_values[i - 1] > max(opens[i - 1], closes[i - 1])
    isGreenCandleCrossingSma = opens[i] < ma_values[i] < closes[i]
    # isLastThreeCandlesFarFromSma = ma_values[i - 1] > max(opens[i - 1], closes[i - 1])
    #
    # if i > 3:
    #     isLastThreeCandlesFarFromSma = isLastThreeCandlesFarFromSma and \
    #                                    ma_values[i - 2] > max(opens[i - 2], closes[i - 2]) and \
    #                                    ma_values[i - 3] > max(opens[i - 3], closes[i - 3])

    isLastThreeCandlesFarFromSma = ma_values[i - 1] > highs[i - 1]

    if i > 3:
        isLastThreeCandlesFarFromSma = isLastThreeCandlesFarFromSma and \
                                       ma_values[i - 2] > highs[i - 2] and \
                                       ma_values[i - 3] > highs[i - 3]
    isSmaDecreasing = True

    if i > 3:
        isSmaDecreasing = ma_values[i - 3] > ma_values[i - 2] > ma_values[i - 1] > ma_values[i]

    return isPriceCrossingSma and isRsiCrossingSmaOfRsi and isRsiBelowMaxValForLong and \
        isRsiMABelowMaxValForLong and isPriceIncreasing and isSmaDecreasing and \
        greenCandle and isPrevCandleFarFromSma and isGreenCandleCrossingSma and \
        isPriceCrossingValid and isLastThreeCandlesFarFromSma


def is_it_a_sell_signal(i, data, closes, ma_values, rsi_values, ma_of_rsi_values, candleBodySize):

    # Extract open, low, high prices
    opens = data['open']
    highs = data['high']
    lows = data['low']

    percentCrossingBelowDiff = abs(float(closes[i]) - ma_values[i]) * 100 / candleBodySize
    percentCrossingAboveDiff = abs(float(ma_values[i]) - opens[i]) * 100 / candleBodySize

    isPriceCrossingValid = percentCrossingAboveDiff > 25 and percentCrossingBelowDiff > 25

    isPriceCrossingSma = float(closes[i]) < ma_values[i] and float(closes[i - 1]) >= ma_values[i - 1]
    isRsiCrossingSmaOfRsi = float(rsi_values[i]) < ma_of_rsi_values[i] and \
                            float(rsi_values[i - 1]) >= ma_of_rsi_values[i - 1]
    isRsiAboveMinValForLong = rsi_values[i] >= rsiMaxValForLong
    isRsiMAAboveMinValForLong = ma_of_rsi_values[i] >= rsiMAMinValForShort
    redCandle = closes[i] < opens[i]
    isPriceDecreasing = closes[i - 1] > closes[i]
    isPrevCandleFarFromSma = ma_values[i - 1] < min(opens[i - 1], closes[i - 1])
    isRedCandleCrossingSma = opens[i] > ma_values[i] > closes[i]
    # isLastThreeCandlesFarFromSma = ma_values[i - 1] < min(opens[i - 1], closes[i - 1])
    #
    # if i > 3:
    #     isLastThreeCandlesFarFromSma = isLastThreeCandlesFarFromSma and \
    #                                    ma_values[i - 2] < min(opens[i - 2], closes[i - 2]) and \
    #                                    ma_values[i - 3] < min(opens[i - 3], closes[i - 3])

    isLastThreeCandlesFarFromSma = ma_values[i - 1] < lows[i - 1]

    if i > 3:
        isLastThreeCandlesFarFromSma = isLastThreeCandlesFarFromSma and \
                                       ma_values[i - 2] < lows[i - 2] and \
                                       ma_values[i - 3] < lows[i - 3]

    isSmaIncreasing = True

    if i > 3:
        isSmaIncreasing = ma_values[i - 3] < ma_values[i - 2] < ma_values[i - 1] < ma_values[i]

    return isPriceCrossingSma and isRsiCrossingSmaOfRsi and isRsiAboveMinValForLong and \
        isRsiMAAboveMinValForLong and isPriceDecreasing and isSmaIncreasing and \
        redCandle and isPrevCandleFarFromSma and isRedCandleCrossingSma and \
        isPriceCrossingValid and isLastThreeCandlesFarFromSma


# # Create a list to hold all epoch times
# sample_epoch_times = [1735237800000, 1735314596000]  # Example epoch times in milliseconds
# epoch_times = sample_epoch_times + [data['open_time'][85]]  # Corrected index access

# # Create a DataFrame
# dff = pd.DataFrame({'epoch_time': epoch_times})

# # Function to convert epoch time to seconds if in milliseconds
# def convert_epoch_time(epoch):
#     if epoch > 1_000_000_000:  # If it's larger than 1 billion, it's likely in milliseconds
#         return epoch / 1000  # Convert to seconds
#     return epoch

# # Apply the conversion function to the 'epoch_time' column
# dff['epoch_time'] = dff['epoch_time'].apply(convert_epoch_time)

# # Convert epoch time to datetime in UTC
# dff['timestamp_utc'] = pd.to_datetime(dff['epoch_time'], unit='s', utc=True)

# # Convert to IST (UTC+5:30)
# dff['timestamp_ist'] = dff['timestamp_utc'].dt.tz_convert('Asia/Kolkata')

# # Display the DataFrame
# print(dff[['epoch_time', 'timestamp_utc', 'timestamp_ist']])