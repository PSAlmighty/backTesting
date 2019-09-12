'''
Created on Sep 11, 2019

@author: I038825
'''
import pandas as pd
from matplotlib import pyplot as plt


df = pd.read_csv("./datas/orders111.csv",index_col = 0)
df["orderid"] = df.index
df["status"] = 0  # 0 unprocessed 1 matched 2, partial match 
df['closeprice'] = 0
df['pnl'] = 0
df_match = df
#cumcost = 0
cumqty = 0
pal = 0
closeprice = 0
#prevdir = 0
openorder = {}
processed = False
umatchqty = 0
matchorder = []
combinedmatch = {}
for oindex, orow in df.iterrows():
    #print(orow)
    odate = orow['Datetime']
    oprice = orow['price']
    oqty = orow["Position"]
    orderid = orow['orderid']
    processed = False
    if cumqty == 0:
        cumqty = oqty
    elif cumqty * oqty > 0:
        #no point to calculate the average price
        #cumcost = (cumcost * abs(cumqty) + oprice * abs(oqty))/(abs(cumqty)+abs(oqty))
        #cumulate order qty with direction
        cumqty = cumqty + oqty
        #update open order
        openorder[orderid] = orow
    else:
        pass
    if orderid == 411:
        pass#print('abc')
    for mindex, mrow in df_match.iterrows():
        if mrow['orderid'] > 410:
            pass#print('efg')
        if mrow['status'] == 1:
            if mrow['orderid'] == orderid:
                processed = True                
                break
            else:
                continue        
        if orderid == mrow['orderid']:
            continue

        mqty = mrow['Position']
        if mqty * oqty > 0:
            continue
        else:
            pass
        
        if abs(cumqty) == abs(mqty):
            #print('111')
            closeprice = mrow['price']
            closetime = mrow["Datetime"]
            if len(openorder) > 0:
                for okey, oval in openorder.items():
                    pal = (closeprice-oval["price"])*oval['Position']*orow['mult']
                    matched = [oval['orderid'],oval['Datetime'],oval['price'],oval['Position'],closetime,closeprice,pal,mrow['orderid']]
                    matchorder.append(matched)
                    o_index = list(df_match.columns).index('status')
                    df_match.iloc[ oval['orderid'],o_index] = 1                      
            else:
                pal = (closeprice-oprice)*orow['Position']*orow['mult']
                matched = [orderid,odate,oprice,oqty,closetime,closeprice,pal,mrow['orderid']]
                matchorder.append(matched)   
                o_index = list(df_match.columns).index('status')
                df_match.iloc[ oindex,o_index] = 1                             
            d_index = list(df_match.columns).index('status')
            df_match.iloc[ mindex,d_index] = 1
            openorder.clear()
            cumqty = 0
            break
            
        elif abs(cumqty) <= abs(mqty):
            closeprice = mrow['price']
            closetime = mrow["Datetime"]
            if len(openorder) > 0:
                for okey, oval in openorder.items():
                    pal = (closeprice-oval["price"])*oval['Position']*orow['mult']
                    matched = [oval['orderid'],oval['Datetime'],oval['price'],oval['Position'],closetime,closeprice,pal,mrow['orderid']]
                    matchorder.append(matched)
                    o_index = list(df_match.columns).index('status')
                    df_match.iloc[ oval['orderid'],o_index] = 1                      
            else:
                pal = (closeprice-oprice)*orow['Position']*orow['mult']
                #matched = [mrow['orderid'],mrow['Datetime'],oprice,mrow['Position'],closetime,closeprice,pal]
                matched = [orderid,odate,oprice,oqty,closetime,closeprice,pal,mrow['orderid']]
                matchorder.append(matched)       
                o_index = list(df_match.columns).index('status')
                df_match.iloc[ oindex,o_index] = 1                        
            d_index = list(df_match.columns).index('status')
            q_index = list(df_match.columns).index('Position')
            df_match.iloc[ mindex,d_index] = 2     
            if mqty > 0:
                umatchqty = mqty -abs(cumqty)
            else:
                umatchqty = (abs(mqty)-abs(cumqty))*-1
            df_match.iloc[ mindex,q_index] = umatchqty
            openorder.clear()
            cumqty = 0
            break            
        else:
            #should only have few case happy, print the problem and manually check
            print("There is cover qty less than open quantity, need check.")
            print(orderid)
            #print(openorder)
            openorder.clear()
            cumqty = 0
            break              
            
                                
    if processed == True:
        cumqty = 0
        openorder.clear()
        continue        
            
labels = ['OrderID', 'OpenTime', 'OpenPrice', 'OpenPosition','CloseTime','ClosePrice','PnL','CloseOrder']
closedlog = pd.DataFrame.from_records(matchorder, columns=labels)     
print(closedlog)
closedlog.to_csv("./datas/orderpnl.csv")   
    