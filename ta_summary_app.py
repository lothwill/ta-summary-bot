
import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="TA Summary Bot", layout="centered")

st.title("Technical Analysis Summary")

ticker_input = st.text_input("Enter a stock ticker (e.g., PLTR, SPY, NVDA):", value="PLTR")

def fibonacci_levels(high, low):
    diff = high - low
    return {
        'Fibonacci 38.2%': round(high - diff * 0.382, 2),
        'Fibonacci 50%': round(high - diff * 0.5, 2),
        'Fibonacci 61.8%': round(high - diff * 0.618, 2)
    }

def calculate_support_resistance(price_series):
    recent = price_series[-20:]
    max_p = recent.max()
    min_p = recent.min()
    last = recent.iloc[-1]
    r1 = round(last + (max_p - last) * 0.5, 2)
    r2 = round(last + (max_p - last), 2)
    s1 = round(last - (last - min_p) * 0.5, 2)
    s2 = round(last - (last - min_p), 2)
    return r1, r2, s1, s2

def get_summary(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    hist = ticker.history(period="1y")
    if hist.empty:
        return None

    last_price = round(hist["Close"][-1], 2)
    high_52wk = round(hist["High"].max(), 2)
    low_52wk = round(hist["Low"].min(), 2)
    fibs = fibonacci_levels(high_52wk, low_52wk)
    sma_50 = round(hist["Close"].rolling(50).mean().dropna()[-1], 2)
    sma_200 = round(hist["Close"].rolling(200).mean().dropna()[-1], 2)
    r1, r2, s1, s2 = calculate_support_resistance(hist["Close"])

    return {
        "Last Price": last_price,
        "1st Resistance Point": r1,
        "2nd Resistance Point": r2,
        "1st Support Level": s1,
        "2nd Support Level": s2,
        **fibs,
        "52-Week High": high_52wk,
        "52-Week Low": low_52wk,
        "50 SMA": sma_50,
        "200 SMA": sma_200
    }

if ticker_input:
    summary = get_summary(ticker_input.upper())
    if summary:
        st.subheader(f"TA Summary for {ticker_input.upper()}")
        df = pd.DataFrame(summary.items(), columns=["Metric", "Value"])
        st.table(df)
    else:
        st.warning("No data found for this ticker.")
