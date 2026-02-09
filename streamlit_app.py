
import streamlit as st
import yfinance as yf
import pandas as pd
from pytickersymbols import PyTickerSymbols

# Simple Practice Gate
if st.text_input("Enter Practice Key", type="password") != "munger2026":
    st.stop() # Stops the rest of the app from loading

# --- 1. CONFIG & API SETUP ---
st.set_page_config(page_title="Inversion Engine Pro", layout="wide")

# --- 2. THE PRACTICE GATE ---
password_attempt = st.sidebar.text_input("Enter Practice Key", type="password")
if password_attempt != "munger2026":
    st.sidebar.warning("Access Restricted.")
    st.stop()

# --- 3. DATA UTILITIES ---
@st.cache_data(ttl=3600)
def get_exchange_rate():
    # Fetches GBP/USD rate for normalising UK vs US prices
    forex = yf.Ticker("GBPUSD=X")
    return forex.fast_info['lastPrice']

@st.cache_data
def load_ticker_universe():
    pts = PyTickerSymbols()
    # Fetching the three core indices
    nasdaq = pts.get_nasdaq_100_nyc_yahoo_tickers()
    dow = pts.get_dow_jones_nyc_yahoo_tickers()
    ftse = pts.get_ftse_100_london_yahoo_tickers()
    return sorted(list(set(nasdaq + dow + ftse)))

# --- 4. THE SCANNING ENGINE ---
@st.cache_data(ttl=3600)
def scan_markets(tickers, limit=50):
    rate = get_exchange_rate()
    results = []
    
    for symbol in tickers[:limit]:
        try:
            t = yf.Ticker(symbol)
            info = t.info
            
            # Normalise Price (GBp pence to GBP pounds to USD)
            raw_price = info.get('currentPrice', 1)
            currency = info.get('currency', 'USD')
            
            price_fixed = raw_price / 100 if currency == 'GBp' else raw_price
            price_usd = price_fixed * rate if currency == 'GBP' else price_fixed
            
            # Key Munger Metrics
            roic = info.get('returnOnAssets', 0) * 200  # ROA proxy
            margin = info.get('operatingMargins', 0) * 100
            div_rate = info.get('dividendRate', 0)
            yield_val = (div_rate / price_fixed * 100) if div_rate else 0
            ebitda = info.get('ebitda', 1)
            debt_ratio = info.get('totalDebt', 0) / ebitda if ebitda > 0 else 99

            results.append({
                "Ticker": symbol,
                "Name": info.get('shortName', 'Unknown'),
                "Price (USD)": price_usd,
                "Yield %": yield_val,
                "ROIC %": roic,
                "Op. Margin %": margin,
                "Debt/EBITDA": debt_ratio,
                "Insider %": info.get('heldPercentInsiders', 0) * 100
            })
        except: continue
    return pd.DataFrame(results)

# --- 5. UI & FILTERS ---
st.title("🧮 Inversion Engine")

st.sidebar.header("🏛 Munger's Thresholds")
user_yield = st.sidebar.slider("Min Yield %", 0.0, 10.0, 3.0)
user_roic = st.sidebar.slider("Min ROIC %", 0, 50, 15)
user_margin = st.sidebar.slider("Min Op. Margin %", 0, 50, 10)
user_debt = st.sidebar.slider("Max Debt/EBITDA", 0.0, 10.0, 3.0)
depth = st.sidebar.select_slider("Scan Depth", options=[20, 50, 100, 200], value=50)

# --- 6. EXECUTION ---
universe = load_ticker_universe() # Name fixed here

with st.spinner("Normalising Currencies & Scoring Universe..."):
    df = scan_markets(universe, limit=depth)
    
    if not df.empty:
        # Applying the user's specific Munger Filters
        mask = (
            (df['Yield %'] >= user_yield) & 
            (df['ROIC %'] >= user_roic) & 
            (df['Op. Margin %'] >= user_margin) &
            (df['Debt/EBITDA'] <= user_debt)
        )
        final_df = df[mask].sort_values(by="ROIC %", ascending=False)

        st.subheader(f"🏆 Found {len(final_df)} Stocks Meeting Your Requirements")
        
        # Display table with heatmap
        st.dataframe(
            final_df.style.background_gradient(cmap='RdYlGn', subset=['ROIC %', 'Yield %'])
            .format({"Price (USD)": "${:.2f}", "Yield %": "{:.2f}%", "ROIC %": "{:.1f}%", "Debt/EBITDA": "{:.1f}x"}),
            use_container_width=True, hide_index=True
        )
    else:
        st.error("No data found. Check your internet connection or ticker universe.")

# --- 7. LEGAL FOOTER ---
st.divider()
st.caption("🚨 **PRACTICE TOOL:** For educational use only. All prices normalised to USD.")
st.caption("🚨 **PERSONAL HOBBY PROJECT - NOT FOR COMMERCIAL USE**")
st.caption("""
    **DISCLAIMER:** This tool is for educational and practice purposes only. 
    It does not constitute financial advice, investment research, or an offer to buy/sell securities. 
    The 'Munger Score' is a mathematical experiment and not a verified indicator of performance. 
    The author is not FCA regulated. Always do your own due diligence.
""")
st.caption("© 2026 | Built for personal educational practice.")






