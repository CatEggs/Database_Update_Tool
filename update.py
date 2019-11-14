# excel libraries
import pandas as pd
from openpyxl import load_workbook
import numpy as np

# my libraries
import updatelib as ud

def col_2(path, filename):

    lf_df = pd.read_excel(r'./excel_results/LF.xlsx')
    combined_df = pd.read_excel(r'./excel_results/Full_Analysis.xlsx')
    happypath = pd.read_excel(r'./excel_results/HappyPath.xlsx')
    addliens = pd.read_excel(r'./excel_results/NewLiens.xlsx')
    null_colid = pd.isnull(addliens['COL Id'])
    addlien_null_colid = addliens[null_colid]


    # Get all happy path claim ref ids for cms and lf tab
    hp_id_lf_initial = set(np.asarray(happypath['Claim Ref #']))
    hp_id_cms_initial = np.asarray(happypath['COL Id'])
    al_id_lf = set(np.asarray(addliens['Claim Ref #']))
    al_id_cms = set(np.asarray(addliens['COL Id']))
    al_lienid = set(np.asarray(addlien_null_colid['SLAM LienId']))
    hp_id_lf = set().union(hp_id_lf_initial,al_id_lf)
    hp_id_cms = set().union(hp_id_cms_initial,al_id_cms)
       
    
    #### Happy Path Update ####

    #Pull in lf & cms worksheets
    full_path = path + filename
    cms = pd.read_excel(full_path,  sheet_name = 'CMS_Third Party Liens')
    lf = pd.read_excel(full_path,  sheet_name = 'Law Firm Representation')
    version_tab = pd.read_excel(full_path,  sheet_name = 'Version')

    #Update happypath clamaints to TRUE
    ud.update_label(lf, hp_id_lf, 'Claim Ref #','Process', True)

    # Add new liens to CMS tab and change those claimant to TRUE
    final_cms = ud.add_liens(cms, version_tab, addlien_null_colid)

    # Update the original bulk edit with happy path info for LF tab
    ud.update_df(lf, lf_df, hp_id_lf, 'Medicare entitled', 'Updated Mcare','Claim Ref #', 'Claim Ref #')
    ud.update_df(lf, lf_df, hp_id_lf, 'Non plrp plan enrolled', 'Updated Non PLRP','Claim Ref #', 'Claim Ref #')
    ud.update_df(lf, lf_df, hp_id_lf, 'Medicaid entitled', 'Updated Mcaid','Claim Ref #', 'Claim Ref #')
    ud.update_df(lf, lf_df, hp_id_lf, 'Third party enrolled', 'Updated Third Party','Claim Ref #', 'Claim Ref #')
    ud.update_df(lf, lf_df, hp_id_lf, 'Plrp obligation', 'Updated PLRP','Claim Ref #', 'Claim Ref #')    
    ud.update_df(lf, lf_df, hp_id_lf, 'Holdback amount', 'SLAM HB/Updated HB','Claim Ref #', 'Claim Ref #')

    # Update the original bulk edit with happy path info for CMS tab
    ud.update_df(final_cms, combined_df, hp_id_cms, 'Status', 'Updated Status','Id', 'COL Id')
    ud.update_df(final_cms, combined_df, hp_id_cms, 'Lien type', 'SLAM LienType','Id', 'COL Id')
    ud.update_df(final_cms, combined_df, hp_id_cms, 'Lien holder', 'SLAM Lienholder','Id', 'COL Id')
    ud.update_dups(final_cms, combined_df, hp_id_cms,  'Amount', 'Question number',  'Updated Amount', 'SLAM Question #', 'Id', 'COL Id')

    # Update the original bulk edit with add_lien info for CMS tab
    ud.update_df(final_cms, combined_df, al_lienid, 'Status', 'Updated Status','Lien Id', 'SLAM LienId')
    ud.update_df(final_cms, combined_df, al_lienid, 'Lien type', 'SLAM LienType','Lien Id', 'SLAM LienId')
    ud.update_df(final_cms, combined_df, al_lienid, 'Lien holder', 'SLAM Lienholder','Lien Id', 'SLAM LienId')
    ud.update_dups(final_cms, combined_df, al_lienid,  'Amount', 'Question number',  'Updated Amount', 'SLAM Question #', 'Lien Id', 'SLAM LienId')

    # Add Updated DF to original wb
    wb = load_workbook(full_path)
    ud.add_ws(full_path, wb, lf, 'LF', 0)
    ud.add_ws(full_path, wb, final_cms, 'CMS', 8)

    return print(f'Done with {filename} update')




