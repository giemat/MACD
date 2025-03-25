import matplotlib
matplotlib.use('TkAgg')  # You can also try 'Qt5Agg' or 'Agg' for headless environments
import matplotlib.pyplot as plt
from data import *


data = get_SP500()
# data = get_INTC()
# data = get_NVDA()
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



# plt.plot(data["Data"],data["Zamkniecie"],label="S&P500")
# plt.xlabel("Data")
# plt.ylabel("Cena")
# plt.title("Notowania S&P500")
# plt.legend()
# plt.savefig("img/notowania_s&p500.png")
# plt.figure()
# data1 = data[:100]
# plt.plot(data1["Data"],data1["MACD"],label="MACD")
# plt.plot(data1["Data"],data1["SIGNAL"],label="SIGNAL")
#
# # Plot red triangles for 'SELL' actions
# sell_data = data1[data1["ACTION"] == 'SELL']
# plt.scatter(sell_data["Data"], sell_data["MACD"], color='red', marker='v', label='SELL')
#
# # Plot green dots for 'BUY' actions
# buy_data = data1[data1["ACTION"] == 'BUY']
# plt.scatter(buy_data["Data"], buy_data["MACD"], color='green', marker='o', label='BUY')
#
# plt.savefig("img/analiza_macd.png")
# plt.legend()
# plt.show()

# Trading simulation
def trading_sim(data):
    initial_money = 1000
    money = initial_money
    stocks = 0
    portfolio_value = []
    profitable_trades = 0
    losing_trades = 0

    for i in range(1, len(data.index)):
        if data.loc[i, "ACTION"] == 'BUY':
            stocks = money / data.loc[i, 'Zamkniecie']
            money = 0
        elif data.loc[i, "ACTION"] == 'SELL' and stocks > 0:
            money = stocks * data.loc[i, 'Zamkniecie']
            stocks = 0
            if money > initial_money:
                profitable_trades += 1
            else:
                losing_trades += 1
            initial_money = money
        portfolio_value.append(money + stocks * data.loc[i, 'Zamkniecie'])

    return money + stocks * data.loc[len(data.index) - 1, 'Zamkniecie'], portfolio_value, profitable_trades, losing_trades

final_capital, portfolio_value, profitable_trades, losing_trades = trading_sim(data)

# Plot portfolio value over time
plt.plot(portfolio_value, label="Portfolio Value")
plt.xlabel("Time")
plt.ylabel("Portfolio Value")
plt.title("Portfolio Value Over Time")
plt.legend()
plt.show()

# Simulation results
print(f"Final Capital: {final_capital}")
print(f"Profitable Trades: {profitable_trades}")
print(f"Losing Trades: {losing_trades}")
print(f"Total Trades: {profitable_trades + losing_trades}")
print(f"Success Rate: {profitable_trades / (profitable_trades + losing_trades) * 100:.2f}%")

def plot_transactions(data, start, end):
    plt.figure()
    plt.plot(data["Data"][start:end], data["MACD"][start:end], label="MACD")
    plt.plot(data["Data"][start:end], data["SIGNAL"][start:end], label="SIGNAL")

    # Plot red triangles for 'SELL' actions
    sell_data = data[(data["ACTION"] == 'SELL') & (data.index >= start) & (data.index < end)]
    plt.scatter(sell_data["Data"], sell_data["MACD"], color='red', marker='v', label='SELL')

    # Plot green dots for 'BUY' actions
    buy_data = data[(data["ACTION"] == 'BUY') & (data.index >= start) & (data.index < end)]
    plt.scatter(buy_data["Data"], buy_data["MACD"], color='green', marker='o', label='BUY')

    plt.xlabel("Data")
    plt.ylabel("MACD Value")
    plt.title("MACD and SIGNAL with Buy/Sell Actions")
    plt.legend()
    plt.show()

plot_transactions(data, 50, 100)
plot_transactions(data, 150, 200)