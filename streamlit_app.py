
    
import streamlit as st
import yfinance as yf
import pandas as pd
from pytickersymbols import PyTickerSymbols

# Simple Practice Gate
if st.text_input("Enter Practice Key", type="password") != "munger2026":
    st.stop() # Stops the rest of the app from loading


# --- 1. CONFIG & CURRENCY SCOUT ---
st.set_page_config(page_title="Inversion Engine: Munger Pro", layout="wide")

@st.cache_data(ttl=3600)
def get_exchange_rate():
    # Fetches GBP/USD rate
    forex = yf.Ticker("GBPUSD=X")
    return forex.fast_info['lastPrice']

# --- 2. THE ADVANCED SCANNER ---
@st.cache_data(ttl=3600)
def scan_munger_universe(tickers, base_currency="USD", limit=50):
    rate = get_exchange_rate()
    results = []
    
    for symbol in tickers[:limit]:
        try:
            t = yf.Ticker(symbol)
            info = t.info
            
            # Normalise Price (Convert GBp to GBP, then to USD if needed)
            raw_price = info.get('currentPrice', 1)
            currency = info.get('currency', 'USD')
            
            price_fixed = raw_price / 100 if currency == 'GBp' else raw_price
            price_usd = price_fixed * rate if currency == 'GBP' else price_fixed
            
            # Munger Quality Metrics
            roic = info.get('returnOnAssets', 0) * 2 # Proxy for ROIC in yfinance
            margin = info.get('operatingMargins', 0) * 100
            fcf = info.get('freeCashflow', 0)
            mcap = info.get('marketCap', 1)
            fcf_yield = (fcf / mcap) * 100 if mcap > 0 else 0
            
            results.append({
                "Ticker": symbol,
                "Name": info.get('shortName', 'Unknown'),
                "Price (USD)": price_usd,
                "Yield %": (info.get('dividendRate', 0) / price_fixed * 100),
                "ROIC %": roic * 100,
                "Op. Margin %": margin,
                "FCF Yield %": fcf_yield,
                "Debt/EBITDA": info.get('totalDebt', 0) / info.get('ebitda', 1)
            })
        except: continue
    return pd.DataFrame(results)

# --- 3. THE UI FILTERS ---
st.sidebar.header("🏛 Munger's Essential Filters")
target_yield = st.sidebar.slider("Min Yield %", 0.0, 8.0, 3.0)
min_roic = st.sidebar.slider("Min ROIC % (Quality)", 0, 50, 15)
min_margin = st.sidebar.slider("Min Op. Margin % (Moat)", 0, 50, 10)
max_debt = st.sidebar.slider("Max Debt/EBITDA (Safety)", 0.0, 10.0, 3.0)

# --- 4. EXECUTION & RESULTS ---
pts = PyTickerSymbols()
all_tickers = sorted(list(set(pts.get_ftse_100_london_yahoo_tickers() + pts.get_nasdaq_100_nyc_yahoo_tickers())))

with st.spinner("Normalising Currencies & Inverting Markets..."):
    df = scan_munger_universe(all_tickers)
    
    # APPLY THE FILTERS
    mask = (
        (df['Yield %'] >= target_yield) & 
        (df['ROIC %'] >= min_roic) & 
        (df['Op. Margin %'] >= min_margin) &
        (df['Debt/EBITDA'] <= max_debt)
    )
    final_df = df[mask].sort_values(by="ROIC %", ascending=False)

st.subheader(f"🏆 Found {len(final_df)} 'Wonderful Companies' at Fair Prices")
st.dataframe(final_df.style.background_gradient(cmap='RdYlGn', subset=['ROIC %', 'FCF Yield %']), use_container_width=True)

# --- 5. Main Logic & Sorting ---
all_tickers = get_universe()
limit_val = len(all_tickers) if scan_limit == "Full" else scan_limit

with st.spinner(f"Inverting {limit_val} stocks..."):
    df = scan_markets(all_tickers, limit=limit_val)
    
    if not df.empty:
        # Calculate Scores
        df['Munger Score'] = df.apply(lambda x: calculate_munger_score(x, user_yield), axis=1)
        
        # UX IMPROVEMENT: The "Strict Hierarchy" Filter
        # 1. Filter by your sidebar requirements
        mask = (df['Yield %'] >= user_yield) & (df['Munger Score'] >= 40)
        filtered_df = df[mask].copy()
        
        # 2. SORT by Score (Highest First) then Yield
        filtered_df = filtered_df.sort_values(by=['Munger Score', 'Yield %'], ascending=[False, False])

# --- 6. The Results Display ---
st.subheader("🏆 The 'Fat Pitch' Shortlist")

if not filtered_df.empty:
    # UX IMPROVEMENT: Dynamic column formatting
    st.dataframe(
        filtered_df.style.background_gradient(subset=['Munger Score'], cmap='RdYlGn')
        .format({
            "Yield %": "{:.2f}%",
            "Debt/EBITDA": "{:.1f}x",
            "Insider %": "{:.2f}%",
            "Price": "{:.2f}",
            "P/E": "{:.1f}"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    # Download Button
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Shortlist (CSV)", csv, "munger_shortlist.csv", "text/csv")
else:
    st.warning("No stocks currently meet your requirements. Try lowering the 'Min Yield' or increasing 'Scan Depth'.")
st.divider()
st.divider()
st.caption("🚨 **PERSONAL HOBBY PROJECT - NOT FOR COMMERCIAL USE**")
st.caption("""
    **DISCLAIMER:** This tool is for educational and practice purposes only. 
    It does not constitute financial advice, investment research, or an offer to buy/sell securities. 
    The 'Munger Score' is a mathematical experiment and not a verified indicator of performance. 
    The author is not FCA regulated. Always do your own due diligence.
""")
st.caption("© 2026 | Built for personal educational practice.")





