'''
Created on Oct 14, 2019

@author: I038825
Reference: https://ntguardian.wordpress.com/2017/06/12/getting-started-with-backtrader/
'''
import backtrader as bt
#import backtrader.analyzers as btanalyzers
class AcctStats(bt.Analyzer):
    """A simple analyzer that gets the gain in the value of the account; should be self-explanatory"""
 
    def __init__(self):
        self.start_val = self.strategy.broker.get_value()
        self.end_val = None
 
    def stop(self):
        self.end_val = self.strategy.broker.get_value()
 
    def get_analysis(self):
        return {"start": self.start_val, "end": self.end_val,
                "growth": self.end_val - self.start_val, "return": self.end_val / self.start_val}
