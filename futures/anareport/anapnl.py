'''
Created on Sep 10, 2019

@author: I038825
'''
import pandas as pd
from matplotlib import pyplot as plt

df = pd.read_csv("./datas/pnl.csv")
df["zeros"] = 0
df["std"] = df['pnl']/df['pnl'].std()
ax = df.plot.scatter(x = 0,y='pnl')
df.plot.line(x=0, y='zeros', ax=ax)
plt.show()

ax1 = df.plot.scatter(x = 0,y = 'std')
plt.show()