# excel libraries
import pandas as pd
from openpyxl import load_workbook
import xlsxwriter
import numpy as np
import xlrd

# my libraries
import updatelib as ud

def col_3(path):
    ### Human Intervention ###
    # Takes in all 3 spreadsheets for update. Will use the combined spreadsheet to update the labels for the CMS and LF tab 
    # Then export them into different tabbs of a workbook

    # import spreadsheets
    combined_df = pd.read_excel(r'./excel_results/Full_Analysis.xlsx')

    # seperate each label into its own df
    df_hi = combined_df.groupby('LF_Label')
    try:
        hi_cm = df_hi.get_group('Human Intervention (CM)')
    except KeyError:
        pass
    try:
        hi_level1 = df_hi.get_group('Human Intervention (fix this week)')
    except KeyError:
        pass
    try:
        hi_level2 = df_hi.get_group('Human Intervention (fix this week if time)')
    except KeyError:
        pass
    try:
        hi_level3 = df_hi.get_group('Human Intervention (fix when you can)')
    except KeyError:
        pass
    try:
        hi_level4 = df_hi.get_group('Human Intervention - Close in SLAM')
    except KeyError:
        pass
    try:
        no_change = df_hi.get_group('No Changes, No Issues')
    except KeyError:
        pass
    try:
        look_into = df_hi.get_group('Look Into')
    except KeyError:
        pass
    try:
        add_lien = df_hi.get_group('Add Lien')
    except KeyError:
        pass
 

    # export into worksheet and put a filename into it
    try:
        ud.export(combined_df, "Full_Analysis QA - ", path)
    except UnboundLocalError:
        pass
    try:
        ud.export(hi_cm, "Human_Intervention_CM - ", path)
    except UnboundLocalError:
        pass
    try:
        ud.export(hi_level1, "Human_Intervention_L1 - ", path)
    except UnboundLocalError:
        pass
    try:
        ud.export(hi_level2, "Human_Intervention_L2 - ", path)
    except UnboundLocalError:
        pass
    try:
        ud.export(hi_level3, "Human_Intervention_L3 - ", path)
    except UnboundLocalError:
        pass
    try:
        ud.export(hi_level4, "Human_Intervention_L4 - ", path)
    except UnboundLocalError:
        pass
    try:
        ud.export(no_change, "No_Change - ", path)
    except UnboundLocalError:
        pass
    try:
        ud.export(look_into, "Check Query - ", path)
    except UnboundLocalError:
        pass
    try:
        ud.export(add_lien, "Add Liens - ", path)
    except UnboundLocalError:
        pass
    
    print('Human Intervention is done, the script is done.')
    