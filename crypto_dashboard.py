import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import MACD
from ta.momentum import StochasticOscillator

# ตั้งค่าหน้า Streamlit
st.set_page_config(page_title="Crypto Dashboard", layout="wide")
st.title("📊 Crypto Dashboard with MACD & Stochastic Indicators")

# เลือกเหรียญ
coins = {
    "Bitcoin (BTC)": "BTC-USD",
    "Ethereum (ETH)": "ETH-USD",
    "Binance Coin (BNB)": "BNB-USD",
    "Solana (SOL)": "SOL-USD"
}

coin_name = st.selectbox("เลือกเหรียญที่ต้องการวิเคราะห์", list(coins.keys()))
symbol = coins[coin_name]

# ดึงข้อมูลจาก Yahoo Finance
@st.cache_data
def load_data(symbol):
    data = yf.download(symbol, start="2022-01-01")
    data.dropna(inplace=True)
    return data

data = load_data(symbol)

# คำนวณ MACD
macd_calc = MACD(close=data["Close"], window_slow=26, window_fast=12, window_sign=9)
data["MACD_Line"] = macd_calc.macd()
data["MACD_Signal"] = macd_calc.macd_signal()
data["MACD_Hist"] = macd_calc.macd_diff()

# คำนวณ Stochastic Oscillator
stoch = StochasticOscillator(high=data["High"], low=data["Low"], close=data["Close"], window=14, smooth_window=3)
data["%K"] = stoch.stoch()
data["%D"] = stoch.stoch_signal()

# กราฟราคาปิด
st.subheader(f"📈 {coin_name} Closing Price")
fig_price = go.Figure()
fig_price.add_trace(go.Scatter(x=data.index, y=data["Close"], name="Close", line=dict(color='royalblue')))
fig_price.update_layout(height=400, margin=dict(l=10, r=10, t=30, b=10))
st.plotly_chart(fig_price, use_container_width=True)

# กราฟ MACD
st.subheader("📉 MACD Indicator")
fig_macd = go.Figure()
fig_macd.add_trace(go.Scatter(x=data.index, y=data["MACD_Line"], name="MACD Line", line=dict(color='blue')))
fig_macd.add_trace(go.Scatter(x=data.index, y=data["MACD_Signal"], name="Signal Line", line=dict(color='red')))
fig_macd.add_trace(go.Bar(x=data.index, y=data["MACD_Hist"], name="Histogram", marker_color='gray'))
fig_macd.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10))
st.plotly_chart(fig_macd, use_container_width=True)

# กราฟ Stochastic Oscillator
st.subheader("📊 Stochastic Oscillator")
fig_stoch = go.Figure()
fig_stoch.add_trace(go.Scatter(x=data.index, y=data["%K"], name="%K", line=dict(color='green')))
fig_stoch.add_trace(go.Scatter(x=data.index, y=data["%D"], name="%D", line=dict(color='orange')))
fig_stoch.add_hline(y=80, line_dash="dot", line_color="red")
fig_stoch.add_hline(y=20, line_dash="dot", line_color="green")
fig_stoch.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10))
st.plotly_chart(fig_stoch, use_container_width=True)
