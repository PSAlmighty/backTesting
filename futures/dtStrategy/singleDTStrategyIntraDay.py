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
            if atr != None:  
                riskFactor = atr * comminfo.p.mult * 2
                size = math.floor((totalval  * self.p.risk) / riskFactor)
                return size
            else:
                return 0
        else:
            return position.size


# Create a Stratey
class DTStrategy01(bt.Strategy):
    params = (
        ('ordersize', 1),
        ('k',2 ),
        ('differ',1 ),
        ('rangeDays',10 )
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
        print('%.2f,%.2f,%.2f,%.2f,,%2d,%2d,%.2f' %
                 (self.params.k,self.params.differ,self.params.rangeDays, self.tradeCount,self.winCount,self.loseCount,self.broker.getvalue()))


def pretty(d, indent=0):
    for key, value in d.items():
        if isinstance(value, dict):
            print ('\t' * indent + (("%10s: {\n") % str(key).upper()))
            pretty(value, indent+1)
            print ('\t' * indent + ' ' * 12 + ('} # %s #\n' % str(key).upper()))
        elif isinstance(value, list):
            for val in value:
                print ('\t' * indent + (("%30s: [\n") % str(key).upper()))
                pretty(val, indent+1)
                print ('\t' * indent + ' ' * 12 + ('] # %s #\n' % str(key).upper()))
        else:
            print ('\t' * indent + (("%10s: %s") % (str(key).upper(),str(value))))

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro(maxcpus=6,tradehistory=True)
        
    cerebro.addstrategy(DTStrategy01)
    cerebro.addsizer(maxRiskSizer)
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe')
    cerebro.addanalyzer(btanalyzers.AnnualReturn, _name='annual')    
    # Set the commission
    cerebro.broker.setcommission(leverage=1,mult =10,commission=0.01)
    #cerebro.broker.setcommission(commission=0.0)
    # Add a strategy
    #cerebro.addstrategy(DTStrategy01)
    #cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe')
    #cerebro.addanalyzer(btanalyzers.AnnualReturn, _name='annual')
   
    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '../../datas/rbindex.csv')

    tframes = dict(daily=bt.TimeFrame.Days, weekly=bt.TimeFrame.Weeks,
                   monthly=bt.TimeFrame.Months)
    

    
    #print(datapath)
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
    p0 = p0.dropna()
    #print(p0)
    data = bt.feeds.PandasData(dataname = p0,fromdate=datetime.datetime(2009, 1, 2),
        todate=datetime.datetime(2019, 6, 1),
        timeframe= bt.TimeFrame.Minutes,
        compression=1)
    

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    cerebro.resampledata(data, timeframe=tframes["daily"],compression=1)

    #cerebro.resampledata(data, timeframe=tframes["daily"],compression=1)

    # Set our desired cash start
    cerebro.broker.setcash(300000.0)

    # Add a FixedSize sizer according to the stake
    #cerebro.addsizer(bt.sizers.FixedSize, stake=3)

    # Set the commission
    #cerebro.broker.setcommission(commission=0.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    print('P1,P2,P3,TradeCount,Winning,Losing,Final Value')
    # Run over everything
    # Run over everything
    cerebro.addanalyzer(btanalyzers.VWR, _name='vwr',timeframe=bt.TimeFrame.Years)
    #cerebro.addanalyzer(btanalyzers.AnnualReturn, _name='annual')
    cerebro.addanalyzer(btanalyzers.Returns, _name='logreturn',timeframe=bt.TimeFrame.Years)
    cerebro.addanalyzer(btanalyzers.SQN, _name='SQN')
    cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='TradeAnalyzer')    
    cerebro.addanalyzer(btanalyzers.Transactions, _name='TXs')
    thestrats = cerebro.run()
    thestrat = thestrats[0]
    # Print out the final result

    # Plot the result
    #cerebro.plot(style='bar')
    #cerebro.report('./outPDF')
    print('VWR:', thestrat.analyzers.vwr.get_analysis()) 
    print('logreturn:',  thestrat.analyzers.logreturn.get_analysis()) 
    print('Anual Ratio:',  thestrat.analyzers.SQN.get_analysis()) 
    print('Anual Ratio:',  thestrat.analyzers.TradeAnalyzer.get_analysis()) 
    tempDict=thestrat.analyzers.TXs.get_analysis()
    orderList = []
    
    for key in tempDict:
        #print(tempDict[key])
        #sys.exit(0)
        line = [key,tempDict[key][0][0],tempDict[key][0][1]]
        orderList.append(line )
    
    print(orderList)    
    dt = [i[0] for i in orderList]
    position = [i[1] for i in orderList]
    price = [i[2] for i in orderList]
    tempDict = {'Datetime':dt,'Position':position,'price':price}
    cntDF = pd.DataFrame(tempDict)     
    cntDF.to_csv("./tempOut/orders.csv")
    tradedict = thestrat.analyzers.TradeAnalyzer.get_analysis()
    print("below is for trade")

    tradeAnalyzer = thestrat.analyzers.getbyname('TradeAnalyzer')  
    print(tradeAnalyzer)           
    pretty(tradeAnalyzer.get_analysis())
    #trades = [str(trade).splitlines() for trade in (thestrat._trades.values())[0][0]]
    #print(trades)
    #td = thestrat._trades.values()
    
    ddd =  thestrat._trades
    for key, value in ddd.items():
        print(key,value)
        for kk,vv in value.items():
            print(kk,vv)
            td = vv
        
    #print(td)
    pnl = []
    for value in td:
        if value.status == 2:
            pnl.append(value.pnlcomm)
    df = pd.DataFrame(pnl,columns = ["pnl"])
    df.to_csv("./pnl.csv")
    #print(td)
    #print(cntDF  )       