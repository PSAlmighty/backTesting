from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import pandas as pd


filename = "/home/leon/backTraderFolder/backTestFolder/backTesting/datas/test1Minnew.csv"
org = pd.read_csv(filename,parse_dates=['datetime'])

columns  = ["datetime","open","high","low","close","volume","openInterest"]

org = org[columns]
#org["hours"] = org["Datetime"].hour

def funcTime(datetimeX):
    hourDelta = 0
    
    calcTime = datetimeX
    
    if datetimeX.weekday() == 4:
        hourDelta = 52
    else:
        hourDelta = 4
        
    if datetimeX.hour >=21 or datetimeX.hour <= 8:
        calcTime = datetimeX + pd.DateOffset(hours=hourDelta)
    return calcTime    

org["datetime"] = org["datetime"].apply(lambda x: funcTime(x) )
#org["hs"] = org["Datetime"].apply(lambda x :x.hour)
print(org.head())

org.to_csv("opt.csv")
