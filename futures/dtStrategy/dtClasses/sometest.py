'''
Created on Sep 26, 2019

@author: I038825
'''
import numpy as np
import pandas as pd
import os.path
import sys
from sklearn.model_selection import TimeSeriesSplit
print("test")

modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
datapath = os.path.join(modpath, '../../../datas/Tindex.csv')
p0 = pd.read_csv(datapath, index_col='datetime', parse_dates=True)
p0.drop("seqno",axis=1, inplace=True)
p0 = p0.dropna()
p0 = p0[p0['volume'] !=0]
    
X = p0
print(X.head(10))
tscv = TimeSeriesSplit(n_splits=5)
print(tscv)  

for train_index, test_index in tscv.split(X):
    print("TRAIN:", train_index, "TEST:", test_index)
    X_train, X_test = X[train_index], X[test_index]
    print(X_train.head(10))