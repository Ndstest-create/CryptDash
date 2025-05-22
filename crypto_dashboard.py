import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import MACD

# ตั้งค่าหน้า
st.set_page_config(page_title="Crypto Dashboard", layout="wide")
st.title("📊 Crypto Technical Dashboard")

# เลือกเหรียญ
symbol = st.selectbox("เลือกเหรียญ", ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "ADA-USD"])

# โหลดข้อมูล
data = yf.download(symbol, start="2022-01-01")

# เช็กว่าโหลดข้อมูลได้ไหม
if data.empty:
    st.error("⚠️ ไม่พบข้อมูลจาก Yahoo Finance")
    st.stop()
else:
    st.error("❌ ไม่พบคอลัมน์ 'Close' ในข้อมูลที่โหลดมา")
    st.write("คอลัมน์ที่พบ:", list(data.columns))


# คำนวณ MACD
macd_calc = MACD(close=data["Close"], window_slow=26, window_fast=12, window_sign=9)
data["MACD_Line"] = macd_calc.macd().values
data["Signal_Line"] = macd_calc.macd_signal().values
data["MACD_Hist"] = macd_calc.macd_diff().values

# ตารางข้อมูล
with st.expander("📄 ดูข้อมูลดิบ"):
    st.dataframe(data.tail(30))

# สร้างกราฟ
fig = go.Figure()

fig.add_trace(go.Scatter(x=data.index, y=data["Close"], name='Close Price', line=dict(color='blue')))
fig.add_trace(go.Scatter(x=data.index, y=data["MACD_Line"], name='MACD Line', line=dict(color='orange')))
fig.add_trace(go.Scatter(x=data.index, y=data["Signal_Line"], name='Signal Line', line=dict(color='green')))
fig.add_trace(go.Bar(x=data.index, y=data["MACD_Hist"], name='MACD Histogram', marker_color='gray', opacity=0.5))

fig.update_layout(
    title=f"{symbol} - ราคาปิดและ MACD",
    xaxis_title="วันที่",
    yaxis_title="ราคา (USD)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=40, r=40, t=80, b=40),
    height=600
)

st.plotly_chart(fig, use_container_width=True)
