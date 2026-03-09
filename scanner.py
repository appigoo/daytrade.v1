def breakout_signal(data):

    latest = data.iloc[-1]

    signal = (
        (latest["Momentum"] > latest["MomentumMA"]) and
        (latest["MACD"] > latest["MACD_signal"]) and
        (latest["Volume"] > 2 * latest["VolumeMA"]) and
        (latest["Close"] > latest["EMA50"]) and
        (latest["ATR"] < latest["ATR_MA"])
    )

    return signal
