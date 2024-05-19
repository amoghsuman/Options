import backtrader as bt
import datetime

class VIXHedgingStrategy(bt.Strategy):
    params = (
        ('spy_allocation', 0.6),
        ('ief_allocation', 0.4),
        ('vix_call_weight_low', 0.01),
        ('vix_call_weight_high', 0.005),
        ('vix_lower_bound', 15),
        ('vix_upper_bound', 50),
    )
    
    def __init__(self):
        self.spy = self.datas[0]
        self.ief = self.datas[1]
        self.vix = self.datas[2]
        self.vix_futures = self.datas[3]
        self.vix_call_options = self.datas[4:8]  # 1-month to 4-month VIX call options

    def next(self):
        # Determine VIX call options weight
        vix_call_weight = 0
        if self.vix[0] > self.params.vix_lower_bound and self.vix[0] <= 30:
            vix_call_weight = self.params.vix_call_weight_low
        elif self.vix[0] > 30 and self.vix[0] <= self.params.vix_upper_bound:
            vix_call_weight = self.params.vix_call_weight_high

        # Allocate to SPY and IEF
        self.order_target_percent(self.spy, self.params.spy_allocation)
        self.order_target_percent(self.ief, self.params.ief_allocation)

        # Allocate to VIX call options
        if vix_call_weight > 0:
            for option_data in self.vix_call_options:
                option_price = option_data.close[0] * 1.35  # 135% moneyness
                option_value = self.broker.getvalue() * vix_call_weight / len(self.vix_call_options)
                option_size = option_value // option_price
                self.buy(data=option_data, size=option_size)

        # Roll options and rebalance the day before expiration
        if self.datetime.date() + datetime.timedelta(days=1) == self.vix_futures.expiredate[0]:
            for option_data in self.vix_call_options:
                self.close(data=option_data)
            self.rebalance()

    def rebalance(self):
        cash = self.broker.get_cash()
        self.order_target_value(self.spy, cash * self.params.spy_allocation)
        self.order_target_value(self.ief, cash * self.params.ief_allocation)

cerebro = bt.Cerebro()

# Add data feeds for SPY, IEF, VIX, VIX Futures, and VIX call options
# ...

cerebro.addstrategy(VIXHedgingStrategy)
cerebro.run()
