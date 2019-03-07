from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt


# Create a Stratey
class TurtleStrategy01(bt.Strategy):
    params = (
        ('maperiod', 5),
        ('longIN',20 ),
        ('shortIN',20 ),
        ('longExit',10 ),
        ('shortExit',10 ),
        ('atrDays',20 ),
        ('atrNo',2)
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

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
            self.datas[1],period=self.params.shortIN)
        self.longExit = bt.indicators.Lowest(
            self.datas[1], period=self.params.longExit)

        self.shortExit = bt.indicators.Highest(
            self.datas[1], period=self.params.shortExit)
        
        
        self.atrValue = bt.indicators.ATR(
            self.datas[1], period=self.params.atrDays, plot=False)
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[1], period=self.params.maperiod)
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
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                self.bar_executed = len(self)
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

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
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.log('Long Entry, %.2f' % self.longEntry[0])
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()
                self.entryNo += 1
                self.lastEntryPrice = self.dataclose[0]
                self.entryAtr = self.atrValue[0]
            
            elif self.dataclose[0] < self.shortEntry[0]:
                self.log('Short Create, %.2f'% self.dataclose[0])
                self.order =self.sell()
                self.entryNo += 1
                self.lastEntryPrice = self.dataclose[0]     
                self.entryAtr = self.atrValue[0]           
            
        else:
            if self.position > 0 :
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
                    self.log('BUY CREATE, %.2f' % self.dataclose[0])
    
                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.buy()
                    self.entryNo += 1
                    self.lastEntryPrice = self.dataclose[0]                    
                elif self.entryNo ==2 and self.lastEntryPrice >  0 \
                    and self.dataclose[0] > self.lastEntryPrice + 0.5*self.entryAtr:

                    self.log('BUY CREATE, %.2f' % self.dataclose[0])
    
                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.buy()
                    self.entryNo += 1
                    self.lastEntryPrice = self.dataclose[0]  
                elif self.dataclose[0] < self.exitPrice:
                    self.close()
                else:
                    pass
            else:
                if self.position < 0 :
                    if self.lastEntryPrice + 2* self.entryAtr < self.shortExit[0]:
                        self.exitPrice = self.lastEntryPrice + 2* self.entryAtr
                    else:
                        self.exitPrice = self.shortExit[0]
                    if self.entryNo ==1 and self.lastEntryPrice >  0 \
                        and self.dataclose[0] < self.lastEntryPrice - self.entryAtr:
                        self.log('SELL CREATE, %.2f' % self.dataclose[0])
        
                        # Keep track of the created order to avoid a 2nd order
                        self.order = self.sell()
                        self.entryNo += 1
                        self.lastEntryPrice = self.dataclose[0]                    
                    elif self.entryNo ==2 and self.lastEntryPrice >  0 \
                        and self.dataclose[0] < self.lastEntryPrice - 0.5*self.entryAtr:
    
                        self.log('SELL CREATE, %.2f' % self.dataclose[0])
        
                        # Keep track of the created order to avoid a 2nd order
                        self.order = self.sell()
                        self.entryNo += 1
                        self.lastEntryPrice = self.dataclose[0]  
                    elif self.dataclose[0] > self.exitPrice:
                        self.close()
                    else:
                        pass                
  
    def stop(self):
        #check why log does not work.use print first 
        print('(Long Entry Period %2d , Short Entry Period %2d) Ending Value %.2f' %(self.params.longIN,self.params.shortIN, self.broker.getvalue()))


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    #cerebro.addstrategy(TurtleStrategy01)   
    
    strats = cerebro.optstrategy(
        TurtleStrategy01,
        maperiod=5,
        longIN=xrange(18, 21),
        shortIN=xrange(18, 21),
        longExit=10,
        shortExit=10,
        atrDays=20,  
        atrNo=2                                            
        )    

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, './datas/test1Minnew.csv')

    tframes = dict(daily=bt.TimeFrame.Days, weekly=bt.TimeFrame.Weeks,
                   monthly=bt.TimeFrame.Months)
    # Create a Data Feed
    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        datetime=9,
        fromdate=datetime.datetime(2006, 01, 02),
        todate=datetime.datetime(2006, 03, 01),
        timeframe= bt.TimeFrame.Minutes,
        compression=1,
        dtformat=('%Y-%m-%d %H:%M:%S'),
        open=3,
        high=4,
        low=5,
        close=6,
        volume=7,
        openinterest=8)



    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    cerebro.resampledata(data, timeframe=tframes["daily"],compression=1)

    # Set our desired cash start
    cerebro.broker.setcash(20000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Plot the result
    #cerebro.plot(style='bar')