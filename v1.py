import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import requests
import plotly.graph_objects as go

st.set_page_config(page_title="AI Momentum Scanner", layout="wide")

st.title("🚀 AI Momentum Breakout Scanner")

# 股票列表
symbols = st.text_input(
    "Stock List",
    "TSLA,NVDA,COIN,PLTR,AMD,META"
)

interval = st.selectbox(
    "Timeframe",
    ["15m","30m","1h","1d"]
)

symbol_list = [s.strip() for s in symbols.split(",")]

# Telegram secrets
BOT_TOKEN = st.secrets["telegram"]["bot_token"]
CHAT_ID = st.secrets["telegram"]["chat_id"]

def send_telegram(msg):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    requests.post(url, data=payload)


breakouts = []

for ticker in symbol_list:

    try:

        data = yf.download(ticker, period="3mo", interval=interval)

        if data.empty:
            continue

        # 修復 pandas multi column bug
        data.columns = data.columns.get_level_values(0)

        close = data["Close"]
        high = data["High"]
        low = data["Low"]
        volume = data["Volume"]

        # 指標
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

        # breakout logic
        data["Breakout"] = (
            (data["Momentum"] > data["MomentumMA"]) &
            (data["MACD"] > data["MACD_signal"]) &
            (volume > 2 * data["VolumeMA"]) &
            (close > data["EMA50"]) &
            (data["ATR"] < data["ATR_MA"])
        )

        latest = data.iloc[-1]

        if latest["Breakout"]:
            breakouts.append((ticker, latest["Close"]))

    except:
        pass


st.subheader("🔥 Breakout Stocks")

if len(breakouts) == 0:
    st.write("No breakout detected")

for stock, price in breakouts:

    st.success(f"{stock} Breakout - Price {round(price,2)}")

    message = f"""
🚀 MOMENTUM BREAKOUT

Stock: {stock}
Price: {round(price,2)}

Momentum ↑
MACD Golden Cross
Volume Spike
"""

    send_telegram(message)


# 圖表
ticker_chart = st.selectbox("Chart", symbol_list)

data = yf.download(ticker_chart, period="3mo", interval=interval)
data.columns = data.columns.get_level_values(0)

fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=data.index,
    open=data["Open"],
    high=data["High"],
    low=data["Low"],
    close=data["Close"]
))

st.plotly_chart(fig)
