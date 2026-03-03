import backtrader as bt
import yfinance as yf
import pandas as pd
from datetime import datetime

from request_snippet import get_eia_inventory_data
from gdelt_snippet import get_gdelt_conflict_score
from metrics_snippet import print_backtest_metrics

class GeoOilData(bt.feeds.PandasData):
    lines = ('conflict_score', 'inventory_change',)
    params = (
        ('conflict_score', 'conflict_score'), 
        ('inventory_change', 'inventory_change'),
    )

class GeopoliticalOilStrategy(bt.Strategy):
    params = (
        ('risk_threshold', 0.35), 
        ('profit_target', 0.3),  
        ('stop_loss', 0.1),
        ('sma_period', 5),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.conflict = self.datas[0].conflict_score
        self.inventory = self.datas[0].inventory_change
        
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.sma_period)
        
        self.order = None
        self.buyprice = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                print(f"BUY EXECUTED at {order.executed.price:.2f}")
                self.buyprice = order.executed.price
            elif order.issell():
                print(f"SELL EXECUTED at {order.executed.price:.2f}")
        self.order = None 

    def next(self):
        if len(self) < self.params.sma_period:
            return

        if self.order:
            return

        if not self.position:
            if (self.conflict[0] > self.params.risk_threshold and 
                self.inventory[0] < 0 and 
                self.dataclose[0] > self.sma[0]): 
                
                print(f"\n{self.datas[0].datetime.date(0)} - SIGNAL: High Risk ({self.conflict[0]:.2f}) & UPTREND.")
                self.order = self.buy()
        else:
            current_return = (self.dataclose[0] - self.buyprice) / self.buyprice
            if current_return >= self.params.profit_target:
                print(f"{self.datas[0].datetime.date(0)} - EXIT: Take Profit Hit")
                self.order = self.sell()
            elif current_return <= -self.params.stop_loss:
                print(f"{self.datas[0].datetime.date(0)} - EXIT: Stop Loss Hit")
                self.order = self.sell()

# 2 -> Data pipeline
def build_complete_dataset(eia_key, google_key_path):
    today_yf = datetime.today().strftime('%Y-%m-%d')
    today_gdelt = datetime.today().strftime('%Y%m%d')

    print(f"Downloading historical price data (USO) up to {today_yf}...")
    price_df = yf.download('USO', start='2022-01-01', end=today_yf)
    
    if isinstance(price_df.columns, pd.MultiIndex):
        price_df.columns = price_df.columns.get_level_values(0)
    
    price_df.reset_index(inplace=True)
    price_df['Date'] = price_df['Date'].dt.tz_localize(None) 
    
    eia_df = get_eia_inventory_data(eia_key)
    eia_df['Date'] = eia_df['Date'].dt.tz_localize(None)
    
    gdelt_df = get_gdelt_conflict_score(google_key_path, start_date='20220101', end_date=today_gdelt)
    gdelt_df['Date'] = gdelt_df['Date'].dt.tz_localize(None)

    print("Merging datasets...")
    merged_df = pd.merge_asof(
        price_df.sort_values('Date'), 
        eia_df.sort_values('Date'), 
        on='Date', 
        direction='backward' 
    )

    merged_df = pd.merge_asof(
        merged_df.sort_values('Date'),
        gdelt_df.sort_values('Date'),
        on='Date',
        direction='backward'
    )
    
    merged_df.set_index('Date', inplace=True)
    merged_df.dropna(inplace=True)
    
    return merged_df


# 3 -> Run the engine

if __name__ == '__main__':
    MY_EIA_KEY = "place your own eia api key here"
    MY_GOOGLE_KEY = "google_key.json" 
    
    cerebro = bt.Cerebro()
    
    cerebro.addstrategy(GeopoliticalOilStrategy)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=90) 

    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.03) 
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

    try:
        raw_data = build_complete_dataset(MY_EIA_KEY, MY_GOOGLE_KEY)
        
        if len(raw_data) > 0:
            data = GeoOilData(dataname=raw_data)
            cerebro.adddata(data)

            cerebro.broker.setcash(10000.0)
            print(f"\nStarting Portfolio Value: ${cerebro.broker.getvalue():.2f}")
            
            results = cerebro.run()
            strat = results[0] 
            
            print(f"Ending Portfolio Value: ${cerebro.broker.getvalue():.2f}")
            
            print_backtest_metrics(strat)
            
            cerebro.plot(style='candlestick', volume=False)
            
        else:
            print("Error: Your dataset is empty.")
            
    except Exception as e:
        print(f"\n Pipeline Halted with Error: {e}")