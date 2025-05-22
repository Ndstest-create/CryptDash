import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from ta.trend import MACD
from ta.momentum import StochasticOscillator
from datetime import date

st.set_page_config(page_title="Crypto Dashboard", layout="wide")

st.title("📊 Crypto Investment Dashboard")
st.markdown("แดชบอร์ดวิเคราะห์ราคา BTC, ETH, BNB, SOL พร้อม MACD และ Stochastic Oscillator")

# --- Sidebar ---
st.sidebar.header("ตั้งค่า")
crypto_options = {
    "Bitcoin (BTC)": "BTC-USD",
    "Ethereum (ETH)": "ETH-USD",
    "BNB (BNB)": "BNB-USD",
    "Solana (SOL)": "SOL-USD"
}
crypto_name = st.sidebar.selectbox("เลือกเหรียญ", list(crypto_options.keys()))
crypto_symbol = crypto_options[crypto_name]

start_date = st.sidebar.date_input("วันที่เริ่มต้น", date(2021, 1, 1))
end_date = st.sidebar.date_input("วันที่สิ้นสุด", date.today())

# --- Load Data ---
@st.cache_data
def load_data(symbol, start, end):
    df = yf.download(symbol, start=start, end=end)
    if df.empty or "Close" not in df.columns:
        return pd.DataFrame()
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.dropna(inplace=True)
    df.reset_index(inplace=True)
    return df

data = load_data(crypto_symbol, start_date, end_date)

if data.empty or "Close" not in data.columns:
    st.error("⚠️ ไม่สามารถโหลดข้อมูลได้ กรุณาตรวจสอบชื่อเหรียญหรือช่วงเวลา")
    st.stop()

# --- Indicators ---
macd_calc = MACD(close=data["Close"])
data["MACD"] = macd_calc.macd()
data["Signal"] = macd_calc.macd_signal()

stoch_calc = StochasticOscillator(high=data["High"], low=data["Low"], close=data["Close"])
data["Stoch_%K"] = stoch_calc.stoch()
data["Stoch_%D"] = stoch_calc.stoch_signal()

# --- Display Charts ---
st.subheader(f"📈 กราฟราคา {crypto_name}")
fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(data["Date"], data["Close"], label="Close Price")
ax.set_title(f"{crypto_name} - Close Price")
ax.set_ylabel("USD")
ax.grid(True)
ax.legend()
st.pyplot(fig)

st.subheader("📉 MACD")
fig2, ax2 = plt.subplots(figsize=(12, 3))
ax2.plot(data["Date"], data["MACD"], label="MACD", color="blue")
ax2.plot(data["Date"], data["Signal"], label="Signal", color="orange")
ax2.axhline(0, color="gray", linestyle="--", linewidth=1)
ax2.legend()
ax2.grid(True)
st.pyplot(fig2)

st.subheader("📊 Stochastic Oscillator")
fig3, ax3 = plt.subplots(figsize=(12, 3))
ax3.plot(data["Date"], data["Stoch_%K"], label="%K", color="purple")
ax3.plot(data["Date"], data["Stoch_%D"], label="%D", color="green")
ax3.axhline(80, color="red", linestyle="--", linewidth=1)
ax3.axhline(20, color="blue", linestyle="--", linewidth=1)
ax3.legend()
ax3.grid(True)
st.pyplot(fig3)
