# excel libraries
import pandas as pd
from openpyxl import load_workbook
import xlsxwriter
import numpy as np
import xlrd

# my libraries
import updatelib as ud

# os
import os, os.path
import glob

def col_2(path, filename):

    lf_df = pd.read_excel(r'LF.xlsx')
    combined_df = pd.read_excel(r'Full_Analysis.xlsx')
    happypath = pd.read_excel(r'HappyPath.xlsx')
    addliens = pd.read_excel(r'NewLiens.xlsx')

    # Get all happy path claim ref for lf
    hp_id_lf = set(np.asarray(happypath['Claim Ref #']))
    hp_id_cms = np.asarray(happypath['COL Id'])
    al_id_cms = set(np.asarray(addliens['Claim Ref #']))
    ##Need to create a script that takes into account duplicate liens for happypath

    #### Happy Path Update ####

    #Pull in lf & cms worksheets
    full_path = path + filename
    cms = pd.read_excel(full_path,  sheet_name = 'CMS_Third Party Liens')
    lf = pd.read_excel(full_path,  sheet_name = 'Law Firm Representation')
    version_tab = pd.read_excel(full_path,  sheet_name = 'Version')

    #Update happypath clamants to TRUE
    ud.update_label(lf, hp_id_lf, 'Claim Ref #','Process', True)


    # Update the original bulk edit with happy path info for LF tab
    ud.update_df(lf, lf_df, hp_id_lf, 'Medicare entitled', 'Updated Mcare','Claim Ref #', 'Claim Ref #')
    ud.update_df(lf, lf_df, hp_id_lf, 'Non plrp plan enrolled', 'Updated Non PLRP','Claim Ref #', 'Claim Ref #')
    ud.update_df(lf, lf_df, hp_id_lf, 'Medicaid entitled', 'Updated Mcaid','Claim Ref #', 'Claim Ref #')
    ud.update_df(lf, lf_df, hp_id_lf, 'Third party enrolled', 'Updated Third Party','Claim Ref #', 'Claim Ref #')
    ud.update_df(lf, lf_df, hp_id_lf, 'Plrp obligation', 'Updated PLRP','Claim Ref #', 'Claim Ref #')    
    ud.update_df(lf, lf_df, hp_id_lf, 'Holdback amount', 'SLAM HB/Updated HB','Claim Ref #', 'Claim Ref #')

   
    # Update the original bulk edit with happy path info for CMS tab
    ud.update_df(cms, combined_df, hp_id_cms, 'Status', 'SLAM Status','Id', 'COL Id')
    #ud.update_df(cms, combined_df, hp_id_cms, 'Amount', 'SLAM Amount', 'Amount', 'SLAM Amount', 'Id', 'COL Id')
    ud.update_df(cms, combined_df, hp_id_cms, 'Lien type', 'SLAM LienType','Id', 'COL Id')
    ud.update_df(cms, combined_df, hp_id_cms, 'Lien holder', 'SLAM Lienholder','Id', 'COL Id')
    ud.update_dups(cms, combined_df, hp_id_cms,  'Amount', 'Question number',  'SLAM Amount', 'SLAM Question #', 'Id', 'COL Id')

    # Add new liens to CMS tab

    final_cms = ud.add_liens(cms, version_tab, addliens)
    ud.update_label(lf, al_id_cms, 'Claim Ref #','Process', True)

    # Add Updated DF to original wb
    wb = load_workbook(full_path)
    ud.add_ws(full_path, wb, lf, 'LF', 0)
    ud.add_ws(full_path, wb, final_cms, 'CMS', 8)




