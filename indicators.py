import ta

def add_indicators(data):

    close = data["Close"]
    high = data["High"]
    low = data["Low"]
    volume = data["Volume"]

    data["EMA50"] = ta.trend.ema_indicator(close, window=50)

    macd = ta.trend.MACD(close)

    data["MACD"] = macd.macd()
    data["MACD_signal"] = macd.macd_signal()

    data["Momentum"] = close - close.shift(10)
    data["MomentumMA"] = data["Momentum"].rolling(10).mean()

    data["VolumeMA"] = volume.rolling(20).mean()

    atr = ta.volatility.average_true_range(high, low, close, window=14)
    data["ATR"] = atr
    data["ATR_MA"] = atr.rolling(20).mean()

    return data
