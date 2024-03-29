from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
import pandas as pd

# Create a Stratey
class TurtleStrategy01(bt.Strategy):
    params = (
        ('longIN',20 ),
        ('differIN',1 ),
        ('longExit',10 ),
        ('differExit',1 ),
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
        # Add a MovingAverageSimple indicator
        self.longEntry = bt.indicators.Highest(self.datas[1],period=self.params.longIN)
        #bt.indicators.Highest(
        #    self.data1, self.params.longIN)
        self.shortEntry = bt.indicators.Lowest(
            self.datas[1],period=(self.params.longIN+self.params.differIN))
        self.longExit = bt.indicators.Lowest(
            self.datas[1], period=self.params.longExit)

        self.shortExit = bt.indicators.Highest(
            self.datas[1], period=(self.params.longExit+self.params.differExit))
        
        
        self.atrValue = bt.indicators.ATR(
            self.datas[1], period=self.params.atrDays, plot=False)

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
            self.tradeCount += 1

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
    def next(self):

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
                 (self.params.longIN,self.params.differIN,self.params.longExit,self.params.differExit,self.params.atrDays, self.tradeCount,self.winCount,self.loseCount,self.broker.getvalue()))


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro(maxcpus=6)

    # Add a strategy
    #cerebro.addstrategy(TurtleStrategy01)   
    
    strats = cerebro.optstrategy(
        TurtleStrategy01,
        longIN=range(25, 28),
        differIN=range(-1, 2),
        longExit=range(12, 15),
        differExit=range(-1, 2),
        atrDays=20,  
        atrNo=range(2, 3)                                            
        )    
    # Set the commission
    cerebro.broker.setcommission(leverage=1,mult =10,commission=0.01)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, './datas/rbindex.csv')

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
    data = bt.feeds.PandasData(dataname = p0,fromdate=datetime.datetime(2009, 1, 2),
        todate=datetime.datetime(2019,4, 1),
        timeframe= bt.TimeFrame.Minutes,
        compression=10)
    

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    cerebro.resampledata(data, timeframe=tframes["daily"],compression=1)

    #cerebro.resampledata(data, timeframe=tframes["daily"],compression=1)

    # Set our desired cash start
    cerebro.broker.setcash(50000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=2)
    # Add a FixedSize sizer according to the stake
    #cerebro.addsizer(bt.sizers.FixedSize, stake=3)

    # Set the commission
    #cerebro.broker.setcommission(commission=0.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    print("LongIn,DifferIn,longExit,DifferExit,atrDays,TradeCount,Winning,Losing,Final Value")
    
    # Run over everything
    cerebro.run()

    # Print out the final result
    #print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Plot the result
    #cerebro.plot(style='bar')