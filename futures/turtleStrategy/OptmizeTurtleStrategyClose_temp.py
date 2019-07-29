from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
import pandas as pd
import backtrader.analyzers as btanalyzers
# Create a Stratey
class TurtleStrategy01(bt.Strategy):
    params = (
        ('longIN',20 ),
        ('differIN',0 ),
        ('longExitDiffer',0 ),
        ('shortExitDiffer',0 ),
        ('atrDays',20 ),
        ('atrNo',2)
    )
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        #print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
      
        self.dataclose = self.datas[0].close
        self.tradeCount = 0
        #self.tradeCount += 1
        self.winCount = 0
        self.loseCount = 0
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.entryprice = None
        self.buycomm = None
        self.entryNo = 0
        self.lastEntryPrice = 0
        self.entryAtr = None
        self.longEntry = None
        self.shortEntry = None
        self.longExit = None
        self.shortExit = None
        self.atrValue = None
        self.exitPrice = 0
        self.longExitParam = int(self.params.longIN/2)+self.params.longExitDiffer
        self.shortExitParam = int((self.params.longIN+self.params.differIN)/2)+self.params.shortExitDiffer
        # Add a MovingAverageSimple indicator
        if (self.params.longIN - self.longExitParam) < 4:
            print(self.params.longIN - self.longExitParam)
            return     
    
        self.atrValue = bt.indicators.ATR(
            self.datas[1], period=self.params.atrDays, plot=False)             
        self.dayclose = self.datas[1]
        self.dayclose.open = self.datas[1].close
        self.dayclose.high = self.datas[1].close
        self.dayclose.low = self.datas[1].close
        self.dayclose.close = self.datas[1].close          
        
        self.longEntry = bt.indicators.Highest(self.dayclose,period=self.params.longIN)
        #bt.indicators.Highest(
        #    self.data1, self.params.longIN)
        self.shortEntry = bt.indicators.Lowest(
            self.dayclose,period=(self.params.longIN+self.params.differIN))
        self.longExit = bt.indicators.Lowest(
            self.dayclose, period=self.longExitParam)

        self.shortExit = bt.indicators.Highest(
            self.dayclose, period=(self.shortExitParam))
        
        


        '''
        # Indicators for the plotting show
        bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
                                            subplot=True)
        bt.indicators.StochasticSlow(self.datas[0])
        bt.indicators.MACDHisto(self.datas[0])
        rsi = bt.indicators.RSI(self.datas[0])
        bt.indicators.SmoothedMovingAverage(rsi, period=10)
        bt.indicators.ATR(self.datas[0], plot=False)
        '''

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                #self.log(
                #    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                #    (order.executed.price,
                #     order.executed.value,
                #     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                self.bar_executed = len(self)
            else:  # Sell
                #self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                #         (order.executed.price,
                #          order.executed.value,
                #          order.executed.comm))
                pass
            self.bar_executed = len(self)
            

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            
            #self.log('Order Canceled/Margin/Rejected')
            pass
        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        #self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
        #         (trade.pnl, trade.pnlcomm))
        if trade.pnl > 0:
            self.winCount += 1
        else:
            self.loseCount += 1
        self.tradeCount += 1    
    def next(self):
        if self.params.longIN < self.longExitParam + 4:
            return
        # Simply log the closing price of the series from the reference
        #self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            self.entryNo = 0 
            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] > self.longEntry[0]:

                # BUY, BUY, BUY!!! (with all possible default parameters)
                #self.log('BUY CREATE, %.2f' % self.dataclose[0])
                #self.log('Long Entry, %.2f' % self.longEntry[0])
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()
                self.entryNo += 1
                self.lastEntryPrice = self.dataclose[0]
                self.entryAtr = self.atrValue[0]
            
            elif self.dataclose[0] < self.shortEntry[0]:
                #self.log('Short Create, %.2f'% self.dataclose[0])
                self.order =self.sell()
                self.entryNo += 1
                self.lastEntryPrice = self.dataclose[0]     
                self.entryAtr = self.atrValue[0]           
            
        else:
            if self.position.size > 0 :
                if self.lastEntryPrice - 2* self.entryAtr > self.longExit[0]:
                    self.exitPrice = self.lastEntryPrice - 2* self.entryAtr
                else:
                    self.exitPrice = self.longExit[0]
                #self.log('Exit Entry, %.2f'% self.exitPrice) 
                #self.log('Long Exit, %.2f'% self.longExit[0])                 
                #self.log('Last Entry, %.2f'% self.lastEntryPrice)
                #self.log('Entry ATR, %.2f'% self.entryAtr)                                                      
                if self.entryNo ==1 and self.lastEntryPrice >  0 \
                    and self.dataclose[0] > self.lastEntryPrice + self.entryAtr:
                    #self.log('BUY CREATE, %.2f' % self.dataclose[0])
    
                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.buy()
                    self.entryNo += 1
                    self.lastEntryPrice = self.dataclose[0]                    
                elif self.entryNo ==2 and self.lastEntryPrice >  0 \
                    and self.dataclose[0] > self.lastEntryPrice + 0.5*self.entryAtr:

                    #self.log('BUY CREATE, %.2f' % self.dataclose[0])
    
                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.buy()
                    self.entryNo += 1
                    self.lastEntryPrice = self.dataclose[0]  
                elif self.dataclose[0] < self.exitPrice:
                    self.close()
                else:
                    pass
            else:
                if self.position.size < 0 :
                    if self.lastEntryPrice + 2* self.entryAtr < self.shortExit[0]:
                        self.exitPrice = self.lastEntryPrice + 2* self.entryAtr
                    else:
                        self.exitPrice = self.shortExit[0]
                    if self.entryNo ==1 and self.lastEntryPrice >  0 \
                        and self.dataclose[0] < self.lastEntryPrice - self.entryAtr:
                        #self.log('SELL CREATE, %.2f' % self.dataclose[0])
        
                        # Keep track of the created order to avoid a 2nd order
                        self.order = self.sell()
                        self.entryNo += 1
                        self.lastEntryPrice = self.dataclose[0]                    
                    elif self.entryNo ==2 and self.lastEntryPrice >  0 \
                        and self.dataclose[0] < self.lastEntryPrice - 0.5*self.entryAtr:
    
                        #self.log('SELL CREATE, %.2f' % self.dataclose[0])
        
                        # Keep track of the created order to avoid a 2nd order
                        self.order = self.sell()
                        self.entryNo += 1
                        self.lastEntryPrice = self.dataclose[0]  
                    elif self.dataclose[0] > self.exitPrice:
                        self.close()
                    else:
                        pass                
  
    def stop(self):
        print('%2d,%2d,%2d,%2d,%2d,%2d,%2d,%2d,%.2f' %
                 (self.params.longIN,self.params.differIN,self.params.longExitDiffer,self.params.shortExitDiffer,self.params.atrDays, self.tradeCount,self.winCount,self.loseCount,self.broker.getvalue()))


