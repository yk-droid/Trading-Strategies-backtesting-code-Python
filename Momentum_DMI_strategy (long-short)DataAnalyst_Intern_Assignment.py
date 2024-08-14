#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import datetime as dt
import ta


# In[18]:


t = pd.read_csv("C:\\Users\\2000y\\Downloads\\TRADEBOT_Market_Data.csv")
t


# In[19]:


# parse the time. 
t.DateTime = pd.to_datetime(t.DateTime, format="%m/%d/%Y %H:%M")

#make the time the index. 
t = t.set_index("DateTime")
t


# In[20]:


# Calculate the Rate of Change (ROC)
t['ROC'] = t['Close'].pct_change()

# Calculate the average ROC over a given period
t['Avg_ROC'] = t['ROC'].rolling(window=5).mean()

# Calculate the average Volume over a given period
t['Avg_Volume'] = t['Volume'].rolling(window=5).mean()

period =14
# Calculate True Range (TR)
t['Prev_Close'] = t['Close'].shift(1)
t['TR'] = t[['High', 'Low', 'Prev_Close']].apply(
    lambda x: max(x['High'] - x['Low'], 
                  abs(x['High'] - x['Prev_Close']), 
                  abs(x['Low'] - x['Prev_Close'])), 
    axis=1
)

# Calculate Directional Movement (+DM and -DM)
t['Prev_High'] = t['High'].shift(1)
t['Prev_Low'] = t['Low'].shift(1)

t['+DM'] = np.where((t['High'] - t['Prev_High']) > (t['Prev_Low'] - t['Low']), 
                     np.maximum(t['High'] - t['Prev_High'], 0), 
                     0)
t['-DM'] = np.where((t['Prev_Low'] - t['Low']) > (t['High'] - t['Prev_High']), 
                     np.maximum(t['Prev_Low'] - t['Low'], 0), 
                     0)

# Calculate Smoothed TR, +DM, and -DM
t['Smoothed_TR'] = t['TR'].rolling(window=period, min_periods=1).sum()
t['Smoothed_+DM'] = t['+DM'].rolling(window=period, min_periods=1).sum()
t['Smoothed_-DM'] = t['-DM'].rolling(window=period, min_periods=1).sum()

# Calculate +DI and -DI
t['+DI'] = (t['Smoothed_+DM'] / t['Smoothed_TR']) * 100
t['-DI'] = (t['Smoothed_-DM'] / t['Smoothed_TR']) * 100

# Calculate DX and ADX
t['DX'] = (abs(t['+DI'] - t['-DI']) / (t['+DI'] + t['-DI'])) * 100
t['ADX'] = t['DX'].rolling(window=period, min_periods=1).mean()

# Clean up temporary columns
t = t.drop(columns=['Prev_Close', 'Prev_High', 'Prev_Low', 'TR', '+DM', '-DM', 'Smoothed_TR', 'Smoothed_+DM', 'Smoothed_-DM', 'DX'])


# Calculate RSI
delta = t['Close'].diff(1)
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
avg_gain = gain.rolling(window=14).mean()
avg_loss = loss.rolling(window=14).mean()
rs = avg_gain / avg_loss
t['RSI'] = 100 - (100 / (1 + rs))

t


# In[7]:


pip install --upgrade ta


# In[21]:


t = t.iloc[14 :]
t


# In[27]:


#backtesting code

pos=0
num=0
percentchange=[]


# brokerage costs and tax rate
br_cost = 0.0005  # 0.05% per trade
tax_rate = 0.20  # 20% short term capital gains tax


for i in t.index:

    close=t["Close"][i]
    
    if(abs(t["ROC"][i]) > abs(t["Avg_ROC"][i]) and t["Volume"][i] > t["Avg_Volume"][i] and t['ADX'][i] > 25 and 27 <= t['RSI'][i] <= 39):
        print("increasing momentum")
        if(pos==0):
            if(t['+DI'][i] > t['-DI'][i]):
                bp=close
                pos=1
                print("Opening long position now at "+str(bp))
            elif(t['+DI'][i] < t['-DI'][i]):
                sp=close
                pos=-1
                print("Opening short position now at "+str(sp))



    elif(abs(t["ROC"][i]) < abs(t["Avg_ROC"][i]) and t["Volume"][i] < t["Avg_Volume"][i] and t['ADX'][i] < 25):
        print("low momentum")
        if(pos==1):
            pos=0
            sp=close
            print("Closing long position now at "+str(sp))
            pc=(sp/bp-1 - br_cost)*100
            percentchange.append(pc)
        if(pos==-1):
            pos=0
            bp=close
            print("Closing short position now at "+str(bp))
            pc=(sp/bp-1 - br_cost)*100
            percentchange.append(pc)
        
    if(num==t["Close"].count()-1 and pos!=0):
        if(pos==1):
            pos=0
            sp=close
            print("Closing long position now at "+str(sp))
            pc=(sp/bp-1 - br_cost)*100
            percentchange.append(pc)
        if(pos==-1):
            pos=0
            bp=close
            print("Closing short position now at "+str(bp))
            pc=(sp/bp-1 - br_cost)*100
            percentchange.append(pc)
        

    num+=1


# In[28]:


print(percentchange)


# In[29]:


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

totalR=round((totalR-1)*100*(1 - tax_rate),2)

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


# In[30]:


print()
print("Results for DMI_Momentum strategy for TRADEBOT 5min TF data going back to "+str(t.index[0])+", Sample size: "+str(ng+nl)+" trades")
print("DMI Period used: "+str(14))
print("Batting Avg: "+ str(battingAvg))
print("Gain/loss ratio: "+ ratio)
print("Average Gain: "+ str(avgGain))
print("Average Loss: "+ str(avgLoss))
print("Max Return: "+ maxR)
print("Max Loss: "+ maxL)
print("Total after tax return over "+str(ng+nl)+ " trades: "+ str(totalR)+"%" )
print()


# In[ ]:




