import csv
import os
import numpy as np
import pandas as pd
from statistics import mean
import sys
import math, ast
from tqdm import tqdm

# Get a unique choice list of proposals -- and then save "scores.csv" 

score=pd.DataFrame({"Scores":[],
					"Mark":[]})
path = "additional_proposals"
dir_list = os.listdir(path)

for file in tqdm(dir_list):
	print(file)
	data_p=pd.read_csv('additional_proposals\\'+file, encoding='unicode_escape')
	if str(data_p["BlockNumberChoices"].iloc[0]).isdigit():
		choices=data_p["choices"]
	else:
		choices=data_p["BlockNumberChoices"]
	for i in range(len(choices)):
		if len(choices.iloc[i].split("', '"))==3:
			if 'abstain' in choices.iloc[i].lower():
				if ('yes' in choices.iloc[i].lower()) |\
				('no' in choices.iloc[i].lower()) |\
				('yae' in choices.iloc[i].lower()) |\
				('nay' in choices.iloc[i].lower()):
					score.loc[len(score.index)]=[choices.iloc[i],1]
				else:
					score.loc[len(score.index)]=[choices.iloc[i],None]
			else:
				score.loc[len(score.index)]=[choices.iloc[i],0]
		elif len(choices.iloc[i].split("', '"))==2:
			if ('yes' in choices.iloc[i].lower()) |\
				('no' in choices.iloc[i].lower()) |\
				('yae' in choices.iloc[i].lower()) |\
				('nay' in choices.iloc[i].lower()):
					score.loc[len(score.index)]=[choices.iloc[i],1]
			else:
				score.loc[len(score.index)]=[choices.iloc[i],None]
		else:
			score.loc[len(score.index)]=[choices.iloc[i],0]

score=score.drop_duplicates()
score.to_csv('additional_cleaned_data\\scores.csv')
