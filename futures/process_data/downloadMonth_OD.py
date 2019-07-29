'''
Created on Jun 6, 2019

@author: I038825
'''
import jqdatasdk as jqd
import pandas as pd
import numpy as np
import sys



jqd.auth("18621861857", "P4ssword")

#symbollist = [ "SM1905.XZCE","J1905.XDCE","ZC1905.XZCE","I1905.XDCE","SF1905.XZCE","T8888.CCFX","RB1905.XSGE","JM1905.XDCE","TA1905.XZCE","HC1905.XSGE","MA1905.XZCE","RU1905.XSGE","AP1905.XZCE","JD1905.XDCE","PP1905.XDCE","AL8888.XSGE","SR1905.XZCE","NI1905.XSGE","CF1905.XZCE","EG1905.XDCE","CJ1905.XZCE"]
#symbollist = [ "SM1901.XZCE","J1901.XDCE","ZC1901.XZCE","I1901.XDCE","SF1901.XZCE","RB1901.XSGE","JM1901.XDCE","TA1901.XZCE","HC1901.XSGE","MA1901.XZCE","RU1901.XSGE","AP1901.XZCE","JD1901.XDCE","PP1901.XDCE","SR1901.XZCE","NI1901.XSGE","CF1901.XZCE","EG1901.XDCE","CJ1901.XZCE"]
#symbollist = [ "SM1809.XZCE","J1809.XDCE","ZC1809.XZCE","I1809.XDCE","SF1809.XZCE","RB1810.XSGE","JM1809.XDCE","TA1809.XZCE","HC1810.XSGE","MA1809.XZCE","RU1809.XSGE","AP1810.XZCE","JD1809.XDCE","PP1809.XDCE","SR1809.XZCE","NI1809.XSGE","CF1809.XZCE","EG1809.XDCE","CJ1809.XZCE"]
symbollist = ["T1903.CCFX",]

filepre = "./futurescontracts/"
for sb in symbollist:
    fname = filepre+sb[:-5] +".csv"
    print(fname)   
    tempDF = jqd.get_price(sb, start_date='2018-01-01', end_date='2019-07-01', frequency='1m',fields=['open','close','high','low','volume']) # 获得IC1506.CCFX的分钟数据, 只获取open+close字段
    tempDF.to_csv(fname)
        
