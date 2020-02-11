# excel libraries
import pandas as pd
from openpyxl import load_workbook
import xlsxwriter
import numpy as np
import xlrd

# my library
import updatelib as ud

# sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
import pyodbc
import config

# SQL query
from sql import lf_query, cms_query

# os
import os, os.path
import glob

def col_1():

    # create engine, make connection to reporting DB
      
    sql_connect = "mssql+pyodbc://" + config.username + ":" + config.password + "@" + config.local + "?driver=SQL+Server+Native+Client+11.0"
    engine = create_engine(sql_connect)

    # import S3Reporting MetaData
    metadata = MetaData(bind=engine)

    # run SQL queries for LF and CMS tabs
    lf_df = pd.read_sql(lf_query, con = engine)
    cms_df = pd.read_sql(cms_query, con = engine)
    print('SQL query done')
	
    # merge dataframes to compare, rename columns
	
    lf_df['Claim Ref #']=lf_df['Claim Ref #'].astype(int)
    cms_df['Claim Ref #']=cms_df['Claim Ref #'].astype(int)
    combined_df = pd.merge(lf_df, cms_df, on = 'Claim Ref #', how = 'outer')
    combined_df[['Initial_CMS_Label', 'CMS_Label']] = combined_df[['Initial_CMS_Label', 'CMS_Label']].fillna(value = 'No Lien Info')
    combined_df = pd.DataFrame.drop_duplicates(combined_df)

    
	# Create a df based off label value.

    df_cms = combined_df.groupby('CMS_Label')
    df_lf = combined_df.groupby('LF_Label')
    lf_ne = df_lf.get_group('Not Eligible')
    cms_ne = df_cms.get_group('Not Eligible')
    cms_null = df_cms.get_group('No Lien Info')
    # try:
    # 	cms_null = df_cms.get_group('')
    # except KeyError:
    # 	pass
    try:
    	lf_li = df_lf.get_group('Look Into')
    except KeyError:
    	pass
    try:
    	cms_li = df_cms.get_group('Look Into')
    except KeyError:
    	pass

    try:
    	lf_hi1 = df_lf.get_group('Human Intervention (fix this week)')
    except KeyError:
    	pass
    try:
    	cms_hi1 = df_cms.get_group('Human Intervention (fix this week)')
    except KeyError:
    	pass
    try:
    	lf_hi2 = df_lf.get_group('Human Intervention (CM)')
    except KeyError:
    	pass
    try:
    	lf_hi3 = df_lf.get_group('Human Intervention (fix this week if time)')
    except KeyError:
    	pass
    try:
    	lf_hi4 = df_lf.get_group('Human Intervention (fix when you can)')
    except KeyError:
    	pass
    try:
    	cms_hi4 = df_cms.get_group('Human Intervention (fix when you can)')
    except KeyError:
    	pass
    try:
    	lf_hi5 = df_lf.get_group('Human Intervention - Close in SLAM')
    except KeyError:
    	pass
    try:
    	lf_nc = df_lf.get_group('No change, no issue')
    except KeyError:
    	pass
    try:
    	cms_nc = df_cms.get_group('No change, no issue')
    except KeyError:
    	pass
    try:
    	lf_hp = df_lf.get_group('Happy Path')
    except KeyError:
    	pass
    try:
    	cms_hp = df_cms.get_group('Happy Path')
    except KeyError:
    	pass
    try:
    	cms_al = df_cms.get_group('Add Lien')
    except KeyError:
    	pass
    print('Done with df grouping')

    ## Grab the ids in each df an put it in a list

    cms_null_id = set(np.asarray(cms_null['Claim Ref #']))
    lf_ne_id = set(np.asarray(lf_ne['Claim Ref #']))
    #try:
    cms_ne_id = set(np.asarray(cms_ne['Claim Ref #']))
    # except UnboundLocalError:
    # 	pass
    try:
    	lf_li_id = set(np.asarray(lf_li['Claim Ref #']))
    except UnboundLocalError:
    	pass
    try:
    	cms_li_id = set(np.asarray(cms_li['Claim Ref #']))
    except UnboundLocalError:
    	pass
    try:
    	lf_hi1_id = set(np.asarray(lf_hi1['Claim Ref #']))
    except UnboundLocalError:
    	pass
    try:
    	cms_hi1_id = set(np.asarray(cms_hi1['Claim Ref #']))
    except UnboundLocalError:
    	pass
    try:
    	lf_hi2_id = set(np.asarray(lf_hi2['Claim Ref #']))
    except UnboundLocalError:
    	pass
    try:
    	lf_hi3_id = set(np.asarray(lf_hi3['Claim Ref #']))
    except UnboundLocalError:
    	pass
    try:
    	lf_hi4_id = set(np.asarray(lf_hi4['Claim Ref #']))
    except UnboundLocalError:
    	pass
    try:
    	cms_hi4_id = set(np.asarray(cms_hi4['Claim Ref #']))
    except UnboundLocalError:
    	pass
    try:
    	lf_hi5_id = set(np.asarray(lf_hi5['Claim Ref #']))
    except UnboundLocalError:
    	pass
    try:
    	lf_nc_id = set(np.asarray(lf_nc['Claim Ref #']))
    except UnboundLocalError:
    	pass
    try:
    	cms_nc_id = set(np.asarray(cms_nc['Claim Ref #']))
    except UnboundLocalError:
    	pass
    try:
    	lf_hp_id = set(np.asarray(lf_hp['Claim Ref #']))
    except UnboundLocalError:
    	pass
    try:
    	cms_hp_id = set(np.asarray(cms_hp['Claim Ref #']))
    except UnboundLocalError:
    	pass
    try:
    	cms_al_id = set(np.asarray(cms_al['Claim Ref #']))
    except UnboundLocalError:
    	pass

    print('Done with the Id grouping')

    ## Now we will iterate thru the list of id's.
    ## This is so that the Final Label will be based off a matrix that includes intersection
    ## between both labels found in the CMS_Label column and the LF_Label column

	## Happy Path ##	

	# Null Liens
    try:
    	hp_null = lf_hp_id.intersection(cms_null_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hp_id,cms_null_id,hp_null,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Happy Path')
    except UnboundLocalError:
    	pass

	# Happy Path
    try:
    	hp_hp = lf_hp_id.intersection(cms_hp_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hp_id,cms_hp_id,hp_hp,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Happy Path')
    except UnboundLocalError:
    	pass

	# No change, no issue
    try:
    	hp_nc = lf_hp_id.intersection(cms_nc_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hp_id,cms_nc_id,hp_nc,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Happy Path')
    except UnboundLocalError:
    	pass
	# Add Lien

    try:
    	hp_al = lf_hp_id.intersection(cms_al_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hp_id,cms_al_id,hp_al,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Add Lien')
    except UnboundLocalError:
    	pass

	# HI - Fix this week (fix when you can)
    try:
    	hp_hi4 = lf_hp_id.intersection(cms_hi4)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hp_id,cms_hi4,hp_hi4,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix when you can)')
    except UnboundLocalError:
    	pass

	# HI - Fix this week
    try:
    	hp_hi1 = lf_hp_id.intersection(cms_hi1_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hp_id,cms_hi1_id,hp_hi1,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix this week)')
    except UnboundLocalError:
    	pass
    print('Finished 1st matrix group')

	## No change, no issue ##

	# Null CMS Liens
    try:
    	nc_null = lf_nc_id.intersection(cms_null_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_nc_id,cms_null_id,nc_null,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'No change, no issue')
    except UnboundLocalError:
    	pass


	# No change, no issue
    try:
    	nc_nc = lf_nc_id.intersection(cms_nc_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_nc_id,cms_nc_id,nc_nc,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'No change, no issue')
    except UnboundLocalError:
    	pass

    # Add Lien
    try:
    	nc_al = lf_nc_id.intersection(cms_al_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_nc_id,cms_al_id,nc_al,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Add Lien')
    except UnboundLocalError:
    	pass

	# Happy Path
    try:
    	nc_hp = lf_nc_id.intersection(cms_hp_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_nc_id,cms_hp_id,nc_hp,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Happy Path')
    except UnboundLocalError:
    	pass

	# HI - Fix this week (fix when you can)
    try:
    	nc_hi4 = lf_nc_id.intersection(cms_hi4)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_nc_id,cms_hi4,nc_hi4,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix when you can)')
    except UnboundLocalError:
    	pass

	# HI - Fix this week
    try:
    	nc_hi1 = lf_nc_id.intersection(cms_hi1_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_nc_id,cms_hi1_id,nc_hi1,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix this week)')
    except UnboundLocalError:
    	pass
    print('Finished 2nd matrix group')

	## Human Intervention - Close in SLAM ##	

	# Null CMS Liens
    try:
    	hi5_null = lf_hi5_id.intersection(cms_null_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi5_id,cms_null_id,hi5_null,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention - Close in SLAM')
    except UnboundLocalError:
    	pass

	# Happy Path
    try:
    	hi5_hp = lf_hi5_id.intersection(cms_hp_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi5_id,cms_hp_id,hi5_hp,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix this week)')
    except UnboundLocalError:
    	pass

	# No change, no issue
    try:
    	hi5_nc = lf_hi5_id.intersection(cms_nc_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi5_id,cms_nc_id,hi5_nc,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention - Close in SLAM')
    except UnboundLocalError:
    	pass

	# Add Lien
    try:
    	hi5_al = lf_hi5_id.intersection(cms_al_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi5_id,cms_al_id,hi5_al,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix this week)')
    except UnboundLocalError:
    	pass

	# HI - Fix this week (fix when you can)
    try:
    	hi5_hi4 = lf_hi5_id.intersection(cms_hi4)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi5_id,cms_hi4,hi5_hi4,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix this week)')
    except UnboundLocalError:
    	pass

	# HI - Fix this week
    try:
    	hi5_hi1 = lf_hi5_id.intersection(cms_hi1_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi5_id,cms_hi1_id,hi5_hi1,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix this week)')
    except UnboundLocalError:
    	pass
    print('Finished 3rd matrix group')

	## Human Intervention (fix when you can) ##	

	# Null Liens
    try:
    	hi4_null = lf_hi4_id.intersection(cms_null_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi4_id,cms_null_id,hi4_null,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix when you can)')
    except UnboundLocalError:
    	pass

	# Happy Path
    try:
    	hi4_hp = lf_hi4_id.intersection(cms_hp_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi4_id,cms_hp_id,hi4_hp,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix when you can)')
    except UnboundLocalError:
    	pass

	# No change, no issue
    try:
    	hi4_nc = lf_hi4_id.intersection(cms_nc_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi4_id,cms_nc_id,hi4_nc,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix when you can)')
    except UnboundLocalError:
    	pass

	# Add Lien
    try:
    	hi4_al = lf_hi4_id.intersection(cms_al_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi4_id,cms_al_id,hi4_al,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix when you can)')
    except UnboundLocalError:
    	pass

	# HI - Fix this week (fix when you can)
    try:
    	hi4_hi4 = lf_hi4_id.intersection(cms_hi4)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi4_id,cms_hi4,hi4_hi4,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix when you can)')
    except UnboundLocalError:
    	pass

	# HI - Fix this week
    try:
    	hi4_hi1 = lf_hi4_id.intersection(cms_hi1_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi4_id,cms_hi1_id,hi4_hi1,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix this week)')
    except UnboundLocalError:
    	pass
    print('Finished 4th matrix group')

	## Human Intervention (fix this week) (If time) ##

	# Null Liens
    try:
    	hi3_null = lf_hi3_id.intersection(cms_null_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi3_id,cms_null_id,hi3_null,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix this week) (if time)')
    except UnboundLocalError:
    	pass

	# Happy Path
    try:
    	hi3_hp = lf_hi3_id.intersection(cms_hp_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi3_id,cms_hp_id,hi3_hp,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix this week) (if time)')
    except UnboundLocalError:
    	pass

	# No change, no issue
    try:
    	hi3_nc = lf_hi3_id.intersection(cms_nc_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi3_id,cms_nc_id,hi3_nc,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix this week) (if time)')
    except UnboundLocalError:
    	pass

	# Add Lien
    try:
    	hi3_al = lf_hi3_id.intersection(cms_al_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi3_id,cms_al_id,hi3_al,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix this week) (if time)')
    except UnboundLocalError:
    	pass

	# HI - Fix this week (fix when you can)
    try:
    	hi3_hi4 = lf_hi3_id.intersection(cms_hi4)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi3_id,cms_hi4,hi3_hi4,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix this week) (if time)')
    except UnboundLocalError:
    	pass


	# HI - Fix this week
    try:
    	hi3_hi1 = lf_hi3_id.intersection(cms_hi1_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi3_id,cms_hi1_id,hi3_hi1,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix this week)')
    except UnboundLocalError:
    	pass
    print('Finished 5th matrix group')


	## Human Intervention (fix this week) ##

	# NUll Liens
    try:
    	hi1_null = lf_hi1_id.intersection(cms_null_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi1_id,cms_null_id,hi1_null,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix this week)')
    except UnboundLocalError:
    	pass

	# Happy Path
    try:
    	hi1_hp = lf_hi1_id.intersection(cms_hp_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi1_id,cms_hp_id,hi1_hp,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix this week)')
    except UnboundLocalError:
    	pass

	# No change, no issue
    try:
    	hi1_nc = lf_hi1_id.intersection(cms_nc_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi1_id,cms_nc_id,hi1_nc,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix this week)')
    except UnboundLocalError:
    	pass

	# Add Lien
    try:
    	hi1_al = lf_hi1_id.intersection(cms_al_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi1_id,cms_al_id,hi1_al,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix this week)')
    except UnboundLocalError:
    	pass

	# HI - Fix this week (fix when you can)
    try:
    	hi1_hi4 = lf_hi1_id.intersection(cms_hi4)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi1_id,cms_hi4,hi1_hi4,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix this week)')
    except UnboundLocalError:
    	pass

	# HI - Fix this week
    try:
    	hi1_hi1 = lf_hi1_id.intersection(cms_hi1_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi1_id,cms_hi1_id,hi1_hi1,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (fix this week)')
    except UnboundLocalError:
    	pass
    print('Finished 6th matrix group')

	## Human Inetervention (CM) ##
	
	# Null Liens
    try:
    	hi2_null = lf_hi2_id.intersection(cms_null_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi2_id,cms_null_id,hi2_null,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (CM)')
    except UnboundLocalError:
    	pass

	# Happy Path
    try:
    	hi2_hp = lf_hi2_id.intersection(cms_hp_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi2_id,cms_hp_id,hi2_hp,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (CM)')
    except UnboundLocalError:
    	pass

	# No change, no issue
    try:
    	hi2_nc = lf_hi2_id.intersection(cms_nc_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi2_id,cms_nc_id,hi2_nc,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (CM)')
    except UnboundLocalError:
    	pass

	# Add Lien
    try:
    	hi2_al = lf_hi2_id.intersection(cms_al_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi2_id,cms_al_id,hi2_al,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (CM)')
    except UnboundLocalError:
    	pass

	# HI - Fix this week (fix when you can)
    try:
    	hi2_hi4 = lf_hi2_id.intersection(cms_hi4)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi2_id,cms_hi4,hi2_hi4,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (CM)')
    except UnboundLocalError:
    	pass


	# HI - Fix this week
    try:
    	hi2_hi1 = lf_hi2_id.intersection(cms_hi1_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi2_id,cms_hi1_id,hi2_hi1,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (CM)')
    except UnboundLocalError:
    	pass
    print('Finished the full Intersection')

    # These supercede all other options

	### Look Into ###

    try:
    	ud.matrix_finalupdate(cms_li_id, combined_df, 'Claim Ref #' , 'LF_Label', 'Look Into')
    except UnboundLocalError:
    	pass
    try:		
    	ud.matrix_finalupdate(cms_li_id, combined_df, 'Claim Ref #' , 'CMS_Label', 'Look Into')
    except UnboundLocalError:
    	pass

    try:
    	ud.matrix_finalupdate(lf_li_id, combined_df, 'Claim Ref #' , 'CMS_Label', 'Look Into')
    except UnboundLocalError:
    	pass
    try:
    	ud.matrix_finalupdate(lf_li_id, combined_df, 'Claim Ref #' , 'LF_Label', 'Look Into')
    except UnboundLocalError:
    	pass

	### Not Eligible ###

    ud.matrix_finalupdate(cms_ne_id, combined_df, 'Claim Ref #' , 'CMS_Label', 'Not Eligible')
    ud.matrix_finalupdate(cms_ne_id, combined_df, 'Claim Ref #' , 'LF_Label', 'Not Eligible')

    ud.matrix_finalupdate(lf_ne_id, combined_df, 'Claim Ref #' , 'CMS_Label', 'Not Eligible')
    ud.matrix_finalupdate(lf_ne_id, combined_df, 'Claim Ref #' , 'LF_Label', 'Not Eligible')

    print('Done with the Matrix')

    #Pull original LF analysis, Happy path and Combined Analysis into spreadsheet for col2.py 
	
    lf_df = pd.DataFrame.drop_duplicates(lf_df)
    lf_df.to_excel('./excel_results/LF.xlsx', index = False)
    cms_df = pd.DataFrame.drop_duplicates(cms_df)
    cms_df.to_excel('./excel_results/CMS.xlsx', index = False)
    happypath = combined_df[combined_df['LF_Label'] == 'Happy Path']
    happypath = pd.DataFrame.drop_duplicates(happypath)
    happypath.to_excel('./excel_results/HappyPath.xlsx',index = False)
    addlien = combined_df[combined_df['LF_Label'] == 'Add Lien']
    addlien = pd.DataFrame.drop_duplicates(addlien)
    addlien.to_excel('./excel_results/NewLiens.xlsx')
    combined_df.to_excel('./excel_results/Full_Analysis.xlsx', index = False)
    print('SQL code has completed, on to updates!')