if __name__ == '__main__':
    # Create a cerebro entity
    
    import time
    time.sleep(3600*20)
    cerebro = bt.Cerebro(maxcpus=6,optreturn=False,stdstats=False)

    # Add a strategy
    #cerebro.addstrategy(TurtleStrategy01)   
     
    strats = cerebro.optstrategy(
        TurtleStrategy01,
        longIN=range(18, 38,2),
        differIN=range(-2, 4,2),
        longExitDiffer=range(-1, 2),
        shortExitDiffer=range(-1, 2),
        atrDays=20,  
        atrNo=range(2, 3)                                            
        ) 
    
    # Set the commission
    cerebro.broker.setcommission(leverage=1,mult =10,commission=0.01)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '../../datas/SFindex.csv')

    tframes = dict(daily=bt.TimeFrame.Days, weekly=bt.TimeFrame.Weeks,
                   monthly=bt.TimeFrame.Months)
    

    
    print(datapath)
    # Create a Data Feed
    
    '''
    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        datetime=1,
        fromdate=datetime.datetime(2009, 01, 01),
        todate=datetime.datetime(2009, 07, 10),
        timeframe= bt.TimeFrame.Minutes,
        compression=1,
        dtformat=('%Y-%m-%d %H:%M:%S'),
        open=2,
        high=3,
        low=4,
        close=5,
        volume=6)
    '''
    p0 = pd.read_csv(datapath, index_col='datetime', parse_dates=True)
    p0.drop("seqno",axis=1, inplace=True)
    #print(p0)
    p0 = p0.dropna()
    data = bt.feeds.PandasData(dataname = p0,fromdate=datetime.datetime(2009, 1, 2),
        todate=datetime.datetime(2019,4, 1),
        timeframe= bt.TimeFrame.Minutes,
        compression=1)  
    # Add the Data Feed to Cerebro
    cerebro.adddata(data)


    # Add the Data Feed to Cerebro
    #cerebro.resampledata(data,timeframe=bt.TimeFrame.Minutes,compression=10)

    cerebro.resampledata(data, timeframe=tframes["daily"],compression=1)

    #cerebro.resampledata(data, timeframe=tframes["daily"],compression=1)

    # Set our desired cash start
    cerebro.broker.setcash(200000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)
    # Add a FixedSize sizer according to the stake
    #cerebro.addsizer(bt.sizers.FixedSize, stake=3)

    # Set the commission
    #cerebro.broker.setcommission(commission=0.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    print("LongIn,DifferIn,longExit,DifferExit,atrDays,TradeCount,Winning,Losing,Final Value")

    cerebro.addanalyzer(btanalyzers.VWR, _name='vwr',timeframe=bt.TimeFrame.Years)
    #cerebro.addanalyzer(btanalyzers.AnnualReturn, _name='annual')
    cerebro.addanalyzer(btanalyzers.Returns, _name='logreturn',timeframe=bt.TimeFrame.Years)
    cerebro.addanalyzer(btanalyzers.SQN, _name='SQN')
    cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='TradeAnalyzer')
    cerebro.addanalyzer(btanalyzers.DrawDown, _name='Drawdown')
    cerebro.addanalyzer(btanalyzers.TimeDrawDown, _name='TimeDrawdown',timeframe=bt.TimeFrame.Days)    
    # Run over everything
    opt_runs = cerebro.run()

    final_results_list = []
    ttt = 1
    for run in opt_runs:
        for strategy in run:
            #value = round(strategy.broker.get_value(),2)
            #PnL = round(value - startcash,2)
            longin = strategy.params.longIN
            differin = strategy.params.differIN
            longexitdiffer = strategy.params.longExitDiffer
            shortexitdiffer = strategy.params.shortExitDiffer

            rvwr = strategy.analyzers.vwr.get_analysis()
            rsqn = strategy.analyzers.SQN.get_analysis()
            rlogreturn = strategy.analyzers.logreturn.get_analysis()
            rTradeAnalyzer = strategy.analyzers.TradeAnalyzer.get_analysis()
            if (len(rTradeAnalyzer) < 3):
                continue
            netpnl = rTradeAnalyzer["pnl"]["net"]["total"]
            avgpnl = rTradeAnalyzer["pnl"]["net"]["average"]
            tcnt = rTradeAnalyzer["total"]["total"]
            if tcnt == 0:
                continue
            won = rTradeAnalyzer["won"]["total"]
            lost = rTradeAnalyzer["lost"]["total"]

            wlr = float(won/(won+lost))
            if abs(rTradeAnalyzer['lost']['pnl']['total']) <0.001:
                plr = 0
            else:
                plr = abs( rTradeAnalyzer['won']['pnl']['total'])/abs(rTradeAnalyzer['lost']['pnl']['total'])
            profitfactor = wlr*plr/(1-wlr)
            
            longavg = rTradeAnalyzer["long"]["pnl"]["average"]
            shortavg = rTradeAnalyzer["short"]["pnl"]["average"]
            ddAna = strategy.analyzers.Drawdown.get_analysis()

            tmAna = strategy.analyzers.TimeDrawdown.get_analysis() 

            maxDD = ddAna["max"]["drawdown"]
            
            tmDD = tmAna["maxdrawdownperiod"]
            

            final_results_list.append([longin,differin,longexitdiffer,shortexitdiffer,netpnl,avgpnl,tcnt,profitfactor,won,lost,longavg,shortavg,rvwr["vwr"],rsqn["sqn"],rlogreturn["rtot"],rlogreturn["ravg"],rlogreturn["rnorm"],maxDD,tmDD])
            #print(ttt)
            ttt=ttt+1
    clms = ["longin","differin","longexitdiffer","shortexitdiffer","netpnl","avgpnl","totalcnt","profitfactor","won","lost","longavgprofit","shortavgprofit","vwr","sqn","totallogReturn","avglog","anuanlog","MaxDrawdown","TimeDrawdown"]
    df = pd.DataFrame(final_results_list, columns=clms) 
    df.to_csv("./tempOut/TT_SF_ANA.csv")
