'''
Created on Oct 17, 2019

@author: I038825
'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from audioop import avg

def split_line(text,idx):
    l = [word for word in text.split(",")]
    return l[idx]
lv_path = "./datas/I.csv"

df = pd.read_csv(lv_path,index_col = 0)
df = df[df["Count"]>8]
df = df[df["Count"]<400]
df = df[df["Sharp"]<8]
print(df)
#tempdf = df["TimeGroup"]
tempdf= pd.DataFrame()
tempdf["TimeGroup"] = df["TimeGroup"]
tempdf["KValue"] = df["KValue"]
tempdf["DValue"] = df["DValue"]

df.drop("Enddate",axis=1, inplace=True)

df.drop("TimeGroup",axis=1, inplace=True)
#[0]
#df["d"] = df["Parameters"].map(split_line)[1]
#df["r"] = df["Paramet4ers"].map(split_line)[2]
#df["k"] = tempdf["KValue"]
#df["d"] = tempdf["DValue"]
df1 = df.groupby(["KValue","DValue"]).mean()
df1.to_csv("./datas/score_org.csv")
df.drop("KValue",axis=1, inplace=True)
df.drop("DValue",axis=1, inplace=True)
df_norm = (df - df.mean())/df.std()
print(df_norm)
df_norm["k"] = tempdf["KValue"]
df_norm["d"] = tempdf["DValue"]
df_norm["TimeGroup"] = tempdf["TimeGroup"]
df_new = df_norm.groupby(["k","d"]).mean()
df_new["score"] = (df_new["Sharp"] *1.5 + df_new["VWR"] *1 + df_new["SQN"]*1 + df_new["Logreturn"]*1)/4.5
#df_new = df_new.stack()
df_new.to_csv("./datas/score.csv")

#dfavg = df.groupby("TimeGroup").mean()
