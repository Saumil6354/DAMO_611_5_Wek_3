import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Multi-Stock Price Analysis", layout="wide")

st.title("📊 Multi-Stock Price Analysis with Weekly Averages")

# Sidebar for user inputs
tickers = st.sidebar.text_input(
    "Enter Stock Tickers (comma separated, e.g., AAPL, TSLA, MSFT):",
    "AAPL, TSLA, MSFT"
)
tickers = [t.strip().upper() for t in tickers.split(",")]

period = st.sidebar.selectbox("Select Period:", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y"])
interval = "1d"

# Function to fetch data
@st.cache_data
def load_data(ticker, period, interval):
    df = yf.download(ticker, period=period, interval=interval)
    df['Ticker'] = ticker
    return df

# Fetch data for each ticker
all_data = []
for t in tickers:
    df = load_data(t, period, interval)
    if not df.empty:
        all_data.append(df)
    else:
        st.warning(f"⚠️ No data found for ticker {t}")

if all_data:
    data = pd.concat(all_data)

    # Plot with weekly averages
    fig = go.Figure()

    for t in tickers:
        df_t = data[data['Ticker'] == t].copy()
        df_t['Week'] = df_t.index.to_period('W')
        weekly_avg = df_t.groupby('Week')['Close'].mean().reset_index()
        weekly_avg['Week'] = pd.to_datetime(weekly_avg['Week'].astype(str))

        fig.add_trace(go.Scatter(x=df_t.index, y=df_t['Close'], mode='lines', name=f'{t} Daily'))
        fig.add_trace(go.Scatter(x=weekly_avg['Week'], y=weekly_avg['Close'], mode='lines+markers', name=f'{t} Weekly Avg'))

    fig.update_layout(
        title="Stock Prices & Weekly Averages",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_dark",
        hovermode="x unified"
    )

    # Display chart
    st.plotly_chart(fig, use_container_width=True)

    # Show last 5 rows per ticker
    st.subheader("Latest Data (Last 5 Days per Ticker)")
    for t in tickers:
        st.write(f"**{t}**")
        st.dataframe(data[data['Ticker'] == t].tail(5))
