#!/usr/bin/env python
# coding: utf-8

# In[130]:


import pandas as pd
import numpy as np
import datetime as dt

import matplotlib.pyplot as plt
plt.style.use('default')
get_ipython().run_line_magic('matplotlib', 'inline')


# In[161]:


df = pd.read_csv("C:\\Users\\2000y\\Downloads\\TRADEBOT_Market_Data.csv")
df


# In[162]:


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


# In[124]:


#Save the daily data to a CSV file
t.to_csv("C:\\Users\\2000y\\Downloads\\daily_metrics.csv")


# In[163]:


# Calculate the 12-day and 26-day EMA
t['EMA_12'] = t['Close'].ewm(span=12, adjust=False).mean()
t['EMA_26'] = t['Close'].ewm(span=26, adjust=False).mean()

# Calculate the MACD line
t['MACD'] = t['EMA_12'] - t['EMA_26']

# Calculate the Signal line
t['Signal'] = t['MACD'].ewm(span=9, adjust=False).mean()


# Calculate daily change
t['% change'] = t['Close'].pct_change() * 100

t['Trade_signal'] = 0
t['Trade_points'] = np.nan
t


# In[164]:


#eliminating the first 26 rows

t=t.iloc[26:]


# In[166]:


#backtesting MACD strategy code

pos=0
num=0
percentchange=[]

for i in t.index:

    close=t["Close"][i]
    
    if(t["MACD"][i] > t["Signal"][i]):
        print("buy signal")
        t["Trade_signal"][i] = 1
        if(pos==0):
            bp=close
            pos=1
            t["Trade_points"][i] = 'entry'
            print("Buying now at "+str(bp))


    elif(t["MACD"][i] < t["Signal"][i]):
        print("sell signal")
        t["Trade_signal"][i] = 0
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


# In[167]:


print(percentchange)


# In[168]:


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


# In[169]:


print()
print("Results for given TRADEBOT data" +" going back to "+str(t.index[0])+", Sample size: "+str(ng+nl)+" trades")
print("MACD line window used: 12 and 26")
print("Batting Avg: "+ str(battingAvg))
print("Gain/loss ratio: "+ ratio)
print("Average Gain: "+ str(avgGain))
print("Average Loss: "+ str(avgLoss))
print("Max Return: "+ maxR)
print("Max Loss: "+ maxL)
print("Total return over "+str(ng+nl)+ " trades: "+ str(totalR)+"%" )
print()


# In[170]:


#Save the entry, exit data to a CSV file
t.to_csv("C:\\Users\\2000y\\Downloads\\trade_metrics_MACD.csv")
t


# In[ ]:




