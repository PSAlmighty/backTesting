import os

fn='DT_TAindex.csv'
fp = "./result_ana/"+fn

with open(fp,'r') as f:
    for (num,value) in enumerate(f):
        if len(value)>50:
            print (num)