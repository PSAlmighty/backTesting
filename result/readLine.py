import os

fn='TT_HCindex_0520_2.csv'
fp = "./result_ana/"+fn

with open(fp,'r') as f:
    for (num,value) in enumerate(f):
        if len(value)>40:
            print (num)