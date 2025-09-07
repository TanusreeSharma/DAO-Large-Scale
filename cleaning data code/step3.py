import csv
import os
import numpy as np
import pandas as pd
from statistics import mean
import sys
import math, ast
from tqdm import tqdm

# We encode the option number for list/dict types

path = "additional_proposals"
dir_list = os.listdir(path)

scores=pd.read_csv('additional_cleaned_data\\scores.csv', encoding='unicode_escape')
for file in ['elfork_eth.csv']:
	if ('.py' not in file) & ('scores' not in file):
		print(file)
		data_c=pd.read_csv('additional_cleaned_data\\'+file, encoding='unicode_escape', dtype="string")
		
		data=pd.read_csv('additional_votes\\'+file,\
		dtype={"choice":"string"})
		prop_id=data['proposal_id'].unique().tolist()
		pros_num=len(prop_id)
		data_p=pd.read_csv('additional_proposals\\'+file, encoding='unicode_escape')
		marks=[]
		for i in range(pros_num):		
			if str(data_p["BlockNumberChoices"].iloc[0]).isdigit():
				if prop_id[i] in data_p["ID"]:
					if data_p.loc[data_p["ID"]==prop_id[i],"choices"] in scores["Scores"].values.tolist():
						m=scores.loc[scores["Scores"]==data_p.loc[data_p["ID"]==prop_id[i],"choices"],"Mark"].values[0]
						marks.append(m)
						
					else:
						marks.append(0)
				else:
					marks.append(0)
			else:
				if prop_id[i] in data_p.index:
					if data_p.loc[prop_id[i],"BlockNumberChoices"] in scores["Scores"].values.tolist():
						m=scores.loc[scores["Scores"]==data_p.loc[prop_id[i],"BlockNumberChoices"],"Mark"].values[0]
						
						marks.append(m)
						
					else:
						marks.append(0)
						
				else:
					marks.append(0)
		
		k=0
		for col in data_c.columns.values.tolist()[3:]:
			if marks[k]!=0:
				for i in range(len(data_c)):
					if pd.isna(data_c[col].iloc[i])==False:
						if data_c[col].str.isnumeric()[i]==True:
							break
						elif "{" in data_c[col].iloc[i]:
							new={}
							for key, value in ast.literal_eval(data_c[col].iloc[i]).items():
								if marks[k]==1:
									if int(key)==1:
										new[key]=value
									elif int(key)==2:
										new["-1"]=value
									elif int(key)==3:
										new["0"]=value
								elif marks[k]==2:
									if int(key)==1:
										new[key]=value
									elif int(key)==2:
										new["0"]=value
									elif int(key)==3:
										new["-1"]=value
								elif marks[k]==-1:
									if int(key)==1:
										new["-1"]=value
									elif int(key)==2:
										new["1"]=value
									elif int(key)==3:
										new["0"]=value
										
							data_c[col].iloc[i] =str(new)
						elif "[" in data_c[col].iloc[i]:
							choice=data_c[col].iloc[i].strip('][').split(', ')
							if '' in choice:
								choice.remove('')
							if choice!=None:
								choice = [eval(c) for c in choice]
								if marks[k]==1:
									if 1 in choice:
										choice[choice.index(1)]=1
									if 2 in choice:
										choice[choice.index(2)]=-1
									if 3 in choice:
										choice[choice.index(3)]=0
								elif marks[k]==2:
									if 1 in choice:
										choice[choice.index(1)]=1
									if 2 in choice:
										choice[choice.index(2)]=0
									if 3 in choice:
										choice[choice.index(3)]=-1
								elif marks[k]==-1:
									if 1 in choice:
										choice[choice.index(1)]=-1
									if 2 in choice:
										choice[choice.index(2)]=1
									if 3 in choice:
										choice[choice.index(3)]=0
											
								data_c[col].iloc[i] =str(choice)
							
			k=k+1
		data_c.to_csv("additional_cleaned_data2//"+file, index=False)
