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
    lf_df = pd.read_excel(r'LF.xlsx') 
    cms_df = pd.read_excel(r'CMS.xlsx')
    combined_df = pd.read_excel(r'Full_Analysis.xlsx')

    # seperate each label into its own df
    hi_cm = combined_df[combined_df['LF_Label'] == 'Human Intervention (CM)']
    hi_level1 = combined_df[combined_df['LF_Label'] == 'Human Intervention (fix this week)']
    hi_level2 = combined_df[combined_df['LF_Label'] == 'Human Intervention (fix this week if time)']
    hi_level3 = combined_df[combined_df['LF_Label'] == 'Human Intervention (fix when you can)']
    hi_level4 = combined_df[combined_df['LF_Label'] == 'Human Intervention - Close in SLAM']
    no_change = combined_df[combined_df['LF_Label'] == 'No Changes, No Issues']
    look_into = combined_df[combined_df['LF_Label'] == 'Look Into']
    add_lien = combined_df[combined_df['LF_Label'] == 'Add Lien']

    # # put labels ids in a list for updating
    # # hi_cm_lf = list(set(np.asarray(hi_cm['Claim Ref #'])))
    # # hi_l1_lf = list(set(np.asarray(hi_level1['Claim Ref #'])))
    # hi_l2_lf = list(set(np.asarray(hi_level2['Claim Ref #'])))
    # print(hi_l2_lf)
    # # hi_l3_lf = list(set(np.asarray(hi_level3['Claim Ref #'])))
    # # hi_l4_lf = list(set(np.asarray(hi_level4['Claim Ref #'])))
    # # nochg_lf = list(set(np.asarray(no_change['Claim Ref #'])))
    # # sqlchk_lf = list(set(np.asarray(look_into['Claim Ref #'])))

    # # hi_cm_cms = np.asarray(hi_cm['COL Id'])
    # # hi_l1_cms = np.asarray(hi_level1['COL Id'])
    # hi_l2_cms = np.asarray(hi_level2['COL Id'])
    # # hi_l3_cms = np.asarray(hi_level3['COL Id'])
    # # hi_l4_cms = np.asarray(hi_level4['COL Id'])
    # # nochg_cms = np.asarray(no_change['COL Id'])
    # # sqlchk_cms =  np.asarray(look_into['COL Id'])
    # # #add_liens_cms = np.asarray(add_lien['SLAM LienId'])

    # # # update labels
    # # lf_cm = ud.update_label(lf_df, hi_cm_lf, 'Claim Ref #','LF_Label', 'Human Intervention (CM)')
    # # lf_l1 = ud.update_label(lf_df, hi_l1_lf, 'Claim Ref #','LF_Label', 'Human Intervention (fix this week)')
    # lf_l2 = ud.update_label(lf_df, hi_l2_lf, 'Claim Ref #','LF_Label', 'Human Intervention (fix this week if time)')
    # print(lf_l2)
    # # lf_l3 =ud.update_label(lf_df, hi_l3_lf, 'Claim Ref #','LF_Label', 'Human Intervention (fix when you can)')
    # # lf_l4 =ud.update_label(lf_df, hi_l4_lf, 'Claim Ref #','LF_Label', 'Human Intervention - Close in SLAM')
    # # lf_nochg =ud.update_label(lf_df, nochg_lf, 'Claim Ref #','LF_Label', 'No Changes, No Issues')
    # # lf_sqlchk =ud.update_label(lf_df, sqlchk_lf, 'Claim Ref #','LF_Label', 'Look Into')

    # # cms_cm = ud.update_label(cms_df, hi_cm_cms, 'COL Id','CMS_Label', 'Human Intervention (CM)')
    # # cms_l1 = ud.update_label(cms_df, hi_l1_cms, 'COL Id','CMS_Label', 'Human Intervention (fix this week)')
    # cms_l2 = ud.update_label(cms_df, hi_l2_cms, 'COL Id','CMS_Label', 'Human Intervention (fix this week if time)')
    # # cms_l3 = ud.update_label(cms_df, hi_l3_cms, 'COL Id','CMS_Label', 'Human Intervention (fix when you can)')
    # cms_l4 = ud.update_label(cms_df, hi_l4_cms, 'COL Id','CMS_Label', 'Human Intervention - Close in SLAM')
    # cms_nochg = ud.update_label(cms_df, nochg_cms, 'COL Id','CMS_Label', 'No Changes, No Issues')
    # cms_sqlchk = ud.update_label(cms_df, sqlchk_cms, 'COL Id','CMS_Label', 'Look Into')
    #ud.update_label(cms_df, add_liens_cms, 'SLAM LienId','CMS_Label', 'Add Lien')

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
    # ud.test_export(lf_cm, cms_cm, "Human_Intervention_CM - ", path)
    # ud.test_export(lf_l1, cms_l1, "Human_Intervention_L1 - ", path)
    # ud.test_export(lf_l2, cms_l2, "Human_Intervention_L2 - ", path)
    # ud.test_export(lf_l3, cms_l3, "Human_Intervention_L3 - ", path)
    # ud.test_export(lf_l4, cms_l4, "Human_Intervention_L4 - ", path)
    # ud.test_export(lf_nochg, cms_nochg, "No_Change - ", path)
    # ud.test_export(lf_sqlchk, cms_sqlchk, "Check Query - ", path)
    # #ud.test_export(hi_l1_lf, hi_l1_cms,"Add Liens - ", path)