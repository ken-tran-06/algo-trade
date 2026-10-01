import yfinance as yf
import math

AAPL = yf.Ticker("AAPL")

AAPL_hist = AAPL.history(period="1mo")

# print(AAPL_hist)

# with open("output.txt", "w") as f:
#   f.write(AAPL_hist.to_string())

# print(type(AAPL_hist))
# print(AAPL_hist.head())
# print(AAPL_hist.columns)

# print(AAPL_hist["Close"])
# print(AAPL_hist["Close"].head())

# first_close = AAPL_hist["Close"].iloc[0]
# second_close = AAPL_hist["Close"].iloc[1]

# daily_return = (second_close - first_close) / first_close

# print(f"{daily_return:.2%}")

AAPL_hist["Daily Return"] = AAPL_hist["Close"].pct_change()
day_volatility = AAPL_hist["Daily Return"].std()
ann_volatility = day_volatility * math.sqrt(252) # -> 252 trading days in year

print(AAPL_hist[["Close", "Daily Return"]])
print(f"\nDaily Volatility: {day_volatility:.2%}")
print(f"Annual Volatility: {ann_volatility:.2%}")


