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
        signal_date = data.index[current].date()
        next_day = current + 1

        if next_day >= len(data):
            continue

        execution_date = data.index[next_day].date()
        execution_price = data["Open"].iloc[next_day]
        
        prev_short = data["SMASHORT"].iloc[prev]
        prev_long = data["SMALONG"].iloc[prev]
        curr_short = data["SMASHORT"].iloc[current]
        curr_long = data["SMALONG"].iloc[current]

        if (pd.isna(prev_short) or pd.isna(prev_long) or pd.isna(curr_short) or pd.isna(curr_long)):
            continue
        elif (prev_short <= prev_long and curr_short > curr_long):
            # print(f"{date} BUY")
            signals.append({
                "date": signal_date,
                "signal": "BUY",
                "execution_date": execution_date,
                "price": execution_price
            })
        elif (prev_short >= prev_long and curr_short < curr_long):
            # print(f"{date} SELL")
            signals.append({
                "date": signal_date,
                "execution_date": execution_date,
                "signal": "SELL",
                "price": execution_price
            })

    return signals

def backtest(signals, starting_cash,final_price):
    cash = starting_cash
    shares = 0
    trades = 0
    holding = False

    for trade in signals:
        if trade["signal"] == "BUY" and not holding:
            shares_to_buy = int(cash // trade["price"])
            if shares_to_buy > 0:
                cost = shares_to_buy * trade["price"]
                cash -= cost
                shares = shares_to_buy
                holding = True
                trades += 1

        elif trade["signal"] == "SELL" and holding:
            sale_value = shares * trade["price"]
            cash += sale_value
            shares = 0
            holding = False
            trades += 1

    final_value = cash + (shares * final_price)
    strategy_return = (final_value - starting_cash) / starting_cash

    return final_value,strategy_return, trades

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
# day_volatility = AAPL_hist["Daily Return"].std()
# ann_volatility = day_volatility * math.sqrt(252) # -> 252 trading days in year

# Data Analysis ------------------------------------------------------------

starting_cash = 10000

strategies = [
    (5, 20),
    (10, 30),
    (20, 50)
]

results = []

# All strategies must wait until the largest SMA is available.
largest_window = max(long_window for _, long_window in strategies)

common_start = AAPL_hist.index[largest_window - 1].date()
final_price = AAPL_hist["Close"].iloc[-1]

for short_window, long_window in strategies:

    strategy_data = AAPL_hist.copy()

    strategy_data = calculate_moving_averages(
        strategy_data,
        short_window,
        long_window
    )

    signals = detect_crossovers(strategy_data)

    signals = [
        signal
        for signal in signals
        if signal["execution_date"] >= common_start
    ]

    final_value, strategy_return, trades = backtest(
        signals,
        starting_cash,
        final_price
    )

    results.append({
        "Strategy": f"{short_window}/{long_window} SMA",
        "Final Value": final_value,
        "Return": strategy_return,
        "Trades": trades
    })


# OUTSIDE THE LOOP

common_data = AAPL_hist.iloc[largest_window - 1:]

buy_hold_value, buy_hold_return = buy_and_hold(
    common_data,
    starting_cash
)

results.append({
    "Strategy": "Buy & Hold",
    "Final Value": buy_hold_value,
    "Return": buy_hold_return,
    "Trades": 1
})

results_table = pd.DataFrame(results)

results_table["Final Value"] = results_table["Final Value"].map(
    lambda x: f"${x:,.2f}"
)

results_table["Return"] = results_table["Return"].map(
    lambda x: f"{x:.2%}"
)

print("\nStrategy Comparison")
print(results_table.to_string(index=False))