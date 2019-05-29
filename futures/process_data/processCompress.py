'''
Created on May 7, 2019

@author: I038825
'''
import pandas as pd
import sys
sb='AP'
df = pd.read_csv("./ps_data/"+sb+"index.csv" ,index_col='datetime',parse_dates=True)
#df = df.reset_index(drop=True)
#df = df.set_index('datetime', drop = True)
conversion = {'open' : 'first', 'high' : 'max', 'low' : 'min', 'close' : 'last', 'volume' : 'sum'}
del df["seqno"]

rsp5m = df.resample('10Min').agg(conversion)
rsp5m = rsp5m.reset_index()
rsp5m = rsp5m.dropna()
rsp5m.to_csv("./ps_data/"+sb+"index_10m.csv")
print(rsp5m.head(10))
sys.exit(0)

df.rename(columns = {'Unnamed: 0':'datetime'}, inplace = True)
df = df.reset_index(drop=True)
print(df.head(100))
df.to_csv("./data/1_002049.XSHE.csv")
sys.exit(0)



del df["Unnamed: 0"]
del df["Unnamed: 0.1"]

df.rename(columns = {'Unnamed: 0.1.1':'datetime'}, inplace = True)
#df = df.set_index('datetime', drop=True, append=False, inplace=False, verify_integrity=False) 
df = df.dropna()
df = df.reset_index(drop=True)
print(df.head(100))
df.to_csv("./data/002049.XSHE.csv")