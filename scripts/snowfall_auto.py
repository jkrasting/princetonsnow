import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
import numpy as np

# Get data from online
url = r'https://www.gfdl.noaa.gov/snow-obs-2022-23/'
response = requests.get(url)
soup = BeautifulSoup(response.content,'html.parser')
table = soup.find('table')

year = url[-8:-4]
sn = int(year) - 1975
years = year+'_'+str(int(year)+1)

# Read as pandas table
df =pd.read_html(str(table),header=0)[0]
df['comment'] = [np.nan]*len(df)
# Insert the commnet into the day prior
for i in range(1,len(df),2):
    try:
        combined_str = df.iloc[i].dropna().iloc[0]
        df.at[i-1,'comment'] = combined_str
    except:
        pass

# Clean up the dataframe
df.drop(df.index[1::2],inplace=True)
df = df.reset_index(drop=True)
print(df.head(10))

# seperate the observations into their own columns
print ('Hold Please')
df_list = []
for index, row in df.iterrows():
    if row['Individual Reports'] == 'GFDL':
        pass
    else:
        print (row)       
        obs_dict = {s.split('=')[0]:s.split('=')[1] for s in row['Individual Reports'].split(' ')}
        df_list.append(pd.DataFrame(data=obs_dict,index=[index]))

obs_df = pd.concat(df_list,axis=0)

final_df = pd.merge(df,obs_df,left_index=True,right_index=True)
final_df['start_date'] = pd.to_datetime(final_df['Date']).dt.strftime('%Y-%m-%d')
final_df['mean'] = final_df.Amount
final_df['day_of_season'] = (pd.to_datetime(final_df.start_date) - pd.to_datetime('2022-10-01')).dt.days

# Arrange final df for exporting to json
export_df = final_df[['day_of_season','start_date']+list(obs_dict.keys())+['comment','mean']]
export_df.applymap(pd.to_numeric,errors='ignore').to_json('./data/events/season_'+str(sn)+'_'+years+'.json',indent=4,orient='records')