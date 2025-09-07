import csv
import os
import numpy as np
import pandas as pd
from statistics import mean
import sys
import math, ast
from tqdm import tqdm

# Use the score.csv file to see whether their proposals have yes/no or others. 

path = "additional_proposals"
dir_list = os.listdir(path)

scores=pd.read_csv('additional_cleaned_data\\scores.csv', encoding='unicode_escape')
for file in tqdm(dir_list):
	
	data=pd.read_csv('additional_votes\\'+file)  #,\
	#dtype={"choice":"string"})

	data_p=pd.read_csv('additional_proposals\\'+file) 
	weight=[]

	#writer = pd.ExcelWriter(file[:file.index('.csv')]+'.xlsx', engine='openpyxl') 
	#wb  = writer.book
	df = pd.DataFrame(columns=['address', 'weight', 'proposal marks'])
	address=[]

	for i in range(len(data)):
		if data["address"].iloc[i] not in address:
			address.append(data["address"].iloc[i])
	df["address"]=address

	prop_id=data['proposal_id'].unique().tolist()
	pros_num=len(prop_id)
	marks=[]
	sys_marks=[]
	proposals=[]
	
	for i in range(pros_num):
		proposals.append("Proposal"+str(i))
		if str(data_p["BlockNumberChoices"].iloc[0]).isdigit():
			if prop_id[i] in data_p["ID"]:
				if data_p.loc[data_p["ID"]==prop_id[i],"choices"] in scores["Scores"].values.tolist():
					m=scores.loc[scores["Scores"]==data_p.loc[data_p["ID"]==prop_id[i],"choices"],"Mark"].values[0]
					marks.append(m)
					if m==0:
						sys_marks.append(i)
				else:
					marks.append(0)
					sys_marks.append(i)
			else:
				marks.append(0)
				sys_marks.append(i)
		else:
			if prop_id[i] in data_p.index:
				if data_p.loc[prop_id[i],"BlockNumberChoices"] in scores["Scores"].values.tolist():
					m=scores.loc[scores["Scores"]==data_p.loc[prop_id[i],"BlockNumberChoices"],"Mark"].values[0]
					
					marks.append(m)
					if m==0:
						sys_marks.append(i)
				else:
					marks.append(0)
					sys_marks.append(i)
			else:
				marks.append(0)
				sys_marks.append(i)
	
	df = pd.concat([df,pd.DataFrame(columns=proposals)], axis=1)
	df.loc[df["address"]==address[0], "proposal marks"]=str(sys_marks)
	
	mode=1
	for i in range(len(address)):
		token=0
		
		data2=data[data["address"]==address[i]]
		token=mean(data2["voting_power"])
		for j in range(len(data2)):
			ind = prop_id.index(data2["proposal_id"].iloc[j])
			if marks[ind]==1:
				if data2["choice"].iloc[j]=="2":
					df.loc[i,'Proposal'+str(ind)] = -1
				elif data2["choice"].iloc[j]=="3":
					df.loc[i,'Proposal'+str(ind)] = 0
				else: 
					df.loc[i,'Proposal'+str(ind)] = data2["choice"].iloc[j]
					if (mode==1) & (str(data2["choice"].iloc[j]).isnumeric() == False):
						print(file, "We need to recheck this!")
						mode=0
			elif marks[ind]==2:
				if data2["choice"].iloc[j]=="2":
					df.loc[i,'Proposal'+str(ind)] = 0
				elif data2["choice"].iloc[j]=="3":
					df.loc[i,'Proposal'+str(ind)] = -1
				else: 
					df.loc[i,'Proposal'+str(ind)] = data2["choice"].iloc[j]
					if (mode==1) & (data2["choice"].iloc[j].isnumeric() == False):
						print(file, "We need to recheck this!")
						mode=0
			elif marks[ind]==-1:
				if data2["choice"].iloc[j]=="2":
					df.loc[i,'Proposal'+str(ind)] = 1
				elif data2["choice"].iloc[j]=="1":
					df.loc[i,'Proposal'+str(ind)] = -1
				elif data2["choice"].iloc[j]=="3":
					df.loc[i,'Proposal'+str(ind)] = 0
				else: 
					df.loc[i,'Proposal'+str(ind)] = data2["choice"].iloc[j]
					if (mode==1) & (data2["choice"].iloc[j].isnumeric() == False):
						print(file, "We need to recheck this!")
						mode=0
			else:
				df.loc[i,'Proposal'+str(ind)] = data2["choice"].iloc[j]
		weight.append(token)
		
	df["weight"]=weight
	#df.to_excel(writer, index=False)
	#wb.save(file[:file.index('.csv')]+'.xlsx')
	df.to_csv("additional_cleaned_data\\"+file, index=False)
