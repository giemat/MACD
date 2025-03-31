import matplotlib
matplotlib.use('TkAgg')  # You can also try 'Qt5Agg' or 'Agg' for headless environments
import matplotlib.pyplot as plt
from data import *

# name = "S&P500"
# name = "INTC"
name = "NVDA"
# data = get_SP500()
# data = get_INTC()
data = get_NVDA()
def calculateEMA(data,period,toColumn,fromColumn):
    alpha = 2/(period+1)
    data.loc[0,toColumn] = data.loc[0,fromColumn]
    for i in range(1,len(data)):
        data.loc[i,toColumn] = data.loc[i-1,toColumn]*(1-alpha) + data.loc[i,fromColumn]*alpha


calculateEMA(data,12,"EMA12","Zamkniecie")
calculateEMA(data,26,"EMA26","Zamkniecie")
data["MACD"] = data["EMA12"] - data["EMA26"]
calculateEMA(data,9,"SIGNAL","MACD")
data["OVER"] = data["MACD"] >= data["SIGNAL"]
data["ACTION"] = 'NONE'

for i in range(1, len(data.index)):
    a = data.loc[i, 'OVER']
    b = data.loc[i-1, 'OVER']
    if a and not b:
        data.loc[i, "ACTION"] = 'BUY'
    elif not a and b:
        data.loc[i, "ACTION"] = 'SELL'

# Plot closing prices
plt.figure().set_figwidth(12)
plt.plot(data["Data"],data["Zamkniecie"],label=f"{name}")
plt.xlabel("Date")
plt.ylabel("Close price")
plt.title(f"Exchange listing {name}")
plt.legend()
plt.xticks(data["Data"][::365])
plt.savefig(f"img/closePrice_{name}.png")
plt.figure()

sell_data = data[data["ACTION"] == 'SELL']
buy_data = data[data["ACTION"] == 'BUY']
# Plot MACD and SIGNAL
plt.figure().set_figwidth(12)
plt.plot(data["Data"],data["MACD"],label="MACD")
plt.plot(data["Data"],data["SIGNAL"],label="SIGNAL")
# Plot red triangles for 'SELL' actions
plt.scatter(sell_data["Data"], sell_data["MACD"], color='red', marker='v', label='SELL')
# Plot green dots for 'BUY' actions
plt.scatter(buy_data["Data"], buy_data["MACD"], color='green', marker='o', label='BUY')
plt.title(f"MACD and SIGNAL for {name}")
plt.xticks(data["Data"][::365])
plt.legend()
plt.savefig(f"img/macd_signal_{name}.png")
plt.show()

# Trading simulation
def trading_sim(data):
    initial_money = 1000
    money = initial_money
    stocks = 0
    portfolio_value = []
    profitable_trades = 0
    losing_trades = 0
    trades = []
    last_buy = 0
    for i in range(1, len(data.index)):
        if data.loc[i, "ACTION"] == 'BUY':
            stocks = money / data.loc[i, 'Zamkniecie']
            last_buy = data.loc[i, 'Zamkniecie']
            money = 0
        elif data.loc[i, "ACTION"] == 'SELL' and stocks > 0:
            money = stocks * data.loc[i, 'Zamkniecie']
            profit = money - initial_money
            trades.append((data.loc[i, 'Data'], last_buy, data.loc[i, 'Zamkniecie'], profit))
            stocks = 0
            if profit > 0:
                profitable_trades += 1
            else:
                losing_trades += 1
            initial_money = money
        data.loc[i, "Portfolio Value"] = money + stocks * data.loc[i, 'Zamkniecie']
        portfolio_value.append(money + stocks * data.loc[i, 'Zamkniecie'])

    trades.sort(key=lambda x: x[3], reverse=True)
    most_profitable_trades = trades[:5]
    least_profitable_trades = trades[-5:]

    return money + stocks * data.loc[len(data.index) - 1, 'Zamkniecie'], portfolio_value, profitable_trades, losing_trades, most_profitable_trades, least_profitable_trades

