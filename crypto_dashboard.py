import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from ta.trend import MACD
from ta.momentum import StochasticOscillator

st.set_page_config(layout="wide")
st.title("📊 Crypto Investment Dashboard (BTC, ETH, BNB, SOL)")

# Define coins and their symbols
symbols = {
    "Bitcoin (BTC)": "BTC-USD",
    "Ethereum (ETH)": "ETH-USD",
    "Binance Coin (BNB)": "BNB-USD",
    "Solana (SOL)": "SOL-USD"
}

# Sidebar coin selection
coin_name = st.sidebar.selectbox("เลือกเหรียญ", list(symbols.keys()))
symbol = symbols[coin_name]

# Download data
data = yf.download(symbol, start="2021-01-01")
data = data[["Close"]].dropna()

# Calculate indicators
macd_calc = MACD(close=data["Close"])
data["MACD"] = pd.Series(macd_calc.macd_diff(), index=data.index)

stoch_calc = StochasticOscillator(high=data["Close"], low=data["Close"], close=data["Close"])
data["Stoch %K"] = stoch_calc.stoch()
data["Stoch %D"] = stoch_calc.stoch_signal()

# Plotting
st.subheader(f"📈 {coin_name} Price Chart & Indicators")

fig, axs = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

# Price
axs[0].plot(data.index, data["Close"], label="Close Price", color="orange")
axs[0].set_title(f"{coin_name} Price")
axs[0].set_ylabel("USD")
axs[0].grid()
axs[0].legend()

# MACD
axs[1].plot(data.index, data["MACD"], label="MACD", color="green")
axs[1].axhline(0, linestyle="--", color="gray", linewidth=1)
axs[1].set_title("MACD")
axs[1].grid()
axs[1].legend()

# Stochastic
axs[2].plot(data.index, data["Stoch %K"], label="%K", color="blue")
axs[2].plot(data.index, data["Stoch %D"], label="%D", color="red")
axs[2].axhline(80, linestyle="--", color="gray")
axs[2].axhline(20, linestyle="--", color="gray")
axs[2].set_title("Stochastic Oscillator")
axs[2].set_xlabel("Date")
axs[2].grid()
axs[2].legend()

st.pyplot(fig)

st.caption("ข้อมูลจาก Yahoo Finance | อินดิเคเตอร์โดย `ta` library")
