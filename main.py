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
    signals = []

    for current in range(1, len(data)):
        prev = current - 1
        date = data.index[current].date()
        prev_short = data["SMASHORT"].iloc[prev]
        prev_long = data["SMALONG"].iloc[prev]
        curr_short = data["SMASHORT"].iloc[current]
        curr_long = data["SMALONG"].iloc[current]
        price = data["Close"].iloc[current]

        if (pd.isna(prev_short) or pd.isna(prev_long) or pd.isna(curr_short) or pd.isna(curr_long)):
            continue
        elif (prev_short <= prev_long and curr_short > curr_long):
            # print(f"{date} BUY")
            signals.append({
                "date": date,
                "signal": "BUY",
                "price": price
            })
        elif (prev_short >= prev_long and curr_short < curr_long):
            # print(f"{date} SELL")
            signals.append({
                "date": date,
                "signal": "SELL",
                "price": price
            })

    return signals

def backtest(signals, starting_cash,final_price):
    cash = starting_cash
    shares = 0
    holding = False

    for trade in signals:
        if trade["signal"] == "BUY" and not holding:
            shares_to_buy = int(cash // trade["price"])
            if shares_to_buy > 0:
                cost = shares_to_buy * trade["price"]

                cash -= cost
                shares = shares_to_buy
                holding = True

        elif trade["signal"] == "SELL" and holding:
            sale_value = shares * trade["price"]
            cash += sale_value
            shares = 0
            holding = False

    final_value = cash + (shares * final_price)
    strategy_return = (final_value - starting_cash) / starting_cash

    return final_value,strategy_return

def buy_and_hold(data,starting_cash):
    first_price = data["Close"].iloc[0]
    ending_price = data["Close"].iloc[-1]

    shares_to_buy = int(starting_cash // first_price)
    left_over_cash = starting_cash - (shares_to_buy * first_price)

    final_value = left_over_cash + (shares_to_buy*ending_price)
    strategy_return = (final_value - starting_cash) / starting_cash

    return final_value,strategy_return

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

# Data Setup ---------------------------------------------------------------

AAPL_hist = calculate_moving_averages(AAPL_hist, 20, 50)

signals = detect_crossovers(AAPL_hist)

final_price = AAPL_hist["Close"].iloc[-1]

# Data Analysis ------------------------------------------------------------

final_value, strategy_return = backtest(signals, 10000, final_price)

valid_data = AAPL_hist.dropna(subset=["SMALONG"])
buy_hold_value, buy_hold_return = buy_and_hold(valid_data, 10000)

print("SMA Crossover Strategy")
print(f"Final Portfolio Value: ${final_value:.2f}")
print(f"Strategy Return: {strategy_return:.2%}")

print("\nBuy & Hold")
print(f"Final Portfolio Value: ${buy_hold_value:.2f}")
print(f"Strategy Return: {buy_hold_return:.2%}")