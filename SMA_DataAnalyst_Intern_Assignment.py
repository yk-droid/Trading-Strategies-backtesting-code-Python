#!/usr/bin/env python
# coding: utf-8

# In[84]:


import pandas as pd
import numpy as np
import datetime as dt

import matplotlib.pyplot as plt
plt.style.use('default')
get_ipython().run_line_magic('matplotlib', 'inline')


# In[55]:


df = pd.read_csv("C:\\Users\\2000y\\Downloads\\TRADEBOT_Market_Data.csv")
df


# In[56]:


# parse the time. 
df.DateTime = pd.to_datetime(df.DateTime, format="%m/%d/%Y %H:%M")

#make the time the index. 
df = df.set_index("DateTime")

# group in daily chunks. 
t = df.groupby(pd.Grouper(freq='D')).agg({"Open": "first", 
                                             "Close": "last", 
                                             "Low": "min", 
                                             "High": "max",
                                         "Volume": "sum"})
print(t)


# In[17]:


#Save the daily data to a CSV file
t.to_csv("C:\\Users\\2000y\\Downloads\\daily_metrics.csv")


# In[85]:


# Calculate moving averages
t['MA_7'] = t['Close'].rolling(7, min_periods=2).mean()
t['MA_14'] = t['Close'].rolling(14, min_periods=2).mean()
t['MA_30'] = t['Close'].rolling(30, min_periods=2).mean()
# Calculate daily change
t['% change'] = t['Close'].pct_change() * 100

t['signal'] = 0
t['Trade_points'] = np.nan
t


# In[88]:


#eliminating the first 30 rows

t=t.iloc[30:]


# In[89]:


#backtesting SMA strategy code

pos=0
num=0
percentchange=[]

for i in t.index:

    close=t["Close"][i]
    
    if(t["MA_30"][i] < close):
        print("buy signal")
        t["signal"][i] = 1
        if(pos==0):
            bp=close
            pos=1
            t["Trade_points"][i] = 'entry'
            print("Buying now at "+str(bp))


    elif(t["MA_30"][i] > close):
        print("sell signal")
        t["signal"][i] = 0
        if(pos==1):
            pos=0
            sp=close
            t["Trade_points"][i] = 'exit'
            print("Selling now at "+str(sp))
            pc=(sp/bp-1)*100
            percentchange.append(pc)
    if(num==t["Close"].count()-1 and pos==1):
        pos=0
        sp=close
        print("Selling now at "+str(sp))
        pc=(sp/bp-1)*100
        percentchange.append(pc)

    num+=1


# In[90]:


print(percentchange)


# In[91]:


#summary statistics of the backtested strategy

gains=0
ng=0
losses=0
nl=0
totalR=1

for i in percentchange:
	if(i>0):
		gains+=i
		ng+=1
	else:
		losses+=i
		nl+=1
	totalR=totalR*((i/100)+1)

totalR=round((totalR-1)*100,2)

if(ng>0):
	avgGain=gains/ng
	maxR=str(max(percentchange))
else:
	avgGain=0
	maxR="undefined"

if(nl>0):
	avgLoss=losses/nl
	maxL=str(min(percentchange))
	ratio=str(-avgGain/avgLoss)
else:
	avgLoss=0
	maxL="undefined"
	ratio="inf"

if(ng>0 or nl>0):
	battingAvg=ng/(ng+nl)
else:
	battingAvg=0


# In[92]:


print()
print("Results for given TRADEBOT data" +" going back to "+str(t.index[0])+", Sample size: "+str(ng+nl)+" trades")
print("SMA Period used: 30")
print("Batting Avg: "+ str(battingAvg))
print("Gain/loss ratio: "+ ratio)
print("Average Gain: "+ str(avgGain))
print("Average Loss: "+ str(avgLoss))
print("Max Return: "+ maxR)
print("Max Loss: "+ maxL)
print("Total return over "+str(ng+nl)+ " trades: "+ str(totalR)+"%" )
print()


# In[94]:


#Save the entry, exit data to a CSV file
t.to_csv("C:\\Users\\2000y\\Downloads\\trade_metrics_SMA.csv")
t


# In[ ]:




