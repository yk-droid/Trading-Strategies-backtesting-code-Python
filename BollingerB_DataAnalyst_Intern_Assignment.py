#!/usr/bin/env python
# coding: utf-8

# In[130]:


import pandas as pd
import numpy as np
import datetime as dt

import matplotlib.pyplot as plt
plt.style.use('default')
get_ipython().run_line_magic('matplotlib', 'inline')


# In[144]:


df = pd.read_csv("C:\\Users\\2000y\\Downloads\\TRADEBOT_Market_Data.csv")
df


# In[145]:


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


# In[146]:


#computing bollinger bands
# Assuming window 20
window = 20

t['SMA'] = t['Close'].rolling(window=window, min_periods=2).mean()
t['Std_dev'] = t['Close'].rolling(window=window, min_periods=2).std()
t['Upper_band'] = t['SMA'] + (2 * t['Std_dev'])
t['Lower_band'] = t['SMA'] - (2 * t['Std_dev'])

# Calculate daily change
t['% change'] = t['Close'].pct_change() * 100

t['signal'] = 0
t['Trade_points'] = np.nan
t


# In[147]:


#eliminating the first 20 rows

t=t.iloc[20:]


# In[148]:


#backtesting BB strategy code

pos=0
num=0
percentchange=[]

for i in t.index:

    close=t["Close"][i]
    
    if(t["Lower_band"][i] > close):
        print("close below lb")
        t["signal"][i] = 1
        if(pos==0):
            bp=close
            pos=1
            t["Trade_points"][i] = 'entry'
            print("Buying now at "+str(bp))


    elif(t["Upper_band"][i] < close):
        print("close above up")
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


# In[149]:


print(percentchange)


# In[150]:


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


# In[152]:


print()
print("Results for given TRADEBOT data" +" going back to "+str(t.index[0])+", Sample size: "+str(ng+nl)+" trades")
print("Bollinger Bands window used: 20")
print("Batting Avg: "+ str(battingAvg))
print("Gain/loss ratio: "+ ratio)
print("Average Gain: "+ str(avgGain))
print("Average Loss: "+ str(avgLoss))
print("Max Return: "+ maxR)
print("Max Loss: "+ maxL)
print("Total return over "+str(ng+nl)+ " trades: "+ str(totalR)+"%" )
print()


# In[153]:


#Save the entry, exit data to a CSV file
t.to_csv("C:\\Users\\2000y\\Downloads\\trade_metrics_BB.csv")
t


# In[ ]:




