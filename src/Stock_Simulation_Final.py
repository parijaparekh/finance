#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import openpyxl
import xlsxwriter
import numpy as np
import pdb
from dateutil.relativedelta import *
import glob
import matplotlib.pyplot as plt


# In[2]:


#Converting xls data
shortlisted_companies_df  = pd.DataFrame() 
for input_file  in glob.glob('../../finance_vicky/files/output/backtest/*.xlsx'):
    xl = pd.ExcelFile(input_file)
    if 'Shortlisted Companies' in xl.sheet_names:
        script_df = xl.parse('Shortlisted Companies')
        shortlisted_companies_df = pd.concat([shortlisted_companies_df, script_df])       
shortlisted_companies_df.reset_index(inplace = True)

shortlisted_companies_df.set_index(['Start Date', 'Script Name'], inplace=True)
shortlisted_companies_df.sort_index(level='Start Date', inplace=True)


# In[17]:



print(shortlisted_companies_df.head())
simulated_df = pd.DataFrame()
capital_df = pd.DataFrame()
capital = 10000000
capital_count = 1

#distribute the money equally across all scripts.
for i, data in shortlisted_companies_df.groupby(level = 0):
    sc_df = pd.DataFrame()
    sc_df = pd.concat([sc_df,data.loc[(i)]])
    total_scripts = len(sc_df.index)
    share_per_script = capital/total_scripts 
    if share_per_script > 100:
        for script in sc_df.index.values:
            shares = np.floor(share_per_script/sc_df.loc[script, 'Open for Test Data'])
            sc_df.loc[script, 'No. of Shares'] = shares
            net_pl = shares * sc_df.loc[script, 'Net for Test Data']
            sc_df.loc[script, 'Investment'] = shares * sc_df.loc[script, 'Open for Test Data']
            sc_df.loc[script, 'Balance'] = share_per_script - shares * sc_df.loc[script, 'Open for Test Data']
            sc_df.loc[script, 'Disinvestment'] = shares * sc_df.loc[script, 'Close for Test Data']
            sc_df.loc[script,'net_pl'] = net_pl
            sc_df.loc[script, 'Start Date'] = i
            capital += sc_df.loc[script, 'net_pl']
            capital += sc_df.loc[script, 'Balance']         
        sc_df.reset_index(inplace=True)
        simulated_df = pd.concat([simulated_df, sc_df])
     
        
        df = pd.DataFrame.from_records([{'Invest Date': i, 'Investment': sc_df['Investment'].sum(), 'Gains/Loss' : sc_df['net_pl'].sum(),
                      'Disinvestment': sc_df['Disinvestment'].sum(), 'Balance': sc_df['Balance'].sum(),
                      'Total Funds': sc_df['Disinvestment'].sum() + sc_df['Balance'].sum(), 
                      'Disinvest Date': sc_df['End Date'][0]}], index='Invest Date')
        
        capital_df = pd.concat([capital_df, df])            
    else: 
        capital += 10000000
        capital_count += 1
print(capital, capital_count)
print(shortlisted_companies_df['Investment'])
print(capital_df.head())
#print(simulated_df.columns)
#simulated_df.set_index(['Start Date', 'Script Name'], inplace=True)
#simulated_df.sort_index(level='Start Date', inplace=True)
#print(simulated_df.head())


# In[18]:



output_file = '../../finance_vicky/files/output/backtest/simulation_details.xlsx'
writer = pd.ExcelWriter(output_file, engine='xlsxwriter', datetime_format='mm/dd/yy', date_format='mm/dd/yy')
#pdb.set_trace()
simulated_df.set_index(['Start Date', 'Script Name'], inplace = True)
simulated_df.sort_index(level='Start Date', inplace=True)
simulated_df.to_excel(writer,sheet_name='Sheet') 
capital_df.to_excel(writer, sheet_name='Capital Gains')
writer.save()


# In[19]:


#capital_df.head()
capital_df.dropna(inplace=True)
if 'index' in capital_df.columns:
    capital_df.drop(['index'], axis=1, inplace=True)
capital_df.sort_index(inplace=True)
#capital_df.head(39)


# In[24]:


plt.plot(capital_df['Gains/Loss'])
plt.show()

