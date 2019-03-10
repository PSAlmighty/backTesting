from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
import backtrader.analyzers as btanalyzers
#from btreport.report import Cerebro

# Create a Stratey
class DTStrategy01(bt.Strategy):
    params = (
        ('maperiod', 5),
        ('k1',0.5 ),
        ('k2',0.5 ),
        ('rangeDays',6 )
    )
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low        
        self.rgHigh = bt.indicators.Highest(self.datas[0].high,period=self.params.rangeDays)
        self.rgLow = bt.indicators.Lowest(self.datas[0].low,period=self.params.rangeDays)
        self.closeHigh = bt.indicators.Highest(self.datas[0].close,period=self.params.rangeDays)    
        self.closeLow = bt.indicators.Lowest(self.datas[0].close,period=self.params.rangeDays)
        
        self.range1 = self.rgHigh - self.closeLow
        self.range2 = self.closeHigh-self.rgLow
        

                    
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.entryprice = None
        self.buycomm = None
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
        self.longIn = 0
        self.shortIn = 0
        self.theRange = 0
        if self.range1[-1] > self.range2[-1]:
            self.theRange = self.range1[-1]
        else:
            self.theRange = self.range2[-1]
            
        
        self.longIn = self.dataopen[0] + self.params.k1*self.theRange
        self.shortIn = self.dataopen[0]-self.params.k2*self.theRange
        # Check if we are in the market
        if not self.position:
            
            # Not yet ... we MIGHT BUY if ...
            if self.datahigh[0] > self.longIn:

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.longIn)
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy(price=self.longIn)

            
            elif self.datalow[0] < self.shortIn:
                self.log('Short Create, %.2f'% self.shortIn)
                self.order =self.sell(price=self.shortIn)         
            
        elif self.position > 0 :

            #self.log('Exit Entry, %.2f'% self.exitPrice) 
            #self.log('Long Exit, %.2f'% self.longExit[0])                 
            #self.log('Last Entry, %.2f'% self.lastEntryPrice)
            #self.log('Entry ATR, %.2f'% self.entryAtr)                                                      
            if self.datalow[0] < self.shortIn:
                self.log('Cover CREATE, %.2f' % ( self.shortIn))

                # Keep track of the created order to avoid a 2nd order
                #self.order = self.close(price=self.datalow[0] < self.shortIn)
                self.order = self.sell(price = self.shortIn)  
                #self.order_target_size(size )               
            else:
                pass

        elif self.position < 0 :
                
                if self.datahigh[0] > self.longIn:
                    self.log('Buy CREATE, %.2f' % (self.longIn))
                    self.order = self.buy(price = self.longIn)
           
                else:
                    pass
        else:
            pass              
    def stop(self):
        print('(MA Period %2d) Ending Value %.2f' %
                 (self.params.maperiod, self.broker.getvalue()))


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()


    # Add a strategy
    cerebro.addstrategy(DTStrategy01)
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe')
    cerebro.addanalyzer(btanalyzers.AnnualReturn, _name='annual')
   
    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, './datas/orcl-1995-2014.txt')

    # Create a Data Feed
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # Do not pass values before this date
        fromdate=datetime.datetime(1995, 1, 1),
        # Do not pass values before this date
        todate=datetime.datetime(2005, 5, 31),
        # Do not pass values after this date
        reverse=False)
    '''
    data = bt.feeds.PandasData(dataname = p0,fromdate=datetime.datetime(2006, 01, 02),
        todate=datetime.datetime(2006, 02, 01),
        timeframe= bt.TimeFrame.Minutes,
        compression=1)
    '''

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    #cerebro.resampledata(data, timeframe=tframes["daily"],compression=1)

    # Set our desired cash start
    cerebro.broker.setcash(20000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=1000)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    thestrats = cerebro.run()
    thestrat = thestrats[0]
    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Plot the result
    cerebro.plot(style='bar')
    #cerebro.report('./outPDF')
    print('Sharpe Ratio:', thestrat.analyzers.mysharpe.get_analysis()) 
    print('Anual Ratio:',  thestrat.analyzers.annual.get_analysis()) 
    
      