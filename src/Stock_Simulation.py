#!/usr/bin/env python
# coding: utf-8

# In[160]:

import pandas as pd
import openpyxl
import xlsxwriter
import numpy as np
import pdb
from dateutil.relativedelta import *
import glob

#Converting xls data

compounding = 0
shortlisted_companies_df  = pd.DataFrame() 
for input_file  in glob.glob('../../finance_vicky/files/output/backtest/*.xlsx'):
    print(input_file)
    xl = pd.ExcelFile(input_file)
    script_df = xl.parse('Shortlisted Companies')
    #script_df.set_index('Script Name', inplace = True)
    shortlisted_companies_df = pd.concat([shortlisted_companies_df, script_df])
       
#Simulation: 
print(shortlisted_companies_df)
    
#pdb.set_trace()
shortlisted_companies_df.set_index(['Start Date', 'Script Name'], inplace=True)
shortlisted_companies_df.sort_index(level='Start Date', inplace=True)
print(shortlisted_companies_df.head())
simulated_df = pd.DataFrame()
#pdb.set_trace()
capital = 10000000
capital_count = 1
#distribute the money equally across all scripts.
pdb.set_trace()
for i, data in shortlisted_companies_df.groupby(level = 0):
    #pdb.set_trace()
    sc_df = data.loc[(i)]
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
        print(capital, i)
        simulated_df = pd.concat([simulated_df, sc_df])
        #pdb.set_trace()

    else: 
        capital += 10000000
        capital_count += 1
print(capital, capital_count)
#pdb.set_trace() 

output_file = '../../finance_vicky/files/output/backtest/simulation_details.xlsx'
writer = pd.ExcelWriter(output_file, engine='xlsxwriter', datetime_format='mm/dd/yy', date_format='mm/dd/yy')
pdb.set_trace()
simulated_df.set_index(['Start Date', 'Script Name'], inplace = True)
simulated_df.sort_index(level='Start Date', inplace=True)
simulated_df.to_excel(writer,sheet_name='Sheet')       
writer.save()

