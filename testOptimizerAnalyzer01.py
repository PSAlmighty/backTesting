'''
Author: www.backtest-rookies.com

MIT License

Copyright (c) 2017 backtest-rookies.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import backtrader as bt
from datetime import datetime
import backtrader.analyzers as btanalyzers
class firstStrategy(bt.Strategy):
    params = (
        ('period',21),
        )

    def __init__(self):
        self.startcash = self.broker.getvalue()
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=self.params.period)

    def next(self):
        if not self.position:
            if self.rsi < 30:
                self.buy(size=100)
        else:
            if self.rsi > 70:
                self.sell(size=100)

if __name__ == '__main__':
    #Variable for our starting cash
    startcash = 10000

    #Create an instance of cerebro
    cerebro = bt.Cerebro(optreturn=False)

    #Add our strategy
    cerebro.optstrategy(firstStrategy, period=range(14,21))
    cerebro.addanalyzer(btanalyzers.DrawDown, _name='myDrawDown')
    #Get Apple data from Yahoo Finance.
    data = bt.feeds.YahooFinanceData(
        dataname='AAPL',
        fromdate = datetime(2016,1,1),
        todate = datetime(2017,1,1),
        buffered= True
        )


    #Add the data to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(startcash)

    # Run over everything
    opt_runs = cerebro.run()
    #thestrats = cerebro.run()
    
    #print(opt_runs[0].analyzers.mySharpeRatio.get_analysis())
    # Generate results list
    final_results_list = []
    for run in opt_runs:
        for strategy in run:
            value = round(strategy.broker.get_value(),2)
            PnL = round(value - startcash,2)
            period = strategy.params.period
            drawDown = strategy.analyzers.myDrawDown.get_analysis()
            final_results_list.append([period,PnL,drawDown])

    #Sort Results List
    by_drawDown = sorted(final_results_list, key=lambda x: x[2])
    by_PnL = sorted(final_results_list, key=lambda x: x[1], reverse=True)

    #Print results
    print('Results: Ordered by period:')
    for result in by_drawDown:
        print('Period: {}, PnL: {},DrawDown:{}'.format(result[0], result[1],result[2]))
    print('Results: Ordered by Profit:')
    for result in by_PnL:
        print('Period: {}, PnL: {},DrawDown:{}'.format(result[0], result[1],result[2]))