import backtrader as bt
import mathimport numpy as np

class PutOptionWritingStrategy(bt.Strategy):
    params = (
        ('leverage', 2.0),
        ('strike_price_distance_multiplier', 1.0)
    )

    def __init__(self):
        self.put_option = None
        self.sp500 = self.datas[0]

    def next(self):
        # Calculate the standard deviation of the S&P 500 Index for the last month
        monthly_std = np.std(self.sp500.get(size=21))
        # Calculate the strike price for the put option
        strike_price = self.sp500[0] - (self.params.strike_price_distance_multiplier * monthly_std)
        # Calculate the option premium
        option_premium = max(self.sp500[0] - strike_price, 0)
        # Calculate the required capital to short the put option
        capital_required = option_premium * self.params.leverage
        # Calculate the capital to invest in the risk-free rate
        free_capital = self.broker.get_cash() - capital_required
        # Invest free capital in risk-free rate
        self.buy(data=self.datas[1], size=free_capital)
        # Short the put option
        self.sell(data=self.put_option, size=self.params.leverage, exectype=bt.Order.Put, strike=strike_price)

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    # Add the S&P 500 Index and risk-free rate data feeds
    cerebro.adddata(bt.feeds.YahooFinanceData(dataname='^GSPC', fromdate='2000-01-01', todate='2021-09-30'))
    cerebro.adddata(bt.feeds.FRED(dataname='DTB3', fromdate='2000-01-01', todate='2021-09-30'))
    # Add the put option data feed
    cerebro.adddata(bt.feeds.GenericCSVData(dataname='put_option_data.csv', dtformat=('%Y-%m-%d')))
    cerebro.addstrategy(PutOptionWritingStrategy)
    cerebro.broker.setcash(100000.0)
    cerebro.run()
    cerebro.plot()
