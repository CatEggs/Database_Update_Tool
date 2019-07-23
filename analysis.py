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
		When [COL Claim Number] is null then 'Human Intervention (fix this week)'
		When [Claimant in SLAM correctly?] = 'Human Intervention (fix this week) - Claimant data not pulling' then 'Human Intervention (fix this week)'
		When [Escrow Analysis] = 'Human Intervention (fix this week) - Claimant data not pulling from SLAM' then 'Human Intervention (fix this week)'

		When [Claimant in SLAM correctly?] like 'Not Eligible%' then 'Not Eligible'
		When [Claimant on CSR?] like 'Not Eligible%' then 'Not Eligible'
		When [Escrow Analysis] like 'Not Eligible%' then 'Not Eligible'
		When [Misc. Issues] like 'Not Eligible%' then 'Not Eligible'
		When [SA Matches?] = 'Not Eligible - EIF' then 'Not Eligible'
		When [Rules for Q2, Q4, Questionnaire, Release] like 'Not Eligible%' then 'Not Eligible'
		When [Should we update?] like 'Not Eligible%' then 'Not Eligible'
		When [Update HB?] = 'Not Eligible - pending' then 'Not Eligible'
		When [SSN Research] = 'No Update - pending CM response' then 'Not Eligible'

		When [SSN Research] = 'Look Into' then 'Look Into'
		When [Escrow Analysis] = 'Look Into' then 'Look Into'
		When [Updated SLAM Final] = 'Look Into' then 'Look Into'
		When [Update HB?] = 'Look Into' then 'Look Into'
	
		When [SA Matches?] = 'Human Intervention (CM) - SA mismatch' then 'Human Intervention (CM)'
		When [SSN Research] = 'Notify CM' then 'Human Intervention (CM)'

		When [SSN Research] = 'Research - Add to SSN Research in #Problems; notify CM if needed' then 'Human Intervention (fix this week)'
		When [Escrow Analysis] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
		When [Updated SLAM Final] = 'Human Intervention (fix this week) - No (GRG)' then 'Human Intervention (fix this week)'
		When [Rules for Q2, Q4, Questionnaire, Release] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
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
		When [SSN Research] like 'Research%' then 'Human Intervention (fix this week if time)'
		When [Update HB?] = 'Happy Path - Update Needed' and [SLAM Client Funded] = 'Yes' then 'Human Intervention (fix this week if time)'

		When [Escrow Analysis] like 'Human Intervention (fix when you can)%' then 'Human Intervention (fix when you can)'
		When [Update Questions?] = 'Human Intervention (fix when you can) - Resolved but question changes' then 'Human Intervention (fix when you can)'
		
		When [Escrow Analysis] = 'Human Intervention - Close in SLAM' and [Claimant in SLAM correctly?] = 'Good' and ([Misc. Issues] = 'Good' or [Misc. Issues] like 'Update Carefully%') and [SA Matches?] = 'Good' and ([SSN Research] ='Good - No Issue' or [SSN Research] ='SSN mismatch ok - trust SLAM') and [Rules for Q2, Q4, Questionnaire, Release] ='Normal Update Process' and [Should we update?] = 'Ok to Update' then 'Human Intervention - Close in SLAM'
		
		When [Escrow Analysis] = 'Happy Path - update needed' then 'Happy Path'
		When [Escrow Analysis] = 'Happy Path - Check COL' then 'Happy Path'
		When [Update Questions?] = 'Questions need update' then 'Happy Path'
		When [Update HB?] = 'Happy Path - Update Needed' then 'Happy Path'

		When [Escrow Analysis] = 'No change, no issue - Resolved' and [Claimant in SLAM correctly?] = 'Good' and ([Misc. Issues] = 'Good' or [Misc. Issues] like 'Update Carefully%') and [SA Matches?] = 'Good' and ([SSN Research] ='Good - No Issue' or [SSN Research] ='SSN mismatch ok - trust SLAM') and [Rules for Q2, Q4, Questionnaire, Release] ='Normal Update Process' and [Should we update?] = 'Ok to Update' then 'No change, no issue'
		When [Update Questions?] = 'No change, no issue - final' and [Claimant in SLAM correctly?] = 'Good' and ([Misc. Issues] = 'Good' or [Misc. Issues] like 'Update Carefully%') and [SA Matches?] = 'Good' and ([SSN Research] ='Good - No Issue' or [SSN Research] ='SSN mismatch ok - trust SLAM') and [Rules for Q2, Q4, Questionnaire, Release] ='Normal Update Process' and [Should we update?] = 'Ok to Update' then 'No change, no issue'
		When [Escrow Analysis] = 'No change, no issue - Resolved' then 'No change, no issue'
		When [Escrow Analysis] = 'No change, no issue - Resolved' then 'No change, no issue'
		When [Update Questions?] = 'No change, no issue - final' then 'No change, no issue'
		When [Update Questions?] = 'No change, no issue - resolved, Q Mismatch, but HB is good' then 'No change, no issue'
		When [Updated Mcare] = 'No change, no issue - Q Mismatch, but resolved and HB is good' then 'No change, no issue'
		When [Updated Non PLRP] = 'No change, no issue - Q Mismatch, but resolved and HB is good' then 'No change, no issue'
		When [Updated Mcaid] = 'No change, no issue - Q Mismatch, but resolved and HB is good' then 'No change, no issue'
		When [Updated Third Party] = 'No change, no issue - Q Mismatch, but resolved and HB is good' then 'No change, no issue'
		When [Updated PLRP] = 'No change, no issue - Q Mismatch, but resolved and HB is good' then 'No change, no issue'
		When [Update HB?] = 'No Changes in HB' then 'No change, no issue'
		When [Updated SLAM Final] = 'No change, no issue - Resolved' then 'No change, no issue'

		Else 'Look Into'
		
		End As 'Initial_LF_Label',
	Case
		When [COL Claim Number] is null then 'Human Intervention (fix this week)'
		When [Claimant in SLAM correctly?] = 'Human Intervention (fix this week) - Claimant data not pulling' then 'Human Intervention (fix this week)'
		When [Escrow Analysis] = 'Human Intervention (fix this week) - Claimant data not pulling from SLAM' then 'Human Intervention (fix this week)'

		When [Claimant in SLAM correctly?] like 'Not Eligible%' then 'Not Eligible'
		When [Claimant on CSR?] like 'Not Eligible%' then 'Not Eligible'
		When [Escrow Analysis] like 'Not Eligible%' then 'Not Eligible'
		When [Misc. Issues] like 'Not Eligible%' then 'Not Eligible'
		When [SA Matches?] = 'Not Eligible - EIF' then 'Not Eligible'
		When [Rules for Q2, Q4, Questionnaire, Release] like 'Not Eligible%' then 'Not Eligible'
		When [Should we update?] like 'Not Eligible%' then 'Not Eligible'
		When [Update HB?] = 'Not Eligible - pending' then 'Not Eligible'
		When [SSN Research] = 'No Update - pending CM response' then 'Not Eligible'

		When [SSN Research] = 'Look Into' then 'Look Into'
		When [Escrow Analysis] = 'Look Into' then 'Look Into'
		When [Updated SLAM Final] = 'Look Into' then 'Look Into'
		When [Update HB?] = 'Look Into' then 'Look Into'
	
		When [SA Matches?] = 'Human Intervention (CM) - SA mismatch' then 'Human Intervention (CM)'
		When [SSN Research] = 'Notify CM' then 'Human Intervention (CM)'

		When [SSN Research] = 'Research - Add to SSN Research in #Problems; notify CM if needed' then 'Human Intervention (fix this week)'
		When [Escrow Analysis] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
		When [Updated SLAM Final] = 'Human Intervention (fix this week) - No (GRG)' then 'Human Intervention (fix this week)'
		When [Rules for Q2, Q4, Questionnaire, Release] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
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
		When [SSN Research] like 'Research%' then 'Human Intervention (fix this week if time)'
		When [Update HB?] = 'Happy Path - Update Needed' and [SLAM Client Funded] = 'Yes' then 'Human Intervention (fix this week if time)'

		When [Escrow Analysis] like 'Human Intervention (fix when you can)%' then 'Human Intervention (fix when you can)'
		When [Update Questions?] = 'Human Intervention (fix when you can) - Resolved but question changes' then 'Human Intervention (fix when you can)'
		
		When [Escrow Analysis] = 'Human Intervention - Close in SLAM' and [Claimant in SLAM correctly?] = 'Good' and ([Misc. Issues] = 'Good' or [Misc. Issues] like 'Update Carefully%') and [SA Matches?] = 'Good' and ([SSN Research] ='Good - No Issue' or [SSN Research] ='SSN mismatch ok - trust SLAM') and [Rules for Q2, Q4, Questionnaire, Release] ='Normal Update Process' and [Should we update?] = 'Ok to Update' then 'Human Intervention - Close in SLAM'
		
		When [Escrow Analysis] = 'Happy Path - update needed' then 'Happy Path'
		When [Escrow Analysis] = 'Happy Path - Check COL' then 'Happy Path'
		When [Update Questions?] = 'Questions need update' then 'Happy Path'
		When [Update HB?] = 'Happy Path - Update Needed' then 'Happy Path'

		When [Escrow Analysis] = 'No change, no issue - Resolved' and [Claimant in SLAM correctly?] = 'Good' and ([Misc. Issues] = 'Good' or [Misc. Issues] like 'Update Carefully%') and [SA Matches?] = 'Good' and ([SSN Research] ='Good - No Issue' or [SSN Research] ='SSN mismatch ok - trust SLAM') and [Rules for Q2, Q4, Questionnaire, Release] ='Normal Update Process' and [Should we update?] = 'Ok to Update' then 'No change, no issue'
		When [Update Questions?] = 'No change, no issue - final' and [Claimant in SLAM correctly?] = 'Good' and ([Misc. Issues] = 'Good' or [Misc. Issues] like 'Update Carefully%') and [SA Matches?] = 'Good' and ([SSN Research] ='Good - No Issue' or [SSN Research] ='SSN mismatch ok - trust SLAM') and [Rules for Q2, Q4, Questionnaire, Release] ='Normal Update Process' and [Should we update?] = 'Ok to Update' then 'No change, no issue'
		When [Escrow Analysis] = 'No change, no issue - Resolved' then 'No change, no issue'
		When [Escrow Analysis] = 'No change, no issue - Resolved' then 'No change, no issue'
		When [Update Questions?] = 'No change, no issue - final' then 'No change, no issue'
		When [Update Questions?] = 'No change, no issue - resolved, Q Mismatch, but HB is good' then 'No change, no issue'
		When [Updated Mcare] = 'No change, no issue - Q Mismatch, but resolved and HB is good' then 'No change, no issue'
		When [Updated Non PLRP] = 'No change, no issue - Q Mismatch, but resolved and HB is good' then 'No change, no issue'
		When [Updated Mcaid] = 'No change, no issue - Q Mismatch, but resolved and HB is good' then 'No change, no issue'
		When [Updated Third Party] = 'No change, no issue - Q Mismatch, but resolved and HB is good' then 'No change, no issue'
		When [Updated PLRP] = 'No change, no issue - Q Mismatch, but resolved and HB is good' then 'No change, no issue'
		When [Update HB?] = 'No Changes in HB' then 'No change, no issue'
		When [Updated SLAM Final] = 'No change, no issue - Resolved' then 'No change, no issue'
		
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
				When [Final (SLAM Summary)] <> 'Yes' and ([SLAM Finalized Status Id] = 2 or [SLAM Finalized Status Id] = 3) then 'Human Intervention (fix this week) - Finalization Issue in SLAM'
				When [Final (SLAM Summary)] <> 'Yes' and [SLAM Client Funded] <> 'Yes' then 'Not Eligible - not final in SLAM'

				When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]=[COL HB] and [COL HB]=[Current Escrow] and [SLAM Client Funded] = 'Yes' then 'No change, no issue - Resolved'
				When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]=[COL HB] and [Current Escrow] = 0 and [SLAM Client Funded] = 'Yes' then 'No change, no issue - Resolved'
				When [SLAM Client Funded] = 'Yes' and [Final (SLAM Summary)] = 'Yes' then 'No change, no issue - Resolved'

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
				When [SSN Mismatch Research] is null then 'Research - Add to SSN Research in #Problems; notify CM if needed'
				When [SSN Mismatch Research] = 'Needs Research' --and [Date CM Notified] is null 
				then 'Notify CM'
				--When [SSN Mismatch Research] = 'Needs Research' and [Date CM Notified] <= (getdate()-30) then 'Research - has it been updated in SLAM? If not, notify CM'
				--When [SSN Mismatch Research] = 'Needs Research' and [Date CM Notified] > (getdate()-30) then 'No Update - pending CM response'
				Else 'Look Into'
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
				When [SLAM Client Funded] = 'Yes' and [Final (SLAM Summary)] = 'Yes' then 'No change, no issue - Resolved'
				When [Final (SLAM Summary)] = 'Yes' and [Truly Final/FinalizedStatusId Issue?] = 'Good' then 'Final'
				When [Final (SLAM Summary)] = 'No' and [Truly Final/FinalizedStatusId Issue?] = 'Good' then 'Pending'
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
				When [Final (SLAM Summary)] = 'Yes' and [COL Mcare]=[SLAM Mcare] and [COL Non PLRP]=[SLAM Non PLRP] and [COL Mcaid]=[SLAM Mcaid] and [COL Third Party]=[SLAM Third Party] and [COL PLRP]=[SLAM PLRP] then 'No change, no issue - final'
				When [SLAM Client Funded] = 'Yes' and ([COL Mcare]<>[SLAM Mcare] or [COL Non PLRP]<>[SLAM Non PLRP] or [COL Mcaid]<>[SLAM Mcaid] or [COL Third Party]<>[SLAM Third Party] or [COL PLRP]<>[SLAM PLRP]) and [SLAM HB]=[COL HB] then 'No change, no issue - resolved, Q Mismatch, but HB is good'
				When [SLAM Client Funded] = 'Yes' and ([COL Mcare]<>[SLAM Mcare] or [COL Non PLRP]<>[SLAM Non PLRP] or [COL Mcaid]<>[SLAM Mcaid] or [COL Third Party]<>[SLAM Third Party] or [COL PLRP]<>[SLAM PLRP]) then 'Human Intervention (fix when you can) - Resolved but question changes'
				Else 'Questions need update'
				End as 'Update Questions?',

			Case
				When [SLAM Client Funded] = 'Yes' and [SLAM HB]=[COL HB] and [COL Mcare] <> [SLAM Mcare] then 'No change, no issue - Q Mismatch, but resolved and HB is good'
				When [COL Mcare] = 'Yes' and [SLAM Mcare] <> 'Yes' then 'Human Intervention (fix this week) - Yes in COL but not in SLAM'
				Else [SLAM Mcare]
				End As 'Updated Mcare',
			Case
				When [SLAM Client Funded] = 'Yes' and [SLAM HB]=[COL HB] and [COL Non PLRP] <> [SLAM Non PLRP] then 'No change, no issue - Q Mismatch, but resolved and HB is good'
				When [COL Non PLRP] = 'Yes' and [SLAM Non PLRP] <> 'Yes' then 'Human Intervention (fix this week) - Yes in COL but not in SLAM'
				Else [SLAM Non PLRP]
				End As 'Updated Non PLRP',
			Case
				When [SLAM Client Funded] = 'Yes' and [SLAM HB]=[COL HB] and [COL Mcaid] <> [SLAM Mcaid] then 'No change, no issue- Q Mismatch, but resolved and HB is good'
				When [COL Mcaid] = 'Yes' and [SLAM Mcaid] <> 'Yes' then 'Human Intervention (fix this week) - Yes in COL but not in SLAM'
				Else [SLAM Mcaid]
				End As 'Updated Mcaid',
			Case
				When [SLAM Client Funded] = 'Yes' and [SLAM HB]=[COL HB] and [COL Third Party] <> [SLAM Third Party] then 'No change, no issue - Q Mismatch, but resolved and HB is good'
				When [COL Third Party] = 'Yes' and [SLAM Third Party] <> 'Yes' then 'Human Intervention (fix this week) - Yes in COL but not in SLAM'
				Else [SLAM Third Party]
				End As 'Updated Third Party',
			Case
				When [SLAM Client Funded] = 'Yes' and [SLAM HB]=[COL HB] and [COL PLRP] <> [SLAM PLRP] then 'No change, no issue - Q Mismatch, but resolved and HB is good'
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
			When [COL LienType] = 'Litigation Finance' or [COL LienType] = 'Attorney' or [COL LienType] = 'Child Care' then 'No change, no issue'
			When [COL LienType] = 'Other' and ([COL Lienholder] like '%trustee%' or [COL Lienholder] like '%Ch. 13%' or [COL Lienholder] like '%Ch. 7%' or [COL Lienholder] like '%Bankruptcy%' or [COL Lienholder] like '%chapter%' or [COL Lienholder] like '%law%' or [COL Lienholder] like '%mortgage%') then 'No change, no issue'
			When [COL Question #] > 5 and ([COL Lienholder] like '%trustee%' or [COL Lienholder] like '%Ch. 13%' or [COL Lienholder] like '%Ch. 7%' or [COL Lienholder] like '%Bankruptcy%' or [COL Lienholder] like '%chapter%' or [COL Lienholder] like '%law%' or [COL Lienholder] like '%mortgage%') then 'No change, no issue'
			When [COL Lienholder] like '%EIF%' then 'Not Eligible'
			When [SLAM LienType] = 'Medicare Lien - Duplicate' or [SLAM LienType] = 'Private Lien'  or [SLAM LienType] = 'Look Into' then 'Look Into'
			When [COL LienType] = 'Look Into' then 'Look Into'
			When [Status_Check] = 'Not Eligible' then 'Not Eligible'
			When [New Liens?] = 'Not Eligible' then 'Not Eligible'
			When [LienType_Check] = 'Not Eligible' then 'Not Eligible'
			When [Amount_Check] = 'Not Eligible' then 'Not Eligible'
			When [Lienholder_Check] = 'Not Eligible' then 'Not Eligible'
			When [Question_#_Check] = 'Not Eligible' then 'Not Eligible'
			When [ThirdPartyId_Match?] = 'Not Eligible' then 'Not Eligible'
			When [LienId_Check] = 'Not Eligible' then 'Not Eligible'
			When [InSLAM_Check] = 'Not Eligible' then 'Not Eligible'

			When [Status_Check] = 'Human Intervention (fix this week) - LienId is NULL in COL' then 'Human Intervention (fix this week)'

			When [ThirdPartyId_Match?] = 'Look Into' then 'Look Into'
			When [New Liens?] = 'Look Into' then 'Look Into'
			When [Status_Check] = 'Look Into' then 'Look Into'
			When [LienType_Check] = 'Look Into' then 'Look Into'
			When [LienId_Check] = 'Look Into' then 'Look Into'
			When [Amount_Check] = 'Look Into' then 'Look Into'
			When [Question_#_Check] = 'Look Into' then 'Look Into'
			When [Lienholder_Check] = 'Look Into' then 'Look Into'
			
			When [ThirdPartyId_Match?] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [New Liens?] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [Status_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [LienType_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [LienId_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [Amount_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [Question_#_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [Lienholder_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [InSLAM_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			
			When [New Liens?] = 'Happy Path - Add Lien' then 'Add Lien'
			When [LienId_Check] = 'Happy Path - Add lien' then 'Add Lien'
			
			When [Status_Check] like 'Happy Path%' then 'Happy Path'
			When [Amount_Check] like 'Happy Path%' then 'Happy Path'
			When [Question_#_Check] like 'Happy Path%' then 'Happy Path'
			When [Lienholder_Check] like 'Happy Path%' then 'Happy Path'

			When [ThirdPartyId_Match?] = 'No change, no issue' then 'No change, no issue'
			When [Status_Check] = 'No change, no issue' then 'No change, no issue'
			When [LienType_Check] = 'No change, no issue' then 'No change, no issue'
			When [LienId_Check] = 'No change, no issue' then 'No change, no issue'
			When [Amount_Check] = 'No change, no issue' then 'No change, no issue'
			When [Question_#_Check] = 'No change, no issue' then 'No change, no issue'
			When [Lienholder_Check] = 'No change, no issue' then 'No change, no issue'
			When [InSLAM_Check] = 'No change, no issue' then 'No change, no issue'
			When [New Liens?] = 'No update, no issue' then 'No change, no issue'
			
			Else 'Look Into'
			End as [Initial_CMS_Label],
	
		Case
			When [COL LienType] = 'Litigation Finance' or [COL LienType] = 'Attorney' or [COL LienType] = 'Child Care' then 'No change, no issue'
			When [COL LienType] = 'Other' and ([COL Lienholder] like '%trustee%' or [COL Lienholder] like '%Ch. 13%' or [COL Lienholder] like '%Ch. 7%' or [COL Lienholder] like '%Bankruptcy%' or [COL Lienholder] like '%chapter%' or [COL Lienholder] like '%law%' or [COL Lienholder] like '%mortgage%') then 'No change, no issue'
			When [COL Question #] > 5 and ([COL Lienholder] like '%trustee%' or [COL Lienholder] like '%Ch. 13%' or [COL Lienholder] like '%Ch. 7%' or [COL Lienholder] like '%Bankruptcy%' or [COL Lienholder] like '%chapter%' or [COL Lienholder] like '%law%' or [COL Lienholder] like '%mortgage%') then 'No change, no issue'
			When [COL Lienholder] like '%EIF%' then 'Not Eligible'
			When [SLAM LienType] = 'Medicare Lien - Duplicate' or [SLAM LienType] = 'Private Lien'  or [SLAM LienType] = 'Look Into' then 'Look Into'
			When [COL LienType] = 'Look Into' then 'Look Into'
			When [Status_Check] = 'Not Eligible' then 'Not Eligible'
			When [New Liens?] = 'Not Eligible' then 'Not Eligible'
			When [LienType_Check] = 'Not Eligible' then 'Not Eligible'
			When [Amount_Check] = 'Not Eligible' then 'Not Eligible'
			When [Question_#_Check] = 'Not Eligible' then 'Not Eligible'
			When [Lienholder_Check] = 'Not Eligible' then 'Not Eligible'
			When [ThirdPartyId_Match?] = 'Not Eligible' then 'Not Eligible'
			When [LienId_Check] = 'Not Eligible' then 'Not Eligible'
			When [InSLAM_Check] = 'Not Eligible' then 'Not Eligible'

			When [Status_Check] = 'Human Intervention (fix this week) - LienId is NULL in COL' then 'Human Intervention (fix this week)'

			When [ThirdPartyId_Match?] = 'Look Into' then 'Look Into'
			When [New Liens?] = 'Look Into' then 'Look Into'
			When [Status_Check] = 'Look Into' then 'Look Into'
			When [LienType_Check] = 'Look Into' then 'Look Into'
			When [LienId_Check] = 'Look Into' then 'Look Into'
			When [Amount_Check] = 'Look Into' then 'Look Into'
			When [Question_#_Check] = 'Look Into' then 'Look Into'
			When [Lienholder_Check] = 'Look Into' then 'Look Into'

			When [ThirdPartyId_Match?] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [New Liens?] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [Status_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [LienType_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [LienId_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [Amount_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [Question_#_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [Lienholder_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [InSLAM_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			
			When [New Liens?] = 'Happy Path - Add Lien' then 'Add Lien'
			When [LienId_Check] = 'Happy Path - Add lien' then 'Add Lien'
			
			When [Status_Check] like 'Happy Path%' then 'Happy Path'
			When [Amount_Check] like 'Happy Path%' then 'Happy Path'
			When [Question_#_Check] like 'Happy Path%' then 'Happy Path'
			When [Lienholder_Check] like 'Happy Path%' then 'Happy Path'

			When [ThirdPartyId_Match?] = 'No change, no issue' then 'No change, no issue'
			When [Status_Check] = 'No change, no issue' then 'No change, no issue'
			When [LienType_Check] = 'No change, no issue' then 'No change, no issue'
			When [LienId_Check] = 'No change, no issue' then 'No change, no issue'
			When [Amount_Check] = 'No change, no issue' then 'No change, no issue'
			When [Question_#_Check] = 'No change, no issue' then 'No change, no issue'
			When [Lienholder_Check] = 'No change, no issue' then 'No change, no issue'
			When [InSLAM_Check] = 'No change, no issue' then 'No change, no issue'
			When [New Liens?] = 'No update, no issue' then 'No change, no issue'
			
			Else 'Look Into'
			End as [CMS_Label]

From (
		Select	sub.*,

			--Third Party Id check
				Case
					When [COL Claim number] = [ThirdPartyId] then 'No change, no issue'

					When [SLAM LienId] is not null and [SLAM OnBenefits] is null and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Status] = 'Pending' and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Stage] <> 'Closed' or [SLAM Stage] not like 'final%' and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Stage] is null and [SLAM OnBenefits] is null and [COL LienId] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - Lien Id needs update'

					When [COL Lienholder] is null and [COL LienType] is null and [COL Question #] is null and [COL Status] is null and [COL Amount] is null then 'Human Intervention (fix this week) - delete empty lien from COL'
					When [COL LienId] is null and [Claim Ref #] is not null and [COL LienType] is not null then 'Human Intervention (fix this week) - LienId is NULL in COL'
					When [COL LienId] is null and [COL LienType] is not null and [SLAM LienId] is null then 'Human Intervention (fix this week) - LienId is NULL in COL'

					When [COL LienType] like 'Attorney' and [COL Question #] > 5 then 'No change, no issue'
					When [COL LienType] like 'Litigation Finance' and [COL Question #] > 5 then 'No change, no issue'
					When [COL LienType] like 'Other' then 'Human Intervention (fix this week) - lientype of other'

					When [SLAM Status] = 'Not Entitled' and [COL Status] = 'Not Entitled' then 'No change, no issue'
					When [SLAM Stage] = 'Final No Entitlement' and [COL Status] = 'Not Entitled' then 'No change, no issue'
					When ([SLAM ClosedReason] = 'Resolved - No Entitlement' or [SLAM ClosedReason] = 'Opened in Error' or [SLAM ClosedReason] like 'per att%') and [COL Status] = 'Not Entitled' then 'No change, no issue'

					When [COL Claim number] <> [ThirdPartyId] then 'Human Intervention (fix this week) - ThirdPartyId mismatch'
					
					Else 'Look Into'
					End as [ThirdPartyId_Match?],
					

			--Check for New liens
				Case
					When [COL Lienholder] is null and [COL LienType] is null and [COL Question #] is null and [COL Status] is null and [COL Amount] is null then 'Human Intervention (fix this week) - delete empty lien from COL'
					When [COL LienId] is null and [Claim Ref #] is not null and [COL LienType] is not null then 'Human Intervention (fix this week) - LienId is NULL in COL'
					When [COL LienId] is null and [COL LienType] is not null and [SLAM LienId] is null then 'Human Intervention (fix this week) - LienId is NULL in COL'

					When [SLAM LienId] is not null and [SLAM OnBenefits] is null and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Status] = 'Pending' and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Stage] is null and [SLAM OnBenefits] is null and [COL LienId] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - Lien Id needs update'
					When [SLAM Stage] <> 'Closed' or [SLAM Stage] not like 'final%' and [COL Status] = 'Pending' then 'Not Eligible'

					When [COL Id] is Null and [SLAM Status] = 'Final' and len([COL Lienholder]) <= 50 then 'Happy Path - Add Lien'
					When [COL Id] is Null and [SLAM Status] = 'Final' and len([COL Lienholder]) > 50 then 'Human Intervention (fix this week) - add lien but lienholder name too long' 
					
					When [COL Id] is Null and [SLAM Status] = 'Pending' then 'Not Eligible'
					When [COL Id] is Null and ([SLAM Stage] not like 'Final%' or [SLAM Stage] <> 'Closed') then 'Not Eligible'

					When [COL Id] is not null then 'No update, no issue'

					Else 'Look Into'
					End as [New Liens?],

			--Check Status
				Case
					When [SLAM Status] = 'Look Into' then 'Look Into'

					When [COL Lienholder] is null and [COL LienType] is null and [COL Question #] is null and [COL Status] is null and [COL Amount] is null then 'Human Intervention (fix this week) - delete empty lien from COL'
					When [COL LienId] is null and [Claim Ref #] is not null and [COL LienType] is not null then 'Human Intervention (fix this week) - LienId is NULL in COL'
					When [COL LienId] is null and [COL LienType] is not null and [SLAM LienId] is null then 'Human Intervention (fix this week) - LienId is NULL in COL'
					
					When [SLAM LienId] is not null and [SLAM OnBenefits] is null and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Status] = 'Pending' and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Stage] <> 'Closed' or [SLAM Stage] not like 'final%' and [COL Status] = 'Pending' then 'Not Eligible'
					
					When [SLAM Stage] is null and [SLAM OnBenefits] is null and [COL LienId] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - Lien Id needs update'
					
					When ([SLAM Stage] not like 'Final%' and [SLAM Stage] not like 'Closed') and [COL Status] = 'Final' then 'Human Intervention (fix this week) - final in COL but pending in SLAM'
					When [COL Status] is null and [COL Id] is not null then 'Human Intervention (fix this week) - COL status is null'
					When [COL Status] = 'Final' and [SLAM Status] = 'Pending' then 'Human Intervention (fix this week) - final in COL but pending in SLAM'
					When [COL Status] = 'Not Entitled' and [SLAM Status] = 'Final'  then 'Human Intervention (fix this week) - lien is not entitled in COL but mismatch in SLAM'
					When [SLAM Status] = 'Not Entitled' and ([COL Status] <> 'Not Entitled' or [COL Amount] <> 0) then 'Human Intervention (fix this week) - not entitled in SLAM but COL mismatch'
					When [SLAM Stage] = 'Closed' and [SLAM ClosedReason] like 'Resolved - No Entitlement' and ([COL Status] <> 'Not Entitled' or [COL Amount] <> 0) then 'Human Intervention (fix this week) - not entitled in SLAM but COL mismatch'
					When [SLAM Stage] = 'Closed' and [SLAM ClosedReason] like 'Opened in Error' and ([COL Status] <> 'Not Entitled' or [COL Amount] <> 0) then 'Human Intervention (fix this week) - not entitled in SLAM but COL mismatch'
					When [SLAM Stage] = 'Closed' and [SLAM ClosedReason] like 'Per Att%' and ([COL Status] <> 'Not Entitled' or [COL Amount] <> 0) then 'Human Intervention (fix this week) - not entitled in SLAM but COL mismatch'
					When [SLAM Stage] = 'Final No Entitlement' and [SLAM ClosedReason] like 'Per Att%' and ([COL Status] <> 'Not Entitled' or [COL Amount] <> 0) then 'Human Intervention (fix this week) - not entitled in SLAM but COL mismatch'
					When [SLAM Stage] = 'Closed' and [SLAM ClosedReason] is null then 'Human Intervention (Fix this week) - update SLAM closedreason'
					When [COL LienId] = '9999999' then 'Human Intervention (fix this week) - LienId is not valid - delete out of COL?'
					When [COL LienId] is not null and [COL Id] is not null and [SLAM Stage] is null and [SLAM LienType] is null then 'Human Intervention (fix this week) - Check case in SLAM - claimant is probably not in the right case'
					When [COL LienId] is null and [COL Id] is not null and [SLAM Stage] is null and [SLAM LienType] is null then 'Human Intervention (fix this week) - Lien might not be in SLAM'

					When [COL Status] = 'Pending' and [SLAM Status] = 'Final' then 'Happy Path - Update needed'
					When [COL Status] = 'Pending' and [SLAM Stage] = 'Final No Entitlement' then 'Happy Path - Update needed'
					When [COL Status] = 'Pending' and ([SLAM ClosedReason] = 'Opened in Error' or [SLAM ClosedReason] = 'Resolved - No Entitlement' or [SLAM ClosedReason] like 'Per Att%') then 'Happy Path - Update needed'
					
					
					When [COL Status] = 'Final' and [SLAM Status] = 'Final' then 'No change, no issue'
					When [SLAM Status] = 'Not Entitled' and [COL Status] = 'Not Entitled' and [COL Amount] = 0 then 'No change, no issue'
					When [SLAM Stage] = 'Closed' and [SLAM ClosedReason] like 'Resolved - No Entitlement' and [COL Status] = 'Not Entitled' then 'No Change, no issue'
					When [SLAM Stage] = 'Closed' and [SLAM ClosedReason] like 'Opened in Error' and [COL Status] = 'Not Entitled' then 'No Change, no issue'
					When [SLAM Stage] = 'Closed' and [SLAM ClosedReason] like 'Per Att%' and [COL Status] = 'Not Entitled' then 'No Change, no issue'
					When [SLAM Stage] = 'Final No Entitlement' and [COL Status] = 'Not Entitled' then 'No Change, no issue'

					When [COL LienType] like 'Attorney' and [COL Question #] > 5 then 'No change, no issue'
					When [COL LienType] like 'Litigation Finance' and [COL Question #] > 5 then 'No change, no issue'
					When [COL LienType] like 'Other' then 'Human Intervention (fix this week) - lientype of other'

					Else 'Look Into'
					End as [Status_Check],

			
			--Updated SLAM Status
				Case
					When [COL Lienholder] is null and [COL LienType] is null and [COL Question #] is null and [COL Status] is null and [COL Amount] is null then 'Human Intervention (fix this week) - delete empty lien from COL'
					When [COL LienId] is null and [Claim Ref #] is not null and [COL LienType] is not null then 'Human Intervention (fix this week) - LienId is NULL in COL'
					When [COL LienId] is null and [COL LienType] is not null and [SLAM LienId] is null then 'Human Intervention (fix this week) - LienId is NULL in COL'

					When [COL LienType] like 'Attorney' and [COL Question #] > 5 then [COL Status]
					When [COL LienType] like 'Litigation Finance' and [COL Question #] > 5 then [COL Status]
					
					When [SLAM Status] = 'Final' and [COL Status] = 'Final' then 'Final'
					When [SLAM Status] = 'Final' and [COL Status] = 'Pending' then 'Final'
					When [SLAM Status] = 'Not Entitled' and [COL Status] = 'Not Entitled' then 'Not Entitled'
					When [SLAM Status] = 'Not Entitled' and [COL Status] = 'Pending' then 'Not Entitled'
					When [SLAM Status] = 'Pending' and [COL Status] = 'Pending' then 'Pending'

					When [COL Status] = 'Not Entitled' and [SLAM Status] = 'Not Entitled' then 'Not Entitled'
					When [COL Status] = 'Not Entitled' and [SLAM Stage] = 'Final No Entitlement' then 'Not Entitled'
					When [COL Status] = 'Not Entitled' and [SLAM Stage] = 'Closed' and [SLAM ClosedReason] = 'Opened in Error' then 'Not Entitled'
					When [COL Status] = 'Not Entitled' and [SLAM Stage] = 'Closed' and [SLAM ClosedReason] like 'Per Att%' then 'Not Entitled'
					When [COL Status] = 'Not Entitled' and [SLAM Stage] = 'Closed' and [SLAM ClosedReason] like 'Resolved - No Entitlement' then 'Not Entitled'
					When [COL Status] = 'Pending' and [SLAM Status] = 'Not Entitled' then 'Not Entitled'
					When [COL Status] = 'Pending' and [SLAM Stage] = 'Final No Entitlement' then 'Not Entitled'
					When [COL Status] = 'Pending' and [SLAM Stage] = 'Closed' and [SLAM ClosedReason] = 'Opened in Error' then 'Not Entitled'
					When [COL Status] = 'Pending' and [SLAM Stage] = 'Closed' and [SLAM ClosedReason] like 'Per Att%' then 'Not Entitled'

					When [SLAM Status] = 'Final' and ([COL Status] <> 'Final' or [COL Status] <> 'Pending') then 'Issue'
					When [SLAM Status] = 'Not Entitled' and ([COL Status] = 'Not Entitled' or [COL Status] <> 'Pending') then 'Issue'
					When [SLAM Status] = 'Pending' and [COL Status] <> 'Pending' then 'Issue'
					When ([COL Status] <> 'Pending' or [COL Status] <> 'Not Entitled') and [SLAM Stage] = 'Final No Entitlement' then 'Issue'
					When ([COL Status] <> 'Pending' or [COL Status] <> 'Not Entitled') and [SLAM Stage] = 'Closed' and [SLAM ClosedReason] = 'Opened in Error' then 'Issue'
					When ([COL Status] <> 'Pending' or [COL Status] <> 'Not Entitled') and [SLAM Stage] = 'Closed' and [SLAM ClosedReason] like 'Per Att%' then 'Issue'

					When [COL LienType] like 'Other' then 'Human Intervention (fix this week) - lientype of other'

					Else 'Look Into'
					End as 'Updated Status',


			--Check the lien type
				Case 
					When [COL Lienholder] is null and [COL LienType] is null and [COL Question #] is null and [COL Status] is null and [COL Amount] is null then 'Human Intervention (fix this week) - delete empty lien from COL'
					When [COL LienId] is null and [Claim Ref #] is not null and [COL LienType] is not null then 'Human Intervention (fix this week) - LienId is NULL in COL'
					When [COL LienId] is null and [COL LienType] is not null and [SLAM LienId] is null then 'Human Intervention (fix this week) - LienId is NULL in COL'

					When [SLAM LienId] is not null and [SLAM OnBenefits] is null and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Status] = 'Pending' and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Stage] <> 'Closed' or [SLAM Stage] not like 'final%' and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Stage] is null and [SLAM OnBenefits] is null and [COL LienId] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - Lien Id needs update'
					
					When [COL LienType] is null then 'Human Intervention (fix this week) - COL lientype is null'
					When [COL LienType]<>[SLAM LienType] then 'Human Intervention (fix this week) - COL lientype <> SLAM lientype'
					
					When [COL LienType] = [SLAM LienType] then 'No change, no issue'
					When [SLAM Status] = 'Not Entitled' then 'No change, no issue'
					
					When [SLAM OnBenefits] is null then 'Not Eligible'

					When [COL LienType] like 'Attorney' and [COL Question #] > 5 then 'No change, no issue'
					When [COL LienType] like 'Litigation Finance' and [COL Question #] > 5 then 'No change, no issue'
					When [COL LienType] like 'Other' then 'Human Intervention (fix this week) - lientype of other'

					When [SLAM LienType (converted)] = [COL LienType] and [SLAM LienType] is null and [SLAM Stage] = 'Closed' then 'No Change, no issue'
					When [SLAM LienType (converted)] = [COL LienType] and [SLAM OnBenefits] is null and [COL Status] = 'Pending' and [SLAM LienId] is not null then 'Not Eligible'
					When [SLAM LienType (converted)] = [COL LienType] and [SLAM OnBenefits] is null and [COL Status] <> 'Pending' and [SLAM LienId] is not null then 'Human Intervention (fix this week) - Pending in SLAM but not in COL'
					
					Else 'Look Into'
					End as [LienType_Check],


			--Check LienId
				Case 
					When [COL Lienholder] is null and [COL LienType] is null and [COL Question #] is null and [COL Status] is null and [COL Amount] is null then 'Human Intervention (fix this week) - delete empty lien from COL'
					When [COL LienId] is null and [Claim Ref #] is not null and [COL LienType] is not null then 'Human Intervention (fix this week) - LienId is NULL in COL'
					When [COL LienId] is null and [COL LienType] is not null and [SLAM LienId] is null then 'Human Intervention (fix this week) - LienId is NULL in COL'

					When [SLAM LienId] is not null and [SLAM OnBenefits] is null and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Status] = 'Pending' and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Stage] <> 'Closed' or [SLAM Stage] not like 'final%' and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Stage] is null and [SLAM OnBenefits] is null and [COL LienId] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - Lien Id needs update'
					
					When [COL LienId]<>[SLAM LienId] or [COL LienId] is Null then 'Human Intervention (fix this week) - COL Lien Id needs updating'
					When [COL LienId] = [SLAM LienId] and [COL Claim number]<>[ThirdPartyId] then 'Human Intervention (fix this week) - ThirdPartyId mismatch'

					When [COL LienId] is Null and [COL Question #] <= 5 and [SLAM Onbenefits] = 'Yes'  then 'Happy Path - Add lien'

					When [COL LienId] = [SLAM LienId] then 'No change, no issue'
					When [COL LienId] is Null and [COL Question #] <= 5 and [SLAM Onbenefits] is null then 'No change, no issue'
					When [SLAM Status] is null or [SLAM Status] = 'Not Entitled' then 'No change, no issue'
					
					When [COL LienType] like 'Attorney' and [COL Question #] > 5 then 'No change, no issue'
					When [COL LienType] like 'Litigation Finance' and [COL Question #] > 5 then 'No change, no issue'
					When [COL LienType] like 'Other' then 'Human Intervention (fix this week) - lientype of other'

					Else 'Look Into'
					End as [LienId_Check],


			--Check Amount	
				Case
					When [COL Lienholder] is null and [COL LienType] is null and [COL Question #] is null and [COL Status] is null and [COL Amount] is null then 'Human Intervention (fix this week) - delete empty lien from COL'
				 	When [COL LienId] is null and [Claim Ref #] is not null and [COL LienType] is not null then 'Human Intervention (fix this week) - LienId is NULL in COL'
					When [COL LienId] is null and [COL LienType] is not null and [SLAM LienId] is null then 'Human Intervention (fix this week) - LienId is NULL in COL'
					
					When [SLAM LienId] is not null and [SLAM OnBenefits] is null and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Status] = 'Pending' and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Stage] <> 'Closed' or [SLAM Stage] not like 'final%' and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Stage] is null and [SLAM OnBenefits] is null and [COL LienId] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - Lien Id needs update'
							
					When [COL Status] = 'Pending' and [COL Amount] is not null then 'Human Intervention (fix this week) - Pending in COL but has amount'
					When [COL Amount] <> Round([SLAM Amount],2) and [COL Question #] <= 5 then 'Human Intervention (fix this week) - SLAM and COL lien amounts mismatch'
					When [SLAM Amount] is null and [COL Amount] is not null then 'Human Intervention (fix this week) - COL amount is not null but SLAM is null'
					When [COL Amount] is null and ([COL Status] = 'Final' or [COL Status] = 'Not Entitled') then 'Human Intervention (fix this week) - COL lien is final but no amount'
					When [COL Amount] <> 0 and [COL Status] = 'Not Entitled' then 'Human Intervention (fix this week) - COL lien is final but no amount'

					When [COL Amount] is null and [SLAM Amount] is not null and [COL Question #] <= 5 and [COL Status] = 'Pending' and [SLAM Status] = 'Final' then 'Happy Path - update needed'
										
					When [COL Amount] = Round([SLAM Amount],2) then 'No change, no issue'
					When [COL Amount] is null and [SLAM Status] = 'Pending' and [COL Status] = 'Pending' then 'Not Eligible'
					When [COL Amount] is null and [SLAM Onbenefits] is null and [COL Status] = 'Pending' then 'Not Eligible'
					When [COL Amount] = Round([SLAM Amount],2) and [COL Question #] <= 5 and [COL Status] = 'Final' and [SLAM Status] = 'Final' then 'No change, no issue'
					When [COL Amount] = Round([SLAM Amount],2) and [COL Question #] <= 5 and [COL Status] = 'Not Entitled' and [SLAM Onbenefits] = 'No' then 'No change, no issue'
					When [SLAM Status] = 'Not Entitled' and [COL Amount] = 0 then 'No change, no issue'
					When [SLAM Stage] = 'Final No Entitlement' and [COL Amount] = 0 then 'No change, no issue'
					When ([SLAM ClosedReason] = 'Opened in Error' or [SLAM ClosedReason] = 'Resolved - No Entitlement' or [SLAM ClosedReason] like 'Per att%') and [COL Amount] = 0 then 'No change, no issue'
					When [COL Question #] > 5 and ([COL Status] = 'Final' or [COL Status] = 'Not Entitled') and [COL Amount] = 0 then 'No change, no issue'
					When [COL Question #] > 5 and [COL Status] = 'Pending' and [COL Amount] is null then 'Not Eligible'

					When [COL LienType] like 'Attorney' and [COL Question #] > 5 then 'No change, no issue'
					When [COL LienType] like 'Litigation Finance' and [COL Question #] > 5 then 'No change, no issue'
					When [COL Status] = 'Pending' and [SLAM Status] = 'Pending' then 'Not Eligible'
					When [COL Status] = 'Pending' and [SLAM OnBenefits] is null and [SLAM LienId] is not null then 'Not Eligible'
					When [COL Status] = 'Pending' and [SLAM OnBenefits] is null and [SLAM LienId] is null then 'Human Intervention (fix this week) - missing Lien Id'
					When [COL LienType] like 'Other' then 'Human Intervention (fix this week) - lientype of other'

					Else 'Look Into'
					End as [Amount_Check],


			--Updated Amount
				Case
					When [COL Lienholder] is null and [COL LienType] is null and [COL Question #] is null and [COL Status] is null and [COL Amount] is null then 'Human Intervention (fix this week) - delete empty lien from COL'
					When [COL LienId] is null and [Claim Ref #] is not null and [COL LienType] is not null then 'Human Intervention (fix this week) - LienId is NULL in COL'
					When [COL LienId] is null and [COL LienType] is not null and [SLAM LienId] is null then 'Human Intervention (fix this week) - LienId is NULL in COL'

					When [COL LienType] like 'Attorney' and [COL Question #] > 5 then cast([COL Amount] as varchar)
					When [COL LienType] like 'Litigation Finance' and [COL Question #] > 5 then cast([COL Amount] as varchar)
					When [COL LienType] like 'Other' then 'Human Intervention (fix this week) - lientype of other' 

					When [COL Question #] > 5 and [SLAM Status] = 'Final' then cast(0 as varchar)
					When [COL Question #] > 5 and [SLAM Status] = 'Pending' then ''

					When [SLAM Status] = 'Not Entitled' then cast(0 as varchar)
					When [SLAM Stage] = 'Final No Entitlement' then cast(0 as varchar)
					When [SLAM Stage] = 'Closed' and [SLAM ClosedReason] = 'Opened in Error' then cast(0 as varchar)
					When [SLAM Stage] = 'Closed' and [SLAM ClosedReason] like 'Per Att%' then cast(0 as varchar)

					When [SLAM Status] = 'Pending' then ''
					When [SLAM OnBenefits] is null then ''
					When [SLAM Stage] <> 'Closed' or [SLAM Stage] not like 'Final%' then ''

					When [SLAM Status] = 'Final' then cast([SLAM Amount] as varchar)

					Else 'Look Into'
					End as 'Updated Amount',


			--Check Question number
				Case
					When [COL Lienholder] is null and [COL LienType] is null and [COL Question #] is null and [COL Status] is null and [COL Amount] is null then 'Human Intervention (fix this week) - delete empty lien from COL'
					When [COL LienId] is null and [Claim Ref #] is not null and [COL LienType] is not null then 'Human Intervention (fix this week) - LienId is NULL in COL'
					When [COL LienId] is null and [COL LienType] is not null and [SLAM LienId] is null then 'Human Intervention (fix this week) - LienId is NULL in COL'

					When [SLAM LienId] is not null and [SLAM OnBenefits] is null and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Status] = 'Pending' and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Stage] <> 'Closed' or [SLAM Stage] not like 'final%' and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Stage] is null and [SLAM OnBenefits] is null and [COL LienId] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - Lien Id needs update'
					
					When [COL Question #] <> [SLAM Question #] then 'Human Intervention (fix this week) - Question # mismatch'
						
					When [COL Question #] = [SLAM Question #] then 'No change, no issue'
					When [COL Question #] > 5 then 'No change, no issue'
					When [COL LienType] like 'Attorney' and [COL Question #] > 5 then 'No change, no issue'
					When [COL LienType] like 'Litigation Finance' and [COL Question #] > 5 then 'No change, no issue'
					
					When [COL Status] = 'Pending' and [SLAM OnBenefits] is null and [SLAM LienId] is null then 'Human Intervention (fix this week) - missing Lien Id'

					Else 'Look Into'
					End as [Question_#_Check],


			--Check Lienholder Name

				Case
					When [COL Lienholder] is null and [COL LienType] is null and [COL Question #] is null and [COL Status] is null and [COL Amount] is null then 'Human Intervention (fix this week) - delete empty lien from COL'
					When [COL LienId] is null and [Claim Ref #] is not null and [COL LienType] is not null then 'Human Intervention (fix this week) - LienId is NULL in COL'
					When [COL LienId] is null and [COL LienType] is not null and [SLAM LienId] is null then 'Human Intervention (fix this week) - LienId is NULL in COL'

					When [SLAM LienId] is not null and [SLAM OnBenefits] is null and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Status] = 'Pending' and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Stage] <> 'Closed' or [SLAM Stage] not like 'final%' and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Stage] is null and [SLAM OnBenefits] is null and [COL LienId] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - Lien Id needs update'
					
					When len([COL Lienholder]) > 50 then 'Human Intervention (fix this week) - COL lienholder name is more than 50 characters'
					
					When [COL Lienholder] like '%United Healthcare%' and [SLAM Lienholder] like '%United Healthcare%' then 'No change, no issue'
					When [COL Lienholder] like '%aetna%' and [SLAM Lienholder] like '%aetna%' then 'No change, no issue'
					When [COL Lienholder] like '%humana%' and [SLAM Lienholder] like '%humana%' then 'No change, no issue'
					When [COL Lienholder] like '%BCBS MN%' and [SLAM Lienholder] like '%BCBS Minnesota%' then 'No change, no issue'
					When [COL Lienholder] like '%BCBS Minnesota%' and [SLAM Lienholder] like '%BCBS MN%' then 'No change, no issue'
					When [COL Lienholder] like 'United Healthcare Community Plan of Ohio' and [SLAM Lienholder] like 'United Healthcare Community Plan of Ohio (aka Unison) (OH MCO)' then 'No change, no issue'
					When [COL Lienholder] like 'Medical Health Insuring Corp (OH MCO)' and [SLAM Lienholder] like 'Medical Health Insuring Corp (OH MCO)/Medical Mutual of Ohio' then 'No change, no issue'
					When [COL Lienholder] like 'Tufts%' and [SLAM Lienholder] like 'Tufts%' then 'No change, no issue'
					When [COL Lienholder] like 'Walmart Stores, Inc. Associates H&W Plan' and [SLAM Lienholder] like 'Walmart Stores, Inc. Associates Health and Welfare Plan' then 'No change, no issue'
					When [COL Lienholder] = 'Department of VA Office of General Counsel' and [SLAM Lienholder] = 'Department of Veterans Affairs Office of General Counsel 02 National Collections Group' then 'No change, no issue'
					When [COL Lienholder] = 'Washington County - NY Medicaid - TA' and [SLAM Lienholder] = 'Washington County - NY Medicaid - Temporary Assistance' then 'No change, no issue'
					When [COL Lienholder] = 'Tricare (Army) - Ft. Jackson' and [SLAM Lienholder] = 'Department of the Army' then 'No change, no issue'
					When [COL Lienholder] = 'Walmart Stores, Inc. Associates H&W Plan' and [SLAM Lienholder] = 'Walmart Stores, Inc. Associates Health and Welfare Plan' then 'No change, no issue'
					When [COL Lienholder] = 'IHS - Phoenix Indian Medical Center' and [SLAM Lienholder] = 'Indian Health Services' then 'No change, no issue'
					When [COL Lienholder] = 'Arizona Physicians IPA Inc.' and [SLAM Lienholder] = 'Arizona Physicians IPA Inc/UHC' then 'No change, no issue'
					When [COL Lienholder] = 'NY Medicaid - NYC County' and [SLAM Lienholder] = 'NY Medicaid - NYC' then 'No change, no issue'
					When [COL Lienholder] = 'Community Health Plan' and [SLAM Lienholder] = 'Community Health Plan (WA MCO)' then 'No change, no issue'
					When [COL Lienholder] like '%uhc%' and [SLAM Lienholder] like '%united healthcare%' then 'No change, no issue'
					When [COL Lienholder] = 'NY State Catholic Health Plan (Fidelis Care)' and [SLAM Lienholder] = 'New York State Catholic Health Plan (Fidelis Care)' then 'No change, no issue'
					When [COL Lienholder] = 'Medical Health Insuring Corp/Medical Mutual' and [SLAM Lienholder] = 'Medical Health Insuring Corp (OH MCO)/Medical Mutual of Ohio' then 'No change, no issue'
					When [COL Lienholder] = 'United Mine Workers of America Health&Retirement' and [SLAM Lienholder] = 'United Mine Workers of America Health & Retirement' then 'No change, no issue'
					When [COL Lienholder] = 'Lifemasters Supported Healthcare/Staywell' and [SLAM Lienholder] = 'Lifemasters Supported Healthcare/Staywell/Wellcare' then 'No change, no issue'
					When [COL Lienholder] = 'Central States, SE and SW Area H and W Fund' and [SLAM Lienholder] = 'Central States, Southeast and Southwest Area Health and Welfare Fund' then 'No change, no issue'
					When [COL Lienholder] = 'Office Management & ENT Services Employees Group' and [SLAM Lienholder] = 'Office of Management and Enterprise Services Employees Group Insurance Department' then 'No change, no issue'
					When [COL Lienholder] = 'Monroe County - Temporary Assistance' and [SLAM Lienholder] = 'Monroe County - NY Medicaid - Temporary Assistance' then 'No change, no issue'
					When [COL Lienholder] = 'United  Workers of America Health&Retirement' and [SLAM Lienholder] = 'United Mine Workers of America Health & Retirement' then 'No change, no issue'
					When [COL Lienholder] = 'NY Medicaid - Cattaragus County' and [SLAM Lienholder] = 'NY Medicaid - Cattaraugus County' then 'No change, no issue'
					When [COL Lienholder] = 'Chautauqua County - NY Medicaid - TA' and [SLAM Lienholder] = 'Chautauqua County - NY Medicaid - TA' then 'No change, no issue'
					When [COL Lienholder] = 'Anthem BCMineBS/Wellpoint' and [SLAM Lienholder] = 'Anthem Blue Cross Blue Shield' then 'No change, no issue'
					When [COL Lienholder] = 'Onondaga County - NY Mcaid - Temp Assistance' and [SLAM Lienholder] = 'Onondaga County - NY Medicaid - Temporary Assistance' then 'No change, no issue'
					When [COL Lienholder] = 'OK Medicaid' and [SLAM Lienholder] = 'OK Medicaid - Conduent' then 'No change, no issue'
					When [COL Lienholder] = 'Wellcare' and [SLAM Lienholder] = 'Wellcare - PLRP' then 'No change, no issue'
					When [COL Lienholder] = '%army%' and [SLAM Lienholder] = '%army%' then 'No change, no issue'
					When [COL Lienholder] = 'General Motors LLC' and [SLAM Lienholder] = 'General Motors LLC' then 'No change, no issue'
					When [COL Lienholder] = 'Regence BCBS of Oregon/Utah' and [SLAM Lienholder] = 'Cambia Health Solutions/Regence' then 'No change, no issue'
					When [COL Lienholder] = 'Presbyterian Senior Care HMO' and [SLAM Lienholder] = 'Presbyterian Senior Care (HMO)' then 'No change, no issue'
					When [COL Lienholder] = 'Sunshine State Health Plan/Centene' and [SLAM Lienholder] = 'Sunshine Health/Centene' then 'No change, no issue'
					When [COL Lienholder] = 'Medical Health Insuring Corp (OH MCO)' and [SLAM Lienholder] = 'Medical Health Insuring Corp (OH MCO)%' then 'No change, no issue'
					When [COL Lienholder] = 'United Healthcare Community Plan of Ohio%' and [SLAM Lienholder] = 'United Healthcare Community Plan of Ohio%' then 'No change, no issue'
					When ([COL Lienholder] = '%United Healthcare%' and [SLAM Lienholder] = '%United Healthcare%') or ([COL Lienholder] = 'United Healthcare' and [SLAM Lienholder] = '%UHC%') then 'No change, no issue'
					When ([COL Lienholder] = '%UHC%' and [SLAM Lienholder] = '%United Healthcare%') or ([COL Lienholder] = '%UHC%' and [SLAM Lienholder] = '%UHC%') then 'No change, no issue'
					When [COL Lienholder] like '%HealthSpring%' and [SLAM Lienholder] like '%HealthSpring%' then 'No change, no issue'
					When [COL Lienholder] = '%Kaiser%' and [SLAM Lienholder] = '%Kaiser%' then 'No change, no issue'
					When [COL Lienholder] = '%Department of VA Office of General Counsel%' and [SLAM Lienholder] = '%Department of Veterans Affairs Office of General Counsel 02 National Collections Group%' then 'No change, no issue'
					When [COL Lienholder] = '%Suffolk County - NY Medicaid - TA%' and [SLAM Lienholder] = '%Suffolk County - NY Medicaid - Temporary Assistance%' then 'No change, no issue'
					When [COL Lienholder] = 'Nassau County - NY Medicaid - TA' and [SLAM Lienholder] = 'Nassau County - NY Medicaid - Temporary Assistance' then 'No change, no issue'
					When [COL Lienholder] = 'HCA' and [SLAM Lienholder] = 'HCA, Inc. Medical Plan' then 'No change, no issue'
					When [COL Lienholder] = 'Jefferson County - NY Medicaid (TA)' and [SLAM Lienholder] = 'Jefferson County - NY Medicaid - Temporary Assistance' then 'No change, no issue'

					When len([COL Lienholder]) <= 50 and [COL Lienholder] = [SLAM Lienholder] then 'No change, no issue' 
					
					When [SLAM Status] is null or [SLAM Status] = 'Not Entitled' then 'No change, no issue'

					When [COL LienType] like 'Attorney' and [COL Question #] > 5 then 'No change, no issue'
					When [COL LienType] like 'Litigation Finance' and [COL Question #] > 5 then 'No change, no issue'
					When [COL LienType] like 'Other' then 'Human Intervention (fix this week) - lientype of other'

					When len([COL Lienholder]) <= 50 and [COL Lienholder] <> [SLAM Lienholder] then 'Happy Path - Update Needed' 

					When [COL Status] = 'Pending' and [SLAM OnBenefits] is null and [SLAM LienId] is null then 'Human Intervention (fix this week) - missing Lien Id'

					Else 'Look Into'
					End as [Lienholder_Check],


			--Liens Not Pulling
			Case
				When [COL Lienholder] is null and [COL LienType] is null and [COL Question #] is null and [COL Status] is null and [COL Amount] is null then 'Human Intervention (fix this week) - delete empty lien from COL'
				When [COL LienId] is null and [Claim Ref #] is not null and [COL LienType] is not null then 'Human Intervention (fix this week) - LienId is NULL in COL'
				When [COL LienId] is null and [COL LienType] is not null and [SLAM LienId] is null then 'Human Intervention (fix this week) - LienId is NULL in COL'

				When [SLAM LienId] is not null and [SLAM OnBenefits] is null and [COL Status] = 'Pending' then 'Not Eligible'
				When [SLAM Status] = 'Pending' and [COL Status] = 'Pending' then 'Not Eligible'
				When [SLAM Stage] <> 'Closed' or [SLAM Stage] not like 'final%' and [COL Status] = 'Pending' then 'Not Eligible'
				When [SLAM Stage] is null and [SLAM OnBenefits] is null and [COL LienId] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - Lien Id needs update'
				
				When [SLAM Status] is null or [SLAM Status] = 'Not Entitled' then 'No change, no issue'
				When [ThirdPartyId] is Null then 'Human Intervention (fix this week) - Lien not pulling in SLAM data'
				When [COL LienType] like 'Attorney' and [COL Question #] > 5 then 'No change, no issue'
				When [COL LienType] like 'Litigation Finance' and [COL Question #] > 5 then 'No change, no issue'
				When [COL LienType] like 'Other' then 'Human Intervention (fix this week) - lientype of other'
				
				Else 'No change, no issue'
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
							
							FPV.COL_LienType as 'SLAM LienType (converted)', FPV.Stage as 'SLAM Stage', FPV.ClosedReason as 'SLAM ClosedReason', FPV.OnBenefits as 'SLAM OnBenefits'

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
    print('SQL query done')
	
    # merge dataframes to compare, rename columns
	
    lf_df['Claim Ref #']=lf_df['Claim Ref #'].astype(int)
    cms_df['Claim Ref #']=cms_df['Claim Ref #'].astype(int)
    combined_df = pd.merge(lf_df, cms_df, on = 'Claim Ref #')

    # Create a df based off label value.

    df_cms = combined_df.groupby('CMS_Label')
    df_lf = combined_df.groupby('LF_Label')
    lf_ne = df_lf.get_group('Not Eligible')
    #try:
    cms_ne = df_cms.get_group('Not Eligible')
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

	# Happy Path
    try:
    	hp_hp = lf_hp_id.intersection(cms_hp_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hp_id,cms_hp_id,hp_hp,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Happy Path')
    except UnboundLocalError:
    	pass

	# No Changes, No Issues

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

	# HI - Fix this week
    try:
    	hp_hi1 = lf_hp_id.intersection(cms_hi1_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hp_id,cms_hi1_id,hp_hi1,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention - Fix this week')
    except UnboundLocalError:
    	pass
    # print('Finished 1st matrix group')

	## No Changes, No Issues ##

	# Add Lien
    try:
    	nc_al = lf_nc_id.intersection(cms_al_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_nc_id,cms_al_id,nc_al,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Add Lien')
    except UnboundLocalError:
    	pass

	# No Changes, No Issues
    try:
    	nc_nc = lf_nc_id.intersection(cms_nc_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_nc_id,cms_nc_id,nc_nc,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'No Changes, No Issues')
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

	# HI - Fix this week
    try:
    	nc_hi1 = lf_nc_id.intersection(cms_hi1_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_nc_id,cms_hi1_id,nc_hi1,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention - Fix this week')
    except UnboundLocalError:
    	pass
    # print('Finished 2nd matrix group')

	## Human Intervention - Close In SLAM ##	

	# Happy Path
    try:
    	hi5_hp = lf_hi5_id.intersection(cms_hp_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi5_id,cms_hp_id,hi5_hp,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention - Fix this week (if time)')
    except UnboundLocalError:
    	pass

	# Add Lien
    try:
    	hi5_al = lf_hi5_id.intersection(cms_al_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi5_id,cms_al_id,hi5_al,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention - Fix this week (if time)')
    except UnboundLocalError:
    	pass

	# No Changes, No Issues
    try:
    	hi5_nc = lf_hi5_id.intersection(cms_nc_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi5_id,cms_nc_id,hi5_nc,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention - Close in SLAM')
    except UnboundLocalError:
    	pass

	# HI - Fix this week
    try:
    	hi5_hi1 = lf_hi5_id.intersection(cms_hi1_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi5_id,cms_hi1_id,hi5_hi1,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention - Fix this week (if time)')
    except UnboundLocalError:
    	pass
    # print('Finished 3rd matrix group')

	## Human Intervention - Fix when you can ##	

	# Happy Path
    try:
    	hi4_hp = lf_hi4_id.intersection(cms_hp_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi4_id,cms_hp_id,hi4_hp,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention - Fix when you can')
    except UnboundLocalError:
    	pass

	# No Changes, No Issues
    try:
    	hi4_nc = lf_hi4_id.intersection(cms_nc_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi4_id,cms_nc_id,hi4_nc,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention - Fix when you can')
    except UnboundLocalError:
    	pass

	# Add Lien
    try:
    	hi4_al = lf_hi4_id.intersection(cms_al_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi4_id,cms_al_id,hi4_al,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention - Fix when you can')
    except UnboundLocalError:
    	pass

	# HI - Fix this week
    try:
    	hi4_hi1 = lf_hi4_id.intersection(cms_hi1_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi4_id,cms_hi1_id,hi4_hi1,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention - Fix when you can')
    except UnboundLocalError:
    	pass
    # print('Finished 4th matrix group')

	## Human Intervention - Fix this week (If time) ##

	# Happy Path
    try:
    	hi3_hp = lf_hi3_id.intersection(cms_hp_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi3_id,cms_hp_id,hi3_hp,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention - Fix this week (if time)')
    except UnboundLocalError:
    	pass

	# No Changes, No Issues
    try:
    	hi3_nc = lf_hi3_id.intersection(cms_nc_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi3_id,cms_nc_id,hi3_nc,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention - Fix this week (if time)')
    except UnboundLocalError:
    	pass

	# Add Lien
    try:
    	hi3_al = lf_hi3_id.intersection(cms_al_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi3_id,cms_al_id,hi3_al,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention - Fix this week (if time)')
    except UnboundLocalError:
    	pass

	# HI - Fix this week
    try:
    	hi3_hi1 = lf_hi3_id.intersection(cms_hi1_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi3_id,cms_hi1_id,hi3_hi1,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention - Fix this week (if time)')
    except UnboundLocalError:
    	pass
    # print('Finished 5th matrix group')


	## Human Intervention - Fix this week ##

	# Happy Path
    try:
    	hi1_hp = lf_hi1_id.intersection(cms_hp_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi1_id,cms_hp_id,hi1_hp,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention - Fix this week')
    except UnboundLocalError:
    	pass

	# No Changes, No Issues
    try:
    	hi1_nc = lf_hi1_id.intersection(cms_nc_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi1_id,cms_nc_id,hi1_nc,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention - Fix this week')
    except UnboundLocalError:
    	pass

	# Add Lien
    try:
    	hi1_al = lf_hi1_id.intersection(cms_al_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi1_id,cms_al_id,hi1_al,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention - Fix this week')
    except UnboundLocalError:
    	pass

	# HI - Fix this week
    try:
    	hi1_hi1 = lf_hi1_id.intersection(cms_hi1_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi1_id,cms_hi1_id,hi1_hi1,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention - Fix this week')
    except UnboundLocalError:
    	pass
    # print('Finished 6th matrix group')

	## Human Inetervention (CM) ##
	
	# Happy Path
    try:
    	hi2_hp = lf_hi2_id.intersection(cms_hp_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi2_id,cms_hp_id,hi2_hp,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (CM)')
    except UnboundLocalError:
    	pass

	# No Changes, No Issues
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

	# HI - Fix this week
    try:
    	hi2_hi1 = lf_hi2_id.intersection(cms_hi1_id)
    except UnboundLocalError:
    	pass
    try:
    	ud.list_intersections(lf_hi2_id,cms_hi1_id,hi2_hi1,combined_df, 'Claim Ref #', 'LF_Label','CMS_Label', 'Human Intervention (CM)')
    except UnboundLocalError:
    	pass
    # print('Finished the full Intersection')

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
	
    lf_df.to_excel('./excel_results/LF.xlsx')
    cms_df.to_excel('./excel_results/CMS.xlsx')
    happypath = combined_df[combined_df['LF_Label'] == 'Happy Path']
    happypath.to_excel('./excel_results/HappyPath.xlsx')
    addlien = combined_df[combined_df['LF_Label'] == 'Add Lien']
    addlien.to_excel('./excel_results/NewLiens.xlsx')
    combined_df.to_excel('./excel_results/Full_Analysis.xlsx', index = False)
    print('SQL code has completed, on to updates!')