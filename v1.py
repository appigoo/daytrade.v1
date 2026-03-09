import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import requests

st.title("TSLA Momentum Breakout Detector")

ticker = st.text_input("Stock", "TSLA")
interval = st.selectbox("Timeframe", ["15m","30m","1h","1d"])

data = yf.download(ticker, period="3mo", interval=interval)

# Indicators
data["EMA50"] = ta.trend.ema_indicator(data["Close"], window=50)

macd = ta.trend.MACD(data["Close"])
data["MACD"] = macd.macd()
data["MACD_signal"] = macd.macd_signal()

data["Momentum"] = data["Close"] - data["Close"].shift(10)
data["MomentumMA"] = data["Momentum"].rolling(10).mean()

data["VolumeMA"] = data["Volume"].rolling(20).mean()

data["ATR"] = ta.volatility.average_true_range(
    data["High"], data["Low"], data["Close"], window=14
)

data["ATR_MA"] = data["ATR"].rolling(20).mean()

# Signal logic
data["Breakout"] = (
    (data["Momentum"] > data["MomentumMA"]) &
    (data["MACD"] > data["MACD_signal"]) &
    (data["Volume"] > 2 * data["VolumeMA"]) &
    (data["Close"] > data["EMA50"]) &
    (data["ATR"] < data["ATR_MA"])
)

latest = data.iloc[-1]

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


# Avoid duplicate alerts
if "alert_sent" not in st.session_state:
    st.session_state.alert_sent = False

if latest["Breakout"] and not st.session_state.alert_sent:

    message = f"""
🚀 MOMENTUM BREAKOUT

Stock: {ticker}
Price: {round(latest['Close'],2)}

Momentum ↑
MACD Golden Cross
Volume Spike

Timeframe: {interval}
"""

    send_telegram(message)

    st.session_state.alert_sent = True

    st.success("BREAKOUT ALERT SENT")

elif not latest["Breakout"]:
    st.session_state.alert_sent = False
    st.write("No breakout")

st.line_chart(data["Momentum"])
st.line_chart(data[["MACD","MACD_signal"]])
