import csv, os
import numpy as np
import statistics 
import pandas as pd
import sys
import math
import researchpy as rp
import scipy.stats as stats
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
#import statsmodels.api as sm

#define function to calculate Gini coefficient
def gini(x):
    total = 0
    for i, xi in enumerate(x[:-1], 1):
        total += np.sum(np.abs(xi - x[i:]))
    return total / (len(x)**2 * np.mean(x))
	
def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False
		
#correlation
#weight - metric
#participation - metirc

dec_metric=pd.DataFrame({"System":[],
					"Correlation: voting power vs. participation rate":[],
					"Entropy (considering only voting power)":[],
					"Entropy (considering both voting power and participation rate)":[],
					"Gini (considering only voting power)":[],
					"Gini (considering both voting power and participation rate)":[]})


path = "cleaned data2"
dir_list = os.listdir(path)

for system in dir_list:
  data=pd.read_csv('cleaned data2\\'+system, encoding= 'unicode_escape', dtype="string")
  #data=data[data["timestamp"].astype(str).str.isdigit()]
  entropy_t=0
  gini_t=0

  entropy_p=0
  gini_p=0

  part=[]

  poh=0 
  
  address=data.iloc[:,0].values.tolist()
  weight=data["weight"].values.tolist()
  weight = [float(w) for w in weight]
  
  for i in address:
    data2=data[data.iloc[:,0]==i]
    p=0
    for j in range(len(data2.columns)-3):
      if pd.isna(data2["Proposal"+str(j)].iloc[0])==False:
        p=p+1
    
    part.append(p)
  corr=pearsonr(weight, part) #correlation
  print(corr)

  for i in range(len(weight)):
    if weight[i]>0:
      entropy_t=entropy_t-math.log(weight[i]/sum(weight),2)*weight[i]/sum(weight)
    
  part_score=[]
  for i in range(len(weight)):
    p2=abs(weight[i]*part[i])
    part_score.append(p2)

  #sys.exit()

  for i in range(len(weight)):
    if part_score[i]>0:
      entropy_p=entropy_p-math.log(part_score[i]/sum(part_score),2)*part_score[i]/sum(part_score)

      
  dec_metric.loc[len(dec_metric.index)]=\
  [system[:system.index(".csv")],corr, entropy_t,entropy_p, \
  gini(np.array([i/sum(weight) for i in weight])),\
  gini(np.array([i/sum(part_score) for i in part_score])),None]

dec_metric.to_csv('voting_power_metrics.csv')
