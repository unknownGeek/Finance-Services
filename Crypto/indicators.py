def calculate_rsi(closes, period=14):
    """
    Calculate Relative Strength Index
    """
    if len(closes) < period:
        return []
    
    deltas = [float(closes[i]) - float(closes[i-1]) for i in range(1, len(closes))]
    gains = [delta if delta > 0 else 0 for delta in deltas]
    losses = [-delta if delta < 0 else 0 for delta in deltas]
    
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    rsi_values = []
    
    for i in range(period, len(closes)):
        avg_gain = (avg_gain * (period - 1) + (float(closes[i]) - float(closes[i-1]) if float(closes[i]) - float(closes[i-1]) > 0 else 0)) / period
        avg_loss = (avg_loss * (period - 1) + (-float(closes[i]) + float(closes[i-1]) if float(closes[i]) - float(closes[i-1]) < 0 else 0)) / period
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        rsi_values.append(rsi)
    
    return [None] * period + rsi_values

def calculate_ma(data, length=8):
    """
    Calculate Moving Average
    """
    ma_values = []
    for i in range(len(data)):
        if i < length - 1:
            ma_values.append(None)
        else:
            window = data[i-length+1:i+1]
            ma = sum(float(x) for x in window) / length
            ma_values.append(ma)
    return ma_values