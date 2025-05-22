import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from ta.trend import MACD
from ta.momentum import StochasticOscillator

# กำหนดเหรียญที่ต้องการแสดง
symbols = {
    "Bitcoin (BTC)": "BTC-USD",
    "Ethereum (ETH)": "ETH-USD",
    "BNB (BNB)": "BNB-USD",
    "Solana (SOL)": "SOL-USD"
}

st.set_page_config(page_title="Crypto Dashboard", layout="wide")
st.title("📊 Crypto Investment Dashboard")
st.markdown("เปรียบเทียบราคาและดู Indicator (MACD + Stochastic) ของ BTC, ETH, BNB, SOL")

# เลือกเหรียญ
selected_coin = st.selectbox("เลือกเหรียญ", list(symbols.keys()))
symbol = symbols[selected_coin]

# ดึงข้อมูลย้อนหลัง
@st.cache_data
def load_data(symbol):
    data = yf.download(symbol, start="2021-01-01")  # <-- แก้ตรงนี้ให้สมบูรณ์
    data.reset_index(inplace=True)
    return data

