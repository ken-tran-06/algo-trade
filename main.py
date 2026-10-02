import yfinance as yf
import math
import pandas as pd

def calculate_moving_averages(data, short_window, long_window):
    short_sma = data["Close"].rolling(short_window).mean()    
    long_sma = data["Close"].rolling(long_window).mean()    

    data["SMASHORT"] = short_sma
    data["SMALONG"] = long_sma

    return data

def detect_crossovers(data):
    for current in range(1, len(data)):
        prev = current - 1
        date = data.index[current].date()
        prev_short = data["SMASHORT"].iloc[prev]
        prev_long = data["SMALONG"].iloc[prev]
        curr_short = data["SMASHORT"].iloc[current]
        curr_long = data["SMALONG"].iloc[current]

        if (pd.isna(prev_short) or pd.isna(prev_long) or pd.isna(curr_short) or pd.isna(curr_long)):
            continue
        elif (prev_short <= prev_long and curr_short > curr_long):
            print(f"{date} BUY")
        elif (prev_short >= prev_long and curr_short < curr_long):
            print(f"{date} SELL")

# MAIN:
AAPL = yf.Ticker("AAPL")

AAPL_hist = AAPL.history(period="6mo")

AAPL_hist["Daily Return"] = AAPL_hist["Close"].pct_change()
day_volatility = AAPL_hist["Daily Return"].std()
ann_volatility = day_volatility * math.sqrt(252) # -> 252 trading days in year

# print(AAPL_hist[["Close", "Daily Return"]])
# print(f"\nDaily Volatility: {day_volatility:.2%}")
# print(f"Annual Volatility: {ann_volatility:.2%}")

# print(f"-----------------------------------------------------------")
# AAPL_hist = calculate_moving_averages(AAPL_hist, 20, 50)
# print(AAPL_hist[["Close", "SMASHORT", "SMALONG"]])

AAPL_hist = calculate_moving_averages(AAPL_hist, 20, 50)

detect_crossovers(AAPL_hist)