final_capital, portfolio_value, profitable_trades, losing_trades, most_profitable_trades, least_profitable_trades = trading_sim(data)

# Plot portfolio value over
plt.figure(figsize=(12, 7))
plt.plot(data["Data"], data["Portfolio Value"], label="Portfolio Value")
plt.xlabel("Time")
plt.ylabel("Portfolio Value")
plt.title("Portfolio Value Over Time for " + name)
plt.legend()
plt.xticks(data["Data"][::365], rotation=45)
plt.savefig(f"img/portfolio_value_{name}.png")
plt.show()


# Simulation results
print(f"Final Capital: {final_capital:.2f}({(final_capital*100/1000):.2f}%)")
print(f"Total Trades: {profitable_trades + losing_trades}")
print(f"Profitable Trades: {profitable_trades}")
print(f"Losing Trades: {losing_trades}")
print(f"Success Rate: {profitable_trades / (profitable_trades + losing_trades) * 100:.2f}%")
print("\nMost Profitable Trades:")
for date, buy_price, sell_price, profit in most_profitable_trades:
    print(f"Date: {date}, Buy Price: {buy_price:.2f}, Sell Price: {sell_price:.2f}, Profit: {profit:.2f}")
print("\nLeast Profitable Trades:")
for date, buy_price, sell_price, profit in least_profitable_trades:
    print(f"Date: {date}, Buy Price: {buy_price:.2f}, Sell Price: {sell_price:.2f}, Profit: {profit:.2f}")

# Save trading results
with open(f"trading_results_{name}.txt", 'w') as f:
    f.write(f"Final Capital: {final_capital:.2f}({(final_capital*100/1000):.2f}%)\n")
    f.write(f"Total Trades: {profitable_trades + losing_trades}\n")
    f.write(f"Profitable Trades: {profitable_trades}\n")
    f.write(f"Losing Trades: {losing_trades}\n")
    f.write(f"Success Rate: {profitable_trades / (profitable_trades + losing_trades) * 100:.2f}%\n")
    f.write("\nMost Profitable Trades:\n")
    for date, buy_price, sell_price, profit in most_profitable_trades:
        f.write(f"Date: {date}, Buy Price: {buy_price:.2f}, Sell Price: {sell_price:.2f}, Profit: {profit:.2f}\n")
    f.write("\nLeast Profitable Trades:\n")
    for date, buy_price, sell_price, profit in least_profitable_trades:
        f.write(f"Date: {date}, Buy Price: {buy_price:.2f}, Sell Price: {sell_price:.2f}, Profit: {profit:.2f}\n")

def plot_transactions(data, start, end):
    plt.figure().set_figwidth(12)
    plt.plot(data["Data"][start:end], data["Zamkniecie"][start:end], label="Close Price")

    # Plot red triangles for 'SELL' actions
    sell_data = data[(data["ACTION"] == 'SELL') & (data.index >= start) & (data.index < end)]
    plt.scatter(sell_data["Data"], sell_data["Zamkniecie"], color='red', marker='v', label='SELL')
    for i in sell_data.index:
        plt.text(sell_data["Data"][i], sell_data["Zamkniecie"][i], f'{sell_data["Zamkniecie"][i]:.2f}', color='red')

    # Plot green dots for 'BUY' actions
    buy_data = data[(data["ACTION"] == 'BUY') & (data.index >= start) & (data.index < end)]
    plt.scatter(buy_data["Data"], buy_data["Zamkniecie"], color='green', marker='o', label='BUY')
    for i in buy_data.index:
        plt.text(buy_data["Data"][i], buy_data["Zamkniecie"][i], f'{buy_data["Zamkniecie"][i]:.2f}', color='green')

    plt.xlabel("Data")
    plt.ylabel("Price")
    plt.title("Price with Buy/Sell Actions " + name)
    plt.xticks(data["Data"][start:end][::10])
    plt.legend()
    plt.savefig(f"img/analysis_{name}_{start}_{end}.png")
    plt.show()


plot_transactions(data, 50, 100)
plot_transactions(data, 400, 500)
