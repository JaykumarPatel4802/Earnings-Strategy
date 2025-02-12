import yfinance as yf
import pandas as pd
import pytz
from datetime import datetime, timedelta

def classify_earnings_time(dt):
    """Classify earnings release time as premarket or after-hours."""
    hour = dt.hour
    if hour < 9:  # Before 9:30 AM ET
        return "Premarket"
    elif hour >= 16:  # After 4:00 PM ET
        return "After Hours"
    return "During Market"  # Edge case (rare)

def fetch_earnings_and_prices(ticker):
    """Fetch past 8 earnings dates and compute price differences."""
    stock = yf.Ticker(ticker)

    # Convert to New York timezone
    ny_tz = pytz.timezone("America/New_York")
    today = datetime.now(ny_tz)
    
    # Get only past earnings dates (before today)
    earnings_dates = stock.earnings_dates[stock.earnings_dates.index < today]

    # Select last 8 past earnings reports
    earnings_dates = earnings_dates.head(8).copy()

    # Convert earnings timestamps to New York timezone
    earnings_dates.index = pd.to_datetime(earnings_dates.index).tz_convert(ny_tz)

    # Classify premarket or after-hours
    earnings_dates["Market Session"] = earnings_dates.index.map(classify_earnings_time)

    # Get historical price data around earnings dates
    start_date = (earnings_dates.index.min() - timedelta(days=2)).strftime("%Y-%m-%d")
    end_date = (earnings_dates.index.max() + timedelta(days=2)).strftime("%Y-%m-%d")
    price_data = stock.history(start=start_date, end=end_date)

    # Ensure index is in datetime format
    price_data.index = pd.to_datetime(price_data.index)

    # Compute price differences
    results = []
    for date, row in earnings_dates.iterrows():
        market_session = row["Market Session"]

        # Get current date's row in price_data
        current_day = price_data.loc[price_data.index.date == date.date()]

        # Get previous day's row
        prev_day = price_data.loc[price_data.index.date == (date - timedelta(days=1)).date()]

        # Get next day's row
        next_day = price_data.loc[price_data.index.date == (date + timedelta(days=1)).date()]

        # Compute price difference based on earnings time
        price_diff = None
        if market_session == "Premarket":
            if not prev_day.empty and not current_day.empty:
                price_diff = current_day.iloc[0]["Open"] - prev_day.iloc[0]["Close"]

        elif market_session == "After Hours":
            if not current_day.empty and not next_day.empty:
                price_diff = next_day.iloc[0]["Open"] - current_day.iloc[0]["Close"]

        # Store results
        results.append({
            "Earnings Date": date.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "Market Session": market_session,
            "Price Difference": price_diff
        })

    # Convert results to DataFrame
    earnings_summary = pd.DataFrame(results)
    return earnings_summary

# Example usage
ticker = "MCY"
earnings_data = fetch_earnings_and_prices(ticker)
print(earnings_data)