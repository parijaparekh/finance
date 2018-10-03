
import pandas as pd
import openpyxl
import xlsxwriter
#import matplotlib.pyplot as plt
import numpy as np
import pdb
import glob

#Converting xls data
file_details = []
for input_file  in glob.glob('../../finance_vicky/files/input/backtest/*.xlsx'):
    print(input_file)
    xl = pd.ExcelFile(input_file)
    for sheet in xl.sheet_names:
        output_file = '../../finance_vicky/files/output/backtest/'+sheet+'.xlsx'
        script_df = xl.parse(sheet)
        script_df.drop(script_df.columns[0], axis=1, inplace=True)
        script_df.set_index(script_df.columns[0], inplace=True)
        script_df.index.names = ['Script Name']
        market_cap_df = pd.DataFrame({'Script': script_df.index.values, 'Market Cap': script_df[script_df.columns[0]].values})
        market_cap_df.set_index('Script', inplace=True)
        
        script_df.drop(script_df.columns[0], axis =1, inplace=True)
        if 'Grand Total' in script_df.columns:
            script_df.drop('Grand Total', axis=1, inplace=True)

        #spliting data from 13th month to 16th month
        script_df.columns = pd.to_datetime(script_df.columns)
        print('{}{}{:d}{}{}{}{}'.format(sheet,' : ', len(script_df.columns), ' : ',script_df.columns[0].strftime("%d/%m/%y"),
        ' : ',script_df.columns[len(script_df.columns)-1].strftime("%d/%m/%y")))
        file_details.append({'Sheet Name':sheet, 
                        'No. of Columns':len(script_df.columns),
                        'Start Date':script_df.columns[0].strftime("%d/%m/%y"),
                        'End Date':script_df.columns[len(script_df.columns)-1].strftime("%d/%m/%y")})

#Print the file details to xlsx
file_details_df = pd.DataFrame(file_details)
file_details_df.set_index('Sheet Name', inplace=True)
column_titles = ['No. of Columns', 'Start Date', 'End Date']
file_details_df = file_details_df.reindex(columns = column_titles)
file_details_df['Start Date'] = pd.to_datetime(file_details_df['Start Date'])
file_details_df['End Date'] = pd.to_datetime(file_details_df['End Date'])
file_details_df.sort_values(by='Start Date', inplace = True)
output_file = '../../finance_vicky/files/output/backtest/sheet_details.xlsx'
writer = pd.ExcelWriter(output_file, engine='xlsxwriter', datetime_format='dd/mm/yyyy',
                        date_format='dd/mm/yyyy')
print(file_details_df.head())
pdb.set_trace()
file_details_df.to_excel(writer, sheet_name='data_shape')
writer.save()