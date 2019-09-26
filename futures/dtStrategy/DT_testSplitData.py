from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import backtrader as bt
import backtrader.analyzers as btanalyzers
import time
import pandas as pd
import backtrader.analyzers as btanalyzers
from dtClasses.dtStrategyV12 import maxRiskSizer,dtStrategyV12
from sqlalchemy.dialects.postgresql.ranges import DATERANGE

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
def splitDF(df,itv):
    stime = df.index.min()
    etime = df.index.max()
    endlist = list(date_range(stime,etime,itv))
    print(endlist)
    return endlist
    
#got from stackoverflow, works as charm :-)
def date_range(start, end, intv):
    start = start.replace(hour=0, minute=0, second=0, microsecond=0) 
    end = end.replace(hour=0, minute=0, second=0, microsecond=0) 
    diff = (end  - start ) / intv
    for i in range(intv):
        yield (start + diff * i).replace(hour=0, minute=0, second=0, microsecond=0) 
    yield end.replace(hour=0, minute=0, second=0, microsecond=0) 
    
if __name__ == '__main__':    
    #read K line data and split
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '../../datas/Tindex.csv')
    p0 = pd.read_csv(datapath, index_col='datetime', parse_dates=True)
    p0.drop("seqno",axis=1, inplace=True)
    p0 = p0.dropna()
    p0 = p0[p0['volume'] !=0]
    daterange = splitDF(p0,3)
    for d in DATERANGE:
        pass
        # for every range do the back testing via cebero and save the result in a list
        # save the result and eveluate the performance
    
    sys.exit(0)
    
    
    # Create a cerebro entity
    lv_mult = 10
    cerebro = bt.Cerebro(maxcpus=6,tradehistory=True)
        
    cerebro.addstrategy(dtStrategyV12)
    cerebro.addsizer(maxRiskSizer)
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe')
    cerebro.addanalyzer(btanalyzers.AnnualReturn, _name='annual')    
    # Set the commission
    cerebro.broker.setcommission(leverage=1,mult =lv_mult,commission=0.01)
    #cerebro.broker.setcommission(commission=0.0)
    # Add a strategy
    #cerebro.addstrategy(DTStrategy01)
    #cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe')
    #cerebro.addanalyzer(btanalyzers.AnnualReturn, _name='annual')
   
    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere

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

    #print(p0)
    startyear = 2017
    endyear = 2018
    sbname ="T"
    data = bt.feeds.PandasData(dataname = p0,fromdate=datetime.datetime(startyear, 3, 2),
        todate=datetime.datetime(endyear, 3, 1),
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
    
    #dfdf = pd.DataFrame.from_records(tempDict[0],columns=['ABCDE'])
    #dfdf.to_csv("./tempOut/test.csv")
    
    for key in tempDict:
        #print(tempDict[key])
        #sys.exit(0)
        line = [key,tempDict[key][0][0],tempDict[key][0][1]]
        orderList.append(line )
    
    #print(orderList)    
    dt = [i[0] for i in orderList]
    position = [i[1] for i in orderList]
    price = [i[2] for i in orderList]
    tempDict = {'Datetime':dt,'Position':position,'price':price}
    cntDF = pd.DataFrame(tempDict)  
    cntDF['mult'] = lv_mult   
    cntDF.to_csv("./tempOut/orders"+str(endyear)+".csv")
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
    df.to_csv("./pnl/"+sbname+"_pnl"+str(endyear)+".csv")
    #print(td)
    #print(cntDF  )       