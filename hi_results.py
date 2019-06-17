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
    hi_cm = combined_df[combined_df['LF_Label'] == 'Human Intervention (CM)']
    hi_level1 = combined_df[combined_df['LF_Label'] == 'Human Intervention (fix this week)']
    hi_level2 = combined_df[combined_df['LF_Label'] == 'Human Intervention (fix this week if time)']
    hi_level3 = combined_df[combined_df['LF_Label'] == 'Human Intervention (fix when you can)']
    hi_level4 = combined_df[combined_df['LF_Label'] == 'Human Intervention - Close in SLAM']
    no_change = combined_df[combined_df['LF_Label'] == 'No Changes, No Issues']
    look_into = combined_df[combined_df['LF_Label'] == 'Look Into']
    add_lien = combined_df[combined_df['LF_Label'] == 'Add Lien']

    # export into worksheet
    ud.export(hi_cm, "Human_Intervention_CM - ", path)
    ud.export(hi_level1, "Human_Intervention_L1 - ", path)
    ud.export(hi_level2, "Human_Intervention_L2 - ", path)
    ud.export(hi_level3, "Human_Intervention_L3 - ", path)
    ud.export(hi_level4, "Human_Intervention_L4 - ", path)
    ud.export(no_change, "No_Change - ", path)
    ud.export(look_into, "Check Query - ", path)
    ud.export(add_lien, "Add Liens - ", path)
    print('Human Intervention is done, the script is done.')