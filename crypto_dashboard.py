import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from ta.momentum import StochasticOscillator
from ta.trend import MACD
from sklearn.linear_model import LinearRegression
import numpy as np

st.set_page_config(page_title="Crypto Dashboard", layout="wide")
st.title("📊 Crypto Dashboard: วิเคราะห์ราคาคริปโตพร้อมอินดิเคเตอร์")

# Sidebar
crypto = st.sidebar.selectbox("เลือกเหรียญ", ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD"])
start_date = st.sidebar.date_input("จากวันที่", value=datetime(2021, 1, 1))
end_date = datetime.today().strftime('%Y-%m-%d')

# โหลดข้อมูล
@st.cache_data
def load_data(symbol, start, end):
    df = yf.download(symbol, start=start, end=end)
    if 'Close' not in df.columns:
        return pd.DataFrame()
    df = df[['Close']]
    df.dropna(inplace=True)
    df.reset_index(inplace=True)
    return df

data = load_data(crypto, start_date, end_date)

# หยุดโปรแกรมหากไม่มีข้อมูล
if "Close" in data.columns:
    data.dropna(subset=["Close"], inplace=True)
else:
    st.error("ไม่มีคอลัมน์ 'Close' ในข้อมูล กรุณาตรวจสอบแหล่งข้อมูลหรือชื่อเหรียญ")
    st.stop()


# ลบ NaN อีกรอบสำหรับ MACD/Stochastic
data.dropna(subset=["Close"], inplace=True)

# เตรียมข้อมูลให้เป็น Series 1D สำหรับอินดิเคเตอร์
close_prices = data["Close"].dropna()
close_series = pd.Series(close_prices.values, index=data["Date"].iloc[-len(close_prices):])

# คำนวณ MACD
macd = MACD(close=close_series)
data = data.iloc[-len(close_series):].copy()  # sync ความยาว
data["MACD"] = macd.macd()
data["MACD_Signal"] = macd.macd_signal()

# คำนวณ Stochastic Oscillator
stoch = StochasticOscillator(high=close_series, low=close_series, close=close_series)
data["Stoch_K"] = stoch.stoch()
data["Stoch_D"] = stoch.stoch_signal()

# ลบค่าที่อินดิเคเตอร์ยังคำนวณไม่ครบ
data.dropna(inplace=True)

# พยากรณ์ราคาวันถัดไป
def forecast_price(df):
    df = df.copy()
    df['Day'] = np.arange(len(df)).reshape(-1, 1)
    X = df['Day'].values.reshape(-1, 1)
    y = df['Close'].values.reshape(-1, 1)
    model = LinearRegression()
    model.fit(X, y)
    next_day = np.array([[len(df)]])
    pred_price = model.predict(next_day)[0][0]
    return pred_price

predicted_price = forecast_price(data)

# แสดงกราฟราคาพร้อม MACD
st.subheader(f"📈 ราคาและ MACD: {crypto}")
fig1, ax1 = plt.subplots(figsize=(12, 6))
ax1.plot(data['Date'], data['Close'], label='Close Price', color='blue')
ax1.set_ylabel("Price (USD)")
ax1.legend(loc="upper left")

ax2 = ax1.twinx()
ax2.plot(data['Date'], data['MACD'], label="MACD", color='green')
ax2.plot(data['Date'], data['MACD_Signal'], label="Signal", color='red')
ax2.set_ylabel("MACD")
ax2.legend(loc="upper right")
st.pyplot(fig1)

# แสดง Stochastic Oscillator
st.subheader("📉 Stochastic Oscillator")
fig2, ax3 = plt.subplots(figsize=(12, 3))
ax3.plot(data['Date'], data['Stoch_K'], label='%K', color='purple')
ax3.plot(data['Date'], data['Stoch_D'], label='%D', color='orange')
ax3.axhline(80, color='gray', linestyle='--')
ax3.axhline(20, color='gray', linestyle='--')
ax3.legend()
st.pyplot(fig2)

# แสดงราคาที่คาดการณ์
st.subheader("🔮 พยากรณ์ราคาวันถัดไป")
st.success(f"📌 ราคาที่คาดการณ์สำหรับ {crypto} คือ: **${predicted_price:,.2f} USD**")
