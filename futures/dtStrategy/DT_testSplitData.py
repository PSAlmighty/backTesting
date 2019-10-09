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
from backtrader import cerebro

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
    print(stime)
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
    sbname ="T"
    lv_mult = 10000
    lv_cash = 3000000
    startyear = 2009
    endyear = 2018
    starttime = datetime.datetime(startyear, 1, 1)
    daterange = splitDF(p0,3)
    lv_endval = 0
    lv_sharp = 0
    lv_vwr = 0
    lv_return = 0
    lv_sqn = 0
    lv_avgpnl = 0
    lv_win = 0
    lv_loss = 0
    lv_maxdd = 0
    lv_ddtime = 0
    rst = []
    for idx,val in enumerate(daterange):
        if idx == 0:
            continue
        # for every range do the back testing via cebero and save the result in a list
        # save the result and eveluate the performance
        # Create a cerebro entity    
        cerebro = bt.Cerebro(maxcpus=7,tradehistory=True)
        
        cerebro.addstrategy(dtStrategyV12)
        #cerebro.addsizer(maxRiskSizer)
        cerebro.addsizer(bt.sizers.FixedSize, stake=1)
        #cerebro.addanalyzer(btanalyzers.AnnualReturn, _name='annual')    
        # Set the commission
        cerebro.broker.setcommission(leverage=1,mult =lv_mult,commission=0.01)

        tframes = dict(daily=bt.TimeFrame.Days, weekly=bt.TimeFrame.Weeks,
                       monthly=bt.TimeFrame.Months)
           
        data = bt.feeds.PandasData(dataname = p0,fromdate=starttime,
            todate=val,timeframe= bt.TimeFrame.Minutes,compression=1)
        # Add the Data Feed to Cerebro
        cerebro.adddata(data)

        cerebro.resampledata(data, timeframe=tframes["daily"],compression=1)
        # Set our desired cash start
        cerebro.broker.setcash(lv_cash)
        # Run over everything
        cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe')
        cerebro.addanalyzer(btanalyzers.VWR, _name='vwr',timeframe=bt.TimeFrame.Years)
        #cerebro.addanalyzer(btanalyzers.AnnualReturn, _name='annual')
        cerebro.addanalyzer(btanalyzers.Returns, _name='logreturn',timeframe=bt.TimeFrame.Years)
        cerebro.addanalyzer(btanalyzers.SQN, _name='SQN')
        cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='TradeAnalyzer')    
        cerebro.addanalyzer(btanalyzers.Transactions, _name='TXs')
        thestrats = cerebro.run()
        thestrat = thestrats[0]
        # Print out the final result
        lv_endval = cerebro.broker.getvalue()
        lv_sharp = thestrat.analyzers.mysharpe.get_analysis()['sharperatio']
        lv_vwr = thestrat.analyzers.vwr.get_analysis()['vwr']
        lv_return = thestrat.analyzers.logreturn.get_analysis()['rnorm'] 
        lv_sqn =  thestrat.analyzers.SQN.get_analysis()['sqn']
        td =  thestrat.analyzers.TradeAnalyzer.get_analysis()
        lv_cnt = td['total']['total']
        lv_win = td['won']['total']
        lv_avgpnl = td['pnl']['net']['average']
        lv_winavg = td['won']['pnl']['average']
        lv_lossavg = td['lost']['pnl']['average']
        line = [val,lv_endval,lv_sharp,lv_vwr,lv_return,lv_sqn,lv_cnt,lv_win,lv_avgpnl,lv_winavg,lv_lossavg]
        rst.append(line)
    
    mydf = pd.DataFrame(rst,columns = ['Enddate','Endvalue','Sharp','VWR','Logreturn','SQN','Count','wincnt','AvgPnL','AvgWin','AvgLoss'])
    mydf.to_csv("./tempOut/bt/"+sbname+".csv")
    print("Congratulations, succed!")
