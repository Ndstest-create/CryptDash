import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import MACD

st.set_page_config(layout="wide")
st.title("📊 Crypto Technical Dashboard")

# --- Input ---
symbol = st.text_input("Enter Crypto Symbol (e.g. BTC-USD, ETH-USD):", "BTC-USD")

# --- Load data ---
if symbol:
    data = yf.download(symbol, start="2021-01-01")

    if data is None or data.empty:
        st.error("❌ ไม่สามารถดึงข้อมูลได้ กรุณาตรวจสอบชื่อ Symbol หรือการเชื่อมต่ออินเทอร์เน็ต")
        st.stop()

    if not isinstance(data, pd.DataFrame):
        st.error("❌ ข้อมูลไม่อยู่ในรูปแบบ DataFrame")
        st.stop()

    if "Close" not in data.columns:
        st.error("❌ ข้อมูลไม่มีคอลัมน์ 'Close' ไม่สามารถประมวลผลได้")
        st.write("Columns ที่พบ:", list(data.columns))
        st.stop()

    if data["Close"].isna().all():
        st.error("❌ คอลัมน์ 'Close' ไม่มีข้อมูล")
        st.stop()

    # Drop rows where 'Close' is NaN
    data = data.dropna(subset=["Close"])

    # --- Calculate MACD ---
    macd_calc = MACD(close=data["Close"], window_slow=26, window_fast=12, window_sign=9)
    data["MACD"] = macd_calc.macd()
    data["MACD_Signal"] = macd_calc.macd_signal()
    data["MACD_Diff"] = macd_calc.macd_diff()

    # --- Price Chart ---
    st.subheader(f"{symbol} Price Chart")
    fig_price = go.Figure()
    fig_price.add_trace(go.Scatter(x=data.index, y=data["Close"], name="Close Price", line=dict(color="blue")))
    fig_price.update_layout(
        xaxis_title="Date", yaxis_title="Price (USD)", template="plotly_white", height=400
    )
    st.plotly_chart(fig_price, use_container_width=True)

    # --- MACD Chart ---
    st.subheader("MACD Indicator")
    fig_macd = go.Figure()
    fig_macd.add_trace(go.Scatter(x=data.index, y=data["MACD"], name="MACD", line=dict(color="orange")))
    fig_macd.add_trace(go.Scatter(x=data.index, y=data["MACD_Signal"], name="Signal", line=dict(color="green")))
    fig_macd.add_trace(go.Bar(x=data.index, y=data["MACD_Diff"], name="Histogram", marker_color="gray"))
    fig_macd.update_layout(
        xaxis_title="Date", yaxis_title="MACD", template="plotly_white", height=400
    )
    st.plotly_chart(fig_macd, use_container_width=True)
