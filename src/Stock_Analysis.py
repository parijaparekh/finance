#!/usr/bin/env python
# coding: utf-8

# In[160]:

import pandas as pd
import openpyxl
import xlsxwriter
#import matplotlib.pyplot as plt
import numpy as np
import pdb
from dateutil.relativedelta import *
import glob

#Converting xls data
file_details = []
for input_file  in glob.glob('../../finance_vicky/files/input/backtest/*.xlsx'):
    xl = pd.ExcelFile(input_file)
    for sheet in xl.sheet_names:
        script_df = xl.parse(sheet)
        print(script_df.columns)


        # In[161]:


        #Cleaning up the data
        #Setting_index, Creating a df for market cap, Dropping market_cap from script_df,
        #print(script_df.info(), script_df.index.values)
        #pdb.set_trace()
        script_df.drop(script_df.columns[0], axis=1, inplace=True)
        print(script_df.columns[1])
        script_df.set_index(script_df.columns[0], inplace=True)
        script_df.index.names = ['Script Name']
        market_cap_df = pd.DataFrame({'Script Name': script_df.index.values, 'Market Cap': script_df[script_df.columns[0]].values})
        market_cap_df.set_index('Script Name', inplace=True)
        script_df.drop(script_df.columns[0], axis=1, inplace = True)

        #Dropping a column Grand Total if it exist.
        if 'Grand Total' in script_df.columns:
            pdb.set_trace()
            script_df.drop('Grand Total', axis=1, inplace=True)

        script_df.columns = pd.to_datetime(script_df.columns)
        #cleaning the data of script_df
        #droppping date columns related to weekends. 
        script_df.drop(script_df.loc[:,(pd.Series(script_df.columns).dt.dayofweek > 4).values].columns, axis=1, inplace=True)
        
        #test_df.columns = pd.to_datetime(script_df.columns)
        #print(script_df.head())


        # In[162]:


        
        #print(script_df.loc[:,script_df[pd.Series(script_df.columns).dt.dayofweek > 4]])
        #dayofweek = ts.dt.dayofweek
        #print(ts.head(), dayofweek.head())
        #print(script_df.loc[:,(pd.Series(script_df.columns).dt.dayofweek > 4).values])


        # In[163]:


        #Taking care of blank values
        #removing columns that are meant for weekend date
        #script_df.isnull().sum() ---> There are 251 places where stock values are missing
        #Backward Filling for scripts that start with missing value.
        #Forward Filling for scripts that end with missing value. 


        #Get the name of the scripts where the start is null
        no_value_start_scripts = script_df[script_df[script_df.columns[0]].isnull()].index
        #print(no_value_start_scripts)
        for i in no_value_start_scripts:
            # Get the first valid value
            if i is not None:
                first_valid_date = script_df.loc[i].first_valid_index()
                if first_valid_date is not None:
                    #Back fill the values
                    script_df.loc[i,script_df.columns[0]:first_valid_date] = script_df.loc[i, first_valid_date]

        #Get the name of the scripts where the end is null
        no_value_end_scripts = script_df[script_df[script_df.columns[-1]].isnull()].index
        #print(no_value_end_scripts)
        for i in no_value_end_scripts:
            #forward fill these values. 
            script_df.loc[i].ffill()

        #get scripts with intermittent missing values in between.
        no_value_inbetw_scripts = script_df[script_df.isnull().any(axis=1)].index
        #print(no_value_inbetw_scripts)
        #Interpolate and fill in the missing values
        script_df.interpolate(method='linear',axis=1, inplace=True)
        script_df = script_df.round(2)

        #output_file_name = script_df.columns[0].strftime("%d/%m/%y") + '_to_' +script_df.columns[len(script_df.columns)-1].strftime("%d/%m/%y")
        output_file = '../../finance_vicky/files/output/backtest/'+
                        script_df.columns[0].strftime("%d/%m/%y") + 
                        '_to_' +
                        script_df.columns[len(script_df.columns)-1].strftime("%d/%m/%y")+
                        '.xlsx'

        #Seperating the training and test data
        #pdb.set_trace()
        last_observation = script_df.columns[0] + relativedelta(years=+1)
        test_df = None
        if (script_df.columns[len(script_df.columns) -1].month and script_df.columns[len(script_df.columns) -1].year) > (last_observation.month and last_observation.year):
            script_df = script_df.T.sort_index()
            test_df = script_df[last_observation :].T
            script_df = script_df[script_df.index.values[0] : last_observation].T
            #print(test_df.shape, script_df.shape, test_df.head(), script_df.head())
        
        
        # In[164]:


        #Calculating %change in values: %Data
        #get a transponse of the dataframe 
        t_script_df = script_df.T
        t_pct_change_df = t_script_df.pct_change()*100
        t_pct_change_df = t_pct_change_df.round(2)


        # In[165]:


        #Aggregating +ve and -ve change
        #Get the Nifty % change:
        nifty = t_script_df['Nifty 50']
        t_pct_change_net_df = pd.DataFrame(t_pct_change_df.sum(), columns=['Net']) 
        t_pct_change_neg_df = pd.DataFrame(t_pct_change_df[t_pct_change_df['Nifty 50'] < 0.0].sum(), columns=['Negative'])
        t_pct_change_pos_df = pd.DataFrame(t_pct_change_df[t_pct_change_df['Nifty 50'] > 0.0].sum(), columns=['Positive'])
        #print(t_pct_change_neg_df)
        #t_pct_change_pos_df = pd.DataFrame(t_pct_change_df[t_pct_change_df[t_pct_change_df.columns] > 0.0].sum(), columns=['Positive'])
        t_pct_change_cal_df = pd.concat([t_pct_change_pos_df,t_pct_change_neg_df,t_pct_change_net_df, market_cap_df], axis = 1)


        # In[166]:


        #Printing
        #Transposed_Data
        writer = pd.ExcelWriter(output_file, engine='xlsxwriter', datetime_format='mm/dd/yyyy',
                            date_format='mm/dd/yyyy')
        script_df.to_excel(writer,sheet_name='Data')
        t_pct_change_df.T.to_excel(writer,sheet_name='%Data')
        t_pct_change_cal_df.to_excel(writer, sheet_name='Sum of Positive & Negative')
        t_pct_change_pos_df.sort_values(by=['Positive'], ascending=False, inplace=True)
        t_pct_change_pos_df.to_excel(writer, sheet_name='Positive Sorting')
        t_pct_change_neg_df.sort_values(by=['Negative'], ascending=False, inplace=True)
        t_pct_change_neg_df.to_excel(writer, sheet_name='Negative Sorting')



        # In[167]:


        ## Getting top 10 companies that showed good growth irrespective of the markets
        bucket_size = int(script_df.shape[0]/2.5)
        print(bucket_size)
        final_df = pd.merge(t_pct_change_pos_df.head(bucket_size),t_pct_change_neg_df.head(bucket_size), how='inner', on='Script Name')
        for script in final_df.index.values:
            final_df.loc[script,'Net'] = t_pct_change_net_df.loc[script,'Net']
            final_df.loc[script,'Open'] = script_df.loc[script,script_df.columns[0]]
            final_df.loc[script,'Close'] = script_df.loc[script, script_df.columns[len(script_df.columns) - 1]]
            final_df.loc[script,'Market Cap'] = market_cap_df.loc[script,'Market Cap']
            final_df.loc[script,'P/E'] = final_df.loc[script,'Close']/(final_df.loc[script,'Close'] - final_df.loc[script,'Open'])
            if test_df is not None:
                print(input_file, sheet)
                pdb.set_trace()
                final_df.loc[script,'Open for Test Data'] = test_df.loc[script, test_df.columns[0]]
                final_df.loc[script,'Close for Test Data'] = test_df.loc[script, test_df.columns[len(test_df.columns) -1]]
                final_df.loc[script, 'Net'] = test_df.loc[script, test_df.loc[script, test_df.columns[len(test_df.columns) -1]] - test_df.loc[script, test_df.columns[0]]]    
        final_df.sort_values(by=['P/E'], ascending=True, inplace=True)
        #print(final_df)
        final_df.to_excel(writer, sheet_name='Shortlisted Companies')
        if test_df is not None:
            test_df.to_excel(writer, sheet_name='Test Data')
        writer.save()





