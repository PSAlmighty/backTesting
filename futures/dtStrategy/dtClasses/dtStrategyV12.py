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
import backtrader.analyzers as btanalyzers
import math

# Create a Sizer
class maxRiskSizer(bt.Sizer):
    '''
    Returns the number of shares rounded down that can be purchased for the
    max rish tolerance
    '''
    params = (('risk', 0.01),)

    def __init__(self):
        if self.p.risk > 1 or self.p.risk < 0:
            raise ValueError('The risk parameter is a percentage which must be'
                'entered as a float. e.g. 0.5')
        #self._atr = self.strategy.

    def _getsizing(self, comminfo, cash, data, isbuy):
        
        position = self.broker.getposition(data)
        if not position:
            totalval = self.strategy.broker.get_value()
            atr = self.strategy.atrValue[0]
            #print(atr)
            if atr != None:  
                riskFactor = atr * comminfo.p.mult * 2
                size = math.floor((totalval  * self.p.risk) / riskFactor)
                return size
            else:
                return 0
        else:
            return position.size
    def _getsizing1(self, comminfo, cash, data, isbuy):
        
        position = self.broker.getposition(data)
        
        totalval = self.strategy.broker.get_value()
        atr = self.strategy.atrValue[0]
        if atr != None:  
            riskFactor = atr * comminfo.p.mult * 2
            size = math.floor((totalval  * self.p.risk) / riskFactor)
            return size
        else:
            return 0


# Create a Stratey
class dtStrategyV12(bt.Strategy):
    params = (
        ('ordersize', 1),
        ('k',5 ),
        ('differ',0 ),
        ('rangeDays',6 )
    )
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.tradeCount = 0
        self.winCount = 0
        self.loseCount = 0 
                       

        self.orderSize = self.params.ordersize   
        #self.getsizing(self,self.datas)
        #self.params.ordersize
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        #self.date1 = self.datas[0].datetime.date
        #self.dayclose = self.datas[0].close
        #self.dayopen = self.datas[0].open
        #self.dayhigh = self.datas[0].high
        #self.daylow = self.datas[0].low  
        self.atrValue = bt.indicators.ATR(self.datas[1], period=20, plot=False)      
        self.rgHigh = bt.indicators.Highest(self.datas[1].high,period=self.params.rangeDays)
        self.rgLow = bt.indicators.Lowest(self.datas[1].low,period=self.params.rangeDays)
        self.closeHigh = bt.indicators.Highest(self.datas[1].close,period=self.params.rangeDays)    
        self.closeLow = bt.indicators.Lowest(self.datas[1].close,period=self.params.rangeDays)
        
        self.range1 = abs(self.rgHigh - self.closeLow)
        self.range2 = abs(self.closeHigh-self.rgLow)
        self.theK1 = self.params.k/10
        self.theK2 = (self.params.k+ self.params.differ)/10
        

                    
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.entryprice = None
        self.buycomm = None
        self.todayOpen = 0

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                ####self.log(
                ####    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                ####    (order.executed.price,
                ####     order.executed.value,
                ####     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                self.bar_executed = len(self)
            else:  # Sell
                ####self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                ####         (order.executed.price,
                ####          order.executed.value,
                ####          order.executed.comm))
                pass

            self.bar_executed = len(self)
            self.tradeCount += 1

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            ####self.log('Order Canceled/Margin/Rejected')
            pass

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        ####self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
        ####         (trade.pnl, trade.pnlcomm))
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
           
        #print(self.todayOpen)
        self.longIn = 0
        self.shortIn = 0
        self.theRange = 0
        if self.range1[0] > self.range2[0]:
            self.theRange = self.range1[0]
        else:
            self.theRange = self.range2[0]
            
        
        self.longIn  = self.todayOpen + self.theK1*self.theRange
        self.shortIn = self.todayOpen - self.theK2*self.theRange
        
        '''
        if len(self)%200 == 0:
            print(self.rgHigh[0],self.rgHigh[-1],self.rgHigh[-2],self.rgHigh[-3])
            print(self.closeLow[0],self.closeLow[-1],self.closeLow[-2],self.closeLow[-3])            
            print(self.range1[0],self.range1[-1],self.range1[-2],self.range1[-3])         
        '''
        # Check if we are in the market
        if not self.position:
            if len(self)%300 == 0:
                pass
                ####print('no position')            
            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] > self.longIn:

                # BUY, BUY, BUY!!! (with all possible default parameters)
                ####self.log('BUY CREATE, %.2f' % self.dataclose[0])
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

            
            elif self.dataclose[0] < self.shortIn:
                ####self.log('Short Create, %.2f'% self.dataclose[0])
                self.order =self.sell()         
            
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
                ####self.log('Cover CREATE, %.2f' % ( self.dataclose[0]))

                # Keep track of the created order to avoid a 2nd order
                #self.order = self.close(price=self.datalow[0] < self.shortIn)
                self.order = self.sell()
                #self.order_target_size(size )               
            else:
                pass

        elif self.position.size < 0 :
            if len(self)%300 == 0:
                pass
                #print('short')
                #print(self.getposition())
                
            if self.dataclose[0] > self.longIn:
                ####self.log('Buy CREATE, %.2f' % (self.dataclose[0]))
                self.order = self.buy()
       
            else:
                pass
        else:
            pass              
    def stop(self):
        pass
        #print('%.2f,%.2f,%.2f,%.2f,,%2d,%2d,%.2f' %
        #         (self.params.k,self.params.differ,self.params.rangeDays, self.tradeCount,self.winCount,self.loseCount,self.broker.getvalue()))


