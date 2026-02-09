import streamlit as st
import yfinance as yf
import pandas as pd
from pytickersymbols import PyTickerSymbols

# --- 1. Page Configuration ---
st.set_page_config(page_title="Inversion Engine Pro", layout="wide")
st.title("🧮 Inversion Engine: Advanced Screener")

# --- 2. Load Tickers (FTSE 100, NASDAQ, DOW) ---
@st.cache_data
def load_all_tickers():
    stock_data = PyTickerSymbols()
    # Get tickers from major indices
    nasdaq = stock_data.get_nasdaq_100_nyc_yahoo_tickers()
    dow = stock_data.get_dow_jones_nyc_yahoo_tickers()
    ftse = stock_data.get_ftse_100_london_yahoo_tickers()
    
    # Combine and clean (remove duplicates)
    all_tickers = sorted(list(set(nasdaq + dow + ftse)))
    return all_tickers

tickers_list = load_all_tickers()

# --- 3. Sidebar Filter System ---
st.sidebar.header("🔍 SimplyWallSt Filters")
selected_stock = st.sidebar.selectbox("Search & Select Ticker", options=tickers_list, index=tickers_list.index("AAPL") if "AAPL" in tickers_list else 0)

min_ebitda = st.sidebar.number_input("Min EBITDA ($/£)", value=0)
max_debt = st.sidebar.number_input("Max Total Debt ($/£)", value=10**12) # High default
min_insider = st.sidebar.slider("Min Insider Ownership (%)", 0, 100, 0)

# --- 4. Advanced Data Engine ---
@st.cache_data(ttl=3600)
def fetch_deep_metrics(symbol):
    ticker_obj = yf.Ticker(symbol)
    info = ticker_obj.info
    
    # Accurate Forward Yield Calculation
    price = info.get('currentPrice', 1)
    div_rate = info.get('dividendRate', 0)
    forward_yield = (div_rate / price) * 100 if div_rate else 0
    
    return {
        "Name": info.get('shortName', symbol),
        "Price": price,
        "Forward Yield": forward_yield,
        "EBITDA": info.get('ebitda', 0),
        "Total Debt": info.get('totalDebt', 0),
        "Inside Ownership": info.get('heldPercentInsiders', 0) * 100,
        "Debt to Equity": info.get('debtToEquity', 0)
    }

metrics = fetch_deep_metrics(selected_stock)

# --- 5. Professional Dashboard Layout ---
# Metric "Check" logic
if metrics['EBITDA'] >= min_ebitda and metrics['Total Debt'] <= max_debt and metrics['Inside Ownership'] >= min_insider:
    st.success(f"✅ {metrics['Name']} passes your current filters.")
else:
    st.warning(f"⚠️ {metrics['Name']} fails one or more filters.")

col1, col2, col3 = st.columns(3)
col1.metric("EBITDA", f"{metrics['EBITDA']:,.0f}")
col2.metric("Total Debt", f"{metrics['Total Debt']:,.0f}")
col3.metric("Inside Ownership", f"{metrics['Inside Ownership']:.2f}%")

col4, col5, col6 = st.columns(3)
col4.metric("Market Price", f"{metrics['Price']:.2f}")
col5.metric("Accurate Forward Yield", f"{metrics['Forward Yield']:.2f}%")
col6.metric("Debt to Equity", f"{metrics['Debt to Equity']:.2f}")

st.divider()
st.caption("© 2026 Inversion Engine | Data sourced via yfinance (15m delay)")
