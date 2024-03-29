from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
import backtrader.analyzers as btanalyzers
import time
import pandas as pd
#from btreport.report import Cerebro

# Create a Stratey
class DTStrategy01(bt.Strategy):
    params = (
        ('ordersize', 1),
        ('k',0.6 ),
        ('differ',0 ),
        ('rangeDays',6 )
    )
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        print('P1,P2,P3,Final Value')
        self.tradeCount = 0
        self.winCount = 0
        self.loseCount = 0        
        self.orderSize = self.params.ordersize
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        #self.date1 = self.datas[0].datetime.date
        #self.dayclose = self.datas[0].close
        #self.dayopen = self.datas[0].open
        #self.dayhigh = self.datas[0].high
        #self.daylow = self.datas[0].low        
        self.rgHigh = bt.indicators.Highest(self.datas[1].high,period=self.params.rangeDays)
        self.rgLow = bt.indicators.Lowest(self.datas[1].low,period=self.params.rangeDays)
        self.closeHigh = bt.indicators.Highest(self.datas[1].close,period=self.params.rangeDays)    
        self.closeLow = bt.indicators.Lowest(self.datas[1].close,period=self.params.rangeDays)
        
        self.range1 = abs(self.rgHigh - self.closeLow)
        self.range2 = abs(self.closeHigh-self.rgLow)
        

                    
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.entryprice = None
        self.buycomm = None
        self.todayOpen = 0
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
            self.tradeCount += 1

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))
        if trade.pnl > 0:
            self.winCount += 1
        else:
            self.loseCount += 1
    def next(self):

        # Simply log the closing price of the series from the reference
        #self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        #print("test")
        #print(self.datas[0].datetime[0].date)
        
        if self.order:
            return
        
        if self.datas[0].datetime.date(0) != self.datas[0].datetime.date(-1):
            self.todayOpen = self.datas[0].open[0]
        
        if self.todayOpen == 0:
            return
           
        self.longIn = 0
        self.shortIn = 0
        self.theRange = 0
        if self.range1[0] > self.range2[0]:
            self.theRange = self.range1[0]
        else:
            self.theRange = self.range2[0]
            
        
        self.longIn  = self.todayOpen + self.params.k*self.theRange
        self.shortIn = self.todayOpen - (self.params.k+self.params.differ)*self.theRange
        
        '''
        if len(self)%200 == 0:
            print(self.rgHigh[0],self.rgHigh[-1],self.rgHigh[-2],self.rgHigh[-3])
            print(self.closeLow[0],self.closeLow[-1],self.closeLow[-2],self.closeLow[-3])            
            print(self.range1[0],self.range1[-1],self.range1[-2],self.range1[-3])         
        '''
        # Check if we are in the market
        if not self.position:
            if len(self)%300 == 0:
                print('no position')            
            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] > self.longIn:

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                # Keep track of the created order to avoid a 2nd order
                self.order = self.order_target_size(target=self.orderSize)

            
            elif self.dataclose[0] < self.shortIn:
                self.log('Short Create, %.2f'% self.dataclose[0])
                self.order =self.order_target_size(target=-1*self.orderSize)         
            
        elif self.position.size > 0 :
            if len(self)%300 == 0:
                pass
                #print("long")
                #print(self.getposition())

            #self.log('Exit Entry, %.2f'% self.exitPrice) 
            #self.log('Long Exit, %.2f'% self.longExit[0])                 
            #self.log('Last Entry, %.2f'% self.lastEntryPrice)
            #self.log('Entry ATR, %.2f'% self.entryAtr)                                                      
            if self.dataclose[0] < self.shortIn:
                self.log('Cover CREATE, %.2f' % ( self.dataclose[0]))

                # Keep track of the created order to avoid a 2nd order
                #self.order = self.close(price=self.datalow[0] < self.shortIn)
                self.order = self.order_target_size(target=-1*self.orderSize)
                #self.order_target_size(size )               
            else:
                pass

        elif self.position.size < 0 :
            if len(self)%300 == 0:
                pass
                #print('short')
                #print(self.getposition())
                
            if self.dataclose[0] > self.longIn:
                self.log('Buy CREATE, %.2f' % (self.dataclose[0]))
                self.order = self.order_target_size(target=self.orderSize)
       
            else:
                pass
        else:
            pass              
    def stop(self):
        print('%.2f,%.2f,%.2f,%.2f,,%2d,%2d,%.2f' %
                 (self.params.k,self.params.differ,self.params.rangeDays, self.tradeCount,self.winCount,self.loseCount,self.broker.getvalue()))



if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()
    
    # Set the commission
    cerebro.broker.setcommission(leverage=1,mult =5,commission=0.002)
    #cerebro.broker.setcommission(commission=0.0)
    # Add a strategy
    cerebro.addstrategy(DTStrategy01)
    #cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe')
    #cerebro.addanalyzer(btanalyzers.AnnualReturn, _name='annual')
   
    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, './datas/SMindex_10m.csv')

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
        todate=datetime.datetime(2019, 6, 1),
        timeframe= bt.TimeFrame.Minutes,
        compression=10)
    

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    cerebro.resampledata(data, timeframe=tframes["daily"],compression=1)

    #cerebro.resampledata(data, timeframe=tframes["daily"],compression=1)

    # Set our desired cash start
    cerebro.broker.setcash(150000.0)

    # Add a FixedSize sizer according to the stake
    #cerebro.addsizer(bt.sizers.FixedSize, stake=3)

    # Set the commission
    #cerebro.broker.setcommission(commission=0.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    print('P1,P2,P3,TradeCount,Winning,Losing,Final Value')
    # Run over everything
    thestrats = cerebro.run()
    thestrat = thestrats[0]
    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Plot the result
    #cerebro.plot(style='bar')
    #cerebro.report('./outPDF')
    #print('Sharpe Ratio:', thestrat.analyzers.mysharpe.get_analysis()) 
    #print('Anual Ratio:',  thestrat.analyzers.annual.get_analysis()) 
    
      