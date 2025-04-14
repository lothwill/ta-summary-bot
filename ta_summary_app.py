import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="TA Summary Bot", layout="centered")
st.title("Technical Analysis Summary")

ticker_input = st.text_input("Enter a stock ticker (e.g., PLTR, SPY, NVDA):")

def get_summary(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        
        # 1. Recent 14 trading days (for support/resistance & pivot)
        recent_hist = stock.history(period="21d")
        if recent_hist.empty or len(recent_hist) < 5:
            raise ValueError("Recent price history is missing or too short.")

        recent = recent_hist.tail(10)
        last_close = recent['Close'].iloc[-1]
        high = recent['High'].max()
        low = recent['Low'].min()

        last_day = recent_hist.iloc[-1]
        pivot = (last_day['High'] + last_day['Low'] + last_day['Close']) / 3
        r1 = (2 * pivot) - last_day['Low']
        r2 = pivot + (last_day['High'] - last_day['Low'])
        s1 = (2 * pivot) - last_day['High']
        s2 = pivot - (last_day['High'] - last_day['Low'])

        diff = high - low
        fib_38 = high - 0.382 * diff
        fib_50 = high - 0.5 * diff
        fib_618 = high - 0.618 * diff

        # 2. Full year of historical data (for 52wk stats and SMAs)
        hist = stock.history(period="1y")
        if hist.empty or len(hist) < 50:
            raise ValueError("Not enough historical data for SMA or 52-week calculations.")

        high_52wk = hist['High'].max()
        low_52wk = hist['Low'].min()
        sma_50 = hist['Close'].tail(50).mean()
        sma_200 = hist['Close'].tail(200).mean() if len(hist) >= 200 else "N/A"

        return {
            "Last Price": round(last_close, 4),
            "1st Resistance Point": round(r1, 4),
            "2nd Resistance Point": round(r2, 4),
            "1st Support Level": round(s1, 4),
            "2nd Support Level": round(s2, 4),
            "Fibonacci 38.2%": round(fib_38, 4),
            "Fibonacci 50%": round(fib_50, 4),
            "Fibonacci 61.8%": round(fib_618, 4),
            "52-Week High": round(high_52wk, 4),
            "52-Week Low": round(low_52wk, 4),
            "50 SMA": round(sma_50, 4),
            "200 SMA": round(sma_200, 4) if sma_200 != "N/A" else "N/A"
        }

    except Exception as e:
        print(f"[ERROR] {ticker.upper()} failed: {e}")
        st.error(f"An error occurred while fetching data for {ticker.upper()}: {e}")
        return {"Error": str(e)}

if ticker_input:
    summary = get_summary(ticker_input.upper())
    if summary:
        st.subheader(f"TA Summary for {ticker_input.upper()}")

        st.markdown("""
            <style>
            tbody tr:nth-child(odd) { background-color: #ffe6f0 !important; }
            tbody tr:nth-child(even) { background-color: #f3e6ff !important; }
            thead th {
                background-color: #fdfdfd !important;
                font-weight: bold;
            }
            </style>
        """, unsafe_allow_html=True)

        df = pd.DataFrame(summary.items(), columns=["Metric", "Value"])
        st.table(df)
    else:
        st.warning("No data found for this ticker.")
