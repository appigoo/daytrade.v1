import streamlit as st
import yfinance as yf
from indicators import add_indicators
from scanner import breakout_signal
from telegram_bot import send_message
from streamlit_autorefresh import st_autorefresh



st.title("AI Momentum Scanner")

stocks = ["TSLA","NVDA","COIN","PLTR","AMD","META"]

signals = []

for ticker in stocks:

    data = yf.download(ticker, period="3mo", interval="1h")

    data.columns = data.columns.get_level_values(0)

    data = add_indicators(data)

    if breakout_signal(data):

        price = data.iloc[-1]["Close"]

        signals.append((ticker,price))

for ticker,price in signals:

    st.success(f"{ticker} breakout {round(price,2)}")

    send_message(f"""
🚀 Momentum Breakout

Stock: {ticker}
Price: {round(price,2)}
""")
st_autorefresh(interval=300000)
