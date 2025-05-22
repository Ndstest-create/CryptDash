import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import MACD

# ตั้งค่าเบื้องต้น
st.set_page_config(page_title="Crypto Dashboard", layout="wide")
st.title("📊 Crypto Technical Dashboard")

# เลือกเหรียญ
symbol = st.selectbox("เลือกเหรียญ", ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "ADA-USD"])

# ดึงข้อมูล
data = yf.download(symbol, start="2022-01-01")

# ตรวจสอบข้อมูล
if data.empty:
    st.error("⚠️ ไม่พบข้อมูลสำหรับเหรียญนี้")
    st.stop()

if "Close" not in data.columns:
    st.error("❌ ข้อมูลไม่มีคอลัมน์ 'Close'")
    st.write("Columns ที่พบ:", list(data.columns))
    st.stop()

if data["Close"].isna().all():
    st.error("❌ คอลัมน์ 'Close' ไม่มีข้อมูลที่ใช้ได้")
    st.stop()

# ทำความสะอาดข้อมูล
data = data.dropna(subset=["Close"])

# คำนวณ MACD
macd_calc = MACD(close=data["Close"], window_slow=26, window_fast=12, window_sign=9)
data["MACD_Line"] = macd_calc.macd().values
data["Signal_Line"] = macd_calc.macd_signal().values
data["MACD_Hist"] = macd_calc.macd_diff().values

# แสดงตารางข้อมูล
with st.expander("📄 ดูข้อมูลดิบ"):
    st.dataframe(data.tail(30))

# สร้างกราฟราคาพร้อม MACD
fig = go.Figure()

# กราฟราคาหลัก
fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode='lines', name='Close Price', line=dict(color='blue')))

# Subplot MACD
fig.add_trace(go.Scatter(x=data.index, y=data["MACD_Line"], mode='lines', name='MACD Line', line=dict(color='orange')))
fig.add_trace(go.Scatter(x=data.index, y=data["Signal_Line"], mode='lines', name='Signal Line', line=dict(color='green')))
fig.add_trace(go.Bar(x=data.index, y=data["MACD_Hist"], name='MACD Histogram', marker_color='gray', opacity=0.5))

# อัปเดต layout
fig.update_layout(
    title=f"{symbol} - ราคาและ MACD",
    xaxis_title="วันที่",
    yaxis_title="ราคา (USD)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=40, r=40, t=80, b=40),
    height=600
)

st.plotly_chart(fig, use_container_width=True)
