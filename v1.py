import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objects as go
import requests

st.set_page_config(page_title="Momentum Breakout Scanner", layout="wide")

st.title("🚀 AI Momentum Breakout Scanner")

# ---------- TELEGRAM ----------
BOT_TOKEN = st.secrets["telegram"]["bot_token"]
CHAT_ID = st.secrets["telegram"]["chat_id"]

def send_telegram(msg):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    requests.post(url, data=payload)


# ---------- INPUT ----------
ticker = st.text_input("Stock", "TSLA")

interval = st.selectbox(
    "Timeframe",
    ["15m","30m","1h","1d"]
)

period = "3mo"

# ---------- DOWNLOAD DATA ----------
data = yf.download(ticker, period=period, interval=interval)

# FIX pandas multi column bug
data.columns = data.columns.get_level_values(0)

data = data.dropna()

close = data["Close"]
high = data["High"]
low = data["Low"]
volume = data["Volume"]

# ---------- INDICATORS ----------

data["EMA20"] = ta.trend.ema_indicator(close, window=20)
data["EMA50"] = ta.trend.ema_indicator(close, window=50)

macd = ta.trend.MACD(close)

data["MACD"] = macd.macd()
data["MACD_signal"] = macd.macd_signal()

data["Momentum"] = close - close.shift(10)

data["VolumeMA"] = volume.rolling(20).mean()

data["RVOL"] = volume / data["VolumeMA"]

data["ATR"] = ta.volatility.average_true_range(
    high,
    low,
    close,
    window=14
)

data["ATR_MA"] = data["ATR"].rolling(20).mean()

# ---------- SIGNAL ----------

data["Breakout"] = (
    (data["Momentum"] > 0) &
    (data["MACD"] > data["MACD_signal"]) &
    (data["Close"] > data["EMA50"]) &
    (data["RVOL"] > 2) &
    (data["ATR"] < data["ATR_MA"])
)

latest = data.iloc[-1]

# ---------- TELEGRAM ALERT ----------

if "alert_sent" not in st.session_state:
    st.session_state.alert_sent = False

if latest["Breakout"] and not st.session_state.alert_sent:

    msg = f"""
🚀 MOMENTUM BREAKOUT

Stock: {ticker}
Price: {round(latest['Close'],2)}

Momentum Positive
MACD Golden Cross
Relative Volume > 2

Timeframe: {interval}
"""

    send_telegram(msg)

    st.session_state.alert_sent = True

    st.success("Telegram Alert Sent")

elif not latest["Breakout"]:
    st.session_state.alert_sent = False


# ---------- CHART ----------

st.subheader("Price Chart")

fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=data.index,
    open=data["Open"],
    high=data["High"],
    low=data["Low"],
    close=data["Close"]
))

fig.add_trace(go.Scatter(
    x=data.index,
    y=data["EMA20"],
    name="EMA20"
))

fig.add_trace(go.Scatter(
    x=data.index,
    y=data["EMA50"],
    name="EMA50"
))

st.plotly_chart(fig, use_container_width=True)

# ---------- MOMENTUM ----------

st.subheader("Momentum")

st.line_chart(data["Momentum"])

# ---------- MACD ----------

st.subheader("MACD")

st.line_chart(data[["MACD","MACD_signal"]])

# ---------- RVOL ----------

st.subheader("Relative Volume")

st.line_chart(data["RVOL"])

# ---------- STATUS ----------

st.subheader("Signal Status")

if latest["Breakout"]:
    st.success("🚀 BREAKOUT DETECTED")
else:
    st.warning("No Signal")
