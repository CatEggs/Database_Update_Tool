# excel libraries
import pandas as pd
from openpyxl import load_workbook
import xlsxwriter
import numpy as np
import xlrd

# sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
import pyodbc
import config

# os
import os, os.path
import glob

def col_1():

    # create engine, make connection to reporting DB
      
    sql_connect = "mssql+pyodbc://" + config.username + ":" + config.password + "@" + config.local + "?driver=SQL+Server+Native+Client+11.0"
    engine = create_engine(sql_connect)

    # import S3Reporting MetaData
    metadata = MetaData(bind=engine)

    lf_df = pd.read_sql(
    """
Select sub2.*, 
		Case
		When [Escrow Analysis] = 'Look Into' then 'Look Into'
		When [Updated SLAM Final] = 'Look Into' then 'Look Into'
		When [Update HB?] = 'Look Into' then 'Look Into'
	
		When [Claimant in SLAM correctly?] = 'Not Eligible - Withdrawn' then 'Not Eligible'
		When [Claimant in SLAM correctly?] = 'Not Eligible - EIF' then 'Not Eligible'
		When [Claimant on CSR?] = 'Not Eligible - Not on CSR' then 'Not Eligible'
		When [Escrow Analysis] = 'Not Eligible - prepayment' then 'Not Eligible'
		When [Escrow Analysis] = 'Not Eligible - EIF' then 'Not Eligible'
		When [Misc. Issues] = 'Not Eligible - EIF' then 'Not Eligible'
		When [Misc. Issues] = 'Not Eligible - Not a valid case' then 'Not Eligible'
		When [Misc. Issues] = 'Not Eligible - Burnett and on Bad List' then 'Not Eligible'
		When [Misc. Issues] = 'Not Eligible - Mostyn 2017 and DOI is placeholder' then 'Not Eligible'
		When [Misc. Issues] = 'Not Eligible - #Problems' then 'Not Eligible'
		When [SA Matches?] = 'Not Eligible - EIF' then 'Not Eligible'
		When [Updated SLAM Final] = 'Not Eligible - Resolved' then 'Not Eligible'
		When [Updated SLAM Final] = 'Not Eligible - Pending' then 'Not Eligible'
		When [Rules for Q2, Q4, Questionnaire, Release] ='Not Eligible - Leave Q2 and Q4 at No Answer - Placeholder DOI' then 'Not Eligible'
		When [Rules for Q2, Q4, Questionnaire, Release] ='Not Eligible - Leave Q4 at No Answer - firm answers' then 'Not Eligible'
		When [Rules for Q2, Q4, Questionnaire, Release] ='Not Eligible - Leave Q4 at No Answer (spreadsheet)' then 'Not Eligible'
		When [Rules for Q2, Q4, Questionnaire, Release] ='Not Eligble - Leave Q4 at No Answer - Quest Recd not true' then 'Not Eligible'
		When [Rules for Q2, Q4, Questionnaire, Release] ='Not Eligible - Leave Q2 and Q4 at No Answer - Quest Recd not true' then 'Not Eligible'
		When [Rules for Q2, Q4, Questionnaire, Release] ='Not Eligible - Leave Q4 at no answer - BA within 3 weeks' then 'Not Eligible'
		When [Rules for Q2, Q4, Questionnaire, Release] ='Not Eligible - Leave Q4 at no answer - BA no release' then 'Not Eligible'
		When [Should we update?] = 'Not Eligible - pending' then 'Not Eligible'
		When [Should we update?] = 'Not Eligible - pending' then 'Not Eligible'
		When [Update HB?] = 'Not Eligible - pending' then 'Not Eligible'

		When [SA Matches?] = 'Human Intervention (CM) - SA mismatch' then 'Human Intervention (CM)'
		When [SSN Research] ='Human Intervention (CM) - SSN mismatch' then 'Human Intervention (CM)'

		When [Claimant in SLAM correctly?] = 'Human Intervention (fix this week) - Claimant data not pulling' then 'Human Intervention (fix this week)'
		When [Escrow Analysis] = 'Human Intervention (fix this week) - Claimant data not pulling from SLAM' then 'Human Intervention (fix this week)'
		When [Updated SLAM Final] = 'Human Intervention (fix this week) - No (GRG)' then 'Human Intervention (fix this week)'
		When [Rules for Q2, Q4, Questionnaire, Release] = 'Human Intervention (fix this week) - Q4 should No Answer - Quest Recd not true' then 'Human Intervention (fix this week)'
		When [Rules for Q2, Q4, Questionnaire, Release] = 'Human Intervention (fix this week) - Q2 and Q4 should be No Answer - Quest Recd not true' then 'Human Intervention (fix this week)'
		When [Rules for Q2, Q4, Questionnaire, Release] = 'Human Intervention (fix this week) - Q4 should be no answer - BA within 3 weeks' then 'Human Intervention (fix this week)'
		When [Rules for Q2, Q4, Questionnaire, Release] = 'Human Intervention (fix this week) - Q4 should be no answer - BA no release' then 'Human Intervention (fix this week)'
		When [Rules for Q2, Q4, Questionnaire, Release] = 'Human Intervention (fix this week) - Release Date Issue' then 'Human Intervention (fix this week)'
		When [Updated Mcare] = 'Human Intervention (fix this week) - Yes in COL but not in SLAM' then 'Human Intervention (fix this week)'
		When [Updated Non PLRP] = 'Human Intervention (fix this week) - Yes in COL but not in SLAM' then 'Human Intervention (fix this week)'
		When [Updated Mcaid] = 'Human Intervention (fix this week) - Yes in COL but not in SLAM' then 'Human Intervention (fix this week)'
		When [Updated Third Party] = 'Human Intervention (fix this week) - Yes in COL but not in SLAM' then 'Human Intervention (fix this week)'
		When [Updated PLRP] = 'Human Intervention (fix this week) - Yes in COL but not in SLAM' then 'Human Intervention (fix this week)'

		When [Escrow Analysis] = 'Human Intervention (fix this week if time) - sum of liens is greater than escrow' then 'Human Intervention (fix this week if time)'
		When [Updated SLAM Final] = 'Human Intervention (fix this week if time) - Scope issue' then 'Human Intervention (fix this week if time)'
		When [Updated SLAM Final] = 'Human Intervention (fix this week if time) - Resolved but not final' then 'Human Intervention (fix this week if time)'
		When [Should we update?] = 'Human Intervention (fix this week if time) - Finalized Status Id Issue' then 'Human Intervention (fix this week if time)'
		When [Should we update?] = 'Human Intervention (fix this week if time) - resolved but post payment lien deficient' then 'Human Intervention (fix this week if time)'

		When [Escrow Analysis] = 'Human Intervention (fix when you can) - May need update but not enough escrow' then 'Human Intervention (fix when you can)'
		When [Escrow Analysis] = 'Human Intervention (fix when you can) - HB mismatch and not enough escrow' then 'Human Intervention (fix when you can)'
		When [Escrow Analysis] = 'Human Intervention (fix when you can) - resolved but escrow mismatch' then 'Human Intervention (fix when you can)'
		When [Escrow Analysis] = 'Human Intervention (fix when you can) - resolved but HB mismatch' then 'Human Intervention (fix when you can)'
		When [Escrow Analysis] = 'Human Intervention (fix when you can) - resolved but not final' then 'Human Intervention (fix when you can)'
		When [Escrow Analysis] = 'Human Intervention (fix when you can) - resolved but escrow/HB mismatch' then 'Human Intervention (fix when you can)'
		When [Escrow Analysis] = 'Human Intervention (fix when you can) - resolved but escrow/HB mismatch' then 'Human Intervention (fix when you can)'
		When [Escrow Analysis] = 'Human Intervention (fix when you can) - Not enough escrow'  then 'Human Intervention (fix when you can)'
		When [Update Questions?] = 'Human Intervention (fix when you can) - Resolved but question changes' then 'Human Intervention (fix when you can)'

		When [Claimant in SLAM correctly?] = 'Good' then 'Happy Path'
		When [Claimant on CSR?] = 'Good' then 'Happy Path'
		When [Escrow Analysis] = 'Happy Path - update needed' then 'Happy Path'
		When [Escrow Analysis] = 'Happy Path - Check COL' then 'Happy Path'
		When [Misc. Issues] = 'Good' then 'Happy Path'
		When [SA Matches?] = 'Good' then 'Happy Path'
		When [SSN Research] ='Good - No Issue' then 'Happy Path'
		When [SSN Research] ='SSN mismatch ok - trust SLAM' then 'Happy Path'
		When [Updated SLAM Final] = 'Happy Path - Final' then 'Happy Path'
		When [Rules for Q2, Q4, Questionnaire, Release] ='Normal Update Process' then 'Happy Path'
		When [Should we update?] = 'Ok to Update' then 'Happy Path'
		When [Update Questions?] = 'Questions need update' then 'Happy Path'
		When [Update HB?] = 'Happy Path - Update Needed' then 'Happy Path'

		When [Escrow Analysis] = 'Human Intervention - Close in SLAM' then 'Human Intervention - Close in SLAM'

		When [Escrow Analysis] = 'No Changes, No Issues - Resolved' then 'No Changes, No Issues'
		When [Escrow Analysis] = 'No Changes, No Issues - Resolved' then 'No Changes, No Issues'
		When [Update Questions?] = 'No changes, no issues - final' then 'No Changes, No Issues'
		When [Update Questions?] = 'No changes, no issues - resolved, Q Mismatch, but HB is good' then 'No Changes, No Issues'
		When [Updated Mcare] = 'No changes, no issues - Q Mismatch, but resolved and HB is good' then 'No Changes, No Issues'
		When [Updated Non PLRP] = 'No changes, no issues - Q Mismatch, but resolved and HB is good' then 'No Changes, No Issues'
		When [Updated Mcaid] = 'No changes, no issues - Q Mismatch, but resolved and HB is good' then 'No Changes, No Issues'
		When [Updated Third Party] = 'No changes, no issues - Q Mismatch, but resolved and HB is good' then 'No Changes, No Issues'
		When [Updated PLRP] = 'No changes, no issues - Q Mismatch, but resolved and HB is good' then 'No Changes, No Issues'
		When [Update HB?] = 'No Changes in HB' then 'No Changes, No Issues'
		
		Else 'Look Into'
		
		End As 'Initial_LF_Label',
	Case
		When [Escrow Analysis] = 'Look Into' then 'Look Into'
		When [Updated SLAM Final] = 'Look Into' then 'Look Into'
		When [Update HB?] = 'Look Into' then 'Look Into'
	
		When [Claimant in SLAM correctly?] = 'Not Eligible - Withdrawn' then 'Not Eligible'
		When [Claimant in SLAM correctly?] = 'Not Eligible - EIF' then 'Not Eligible'
		When [Claimant on CSR?] = 'Not Eligible - Not on CSR' then 'Not Eligible'
		When [Escrow Analysis] = 'Not Eligible - prepayment' then 'Not Eligible'
		When [Escrow Analysis] = 'Not Eligible - EIF' then 'Not Eligible'
		When [Misc. Issues] = 'Not Eligible - EIF' then 'Not Eligible'
		When [Misc. Issues] = 'Not Eligible - Not a valid case' then 'Not Eligible'
		When [Misc. Issues] = 'Not Eligible - Burnett and on Bad List' then 'Not Eligible'
		When [Misc. Issues] = 'Not Eligible - Mostyn 2017 and DOI is placeholder' then 'Not Eligible'
		When [Misc. Issues] = 'Not Eligible - #Problems' then 'Not Eligible'
		When [SA Matches?] = 'Not Eligible - EIF' then 'Not Eligible'
		When [Updated SLAM Final] = 'Not Eligible - Resolved' then 'Not Eligible'
		When [Updated SLAM Final] = 'Not Eligible - Pending' then 'Not Eligible'
		When [Rules for Q2, Q4, Questionnaire, Release] ='Not Eligible - Leave Q2 and Q4 at No Answer - Placeholder DOI' then 'Not Eligible'
		When [Rules for Q2, Q4, Questionnaire, Release] ='Not Eligible - Leave Q4 at No Answer - firm answers' then 'Not Eligible'
		When [Rules for Q2, Q4, Questionnaire, Release] ='Not Eligible - Leave Q4 at No Answer (spreadsheet)' then 'Not Eligible'
		When [Rules for Q2, Q4, Questionnaire, Release] ='Not Eligble - Leave Q4 at No Answer - Quest Recd not true' then 'Not Eligible'
		When [Rules for Q2, Q4, Questionnaire, Release] ='Not Eligible - Leave Q2 and Q4 at No Answer - Quest Recd not true' then 'Not Eligible'
		When [Rules for Q2, Q4, Questionnaire, Release] ='Not Eligible - Leave Q4 at no answer - BA within 3 weeks' then 'Not Eligible'
		When [Rules for Q2, Q4, Questionnaire, Release] ='Not Eligible - Leave Q4 at no answer - BA no release' then 'Not Eligible'
		When [Should we update?] = 'Not Eligible - pending' then 'Not Eligible'
		When [Should we update?] = 'Not Eligible - pending' then 'Not Eligible'
		When [Update HB?] = 'Not Eligible - pending' then 'Not Eligible'

		When [SA Matches?] = 'Human Intervention (CM) - SA mismatch' then 'Human Intervention (CM)'
		When [SSN Research] ='Human Intervention (CM) - SSN mismatch' then 'Human Intervention (CM)'

		When [Claimant in SLAM correctly?] = 'Human Intervention (fix this week) - Claimant data not pulling' then 'Human Intervention (fix this week)'
		When [Escrow Analysis] = 'Human Intervention (fix this week) - Claimant data not pulling from SLAM' then 'Human Intervention (fix this week)'
		When [Updated SLAM Final] = 'Human Intervention (fix this week) - No (GRG)' then 'Human Intervention (fix this week)'
		When [Rules for Q2, Q4, Questionnaire, Release] = 'Human Intervention (fix this week) - Q4 should No Answer - Quest Recd not true' then 'Human Intervention (fix this week)'
		When [Rules for Q2, Q4, Questionnaire, Release] = 'Human Intervention (fix this week) - Q2 and Q4 should be No Answer - Quest Recd not true' then 'Human Intervention (fix this week)'
		When [Rules for Q2, Q4, Questionnaire, Release] = 'Human Intervention (fix this week) - Q4 should be no answer - BA within 3 weeks' then 'Human Intervention (fix this week)'
		When [Rules for Q2, Q4, Questionnaire, Release] = 'Human Intervention (fix this week) - Q4 should be no answer - BA no release' then 'Human Intervention (fix this week)'
		When [Rules for Q2, Q4, Questionnaire, Release] = 'Human Intervention (fix this week) - Release Date Issue' then 'Human Intervention (fix this week)'
		When [Updated Mcare] = 'Human Intervention (fix this week) - Yes in COL but not in SLAM' then 'Human Intervention (fix this week)'
		When [Updated Non PLRP] = 'Human Intervention (fix this week) - Yes in COL but not in SLAM' then 'Human Intervention (fix this week)'
		When [Updated Mcaid] = 'Human Intervention (fix this week) - Yes in COL but not in SLAM' then 'Human Intervention (fix this week)'
		When [Updated Third Party] = 'Human Intervention (fix this week) - Yes in COL but not in SLAM' then 'Human Intervention (fix this week)'
		When [Updated PLRP] = 'Human Intervention (fix this week) - Yes in COL but not in SLAM' then 'Human Intervention (fix this week)'

		When [Escrow Analysis] = 'Human Intervention (fix this week if time) - sum of liens is greater than escrow' then 'Human Intervention (fix this week if time)'
		When [Updated SLAM Final] = 'Human Intervention (fix this week if time) - Scope issue' then 'Human Intervention (fix this week if time)'
		When [Updated SLAM Final] = 'Human Intervention (fix this week if time) - Resolved but not final' then 'Human Intervention (fix this week if time)'
		When [Should we update?] = 'Human Intervention (fix this week if time) - Finalized Status Id Issue' then 'Human Intervention (fix this week if time)'
		When [Should we update?] = 'Human Intervention (fix this week if time) - resolved but post payment lien deficient' then 'Human Intervention (fix this week if time)'

		When [Escrow Analysis] = 'Human Intervention (fix when you can) - May need update but not enough escrow' then 'Human Intervention (fix when you can)'
		When [Escrow Analysis] = 'Human Intervention (fix when you can) - HB mismatch and not enough escrow' then 'Human Intervention (fix when you can)'
		When [Escrow Analysis] = 'Human Intervention (fix when you can) - resolved but escrow mismatch' then 'Human Intervention (fix when you can)'
		When [Escrow Analysis] = 'Human Intervention (fix when you can) - resolved but HB mismatch' then 'Human Intervention (fix when you can)'
		When [Escrow Analysis] = 'Human Intervention (fix when you can) - resolved but not final' then 'Human Intervention (fix when you can)'
		When [Escrow Analysis] = 'Human Intervention (fix when you can) - resolved but escrow/HB mismatch' then 'Human Intervention (fix when you can)'
		When [Escrow Analysis] = 'Human Intervention (fix when you can) - resolved but escrow/HB mismatch' then 'Human Intervention (fix when you can)'
		When [Escrow Analysis] = 'Human Intervention (fix when you can) - Not enough escrow'  then 'Human Intervention (fix when you can)'
		When [Update Questions?] = 'Human Intervention (fix when you can) - Resolved but question changes' then 'Human Intervention (fix when you can)'

		When [Claimant in SLAM correctly?] = 'Good' then 'Happy Path'
		When [Claimant on CSR?] = 'Good' then 'Happy Path'
		When [Escrow Analysis] = 'Happy Path - update needed' then 'Happy Path'
		When [Escrow Analysis] = 'Happy Path - Check COL' then 'Happy Path'
		When [Misc. Issues] = 'Good' then 'Happy Path'
		When [SA Matches?] = 'Good' then 'Happy Path'
		When [SSN Research] ='Good - No Issue' then 'Happy Path'
		When [SSN Research] ='SSN mismatch ok - trust SLAM' then 'Happy Path'
		When [Updated SLAM Final] = 'Happy Path - Final' then 'Happy Path'
		When [Rules for Q2, Q4, Questionnaire, Release] ='Normal Update Process' then 'Happy Path'
		When [Should we update?] = 'Ok to Update' then 'Happy Path'
		When [Update Questions?] = 'Questions need update' then 'Happy Path'
		When [Update HB?] = 'Happy Path - Update Needed' then 'Happy Path'

		When [Escrow Analysis] = 'Human Intervention - Close in SLAM' then 'Human Intervention - Close in SLAM'

		When [Escrow Analysis] = 'No Changes, No Issues - Resolved' then 'No Changes, No Issues'
		When [Escrow Analysis] = 'No Changes, No Issues - Resolved' then 'No Changes, No Issues'
		When [Update Questions?] = 'No changes, no issues - final' then 'No Changes, No Issues'
		When [Update Questions?] = 'No changes, no issues - resolved, Q Mismatch, but HB is good' then 'No Changes, No Issues'
		When [Updated Mcare] = 'No changes, no issues - Q Mismatch, but resolved and HB is good' then 'No Changes, No Issues'
		When [Updated Non PLRP] = 'No changes, no issues - Q Mismatch, but resolved and HB is good' then 'No Changes, No Issues'
		When [Updated Mcaid] = 'No changes, no issues - Q Mismatch, but resolved and HB is good' then 'No Changes, No Issues'
		When [Updated Third Party] = 'No changes, no issues - Q Mismatch, but resolved and HB is good' then 'No Changes, No Issues'
		When [Updated PLRP] = 'No changes, no issues - Q Mismatch, but resolved and HB is good' then 'No Changes, No Issues'
		When [Update HB?] = 'No Changes in HB' then 'No Changes, No Issues'
		
		Else 'Look Into'
		
		End As 'LF_Label'


From (
		Select 

		--Claimant Data
			--COL
			FirstName, LastName, [Claim Ref #], [COL Claim Number],[COL Attorney],[COL Case Name],[COL Payment Group], [Claim Status],

			--SLAM
			[S3 Client Id], [SLAM ThirdPartyId], [SLAM CaseName], [SLAM CaseId], 


		--Not in SLAM?
			Case
				When [Claim Status] = 'Withdrawn' then 'Not Eligible - Withdrawn'
				When [SLAM ThirdPartyId] is null then 'Human Intervention (fix this week) - Claimant data not pulling'
				When [SLAM CaseName] like '%EIF%' then 'Not Eligible - EIF'
				Else 'Good'
				End As 'Claimant in SLAM correctly?',


		--CSR
			[Current Escrow],

		--Not on CSR?
			Case
				When [CSR Claim #] is null then 'Not Eligible - Not on CSR'
				Else 'Good'
				End As 'Claimant on CSR?',


		--Escrow/Resolved
			Case
				When [Current Escrow] is NULL then 'Not Eligible - prepayment'
				When [SLAM ThirdPartyId] is null then 'Human Intervention (fix this week) - Claimant data not pulling from SLAM'
				When [SLAM CaseName] like '%EIF%' then 'Not Eligible - EIF'

				When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]<>[COL HB] and [SLAM Client Funded] = 'No' and [Current Escrow]/[COL SA] > .19 and [SLAM HB]>[Current Escrow] then 'Human Intervention (fix this week if time) - sum of liens is greater than escrow'
				When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]=[COL HB] and [COL HB]=[Current Escrow] and [SLAM Client Funded] = 'No' then 'Human Intervention - Close in SLAM'
				
				When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]=[COL HB] and [COL HB]<>[Current Escrow] and [SLAM Client Funded] = 'No' and [Current Escrow]/[COL SA] < .19 then 'Human Intervention (fix when you can) - May need update but not enough escrow'
				When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]<>[COL HB] and [SLAM Client Funded] = 'No' and [Current Escrow]/[COL SA] < .19 then 'Human Intervention (fix when you can) - HB mismatch and not enough escrow'
				When [Final (SLAM Summary)] = 'Yes' and [COL HB]<>[Current Escrow] and [SLAM Client Funded] = 'Yes' and [current escrow] <> 0 then 'Human Intervention (fix when you can) - resolved but escrow mismatch'
				When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]<>[COL HB] and [SLAM Client Funded] = 'Yes' then 'Human Intervention (fix when you can) - resolved but HB mismatch'
				When [Final (SLAM Summary)] <> 'Yes' and [SLAM Client Funded] = 'Yes' then 'Human Intervention (fix when you can) - resolved but not final'
				When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]<>[COL HB] and [SLAM Client Funded] = 'Yes' and [current escrow] <> 0 then 'Human Intervention (fix when you can) - resolved but escrow/HB mismatch'
				When [Final (SLAM Summary)] = 'Yes' and [Current Escrow]<>[COL HB] and [SLAM Client Funded] = 'Yes' and [current escrow] <> 0 then 'Human Intervention (fix when you can) - resolved but escrow/HB mismatch'

				When [Current Escrow]/[COL SA] < .19 then 'Human Intervention (fix when you can) - Not enough escrow' 

				When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]<>[COL HB] and [SLAM Client Funded] = 'No' and [Current Escrow]/[COL SA] > .19 and [SLAM HB]<=[Current Escrow] then 'Happy Path - update needed'
				
				When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]=[COL HB] and [COL HB]=[Current Escrow] and [SLAM Client Funded] = 'Yes' then 'No Changes, No Issues - Resolved'
				When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]=[COL HB] and [Current Escrow] = 0 and [SLAM Client Funded] = 'Yes' then 'No Changes, No Issues - Resolved'
				
				When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]=[COL HB] and [COL HB]<>[Current Escrow] and [SLAM Client Funded] = 'No' then 'Happy Path - Check COL'
				
				Else 'Look Into'
				End As 'Escrow Analysis',


		--Problems
			[#Problems], [Bad List Note], [#Prob Notes],
			Case
				When [COL Case Name] like '%comeback%' then 'Not Eligible - EIF'
				When [COL Case Name] like 'BLIZZARD & NABERS LLP' or [COL Case Name] like 'LEVIN SIMES LLP - WAVE 2' or [COL Case Name] like 'CLARK LOVE & HUTSON' or [COL Case Name] like 'TRACEY & FOX 29' then 'Not Eligible - Not a valid case'
				When [SLAM CaseId] = 2450 and [Bad List Note] is not null then 'Not Eligible - Burnett and on Bad List'
				When [SLAM CaseId] = 2184 and [SLAM DOI] like '%faulty%' then 'Not Eligible - Mostyn 2017 and DOI is placeholder'
				When [#Prob Notes] = 'Do not update in normal process' then 'Not Eligible - #Problems'
				When [#Prob Notes] = 'International Claimant' then 'Update Carefully - International Claimant' 
				Else 'Good'
				End as 'Misc. Issues',
						

		--SA Comparison
			[COL SA], [SLAM SA],
			Case
				When [#Problems] like '%EIF%' then 'Not Eligible - EIF'
				When [COL SA]<>[SLAM SA] then 'Human Intervention (CM) - SA mismatch'
				Else 'Good'
				End as 'SA Matches?',


		--SSN Comparison
			[COL SSN], [SLAM SSN], 
			Case
				When [COL SSN]<>[SLAM SSN] then 'Look Into SSN'
				Else 'Good'
				End as 'SSN Matches?',


		--Pull from SSN Research
			Case 
				When [COL SSN]=[SLAM SSN] then 'Good - No Issue'
				When [SSN Mismatch Research] = 'Trust SLAM' then 'SSN mismatch ok - trust SLAM'
				Else 'Human Intervention (CM) - SSN mismatch'
				End as 'SSN Research',


		--SLAM Final
			[Final (SLAM Summary)], [SLAM Finalized Status Id], [Truly Final/FinalizedStatusId Issue?], [SLAM Client Funded], 
			Case
				When [SLAM CaseId] IN (862) then [SLAM PreExisting Injuries]
				Else 'Ok - Not BA GRG'
				End as 'Completed by GRG HB Report?',
	

			--Calculate Updated SLAM Final
			Case
				When [Truly Final/FinalizedStatusId Issue?] = 'Issue' then 'Human Intervention (fix this week if time) - Scope issue'
				When [SLAM CaseId] IN (862) and [Final (SLAM Summary)] = 'Yes' and [SLAM PreExisting Injuries] not like '%Completed by%' then 'Human Intervention (fix this week) - No (GRG)'
				When [SLAM CaseId] IN (862) and [SLAM Finalized Status Id] = 2 and [SLAM PreExisting Injuries] not like '%Completed by%' then 'Human Intervention (fix this week) - No (GRG)'
				When [SLAM CaseId] IN (862) and [SLAM Finalized Status Id] = 3 and [SLAM PreExisting Injuries] not like '%Completed by%' then 'Human Intervention (fix this week) - No (GRG)'
				When [SLAM CaseId] IN (862) and [Final (SLAM Summary)] = 'Yes' and [SLAM PreExisting Injuries] is null then 'Human Intervention (fix this week) - No (GRG)'
				When [SLAM CaseId] IN (862) and [SLAM Finalized Status Id] = 2 and [SLAM PreExisting Injuries] is null then 'Human Intervention (fix this week) - No (GRG)'
				When [SLAM CaseId] IN (862) and [SLAM Finalized Status Id] = 3 and [SLAM PreExisting Injuries] is null then 'Human Intervention (fix this week) - No (GRG)'
				When [SLAM Client Funded] = 'Yes' and [Final (SLAM Summary)] = 'No' then 'Human Intervention (fix this week if time) - Resolved but not final'
				When [SLAM Client Funded] = 'Yes' and [Final (SLAM Summary)] = 'Yes' then 'Not Eligible - Resolved'
				When [Final (SLAM Summary)] = 'Yes' and [Truly Final/FinalizedStatusId Issue?] = 'Good' then 'Happy Path - Final'
				When [Final (SLAM Summary)] = 'No' and [Truly Final/FinalizedStatusId Issue?] = 'Good' then 'Not Eligible - Pending'
				Else 'Look Into'
				End As 'Updated SLAM Final',
		

		--Rules for Q2, Q4, Questionnaire, Release
			[SLAM Quest Recd], [Electronic Release Date], [Paper Release Date], [Updated Release Date], [Release Returned?], 
			Case
				When [SLAM CaseId] = 2184 and ([SLAM DOI] like '%multiple%' or [SLAM DOI] like '%faulty%') then 'Not Eligible - Leave Q2 and Q4 at No Answer - Placeholder DOI'
				When [SLAM CaseId] IN (2495, 1326, 1312, 2837, 2187, 2244, 402, 489, 2050, 1166, 653) and [COL Q4] = 'No Answer' and [COL HB] > .34 THEN 'Not Eligible - Leave Q4 at No Answer - firm answers'
				When [SLAM CaseId] IN (1910, 470) and [COL Q4] = 'No Answer' and [COL HB] > .34 then 'Not Eligible - Leave Q4 at No Answer (spreadsheet)'
				When [SLAM CaseId] IN (2284, 2450) and [SLAM Quest Recd] <> 1 and [COL Q4] = 'No Answer' and [COL HB] > .34 then 'Not Eligble - Leave Q4 at No Answer - Quest Recd not true'
				When [SLAM CaseId] = 2184 and [SLAM Quest Recd] <> 1 and [COL Q4] = 'No Answer' and [COL Non PLRP] = 'No Answer' and [COL HB] = .4 then 'Not Eligible - Leave Q2 and Q4 at No Answer - Quest Recd not true'
				When [SLAM CaseId] IN (483, 862) and [Release Returned?] = 'Within 3 weeks' and [COL Q4] = 'No Answer' and [COL HB] > .34 then 'Not Eligible - Leave Q4 at no answer - BA within 3 weeks'
				When [SLAM CaseId] IN (483, 862) and [Release Returned?] = 'No release' and [COL Q4] = 'No Answer' and [COL HB] > .34 then 'Not Eligible - Leave Q4 at no answer - BA no release'

				--When [SLAM CaseId] IN (2495, 1326, 1312, 2837, 2187, 2244, 402, 489, 2050, 1166, 653) and ([COL Q4] <> 'No Answer' or [COL HB] < .34) THEN 'Human Intervention (fix this week) - Q4 should be No Answer'
				--When [SLAM CaseId] IN (1910, 470) and ([COL Q4] <> 'No Answer' or [COL HB] < .34) then 'Human Intervention (fix this week) - Q4 should be No Answer (spreadsheet)'
				When [SLAM CaseId] IN (2284, 2450) and [SLAM Quest Recd] <> 1 and ([COL Q4] <> 'No Answer' or [COL HB] < .34) then 'Human Intervention (fix this week) - Q4 should No Answer - Quest Recd not true'
				When [SLAM CaseId] = 2184 and [SLAM Quest Recd] <> 1 and ([COL Q4] <> 'No Answer' or [COL Non PLRP] <> 'No Answer' or [COL HB] <> .4) then 'Human Intervention (fix this week) - Q2 and Q4 should be No Answer - Quest Recd not true'
				When [SLAM CaseId] IN (483, 862) and [Release Returned?] = 'Within 3 weeks' and ([COL Q4] <> 'No Answer' or [COL HB] < .34) then 'Human Intervention (fix this week) - Q4 should be no answer - BA within 3 weeks'
				When [SLAM CaseId] IN (483, 862) and [Release Returned?] = 'No release' and ([COL Q4] <> 'No Answer' or [COL HB] < .34) then 'Human Intervention (fix this week) - Q4 should be no answer - BA no release'
				When [SLAM CaseId] IN (483, 862) and [Release Returned?] = 'Look Into' then 'Human Intervention (fix this week) - Release Date Issue'
				
				Else 'Normal Update Process'
				
				End as 'Rules for Q2, Q4, Questionnaire, Release',

				
		--Should we update?
			Case
				When [SLAM Finalized Status Id] = 1 or [SLAM Finalized Status Id] is null then 'Not Eligible - pending'
				When [Final (SLAM Summary)] ='No' then 'Not Eligible - pending'
				
				When [Truly Final/FinalizedStatusId Issue?] = 'Issue' then 'Human Intervention (fix this week if time) - Finalized Status Id Issue'
				
				When [SLAM Client Funded] = 'Yes' and [Claim Status] = 'Post Payment Lien Deficient' then 'Human Intervention (fix this week if time) - resolved but post payment lien deficient'
				
				Else 'Ok to Update'
				End As 'Should we update?',


  -- Bulk Edit
		--Questions Analysis
			[COL Mcare], [COL Non PLRP], [COL Mcaid], [COL Third Party], [COL PLRP], 
			[SLAM Mcare], [SLAM Non PLRP], [SLAM Mcaid], [SLAM Third Party], [SLAM PLRP],
			
			Case
				When [Final (SLAM Summary)] = 'Yes' and [COL Mcare]=[SLAM Mcare] and [COL Non PLRP]=[SLAM Non PLRP] and [COL Mcaid]=[SLAM Mcaid] and [COL Third Party]=[SLAM Third Party] and [COL PLRP]=[SLAM PLRP] then 'No changes, no issues - final'
				When [SLAM Client Funded] = 'Yes' and ([COL Mcare]<>[SLAM Mcare] or [COL Non PLRP]<>[SLAM Non PLRP] or [COL Mcaid]<>[SLAM Mcaid] or [COL Third Party]<>[SLAM Third Party] or [COL PLRP]<>[SLAM PLRP]) and [SLAM HB]=[COL HB] then 'No changes, no issues - resolved, Q Mismatch, but HB is good'
				When [SLAM Client Funded] = 'Yes' and ([COL Mcare]<>[SLAM Mcare] or [COL Non PLRP]<>[SLAM Non PLRP] or [COL Mcaid]<>[SLAM Mcaid] or [COL Third Party]<>[SLAM Third Party] or [COL PLRP]<>[SLAM PLRP]) then 'Human Intervention (fix when you can) - Resolved but question changes'
				Else 'Questions need update'
				End as 'Update Questions?',

			Case
				When [SLAM Client Funded] = 'Yes' and [SLAM HB]=[COL HB] and [COL Mcare] <> [SLAM Mcare] then 'No changes, no issues - Q Mismatch, but resolved and HB is good'
				When [COL Mcare] = 'Yes' and [SLAM Mcare] <> 'Yes' then 'Human Intervention (fix this week) - Yes in COL but not in SLAM'
				Else [SLAM Mcare]
				End As 'Updated Mcare',
			Case
				When [SLAM Client Funded] = 'Yes' and [SLAM HB]=[COL HB] and [COL Non PLRP] <> [SLAM Non PLRP] then 'No changes, no issues - Q Mismatch, but resolved and HB is good'
				When [COL Non PLRP] = 'Yes' and [SLAM Non PLRP] <> 'Yes' then 'Human Intervention (fix this week) - Yes in COL but not in SLAM'
				Else [SLAM Non PLRP]
				End As 'Updated Non PLRP',
			Case
				When [SLAM Client Funded] = 'Yes' and [SLAM HB]=[COL HB] and [COL Mcaid] <> [SLAM Mcaid] then 'No changes, no issues- (Q Mismatch, but resolved and HB is good'
				When [COL Mcaid] = 'Yes' and [SLAM Mcaid] <> 'Yes' then 'Human Intervention (fix this week) - Yes in COL but not in SLAM'
				Else [SLAM Mcaid]
				End As 'Updated Mcaid',
			Case
				When [SLAM Client Funded] = 'Yes' and [SLAM HB]=[COL HB] and [COL Third Party] <> [SLAM Third Party] then 'No changes, no issues - Q Mismatch, but resolved and HB is good'
				When [COL Third Party] = 'Yes' and [SLAM Third Party] <> 'Yes' then 'Human Intervention (fix this week) - Yes in COL but not in SLAM'
				Else [SLAM Third Party]
				End As 'Updated Third Party',
			Case
				When [SLAM Client Funded] = 'Yes' and [SLAM HB]=[COL HB] and [COL PLRP] <> [SLAM PLRP] then 'No changes, no issues - Q Mismatch, but resolved and HB is good'
				When [COL PLRP] = 'Yes' and [SLAM PLRP] <> 'Yes' then 'Human Intervention (fix this week) - Yes in COL but not in SLAM'
				Else [SLAM PLRP]
				End As 'Updated PLRP',


		--Updated Holdback
			[COL HB], [SLAM HB],
			Case
				When [COL HB] = [SLAM HB] then 'No Changes in HB'
				When [COL HB] <> [SLAM HB] and [Final (SLAM Summary)] = 'Yes' then 'Happy Path - Update Needed'
				When [Final (SLAM Summary)] <> 'Yes' then 'Not Eligible - pending'
				Else 'Look Into'
				End as 'Update HB?',

			[SLAM HB] as 'SLAM HB/Updated HB'





		From 
				(select 
				--COL Search Extract
					JB_COLSearchExtract_Updated.[Implant Claimant First Name] as FirstName, JB_COLSearchExtract_Updated.[Implant Claimant Last Name] as LastName, JB_COLSearchExtract_Updated.[SSN] as 'COL SSN', JB_COLSearchExtract_Updated.[Claim Number] as 'COL Claim Number', 
					JB_COLSearchExtract_Updated.[Claim Status] as 'Claim Status',JB_COLSearchExtract_Updated.[Attorney Last Name] as 'COL Attorney',JB_COLSearchExtract_Updated.[Firm Name] as 'COL Case Name', JB_COLSearchExtract_Updated.Deficiencies as Deficiencies, 
					JB_COLSearchExtract_Updated.[Holdback Amount] as 'COL HB',JB_COLSearchExtract_Updated.[Third Party Enrolled] as 'COL Q4', JB_COLSearchExtract_Updated.[Actual Amount] as 'COL SA',JB_COLSearchExtract_Updated.[Payment Groups] as 'COL Payment Group',
					JB_COLSearchExtract_Updated.[Updated Release Date] as 'Updated Release Date', JB_COLSearchExtract_Updated.[Release Returned?] as 'Release Returned',
					JB_COLSearchExtract_Updated.[Electronic Release Date], JB_COLSearchExtract_Updated.[Paper Release Date], JB_COLSearchExtract_Updated.[Release Returned?], 
				
				--COL Bulk Edit Law Firm
					JB_BulkEdit_LF.[Claim Ref #] as 'Claim Ref #', JB_BulkEdit_LF.Process as Process, JB_BulkEdit_LF.[Claim Number] as 'Claim #', JB_BulkEdit_LF.[Medicare entitled] as 'COL Mcare',
					JB_BulkEdit_LF.[Non plrp plan enrolled] as 'COL Non PLRP', JB_BulkEdit_LF.[Medicaid entitled] as 'COL Mcaid', JB_BulkEdit_LF.[Third party enrolled] as 'COL Third Party',
					JB_BulkEdit_LF.[Plrp obligation] as 'COL PLRP',

				--SLAM Data: GetClientSummaryByCase
					JB_GetClientSummary.ThirdPartyId as 'SLAM ThirdPartyId', JB_GetClientSummary.ClientId as 'S3 Client Id',JB_GetClientSummary.SSN as 'SLAM SSN', JB_GetClientSummary.SettlementAmount as 'SLAM SA', 
					round(JB_GetClientSummary.[Total Holdback],2) as 'SLAM HB', JB_GetClientSummary.Final as 'Final (SLAM Summary)', JB_GetClientSummary.CaseName as 'SLAM CaseName',  
					JB_GetClientSummary.ClientPreExistingInjuries as 'SLAM PreExisting Injuries', JB_GetClientSummary.ClientFunded as 'SLAM Client Funded', JB_GetClientSummary.DescriptionOfInjury as 'SLAM DOI', 
					JB_GetClientSummary.FinalizedStatusId as 'SLAM Finalized Status Id', JB_GetClientSummary.[Truly Final?] as 'Truly Final/FinalizedStatusId Issue?', 
					JB_GetClientSummary.QuestionnaireReceived as 'SLAM Quest Recd', JB_GetClientSummary.MedicareEntitled as 'SLAM Mcare', JB_GetClientSummary.NonPlrpPlanEnrolled as 'SLAM Non PLRP',
					JB_GetClientSummary.MedicaidEntitled as 'SLAM Mcaid', JB_GetClientSummary.ThirdPartyEnrolled as 'SLAM Third Party', JB_GetClientSummary.PlrpObligation as 'SLAM PLRP', JB_GetClientSummary.CaseId as 'SLAM CaseId',

				--CSR
					JB_CSR_AMS.[Claim #] as 'CSR Claim #', JB_CSR_AMS.[Resolved Escrow Balance] as 'Current Escrow',

				--#Problems Summary
					JB_AMSProblems_Summary.[Claim #] as 'Prob Claim #', JB_AMSProblems_Summary.Issue as '#Problems', JB_AMSProblems_Summary.[COL Update Notes] as '#Prob Notes',

				--#Problems SSN Mismatches
					JB_AMSProblems_SSNResearch.[Claim Number], JB_AMSProblems_SSNResearch.[Trust Ours?] as 'SSN Mismatch Research',

				--Bad List
					JB_BurnettBadList.ClientId, JB_BurnettBadList.Note as 'Bad List Note'



					FROM            
						 JB_BulkEdit_LF LEFT OUTER JOIN
                         JB_CSR_AMS ON JB_BulkEdit_LF.[Claim number] = JB_CSR_AMS.[Claim #] LEFT OUTER JOIN
                         JB_COLSearchExtract_Updated ON JB_BulkEdit_LF.[Claim number] = JB_COLSearchExtract_Updated.[Claim number] LEFT OUTER JOIN
						 JB_BurnettBadList ON JB_BulkEdit_LF.[Claim number] = JB_BurnettBadList.ThirdPartyId LEFT OUTER JOIN
                         JB_AMSProblems_SSNResearch ON JB_BulkEdit_LF.[Claim number] = JB_AMSProblems_SSNResearch.[Claim Number] LEFT OUTER JOIN
                         JB_AMSProblems_Summary ON JB_BulkEdit_LF.[Claim number] = JB_AMSProblems_Summary.[Claim #] LEFT OUTER JOIN
                         JB_GetClientSummary ON JB_BulkEdit_LF.[Claim number] = JB_GetClientSummary.[ThirdPartyId] 
						 
				) as sub
		)as sub2


            
    """,
    con = engine
    )

    cms_df = pd.read_sql(
    """

Select	sub2.*,
		Case
			When [ThirdPartyId_Match?] = 'Not Eligible - not our lien type' then 'Not Eligible'
			When [Null_Liens] = 'Not Eligible - not our lien type' then 'Not Eligible'
			When [Status_Check] = 'Not Eligible - not our lien type' then 'Not Eligible'
			When [LienType_Check] = 'Not Eligible - not our lien type' then 'Not Eligible'
			When [LienId_Check] = 'Not Eligible - not our lien type' then 'Not Eligible'
			When [Amount_Check] = 'Not Eligible - not our lien type' then 'Not Eligible'
			When [Question_#_Check] = 'Not Eligible - not our lien type' then 'Not Eligible'
			When [Lienholder_Check] = 'Not Eligible - not our lien type' then 'Not Eligible'
			When [InSLAM_Check] = 'Not Eligible - not our lien type' then 'Not Eligible'

			When [ThirdPartyId_Match?] = 'Look Into' then 'Look Into'
			When [Null_Liens] = 'Look Into' then 'Look Into'
			When [Status_Check] = 'Look Into' then 'Look Into'
			When [LienType_Check] = 'Look Into' then 'Look Into'
			When [LienId_Check] = 'Look Into' then 'Look Into'
			When [Amount_Check] = 'Look Into' then 'Look Into'
			When [Question_#_Check] = 'Look Into' then 'Look Into'
			When [Lienholder_Check] = 'Look Into' then 'Look Into'

			When [ThirdPartyId_Match?] = 'Human Intervention (fix this week) - lientype of other' then 'Human Intervention (fix this week)'
			When [ThirdPartyId_Match?] = 'Human Intervention (fix this week) - ThirdPartyId mismatch' then 'Human Intervention (fix this week)'
			When [Null_Liens] = 'Human Intervention (fix this week) - lientype of other' then 'Human Intervention (fix this week)'
			When [Null_Liens] = 'Human Intervention (fix this week) - add lien but lienholder name too long' then 'Human Intervention (fix this week)'
			When [Status_Check] = 'Human Intervention (fix this week) - lientype of other' then 'Human Intervention (fix this week)'
			When [Status_Check] = 'Human Intervention (fix this week) - delete empty lien from COL' then 'Human Intervention (fix this week)'
			When [Status_Check] = 'Human Intervention (fix this week) - not entitled in COL but SLAM mismatch' then 'Human Intervention (fix this week)'
			When [Status_Check] = 'Human Intervention (fix this week) - lien was unfinalized' then 'Human Intervention (fix this week)'
			When [Status_Check] = 'Human Intervention (fix this week) - lien is not entitled in COL but mismatch in SLAM' then 'Human Intervention (fix this week)'
			When [LienType_Check] = 'Human Intervention (fix this week) - lientype of other' then 'Human Intervention (fix this week)'
			When [LienType_Check] = 'Human Intervention (fix this week) - COL lientype is null' then 'Human Intervention (fix this week)'
			When [LienType_Check] = 'Human Intervention (fix this week) - COL lientype <> SLAM lientype' then 'Human Intervention (fix this week)'
			When [LienId_Check] = 'Human Intervention (fix this week) - lientype of other' then 'Human Intervention (fix this week)'
			When [LienId_Check] = 'Human Intervention (fix this week) - COL Lien Id needs updating' then 'Human Intervention (fix this week)'
			When [LienId_Check] = 'Human Intervention (fix this week) - ThirdPartyId mismatch' then 'Human Intervention (fix this week)'
			When [Amount_Check] = 'Human Intervention (fix this week) - lientype of other' then 'Human Intervention (fix this week)'
			When [Amount_Check] = 'Human Intervention (fix this week) - SLAM and COL lien amounts mismatch' then 'Human Intervention (fix this week)'
			When [Amount_Check] = 'Human Intervention (fix this week) - COL is not null but SLAM is null' then 'Human Intervention (fix this week)'
			When [Amount_Check] = 'Human Intervention (fix this week) - COL lien is final but no amount' then 'Human Intervention (fix this week)'
			When [Question_#_Check] = 'Human Intervention (fix this week) - lientype of other' then 'Human Intervention (fix this week)'
			When [Question_#_Check] = 'Human Intervention (fix this week) - Unfinalized lien (Q#8)' then 'Human Intervention (fix this week)'
			When [Question_#_Check] = 'Human Intervention (fix this week) - Not entitled in COL but SLAM mismatch' then 'Human Intervention (fix this week)'
			When [Question_#_Check] = 'Human Intervention (fix this week) - Question # mismatch' then 'Human Intervention (fix this week)'
			When [Lienholder_Check] = 'Human Intervention (fix this week) - lientype of other' then 'Human Intervention (fix this week)'
			When [Lienholder_Check] = 'Human Intervention (fix this week) - Check lienholder name'  then 'Human Intervention (fix this week)'
			When [InSLAM_Check] = 'Human Intervention (fix this week) - Lien not pulling in SLAM data' then 'Human Intervention (fix this week)'
			When [InSLAM_Check] = 'Human Intervention (fix this week) - lientype of other' then 'Human Intervention (fix this week)'

			When [Null_Liens] = 'Happy Path - Add Lien' then 'Happy Path'
			When [Status_Check] = 'Happy Path - update to FNE' then 'Happy Path'
			When [Status_Check] = 'Happy Path - Update needed' then 'Happy Path'
			When [LienId_Check] = 'Happy Path - Add lien' then 'Happy Path'
			When [Amount_Check] = 'Happy Path - update needed' then 'Happy Path'
			When [Question_#_Check] = 'Happy Path - Update needed' then 'Happy Path'

			When [ThirdPartyId_Match?] = 'No change, no issue' then 'No change, no issue'
			When [Status_Check] = 'No change, no issue - not entitled' then 'No change, no issue'
			When [Status_Check] = 'No change, no issue - pending' then 'No change, no issue'
			When [LienType_Check] = 'No Changes, No Issues' then 'No change, no issue'
			When [LienId_Check] = 'No Changes, No Issues' then 'No change, no issue'
			When [Amount_Check] = 'No changes, no issues' then 'No change, no issue'
			When [Question_#_Check] = 'No changes, no issues' then 'No change, no issue'
			When [Lienholder_Check] = 'No changes, no issues' then 'No change, no issue'
			When [InSLAM_Check] = 'No changes, no issues' then 'No change, no issue'
			When [Null_Liens] = 'No update, no issue' then 'No change, no issue'
			
			Else 'Look Into'
			End as [Initial_CMS_Label],
	
		Case
			When [ThirdPartyId_Match?] = 'Not Eligible - not our lien type' then 'Not Eligible'
			When [Null_Liens] = 'Not Eligible - not our lien type' then 'Not Eligible'
			When [Status_Check] = 'Not Eligible - not our lien type' then 'Not Eligible'
			When [LienType_Check] = 'Not Eligible - not our lien type' then 'Not Eligible'
			When [LienId_Check] = 'Not Eligible - not our lien type' then 'Not Eligible'
			When [Amount_Check] = 'Not Eligible - not our lien type' then 'Not Eligible'
			When [Question_#_Check] = 'Not Eligible - not our lien type' then 'Not Eligible'
			When [Lienholder_Check] = 'Not Eligible - not our lien type' then 'Not Eligible'
			When [InSLAM_Check] = 'Not Eligible - not our lien type' then 'Not Eligible'

			When [ThirdPartyId_Match?] = 'Look Into' then 'Look Into'
			When [Null_Liens] = 'Look Into' then 'Look Into'
			When [Status_Check] = 'Look Into' then 'Look Into'
			When [LienType_Check] = 'Look Into' then 'Look Into'
			When [LienId_Check] = 'Look Into' then 'Look Into'
			When [Amount_Check] = 'Look Into' then 'Look Into'
			When [Question_#_Check] = 'Look Into' then 'Look Into'
			When [Lienholder_Check] = 'Look Into' then 'Look Into'

			When [ThirdPartyId_Match?] = 'Human Intervention (fix this week) - lientype of other' then 'Human Intervention (fix this week)'
			When [ThirdPartyId_Match?] = 'Human Intervention (fix this week) - ThirdPartyId mismatch' then 'Human Intervention (fix this week)'
			When [Null_Liens] = 'Human Intervention (fix this week) - lientype of other' then 'Human Intervention (fix this week)'
			When [Null_Liens] = 'Human Intervention (fix this week) - add lien but lienholder name too long' then 'Human Intervention (fix this week)'
			When [Status_Check] = 'Human Intervention (fix this week) - lientype of other' then 'Human Intervention (fix this week)'
			When [Status_Check] = 'Human Intervention (fix this week) - delete empty lien from COL' then 'Human Intervention (fix this week)'
			When [Status_Check] = 'Human Intervention (fix this week) - not entitled in COL but SLAM mismatch' then 'Human Intervention (fix this week)'
			When [Status_Check] = 'Human Intervention (fix this week) - lien was unfinalized' then 'Human Intervention (fix this week)'
			When [Status_Check] = 'Human Intervention (fix this week) - lien is not entitled in COL but mismatch in SLAM' then 'Human Intervention (fix this week)'
			When [LienType_Check] = 'Human Intervention (fix this week) - lientype of other' then 'Human Intervention (fix this week)'
			When [LienType_Check] = 'Human Intervention (fix this week) - COL lientype is null' then 'Human Intervention (fix this week)'
			When [LienType_Check] = 'Human Intervention (fix this week) - COL lientype <> SLAM lientype' then 'Human Intervention (fix this week)'
			When [LienId_Check] = 'Human Intervention (fix this week) - lientype of other' then 'Human Intervention (fix this week)'
			When [LienId_Check] = 'Human Intervention (fix this week) - COL Lien Id needs updating' then 'Human Intervention (fix this week)'
			When [LienId_Check] = 'Human Intervention (fix this week) - ThirdPartyId mismatch' then 'Human Intervention (fix this week)'
			When [Amount_Check] = 'Human Intervention (fix this week) - lientype of other' then 'Human Intervention (fix this week)'
			When [Amount_Check] = 'Human Intervention (fix this week) - SLAM and COL lien amounts mismatch' then 'Human Intervention (fix this week)'
			When [Amount_Check] = 'Human Intervention (fix this week) - COL is not null but SLAM is null' then 'Human Intervention (fix this week)'
			When [Amount_Check] = 'Human Intervention (fix this week) - COL lien is final but no amount' then 'Human Intervention (fix this week)'
			When [Question_#_Check] = 'Human Intervention (fix this week) - lientype of other' then 'Human Intervention (fix this week)'
			When [Question_#_Check] = 'Human Intervention (fix this week) - Unfinalized lien (Q#8)' then 'Human Intervention (fix this week)'
			When [Question_#_Check] = 'Human Intervention (fix this week) - Not entitled in COL but SLAM mismatch' then 'Human Intervention (fix this week)'
			When [Question_#_Check] = 'Human Intervention (fix this week) - Question # mismatch' then 'Human Intervention (fix this week)'
			When [Lienholder_Check] = 'Human Intervention (fix this week) - lientype of other' then 'Human Intervention (fix this week)'
			When [Lienholder_Check] = 'Human Intervention (fix this week) - Check lienholder name'  then 'Human Intervention (fix this week)'
			When [InSLAM_Check] = 'Human Intervention (fix this week) - Lien not pulling in SLAM data' then 'Human Intervention (fix this week)'
			When [InSLAM_Check] = 'Human Intervention (fix this week) - lientype of other' then 'Human Intervention (fix this week)'

			When [Null_Liens] = 'Happy Path - Add Lien' then 'Happy Path'
			When [Status_Check] = 'Happy Path - update to FNE' then 'Happy Path'
			When [Status_Check] = 'Happy Path - Update needed' then 'Happy Path'
			When [LienId_Check] = 'Happy Path - Add lien' then 'Happy Path'
			When [Amount_Check] = 'Happy Path - update needed' then 'Happy Path'
			When [Question_#_Check] = 'Happy Path - Update needed' then 'Happy Path'

			When [ThirdPartyId_Match?] = 'No change, no issue' then 'No change, no issue'
			When [Status_Check] = 'No change, no issue - not entitled' then 'No change, no issue'
			When [Status_Check] = 'No change, no issue - pending' then 'No change, no issue'
			When [LienType_Check] = 'No Changes, No Issues' then 'No change, no issue'
			When [LienId_Check] = 'No Changes, No Issues' then 'No change, no issue'
			When [Amount_Check] = 'No changes, no issues' then 'No change, no issue'
			When [Question_#_Check] = 'No changes, no issues' then 'No change, no issue'
			When [Lienholder_Check] = 'No changes, no issues' then 'No change, no issue'
			When [InSLAM_Check] = 'No changes, no issues' then 'No change, no issue'
			When [Null_Liens] = 'No update, no issue' then 'No change, no issue'
			
			Else 'Look Into'
			End as [CMS_Label]

From (
		Select	sub.*,

			--Third Party Id check
				Case
					When [COL LienType] like 'Attorney' and [COL Question #] > 5 then 'Not Eligible - not our lien type'
					When [COL LienType] like 'Litigation Finance' and [COL Question #] > 5 then 'Not Eligible - not our lien type'
					When [COL LienType] like 'Other' then 'Human Intervention (fix this week) - lientype of other'

					When [COL Claim number] <> [ThirdPartyId] then 'Human Intervention (fix this week) - ThirdPartyId mismatch'
					When [COL Claim number] = [ThirdPartyId] then 'No change, no issue'
					When [SLAM Status] is null or [SLAM Status] = 'Not Entitled' then 'No change, no issues'

					Else 'Look Into'
					End as [ThirdPartyId_Match?],

			--Check for Null liens
				Case
					When [COL LienType] like 'Attorney' and [COL Question #] > 5 then 'Not Eligible - not our lien type'
					When [COL LienType] like 'Litigation Finance' and [COL Question #] > 5 then 'Not Eligible - not our lien type'
					When [COL LienType] like 'Other' then 'Human Intervention (fix this week) - lientype of other'

					When [COL Id] is Null and [SLAM Status] = 'Final' and len([COL Lienholder]) <= 50 then 'Happy Path - Add Lien'
					When [COL Id] is Null and [SLAM Status] = 'Final' and len([COL Lienholder]) > 50 then 'Human Intervention (fix this week) - add lien but lienholder name too long' 
					
					When [COL Id] is not null then 'No update, no issue'

					Else 'Look Into'
					End as [Null_Liens],

			--Check Status
				Case
					When [COL LienType] like 'Attorney' and [COL Question #] > 5 then 'Not Eligible - not our lien type'
					When [COL LienType] like 'Litigation Finance' and [COL Question #] > 5 then 'Not Eligible - not our lien type'
					When [COL LienType] like 'Other' then 'Human Intervention (fix this week) - lientype of other'

					When [SLAM Status] = 'Look Into' then 'Look Into'

					When [COL Lienholder] is null and [COL LienType] is null and [COL Question #] is null and [COL Status] is null and [COL Amount] is null then 'Human Intervention (fix this week) - delete empty lien from COL'
					
					When [SLAM Status] = 'Not Entitled' and [COL Status] = 'Not Entitled' and [COL Amount] = 0 then 'No change, no issue - not entitled'
					When [SLAM Status] = 'Not Entitled' and [COL Status] <> 'Not Entitled' then 'Human Intervention (fix this week) - not entitled in COL but SLAM mismatch'
					When [SLAM Status] = 'Not Entitled' and [COL Status] = 'Pending' then 'Happy Path - update to FNE'
					
					When [SLAM OnBenefits] is null and [COL Status] = 'pending' then 'No change, no issue - pending'
					
					When [COL Status] = 'Final' and [SLAM Status] = 'Pending'  then 'Human Intervention (fix this week) - lien was unfinalized'
					When [COL Status] = 'Not Entitled' and [SLAM Status] = 'Final'  then 'Human Intervention (fix this week) - lien is not entitled in COL but mismatch in SLAM'
					When [COL Status] = 'Pending' and [SLAM Status] = 'Final' then 'Happy Path - Update needed'
					When [COL Status] is null and [SLAM Status] = 'Final' then 'Human Intervention (fix this week) - COL status is null'
					When [COL Status] = 'Pending' and [SLAM Status] = 'Pending' then 'No change, no issue - pending'
					When [COL Status] = 'Final' and [SLAM Status] = 'Final' then 'No change, no issue - pending'

					Else 'Look Into'
					End as [Status_Check],


			--Check the lien type
				Case 
					When [COL LienType] like 'Attorney' and [COL Question #] > 5 then 'Not Eligible - not our lien type'
					When [COL LienType] like 'Litigation Finance' and [COL Question #] > 5 then 'Not Eligible - not our lien type'
					When [COL LienType] like 'Other' then 'Human Intervention (fix this week) - lientype of other'

					When [COL LienType] is null then 'Human Intervention (fix this week) - COL lientype is null'
					When [COL LienType]<>[SLAM LienType] then 'Human Intervention (fix this week) - COL lientype <> SLAM lientype'
					When [COL LienType] = [SLAM LienType] then 'No Changes, No Issues'
					When [SLAM Status] is null or [SLAM Status] = 'Not Entitled' then 'No changes, no issues'

					Else 'Look Into'
					End as [LienType_Check],

			--Check LienId
				Case 
					When [COL LienType] like 'Attorney' and [COL Question #] > 5 then 'Not Eligible - not our lien type'
					When [COL LienType] like 'Litigation Finance' and [COL Question #] > 5 then 'Not Eligible - not our lien type'
					When [COL LienType] like 'Other' then 'Human Intervention (fix this week) - lientype of other'
					
					When [COL LienId] is Null and [COL Question #] <= 5 and [SLAM Onbenefits] is null then 'No Changes, No Issues'
					When [COL LienId] is Null and [COL Question #] <= 5 and [SLAM Onbenefits] = 'Yes'  then 'Happy Path - Add lien'
					When [COL LienId]<>[SLAM LienId] or [COL LienId] is Null then 'Human Intervention (fix this week) - COL Lien Id needs updating'
					When [COL LienId] = [SLAM LienId] and [COL Claim number]<>[ThirdPartyId] then 'Human Intervention (fix this week) - ThirdPartyId mismatch'
					When [COL LienId] = [SLAM LienId] then 'No Changes, No Issues'
					When [SLAM Status] is null or [SLAM Status] = 'Not Entitled' then 'No changes, no issues'
					Else 'Look Into'
					End as [LienId_Check],

			--Check Amount	
				Case 
					When [COL LienType] like 'Attorney' and [COL Question #] > 5 then 'Not Eligible - not our lien type'
					When [COL LienType] like 'Litigation Finance' and [COL Question #] > 5 then 'Not Eligible - not our lien type'
					When [COL LienType] like 'Other' then 'Human Intervention (fix this week) - lientype of other'
					
					When [COL Amount]<>Round([SLAM Amount],2) and [COL Question #] <= 5 and [COL Status] = 'Final' then 'Human Intervention (fix this week) - SLAM and COL lien amounts mismatch'
					When [SLAM Amount] is null and [COL Amount] is not null then 'Human Intervention (fix this week) - COL is not null but SLAM is null'
					When [COL Amount] is null and ([COL Status] = 'Final' or [COL Status] = 'Not Entitled') then 'Human Intervention (fix this week) - COL lien is final but no amount'
					When [COL Amount] <> 0 and [COL Status] = 'Not Entitled' then 'Human Intervention (fix this week) - COL lien is final but no amount'

					When [COL Amount] is null and [SLAM Amount] is not null and [COL Question #] <= 5 and [COL Status] = 'Pending' and [SLAM Status] = 'Final' then 'Happy Path - update needed'
										
					When [COL Amount] = Round([SLAM Amount],2) and [COL Question #] <= 5  then 'No changes, no issues'
					When [COL Amount] is null and [SLAM Status] = 'Pending' and [COL Status] = 'Pending' then 'No changes, no issues'
					When [COL Amount] is null and [SLAM Onbenefits] is null and [COL Status] = 'Pending' then 'No changes, no issues'
					When [COL Amount] = Round([SLAM Amount],2) and [COL Question #] <= 5 and [COL Status] = 'Final' and [SLAM Status] = 'Final' then 'No changes, no issues'
					When [COL Amount] = Round([SLAM Amount],2) and [COL Question #] <= 5 and [COL Status] = 'Not Entitled' and [SLAM Onbenefits] = 'No' then 'No changes, no issues'
					When [SLAM Status] is null or [SLAM Status] = 'Not Entitled' then 'No changes, no issues'

					Else 'Look Into'
					End as [Amount_Check],


			--Check Question number
				Case
					When [COL LienType] like 'Attorney' and [COL Question #] > 5 then 'Not Eligible - not our lien type'
					When [COL LienType] like 'Litigation Finance' and [COL Question #] > 5 then 'Not Eligible - not our lien type'
					When [COL LienType] like 'Other' then 'Human Intervention (fix this week) - lientype of other'

					When [COL Question #] > 5 and [COL LienType] <> 'Attorney' and [COL LienType] <> 'Other' and [COL LienType] <> 'Litigation Finance' and [COL Status] = 'Final' and [COL Amount] = 0 and [SLAM Status] = 'Final' then 'No changes, no issues'
					When [COL Question #] > 5 and [COL LienType] <> 'Attorney' and [COL LienType] <> 'Other' and [COL LienType] <> 'Litigation Finance' and [COL Status] = 'Pending' and [COL Amount] is null and [SLAM Status] = 'Pending' then 'No changes, no issues'
					When [COL Question #] > 5 and [COL LienType] <> 'Attorney' and [COL LienType] <> 'Other' and [COL LienType] <> 'Litigation Finance' and [COL Status] = 'Final' and [COL Amount] = 0 and [SLAM Onbenefits] = 'No' then 'No changes, no issues'
					When [COL Question #] > 5 and [COL LienType] <> 'Attorney' and [COL LienType] <> 'Other' and [COL LienType] <> 'Litigation Finance' and [COL Status] = 'Pending' and [COL Amount] is null and [SLAM Onbenefits] is null then 'No changes, no issues'

					When [COL Question #] > 5 and [COL LienType] <> 'Attorney' and [COL LienType] <> 'Other' and [COL LienType] <> 'Litigation Finance' and [COL Status] = 'Final' and [COL Amount] = 0 and [SLAM Status] <> 'Final' then 'Human Intervention (fix this week) - Unfinalized lien (Q#8)'
					When [COL Question #] > 5 and [COL LienType] <> 'Attorney' and [COL LienType] <> 'Other' and [COL LienType] <> 'Litigation Finance' and [COL Status] = 'Pending' and [COL Amount] is null and [SLAM Status] <> 'Pending' then 'Happy Path - Update needed'
					When [COL Question #] > 5 and [COL LienType] <> 'Attorney' and [COL LienType] <> 'Other' and [COL LienType] <> 'Litigation Finance' and [COL Status] = 'Final' and [COL Amount] = 0 and [SLAM Onbenefits] <> 'No' then 'Human Intervention (fix this week) - Not entitled in COL but SLAM mismatch'
					When [COL Question #] > 5 and [COL LienType] <> 'Attorney' and [COL LienType] <> 'Other' and [COL LienType] <> 'Litigation Finance' and [COL Status] = 'Pending' and [COL Amount] is null and [SLAM Onbenefits] is not null then 'Happy Path - update needed'

					When [COL Question #]<>[SLAM Question #] and [COL LienType] <> 'Attorney' and [COL LienType] <> 'Other' and [COL LienType] <> 'Litigation Finance' then 'Human Intervention (fix this week) - Question # mismatch'
					
					When [COL Question #] = [SLAM Question #] and [COL LienType] <> 'Attorney' and [COL LienType] <> 'Other' and [COL LienType] <> 'Litigation Finance' then 'No changes, no issues'
					When [SLAM Status] is null or [SLAM Status] = 'Not Entitled' then 'No changes, no issues'

					Else 'Look Into'
					End as [Question_#_Check],

			--Check Lienholder Name

				Case
					When len([COL Lienholder]) > 50 then 'Look Into'
					
					When [COL Lienholder] like '%United Healthcare%' and [SLAM Lienholder] like '%United Healthcare%' then 'No Changes, No Issues'
					When [COL Lienholder] like '%aetna%' and [SLAM Lienholder] like '%aetna%' then 'No Changes, No Issues'
					When [COL Lienholder] like '%humana%' and [SLAM Lienholder] like '%humana%' then 'No Changes, No Issues'
					When [COL Lienholder] like '%BCBS MN%' and [SLAM Lienholder] like '%BCBS Minnesota%' then 'No Changes, No Issues'
					When [COL Lienholder] like '%BCBS Minnesota%' and [SLAM Lienholder] like '%BCBS MN%' then 'No Changes, No Issues'
					When [COL Lienholder] like 'United Healthcare Community Plan of Ohio' and [SLAM Lienholder] like 'United Healthcare Community Plan of Ohio (aka Unison) (OH MCO)' then 'No Changes, No Issues'
					When [COL Lienholder] like 'Medical Health Insuring Corp (OH MCO)' and [SLAM Lienholder] like 'Medical Health Insuring Corp (OH MCO)/Medical Mutual of Ohio' then 'No Changes, No Issues'
					When [COL Lienholder] like 'Tufts%' and [SLAM Lienholder] like 'Tufts%' then 'No Changes, No Issues'
					When [COL Lienholder] like 'Walmart Stores, Inc. Associates H&W Plan' and [SLAM Lienholder] like 'Walmart Stores, Inc. Associates Health and Welfare Plan' then 'No Changes, No Issues'
					When [COL Lienholder] = 'Department of VA Office of General Counsel' and [SLAM Lienholder] = 'Department of Veterans Affairs Office of General Counsel 02 National Collections Group' then 'No Changes, No Issues'
					When [COL Lienholder] = 'Washington County - NY Medicaid - TA' and [SLAM Lienholder] = 'Washington County - NY Medicaid - Temporary Assistance' then 'No Changes, No Issues'
					When [COL Lienholder] = 'Tricare (Army) - Ft. Jackson' and [SLAM Lienholder] = 'Department of the Army' then 'No Changes, No Issues'
					When [COL Lienholder] = 'Walmart Stores, Inc. Associates H&W Plan' and [SLAM Lienholder] = 'Walmart Stores, Inc. Associates Health and Welfare Plan' then 'No Changes, No Issues'
					When [COL Lienholder] = 'IHS - Phoenix Indian Medical Center' and [SLAM Lienholder] = 'Indian Health Services' then 'No Changes, No Issues'
					When [COL Lienholder] = 'Arizona Physicians IPA Inc.' and [SLAM Lienholder] = 'Arizona Physicians IPA Inc/UHC' then 'No Changes, No Issues'
					When [COL Lienholder] = 'NY Medicaid - NYC County' and [SLAM Lienholder] = 'NY Medicaid - NYC' then 'No Changes, No Issues'
					When [COL Lienholder] = 'Community Health Plan' and [SLAM Lienholder] = 'Community Health Plan (WA MCO)' then 'No Changes, No Issues'
					When [COL Lienholder] like '%uhc%' and [SLAM Lienholder] like '%united healthcare%' then 'No Changes, No Issues'
					When [COL Lienholder] = 'NY State Catholic Health Plan (Fidelis Care)' and [SLAM Lienholder] = 'New York State Catholic Health Plan (Fidelis Care)' then 'No Changes, No Issues'
					When [COL Lienholder] = 'Medical Health Insuring Corp/Medical Mutual' and [SLAM Lienholder] = 'Medical Health Insuring Corp (OH MCO)/Medical Mutual of Ohio' then 'No Changes, No Issues'
					When [COL Lienholder] = 'United Mine Workers of America Health&Retirement' and [SLAM Lienholder] = 'United Mine Workers of America Health & Retirement' then 'No Changes, No Issues'
					When [COL Lienholder] = 'Lifemasters Supported Healthcare/Staywell' and [SLAM Lienholder] = 'Lifemasters Supported Healthcare/Staywell/Wellcare' then 'No Changes, No Issues'
					When [COL Lienholder] = 'Central States, SE and SW Area H and W Fund' and [SLAM Lienholder] = 'Central States, Southeast and Southwest Area Health and Welfare Fund' then 'No Changes, No Issues'
					When [COL Lienholder] = 'Office Management & ENT Services Employees Group' and [SLAM Lienholder] = 'Office of Management and Enterprise Services Employees Group Insurance Department' then 'No Changes, No Issues'
					When [COL Lienholder] = 'Monroe County - Temporary Assistance' and [SLAM Lienholder] = 'Monroe County - NY Medicaid - Temporary Assistance' then 'No Changes, No Issues'
					When [COL Lienholder] = 'United  Workers of America Health&Retirement' and [SLAM Lienholder] = 'United Mine Workers of America Health & Retirement' then 'No Changes, No Issues'
					When [COL Lienholder] = 'NY Medicaid - Cattaragus County' and [SLAM Lienholder] = 'NY Medicaid - Cattaraugus County' then 'No Changes, No Issues'
					When [COL Lienholder] = 'Chautauqua County - NY Medicaid - TA' and [SLAM Lienholder] = 'Chautauqua County - NY Medicaid - TA' then 'No Changes, No Issues'
					When [COL Lienholder] = 'Anthem BCMineBS/Wellpoint' and [SLAM Lienholder] = 'Anthem Blue Cross Blue Shield' then 'No Changes, No Issues'
					When [COL Lienholder] = 'Onondaga County - NY Mcaid - Temp Assistance' and [SLAM Lienholder] = 'Onondaga County - NY Medicaid - Temporary Assistance' then 'No Changes, No Issues'
					When [COL Lienholder] = 'OK Medicaid' and [SLAM Lienholder] = 'OK Medicaid - Conduent' then 'No Changes, No Issues'
					When [COL Lienholder] = 'Wellcare' and [SLAM Lienholder] = 'Wellcare - PLRP' then 'No Changes, No Issues'
					When [COL Lienholder] = '%army%' and [SLAM Lienholder] = '%army%' then 'No Changes, No Issues'
					When [COL Lienholder] = 'General Motors LLC' and [SLAM Lienholder] = 'General Motors LLC' then 'No Changes, No Issues'
					When [COL Lienholder] = 'Regence BCBS of Oregon/Utah' and [SLAM Lienholder] = 'Cambia Health Solutions/Regence' then 'No Changes, No Issues'
					When [COL Lienholder] = 'Presbyterian Senior Care HMO' and [SLAM Lienholder] = 'Presbyterian Senior Care (HMO)' then 'No Changes, No Issues'
					When [COL Lienholder] = 'Sunshine State Health Plan/Centene' and [SLAM Lienholder] = 'Sunshine Health/Centene' then 'No Changes, No Issues'
					When [COL Lienholder] = 'Medical Health Insuring Corp (OH MCO)' and [SLAM Lienholder] = 'Medical Health Insuring Corp (OH MCO)%' then 'No Changes, No Issues'
					When [COL Lienholder] = 'United Healthcare Community Plan of Ohio%' and [SLAM Lienholder] = 'United Healthcare Community Plan of Ohio%' then 'No Changes, No Issues'
					When ([COL Lienholder] = '%United Healthcare%' and [SLAM Lienholder] = '%United Healthcare%') or ([COL Lienholder] = 'United Healthcare' and [SLAM Lienholder] = '%UHC%') then 'No Changes, No Issues'
					When ([COL Lienholder] = '%UHC%' and [SLAM Lienholder] = '%United Healthcare%') or ([COL Lienholder] = '%UHC%' and [SLAM Lienholder] = '%UHC%') then 'No Changes, No Issues'
					When [COL Lienholder] like '%HealthSpring%' and [SLAM Lienholder] like '%HealthSpring%' then 'No Changes, No Issues'
					When [COL Lienholder] = '%Kaiser%' and [SLAM Lienholder] = '%Kaiser%' then 'No Changes, No Issues'
					When [COL Lienholder] = '%Department of VA Office of General Counsel%' and [SLAM Lienholder] = '%Department of Veterans Affairs Office of General Counsel 02 National Collections Group%' then 'No Changes, No Issues'
					When [COL Lienholder] = '%Suffolk County - NY Medicaid - TA%' and [SLAM Lienholder] = '%Suffolk County - NY Medicaid - Temporary Assistance%' then 'No Changes, No Issues'
					
					When len([COL Lienholder]) <= 50 and [COL Lienholder] = [SLAM Lienholder] then 'No changes, no issues' 
					When len([COL Lienholder]) <= 50 and [COL Lienholder] <> [SLAM Lienholder] then 'Human Intervention (fix this week) - Check lienholder name' 
					
					When [COL LienType] like 'Attorney' and [COL Question #] > 5 then 'Not Eligible - not our lien type'
					When [COL LienType] like 'Litigation Finance' and [COL Question #] > 5 then 'Not Eligible - not our lien type'
					When [COL LienType] like 'Other' then 'Human Intervention (fix this week) - lientype of other'
					
					When [SLAM Status] is null or [SLAM Status] = 'Not Entitled' then 'No changes, no issues'

					Else 'Look Into'
					End as [Lienholder_Check],


			--Liens Not Pulling
			Case
				When [SLAM Status] is null or [SLAM Status] = 'Not Entitled' then 'No changes, no issues'
				When [ThirdPartyId] is Null then 'Human Intervention (fix this week) - Lien not pulling in SLAM data'
				When [COL LienType] like 'Attorney' and [COL Question #] > 5 then 'Not Eligible - not our lien type'
				When [COL LienType] like 'Litigation Finance' and [COL Question #] > 5 then 'Not Eligible - not our lien type'
				When [COL LienType] like 'Other' then 'Human Intervention (fix this week) - lientype of other'
				Else 'No changes, no issues'
				End as [InSLAM_Check]

		From 
			(

				SELECT 
					--COL Data: CMS Tab
							CAST(CMS.[Claim Ref #] as nvarchar) as 'Claim Ref #', CMS.[Lien Id] as 'COL LienId', CMS.[Lien type] as 'COL LienType', CMS.[Question number] as 'COL Question #',CMS.[Status] as 'COL Status', 
							dbo.fixnumerictext(CMS.[Amount]) as 'COL Amount', CMS.[Lien holder] as 'COL Lienholder', CMS.Id as 'COL Id',
	
					--COL Data: LF Tab
							LF.[Claim number] as 'COL Claim number',SE.[Firm Name] as 'COL CaseName',

					--SLAM Data
							Liens.[ThirdPartyId] as 'ThirdPartyId', Liens.[LienId] as 'SLAM LienId', Liens.[COL_LienType] as 'SLAM LienType', Liens.[Question] as 'SLAM Question #', 
							Liens.[Status] as 'SLAM Status', Liens.[True Final Demand] as 'SLAM Amount', Liens.[LienHolderName] as 'SLAM Lienholder',
							
							FPV.Stage as 'SLAM Stage', FPV.ClosedReason as 'SLAM ClosedReason', FPV.OnBenefits as 'SLAM OnBenefits'

				FROM		CMS_Updated as CMS
							LEFT OUTER JOIN JB_GetClientOnBenefitSummary_JAM as Liens ON CMS.[Lien Id] = Liens.[LienId]  
							LEFT OUTER JOIN JB_BulkEdit_LF as LF ON CMS.[Claim Ref #] = LF.[Claim Ref #]
							LEFT OUTER JOIN JB_COLSearchExtract as SE on CMS.[Claim Number] = SE.[Claim Number]
							LEFT OUTER JOIN JB_GetClientOnBenefitSummary_FPV as FPV ON CMS.[Lien Id] = FPV.[LienId] 

			 ) as sub			
	) as sub2

    """,
    con = engine
    )

    # merge dataframes to compare, rename columns
    lf_df['Claim Ref #']=lf_df['Claim Ref #'].astype(int)
    cms_df['Claim Ref #']=cms_df['Claim Ref #'].astype(int)
    combined_df = pd.merge(lf_df, cms_df, on = 'Claim Ref #')

    #combined_df = combined_df.rename(columns={"LF_Initial_Label": "LF_Label", "CMS_Initial_Label": "CMS_Label"})

    #Pull Labels from both df into a combined df. Set labels based off matrix
    for index, row in combined_df.iterrows():
        
        if row['LF_Label'] != row['CMS_Label']:
        
            # 1. Not Eligible
            if row['LF_Label'] == 'Not Eligible':
                combined_df.loc[index, 'CMS_Label'] = row['LF_Label']
			
			# 2. Look Into
            elif row['LF_Label'] == 'Look Into':
                combined_df.loc[index, 'CMS_Label'] = row['LF_Label']         

            elif row['CMS_Label'] == 'Look Into':
                combined_df.loc[index, 'LF_Label'] = row['CMS_Label']
                
            # 3. Human Intervention 

            elif row['LF_Label'] == 'Human Intervention (CM)':
                combined_df.loc[index, 'CMS_Label'] = row['LF_Label']
            elif row['LF_Label'] == 'Human Intervention (fix this week)':
                combined_df.loc[index, 'CMS_Label'] = row['LF_Label']
            elif row['LF_Label'] == 'Human Intervention (fix this week if time)':
                combined_df.loc[index, 'CMS_Label'] = row['LF_Label']
            elif row['LF_Label'] == 'Human Intervention (fix when you can)':
                combined_df.loc[index, 'CMS_Label'] = row['LF_Label']
            elif row['LF_Label'] == 'Human Intervention - Close in SLAM' and row['CMS_Label'] in ['Human Intervention (fix this week)', 'Happy Path']:#Good
                combined_df.loc[index, 'LF_Label'] = 'Human Intervention (fix this week)'
                combined_df.loc[index, 'CMS_Label'] = 'Human Intervention (fix this week)'
            elif row['LF_Label'] == 'Human Intervention - Close in SLAM' and row['CMS_Label'] == 'No Changes, No Issues':
                combined_df.loc[index, 'CMS_Label'] = 'Human Intervention - Close in SLAM'
            elif row['LF_Label'] == 'Human Intervention - Close in SLAM' and row['CMS_Label'] == 'No Changes, No Issues':
                combined_df.loc[index, 'LF_Label'] = 'Human Intervention - Close in SLAM'
                combined_df.loc[index, 'CMS_Label'] = 'Human Intervention - Close in SLAM'
            elif row['LF_Label'] == 'No Changes, No Issues' and row['CMS_Label'] == 'Human Intervention (fix this week)':
                combined_df.loc[index, 'LF_Label'] = row['CMS_Label']
                
            # 4. No changes
            elif row['LF_Label'] == 'No Changes, No Issues' and row['CMS_Label'] == 'No Changes, No Issues':
                combined_df.loc[index, 'LF_Label'] = 'No Changes, No Issues'
                combined_df.loc[index, 'CMS_Label'] = 'No Changes, No Issues' 
                
            # 5. Happy Path
            elif row['LF_Label'] == 'Happy Path' and row['CMS_Label'] == 'Human Intervention (fix this week)':
                combined_df.loc[index, 'LF_Label'] = row['CMS_Label']
            elif row['LF_Label'] == 'Happy Path' and row['CMS_Label'] == 'Happy Path':
                combined_df.loc[index, 'LF_Label'] = row['CMS_Label']
            elif row['LF_Label'] == 'Happy Path' and row['CMS_Label'] == 'Add Lien':
                combined_df.loc[index, 'LF_Label'] = row['CMS_Label']
            elif row['LF_Label'] == 'Happy Path' and row['CMS_Label'] == 'No Changes, No Issues':
                combined_df.loc[index, 'CMS_Label'] = row['LF_Label']
            elif row['LF_Label'] == 'No Changes, No Issues' and row['CMS_Label'] == 'Happy Path': #Go Over with JB
                combined_df.loc[index, 'LF_Label'] = row['CMS_Label']

    # Pull original LF analysis, Happy path and Combined Analysis into spreadsheet for col2.py 
    lf_df.to_excel('./excel_results/LF.xlsx')
    cms_df.to_excel('./excel_results/CMS.xlsx')
    happypath = combined_df[combined_df['LF_Label'] == 'Happy Path']
    happypath.to_excel('./excel_results/HappyPath.xlsx')
    addlien = combined_df[combined_df['LF_Label'] == 'Add Lien']
    addlien.to_excel('./excel_results/NewLiens.xlsx')
    combined_df.to_excel('./excel_results/Full_Analysis.xlsx', index = False)
    print('SQL code has completed, on to updates!')