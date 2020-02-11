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
    """Select sub2.*, 
Case
		When [Misc. Issues] = 'Not Eligible - BUDNSFW' then 'Not Eligible'
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

		When [Updated SLAM Final] = 'No change, no issue - no questionnaire' then 'Not Eligible'
		When [Updated SLAM Final] = 'Human Intervention (fix this week if time) - Scope issue' then 'Human Intervention (fix this week if time)'
		When [Updated SLAM Final] = 'Human Intervention (fix this week if time) - Resolved but not final' then 'Human Intervention (fix this week if time)'
		When [Updated SLAM Final] = 'Human Intervention (fix this week) - No (GRG)' then 'Human Intervention (fix this week)'

		When [SSN Research] = 'Research - Add to SSN Research in #Problems; notify CM if needed' then 'Human Intervention (fix this week)'
		When [Escrow Analysis] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
		When [Rules for Q2, Q4, Questionnaire, Release] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
		When [Updated Mcare] = 'Human Intervention (fix this week) - Yes in COL but not in SLAM' then 'Human Intervention (fix this week)'
		When [Updated Non PLRP] = 'Human Intervention (fix this week) - Yes in COL but not in SLAM' then 'Human Intervention (fix this week)'
		When [Updated Mcaid] = 'Human Intervention (fix this week) - Yes in COL but not in SLAM' then 'Human Intervention (fix this week)'
		When [Updated Third Party] = 'Human Intervention (fix this week) - Yes in COL but not in SLAM' then 'Human Intervention (fix this week)'
		When [Updated PLRP] = 'Human Intervention (fix this week) - Yes in COL but not in SLAM' then 'Human Intervention (fix this week)'
		When [Should we update?] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'

		When [Escrow Analysis] = 'Human Intervention (fix this week if time) - sum of liens is greater than escrow' then 'Human Intervention (fix this week if time)'
		When [Should we update?] = 'Human Intervention (fix this week if time) - Finalized Status Id Issue' then 'Human Intervention (fix this week if time)'
		When [Should we update?] = 'Human Intervention (fix this week if time) - resolved but post payment lien deficient' then 'Human Intervention (fix this week if time)'
		When [SSN Research] like 'Research%' then 'Human Intervention (fix this week if time)'
		When [Update HB?] = 'Happy Path - Update Needed' and [SLAM Client Funded] = 'Yes' then 'Human Intervention (fix this week if time)'
		When [Truly Final/FinalizedStatusId Issue?] like '%issue%' then 'Human Intervention (fix this week if time)'

		When [Escrow Analysis] like 'Human Intervention (fix when you can)%' then 'Human Intervention (fix when you can)'
		When [Update Questions?] = 'Human Intervention (fix when you can) - Resolved but question changes' then 'Human Intervention (fix when you can)'
		When [Truly Final/FinalizedStatusId Issue?] like '%issue%' then 'Human Intervention (fix this week if time)'

		When [Escrow Analysis] = 'Human Intervention - Close in SLAM' and [Claimant in SLAM correctly?] = 'Good' 
				and ([Misc. Issues] = 'Good' or [Misc. Issues] like 'Update Carefully%') and [SA Matches?] = 'Good' 
				and ([SSN Research] ='Good - No Issue' or [SSN Research] ='SSN mismatch ok - trust SLAM') 
				and [Rules for Q2, Q4, Questionnaire, Release] ='Normal Update Process' 
				and [Should we update?] = 'Ok to Update' and [Update Questions?] <> 'Questions need update' and [Update HB?] <> 'Happy Path - Update Needed'
				then 'Human Intervention - Close in SLAM'
		
		When sub2.[Current Escrow] = 0 and ([Escrow Analysis] = 'Happy Path - update needed' or [Escrow Analysis] = 'Happy Path - Check COL' or [Update Questions?] = 'Questions need update' or [Update HB?] = 'Happy Path - Update Needed') then 'Human Intervention (fix this week)'


		When sub2.[Current Escrow]/sub2.[COL SA] < .19 and [Escrow Analysis] like 'Happy Path%' then 'Human Intervention (fix this week)'
		When sub2.[Current Escrow]/sub2.[COL SA] < .19 and [Update Questions?] = 'Questions need update' then 'Human Intervention (fix this week)'
		When sub2.[Current Escrow]/sub2.[COL SA] < .19 and [Update HB?] = 'Happy Path - Update Needed' then 'Human Intervention (fix this week)'
		
		When [Escrow Analysis] like 'Happy Path%' then 'Happy Path'
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
		When [Updated SLAM Final] like 'No change, no issue%' then 'No change, no issue'

		Else 'Look Into'
		
		End As 'Initial_LF_Label',



	Case
		When [Misc. Issues] = 'Not Eligible - BUDNSFW' then 'Not Eligible'
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

		When [Updated SLAM Final] = 'No change, no issue - no questionnaire' then 'Not Eligible'
		When [Updated SLAM Final] = 'Human Intervention (fix this week if time) - Scope issue' then 'Human Intervention (fix this week if time)'
		When [Updated SLAM Final] = 'Human Intervention (fix this week if time) - Resolved but not final' then 'Human Intervention (fix this week if time)'
		When [Updated SLAM Final] = 'Human Intervention (fix this week) - No (GRG)' then 'Human Intervention (fix this week)'

		When [SSN Research] = 'Research - Add to SSN Research in #Problems; notify CM if needed' then 'Human Intervention (fix this week)'
		When [Escrow Analysis] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
		When [Rules for Q2, Q4, Questionnaire, Release] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
		When [Updated Mcare] = 'Human Intervention (fix this week) - Yes in COL but not in SLAM' then 'Human Intervention (fix this week)'
		When [Updated Non PLRP] = 'Human Intervention (fix this week) - Yes in COL but not in SLAM' then 'Human Intervention (fix this week)'
		When [Updated Mcaid] = 'Human Intervention (fix this week) - Yes in COL but not in SLAM' then 'Human Intervention (fix this week)'
		When [Updated Third Party] = 'Human Intervention (fix this week) - Yes in COL but not in SLAM' then 'Human Intervention (fix this week)'
		When [Updated PLRP] = 'Human Intervention (fix this week) - Yes in COL but not in SLAM' then 'Human Intervention (fix this week)'
		When [Should we update?] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'

		When [Escrow Analysis] = 'Human Intervention (fix this week if time) - sum of liens is greater than escrow' then 'Human Intervention (fix this week if time)'
		When [Should we update?] = 'Human Intervention (fix this week if time) - Finalized Status Id Issue' then 'Human Intervention (fix this week if time)'
		When [Should we update?] = 'Human Intervention (fix this week if time) - resolved but post payment lien deficient' then 'Human Intervention (fix this week if time)'
		When [SSN Research] like 'Research%' then 'Human Intervention (fix this week if time)'
		When [Update HB?] = 'Happy Path - Update Needed' and [SLAM Client Funded] = 'Yes' then 'Human Intervention (fix this week if time)'

		When [Escrow Analysis] like 'Human Intervention (fix when you can)%' then 'Human Intervention (fix when you can)'
		When [Update Questions?] = 'Human Intervention (fix when you can) - Resolved but question changes' then 'Human Intervention (fix when you can)'
		When [Truly Final/FinalizedStatusId Issue?] like '%issue%' then 'Human Intervention (fix this week if time)'

		When [Escrow Analysis] = 'Human Intervention - Close in SLAM' and [Claimant in SLAM correctly?] = 'Good' 
				and ([Misc. Issues] = 'Good' or [Misc. Issues] like 'Update Carefully%') and [SA Matches?] = 'Good' 
				and ([SSN Research] ='Good - No Issue' or [SSN Research] ='SSN mismatch ok - trust SLAM') 
				and [Rules for Q2, Q4, Questionnaire, Release] ='Normal Update Process' 
				and [Should we update?] = 'Ok to Update' and [Update Questions?] <> 'Questions need update' and [Update HB?] <> 'Happy Path - Update Needed'
				then 'Human Intervention - Close in SLAM'
		
		When sub2.[Current Escrow] = 0 and ([Escrow Analysis] = 'Happy Path - update needed' or [Escrow Analysis] = 'Happy Path - Check COL' or [Update Questions?] = 'Questions need update' or [Update HB?] = 'Happy Path - Update Needed') then 'Human Intervention (fix this week)'

		When sub2.[Current Escrow]/sub2.[COL SA] < .19 and [Escrow Analysis] like 'Happy Path%' then 'Human Intervention (fix this week)'
		When sub2.[Current Escrow]/sub2.[COL SA] < .19 and [Update Questions?] = 'Questions need update' then 'Human Intervention (fix this week)'
		When sub2.[Current Escrow]/sub2.[COL SA] < .19 and [Update HB?] = 'Happy Path - Update Needed' then 'Human Intervention (fix this week)'
		
		When [Escrow Analysis] like 'Happy Path%' then 'Happy Path'
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
		When [Updated SLAM Final] like 'No change, no issue%' then 'No change, no issue'
		
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
				When [Claim Status] = 'Release issued' or [Claim Status] = 'Release deficient' then 'Not Eligible - Prepayment'
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
				When [COL Payment Group] is not null and [Final (SLAM Summary)] = 'Yes' and [SLAM HB]=[COL HB] and [COL HB]=[Current Escrow] and [SLAM Client Funded] = 'No' then 'Human Intervention - Close in SLAM'
								
				When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]=[COL HB] and [COL HB]<>[Current Escrow] and [SLAM Client Funded] = 'No' and [Current Escrow]/[COL SA] < .19 then 'Human Intervention (fix when you can) - COL HB and Escrow mismatch'
				When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]<>[COL HB] and [SLAM Client Funded] = 'No' and [Current Escrow]/[COL SA] < .19 then 'Human Intervention (fix when you can) - HB mismatch and not enough escrow'
				When [Final (SLAM Summary)] = 'Yes' and [COL HB]<>[Current Escrow] and [SLAM Client Funded] = 'Yes' and [current escrow] <> 0 then 'Human Intervention (fix when you can) - resolved but escrow mismatch'
				When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]<>[COL HB] and [SLAM Client Funded] = 'Yes' then 'Human Intervention (fix when you can) - resolved but HB mismatch'
				When [Final (SLAM Summary)] <> 'Yes' and [SLAM Client Funded] = 'Yes' then 'Human Intervention (fix when you can) - resolved but not final'
				When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]<>[COL HB] and [SLAM Client Funded] = 'Yes' and [current escrow] <> 0 then 'Human Intervention (fix when you can) - resolved but escrow/HB mismatch'
				When [Final (SLAM Summary)] = 'Yes' and [Current Escrow]<>[COL HB] and [SLAM Client Funded] = 'Yes' and [current escrow] <> 0 then 'Human Intervention (fix when you can) - resolved but escrow/HB mismatch'

				When [Current Escrow]/[COL SA] < .19 then 'Human Intervention (fix when you can) - Not enough escrow' 

				When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]<>[COL HB] and [SLAM Client Funded] = 'No' and [Current Escrow]/[COL SA] > .19 and [SLAM HB]<=[Current Escrow] then 'Happy Path - update needed'
				
				When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]=[COL HB] and [COL HB]<>[Current Escrow] and [SLAM Client Funded] = 'No' then 'No change, no issue'
				
				Else 'Look Into'
				End As 'Escrow Analysis',


		--Problems
			[#Problems], [Bad List Note], [#Prob Notes], BUDNSFW_ClientIssue,
			Case
				When BUDNSFW_ClientIssue is not null then 'Not Eligible - BUDNSFW'
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
				When [#Prob Notes] = 'Do not update in normal process' and [Truly Final/FinalizedStatusId Issue?] = 'Issue' then 'No change, no issue'
				When [Truly Final/FinalizedStatusId Issue?] = 'Issue' and [Claim Status] = 'Withdrawn' then 'No change, no issue - Withdrawn'
				When [SLAM CaseId] IN (862) and [Final (SLAM Summary)] = 'Yes' and [SLAM PreExisting Injuries] not like '%Completed by%' then 'Human Intervention (fix this week) - No (GRG)'
				When [SLAM CaseId] IN (862) and [SLAM Finalized Status Id] = 2 and [SLAM PreExisting Injuries] not like '%Completed by%' then 'Human Intervention (fix this week) - No (GRG)'
				When [SLAM CaseId] IN (862) and [SLAM Finalized Status Id] = 3 and [SLAM PreExisting Injuries] not like '%Completed by%' then 'Human Intervention (fix this week) - No (GRG)'
				When [SLAM CaseId] IN (862) and [Final (SLAM Summary)] = 'Yes' and [SLAM PreExisting Injuries] is null then 'Human Intervention (fix this week) - No (GRG)'
				When [SLAM CaseId] IN (862) and [SLAM Finalized Status Id] = 2 and [SLAM PreExisting Injuries] is null then 'Human Intervention (fix this week) - No (GRG)'
				When [SLAM CaseId] IN (862) and [SLAM Finalized Status Id] = 3 and [SLAM PreExisting Injuries] is null then 'Human Intervention (fix this week) - No (GRG)'
				When [#Problems] like '%EIF%' and [SLAM Client Funded] = 'Yes' and [Final (SLAM Summary)] = 'No' then 'No change, no issue - EIF'

				When [SLAM CaseId] in (2284, 2919, 3634, 2184, 2450) and [Truly Final/FinalizedStatusId Issue?] = 'Issue' and [SLAM Quest Recd] = 0 then 'No change, no issue - no questionnaire'
				When [SLAM CaseId] in (2284, 2919, 3634, 2184, 2450) and [Truly Final/FinalizedStatusId Issue?] = 'Issue' and [SLAM Quest Recd] is null then 'No change, no issue - no questionnaire'
				When [Truly Final/FinalizedStatusId Issue?] = 'Issue' and [Claim Status] <> 'Withdrawn' then 'Human Intervention (fix this week if time) - Scope issue'

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
				When [SLAM CaseId] in (2284, 2919, 3634, 2184, 2450) and [Truly Final/FinalizedStatusId Issue?] = 'Issue' and [SLAM Quest Recd] = 0 then 'No change, no issue - no questionnaire'
				When [SLAM CaseId] in (2284, 2919, 3634, 2184, 2450) and [Truly Final/FinalizedStatusId Issue?] = 'Issue' and [SLAM Quest Recd] is null then 'No change, no issue - no questionnaire'
				When [Truly Final/FinalizedStatusId Issue?] = 'Issue' and [Final (SLAM Summary)] = 'Yes' then 'Human Intervention (fix this week) - Liens final but status not final'

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
				When [SLAM Client Funded] = 'Yes' and [SLAM HB]=[COL HB] and [COL Mcare] <> [SLAM Mcare] then 'No change, no issue - resolved, Q Mismatch, but HB is good'
				When [COL Mcare] = 'Yes' and [SLAM Mcare] <> 'Yes' then 'Human Intervention (fix this week) - Yes in COL but not in SLAM'
				Else [SLAM Mcare]
				End As 'Updated Mcare',
			Case
				When [SLAM Client Funded] = 'Yes' and [SLAM HB]=[COL HB] and [COL Non PLRP] <> [SLAM Non PLRP] then 'No change, no issue - resolved, Q Mismatch, but HB is good'
				When [COL Non PLRP] = 'Yes' and [SLAM Non PLRP] <> 'Yes' then 'Human Intervention (fix this week) - Yes in COL but not in SLAM'
				Else [SLAM Non PLRP]
				End As 'Updated Non PLRP',
			Case
				When [SLAM Client Funded] = 'Yes' and [SLAM HB]=[COL HB] and [COL Mcaid] <> [SLAM Mcaid] then 'No change, no issue - resolved, Q Mismatch, but HB is good'
				When [COL Mcaid] = 'Yes' and [SLAM Mcaid] <> 'Yes' then 'Human Intervention (fix this week) - Yes in COL but not in SLAM'
				Else [SLAM Mcaid]
				End As 'Updated Mcaid',
			Case
				When [SLAM Client Funded] = 'Yes' and [SLAM HB]=[COL HB] and [COL Third Party] <> [SLAM Third Party] then 'No change, no issue - resolved, Q Mismatch, but HB is good'
				When [COL Third Party] = 'Yes' and [SLAM Third Party] <> 'Yes' then 'Human Intervention (fix this week) - Yes in COL but not in SLAM'
				Else [SLAM Third Party]
				End As 'Updated Third Party',
			Case
				When [SLAM Client Funded] = 'Yes' and [SLAM HB]=[COL HB] and [COL PLRP] <> [SLAM PLRP] then 'No change, no issue - resolved, Q Mismatch, but HB is good'
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
					JB_BurnettBadList.ClientId, JB_BurnettBadList.Note as 'Bad List Note',

				--BUDNSFW
					BUDNSFW_Client.[Issue Detail] as BUDNSFW_ClientIssue




					FROM            
						 JB_BulkEdit_LF --Bulk Edit - raw data from COL - only Law Firm tab - downloaded every time you are doing an update - core update file
                         LEFT OUTER JOIN JB_CSR_AMS ON JB_BulkEdit_LF.[Claim number] = JB_CSR_AMS.[Claim #] -- Cross Settlement Report - weekly excel file sent by Ankura with escrow information
                         LEFT OUTER JOIN JB_COLSearchExtract_Updated ON JB_BulkEdit_LF.[Claim number] = JB_COLSearchExtract_Updated.[Claim number] --search extract (another download from COL website) - downloaded weekly for entire case
						 LEFT OUTER JOIN JB_BurnettBadList ON JB_BulkEdit_LF.[Claim number] = JB_BurnettBadList.ThirdPartyId -- a list of claimants with surgery data discrepancies we're not allowed to update  only for Burnet - internal file - temporary hold
                         LEFT OUTER JOIN JB_AMSProblems_SSNResearch ON JB_BulkEdit_LF.[Claim number] = JB_AMSProblems_SSNResearch.[Claim Number] -- internal list of claimants whose SSN don't match between COL and SLAM, but we've researched and can trust our SSN
                         LEFT OUTER JOIN JB_AMSProblems_Summary ON JB_BulkEdit_LF.[Claim number] = JB_AMSProblems_Summary.[Claim #] --another internal list of discrepancies of claimants we won't update - will never update
                         LEFT OUTER JOIN JB_GetClientSummary ON JB_BulkEdit_LF.[Claim number] = JB_GetClientSummary.[ThirdPartyId] --stored procedure getclientsummarybycase - a snapshot of current SLAM data
						 LEFT OUTER JOIN JB_BUDNSFW_Client as BUDNSFW_Client ON JB_BulkEdit_LF.[Claim number] = BUDNSFW_Client.[Claim number]
						 
				) as sub
		)as sub2
""",
    con = engine
    )

    cms_df = pd.read_sql(
    """Select	sub2.*,
		Case
			When [Other lien type] like '%Ch. 13%' or [Other lien type] like '%Bankruptcy%' or [Other lien type] = 'Bk Trustee' or [Other lien type] like '%Chapter 13%' or [Other lien type] like '%Ch. 7%' or [Other lien type] like '%s Comp Lien%' or [Other lien type] = 'Public Welfare Lien' then 'No Change, no issue'
			When Prob_Check like 'Not Eligible%' then 'Not Eligible'
			When [COL LienType] = 'Litigation Finance' or [COL LienType] = 'Attorney' or [COL LienType] = 'Child Care' then 'No change, no issue'
			When [COL LienType] = 'Other' and ([COL Lienholder] like '%trustee%' or [COL Lienholder] like '%Ch. 13%' or [COL Lienholder] like '%Ch. 7%' or [COL Lienholder] like '%Bankruptcy%' or [COL Lienholder] like '%chapter%' or [COL Lienholder] like '%law%' or [COL Lienholder] like '%mortgage%') then 'No change, no issue'
			When [COL Question #] > 5 and ([COL Lienholder] like '%trustee%' or [COL Lienholder] like '%Ch. 13%' or [COL Lienholder] like '%Ch. 7%' or [COL Lienholder] like '%Bankruptcy%' or [COL Lienholder] like '%chapter%' or [COL Lienholder] like '%law%' or [COL Lienholder] like '%mortgage%') then 'No change, no issue'
			When [COL Lienholder] like '%EIF%' then 'Not Eligible'
			When [SLAM LienType] = 'Medicare Lien - Duplicate' or [SLAM LienType] = 'Private Lien' or [SLAM LienType] = 'Look Into' then 'Human Intervention (fix this week)'
			When [COL LienType] = 'Look Into' then 'Human Intervention (fix this week)'
			
			When [Status_Check] = 'Not Eligible' then 'Not Eligible'
			When [New Liens?] = 'Not Eligible' then 'Not Eligible'
			When [LienType_Check] = 'Not Eligible' then 'Not Eligible'
			When [Amount_Check] = 'Not Eligible' then 'Not Eligible'
			When [Lienholder_Check] = 'Not Eligible' then 'Not Eligible'
			When [Question_#_Check] = 'Not Eligible' then 'Not Eligible'
			When [ThirdPartyId_Match?] = 'Not Eligible' then 'Not Eligible'
			When [LienId_Check] = 'Not Eligible' then 'Not Eligible'
			When [InSLAM_Check] = 'Not Eligible' then 'Not Eligible'
			
			When [Status_Check] = 'Human Intervention (fix this week) - LienId is not valid - delete out of COL?' and [Percent Escrow Remaining] < .2 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			When [Status_Check] = 'Human Intervention (fix this week) - LienId is NULL in COL' and [Percent Escrow Remaining] < .2 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			
			When [Status_Check] = 'Human Intervention (fix this week) - LienId is not valid - delete out of COL?' then 'Human Intervention (fix this week)'
			When [Status_Check] = 'Human Intervention (fix this week) - LienId is NULL in COL' then 'Human Intervention (fix this week)'

			When [Updated Status] = 'Look Into' then 'Look Into'
			When [ThirdPartyId_Match?] = 'Look Into' then 'Look Into'
			When [New Liens?] = 'Look Into' then 'Look Into'
			When [Status_Check] = 'Look Into' then 'Look Into'
			When [LienType_Check] = 'Look Into' then 'Look Into'
			When [LienId_Check] = 'Look Into' then 'Look Into'
			When [Amount_Check] = 'Look Into' then 'Look Into'
			When [Question_#_Check] = 'Look Into' then 'Look Into'
			When [Lienholder_Check] = 'Look Into' then 'Look Into'
			When [SLAM LienType (converted)] = 'Look Into' then 'Look Into'
			
			When Prob_Check like 'Human Intervention (fix this week)%' and [Percent Escrow Remaining] < .19 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			When [Updated Status] like 'Human Intervention (fix this week)%' and [Percent Escrow Remaining] < .19 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			When [ThirdPartyId_Match?] like 'Human Intervention (fix this week)%' and [Percent Escrow Remaining] < .19 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			When [New Liens?] like 'Human Intervention (fix this week)%' and [Percent Escrow Remaining] < .19 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			When [Status_Check] like 'Human Intervention (fix this week)%' and [Percent Escrow Remaining] < .19 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			When [LienType_Check] like 'Human Intervention (fix this week)%' and [Percent Escrow Remaining] < .19 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			When [LienId_Check] like 'Human Intervention (fix this week)%' and [Percent Escrow Remaining] < .19 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			When [Amount_Check] like 'Human Intervention (fix this week)%' and [Percent Escrow Remaining] < .19 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			When [Question_#_Check] like 'Human Intervention (fix this week)%' and [Percent Escrow Remaining] < .19 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			When [Lienholder_Check] like 'Human Intervention (fix this week)%' and [Percent Escrow Remaining] < .19 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			When [InSLAM_Check] like 'Human Intervention (fix this week)%' and [Percent Escrow Remaining] < .19 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			
			When Prob_Check like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [Updated Status] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [ThirdPartyId_Match?] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [New Liens?] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [Status_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [LienType_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [LienId_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [Amount_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [Question_#_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [Lienholder_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [InSLAM_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			
			When [New Liens?] = 'Happy Path - Add Lien' and [Percent Escrow Remaining] < .19 then 'Human Intervention (fix this week)'
			When [LienId_Check] = 'Happy Path - Add lien' and [Percent Escrow Remaining] < .19 then 'Human Intervention (fix this week)'
			
			When [Status_Check] like 'Happy Path%' and [Percent Escrow Remaining] < .19 then 'Human Intervention (fix this week)'
			When [Amount_Check] like 'Happy Path%' and [Percent Escrow Remaining] < .19 then 'Human Intervention (fix this week)'
			When [Question_#_Check] like 'Happy Path%' and [Percent Escrow Remaining] < .19 then 'Human Intervention (fix this week)'
			When [Lienholder_Check] like 'Happy Path%' and [Percent Escrow Remaining] < .19 then 'Human Intervention (fix this week)'
			
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
			When [Prob_Check] like 'No update, no issue%' then 'No change, no issue'
						
			Else 'Look Into'
			End as [Initial_CMS_Label],
	
		Case
			When [Other lien type] like '%Ch. 13%' or [Other lien type] like '%Bankruptcy%' or [Other lien type] = 'Bk Trustee' or [Other lien type] like '%Chapter 13%' or [Other lien type] like '%Ch. 7%' or [Other lien type] like '%s Comp Lien%' or [Other lien type] = 'Public Welfare Lien' then 'No Change, no issue'
			When Prob_Check like 'Not Eligible%' then 'Not Eligible'
			When [COL LienType] = 'Litigation Finance' or [COL LienType] = 'Attorney' or [COL LienType] = 'Child Care' then 'No change, no issue'
			When [COL LienType] = 'Other' and ([COL Lienholder] like '%trustee%' or [COL Lienholder] like '%Ch. 13%' or [COL Lienholder] like '%Ch. 7%' or [COL Lienholder] like '%Bankruptcy%' or [COL Lienholder] like '%chapter%' or [COL Lienholder] like '%law%' or [COL Lienholder] like '%mortgage%') then 'No change, no issue'
			When [COL Question #] > 5 and ([COL Lienholder] like '%trustee%' or [COL Lienholder] like '%Ch. 13%' or [COL Lienholder] like '%Ch. 7%' or [COL Lienholder] like '%Bankruptcy%' or [COL Lienholder] like '%chapter%' or [COL Lienholder] like '%law%' or [COL Lienholder] like '%mortgage%') then 'No change, no issue'
			When [COL Lienholder] like '%EIF%' then 'Not Eligible'
			When [SLAM LienType] = 'Medicare Lien - Duplicate' or [SLAM LienType] = 'Private Lien' or [SLAM LienType] = 'Look Into' then 'Human Intervention (fix this week)'
			When [COL LienType] = 'Look Into' then 'Human Intervention (fix this week)'
			
			When [Status_Check] = 'Not Eligible' then 'Not Eligible'
			When [New Liens?] = 'Not Eligible' then 'Not Eligible'
			When [LienType_Check] = 'Not Eligible' then 'Not Eligible'
			When [Amount_Check] = 'Not Eligible' then 'Not Eligible'
			When [Question_#_Check] = 'Not Eligible' then 'Not Eligible'
			When [Lienholder_Check] = 'Not Eligible' then 'Not Eligible'
			When [ThirdPartyId_Match?] = 'Not Eligible' then 'Not Eligible'
			When [LienId_Check] = 'Not Eligible' then 'Not Eligible'
			When [InSLAM_Check] = 'Not Eligible' then 'Not Eligible'

			When [Status_Check] = 'Human Intervention (fix this week) - LienId is not valid - delete out of COL?' and [Percent Escrow Remaining] < .2 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			When [Status_Check] = 'Human Intervention (fix this week) - LienId is NULL in COL' and [Percent Escrow Remaining] < .2 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			
			When [Status_Check] = 'Human Intervention (fix this week) - LienId is not valid - delete out of COL?' then 'Human Intervention (fix this week)'
			When [Status_Check] = 'Human Intervention (fix this week) - LienId is NULL in COL' then 'Human Intervention (fix this week)'

			When [Updated Status] = 'Look Into' then 'Look Into'
			When [ThirdPartyId_Match?] = 'Look Into' then 'Look Into'
			When [New Liens?] = 'Look Into' then 'Look Into'
			When [Status_Check] = 'Look Into' then 'Look Into'
			When [LienType_Check] = 'Look Into' then 'Look Into'
			When [LienId_Check] = 'Look Into' then 'Look Into'
			When [Amount_Check] = 'Look Into' then 'Look Into'
			When [Question_#_Check] = 'Look Into' then 'Look Into'
			When [Lienholder_Check] = 'Look Into' then 'Look Into'
			When [SLAM LienType (converted)] = 'Look Into' then 'Look Into'

			When Prob_Check like 'Human Intervention (fix this week)%' and [Percent Escrow Remaining] < .19 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			When [Updated Status] like 'Human Intervention (fix this week)%' and [Percent Escrow Remaining] < .19 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			When [ThirdPartyId_Match?] like 'Human Intervention (fix this week)%' and [Percent Escrow Remaining] < .19 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			When [New Liens?] like 'Human Intervention (fix this week)%' and [Percent Escrow Remaining] < .19 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			When [Status_Check] like 'Human Intervention (fix this week)%' and [Percent Escrow Remaining] < .19 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			When [LienType_Check] like 'Human Intervention (fix this week)%' and [Percent Escrow Remaining] < .19 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			When [LienId_Check] like 'Human Intervention (fix this week)%' and [Percent Escrow Remaining] < .19 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			When [Amount_Check] like 'Human Intervention (fix this week)%' and [Percent Escrow Remaining] < .19 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			When [Question_#_Check] like 'Human Intervention (fix this week)%' and [Percent Escrow Remaining] < .19 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			When [Lienholder_Check] like 'Human Intervention (fix this week)%' and [Percent Escrow Remaining] < .19 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			When [InSLAM_Check] like 'Human Intervention (fix this week)%' and [Percent Escrow Remaining] < .19 and [SLAM Final] <> 'Yes' then 'Human Intervention (fix when you can)'
			
			When Prob_Check like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [Updated Status] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [ThirdPartyId_Match?] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [New Liens?] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [Status_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [LienType_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [LienId_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [Amount_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [Question_#_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [Lienholder_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			When [InSLAM_Check] like 'Human Intervention (fix this week)%' then 'Human Intervention (fix this week)'
			
			When [New Liens?] = 'Happy Path - Add Lien' and [Percent Escrow Remaining] < .19 then 'Human Intervention (fix this week)'
			When [LienId_Check] = 'Happy Path - Add lien' and [Percent Escrow Remaining] < .19 then 'Human Intervention (fix this week)'
			
			When [Status_Check] like 'Happy Path%' and [Percent Escrow Remaining] < .19 then 'Human Intervention (fix this week)'
			When [Amount_Check] like 'Happy Path%' and [Percent Escrow Remaining] < .19 then 'Human Intervention (fix this week)'
			When [Question_#_Check] like 'Happy Path%' and [Percent Escrow Remaining] < .19 then 'Human Intervention (fix this week)'
			When [Lienholder_Check] like 'Happy Path%' and [Percent Escrow Remaining] < .19 then 'Human Intervention (fix this week)'
			
			When [New Liens?] = 'Happy Path - Add Lien' then 'Add Lien'
			When [LienId_Check] = 'Happy Path - Add lien' then 'Add Lien'
			
			When [Status_Check] like 'Happy Path%' then 'Happy Path'
			When [Amount_Check] like 'Happy Path%' then 'Happy Path'
			When [Question_#_Check] like 'Happy Path%' then 'Happy Path'
			When [Lienholder_Check] like 'Happy Path%' then 'Happy Path'
			When [New Liens?] like 'Happy Path%' then 'Happy Path'

			When [ThirdPartyId_Match?] = 'No change, no issue' then 'No change, no issue'
			When [Status_Check] = 'No change, no issue' then 'No change, no issue'
			When [LienType_Check] = 'No change, no issue' then 'No change, no issue'
			When [LienId_Check] = 'No change, no issue' then 'No change, no issue'
			When [Amount_Check] = 'No change, no issue' then 'No change, no issue'
			When [Question_#_Check] = 'No change, no issue' then 'No change, no issue'
			When [Lienholder_Check] = 'No change, no issue' then 'No change, no issue'
			When [InSLAM_Check] = 'No change, no issue' then 'No change, no issue'
			When [New Liens?] = 'No update, no issue' then 'No change, no issue'
			When [Prob_Check] like 'No update, no issue%' then 'No change, no issue'
			
			Else 'Look Into'
			End as [CMS_Label]

From (
		Select	sub.*,
			--#Problems Check
				Case
					When Prob_Notes = 'Do not update in normal process' then 'Not Eligible - #Problems'
					When CaseName like '%EIF' or CaseName like '%hold%' or CaseName like '%Closed%' then 'Not Eligible - EIF or hold or closed case'
					When [Case Name] like '%EIF' or [Case Name] like '%hold%' or [Case Name] like '%Closed%' then 'Not Eligible - EIF or hold or closed case'
					When BUDNSFW_ClientIssue_CMS is not null then 'Not Eligible - BUDNSFW client issue'
					When BUDNSFW_LienIssue is not null then 'Not Eligible - BUDNSFW lien issue'
					When [SLAM Final] = 'No' then 'Not Eligible - Pending'
					When [Claimant on CSR?] like 'Not Eligible%' then 'Not Eligible - Not on CSR'
					
					When [Client Truly Final] = 'Issue' and [SLAM CaseId] in (2284, 2919, 3634, 2184, 2450) and ([SLAM Quest] is null or [SLAM Quest] = 0) then 'No Change, No Issue - no questionnaire'
					When [Client Truly Final] = 'Issue' and [SLAM CaseId] in (2284, 2919, 3634, 2184, 2450) and [SLAM Quest] = 1 then 'Human Intervention (fix this week) - Final status issue'
					When [Client Truly Final] = 'Issue' and [SLAM CaseId] not in (2284, 2919, 3634, 2184, 2450) then 'Human Intervention (fix this week) - Final status issue'
					
					Else 'No change, no issue'
					End As Prob_Check,

			--Third Party Id check
				Case
					When [COL Claim number] = [ThirdPartyId] then 'No change, no issue'

					When [COL Claim number] <> [ThirdPartyId] then 'Human Intervention (fix this week) - ThirdPartyId mismatch'

					When [ThirdPartyId] is null and [SLAM Stage] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - SLAM data not pulling'

					Else 'Look Into'
					End as [ThirdPartyId_Match?],
					

			--Check for New liens
				Case
					When [COL Lienholder] is null and [COL LienType] is null and [COL Question #] is null and [COL Status] is null and [COL Amount] is null then 'Human Intervention (fix this week) - delete empty lien from COL'
					--When [COL LienId] is null and [Claim Ref #] is not null and [COL LienType] is not null then 'Human Intervention (fix this week) - LienId is NULL in COL'
					--When [COL LienId] is null and [COL LienType] is not null and [SLAM LienId] is null then 'Human Intervention (fix this week) - LienId is NULL in COL'
					
					When [COL Id] is Null and [SLAM Stage] = 'Closed' and [SLAM ClosedReason] like 'Resolved - Final Demand' then 'Human Intervention (fix this week) - Lien is resolved in SLAM but not in COL at all'
					--When [SLAM Stage] is null and [SLAM OnBenefits] is null and [COL LienId] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - Lien Id needs update'
					
					--When [COL Id] is not null and ([SLAM Stage] like 'final%' or [SLAM Status] = 'Final' or [SLAM Stage] = 'Closed') and [COL Status] = 'Final' then 'No update, no issue'

					--When [COL Id] is not null and [SLAM Status] = 'Not Entitled' and [COL Status] = 'Not Entitled' then 'No update, no issue'
					--When [COL Id] is not null and ([SLAM Stage] = 'Closed' or [SLAM Stage] like 'final no entitlement') and [COL Status] = 'Not Entitled' then 'No update, no issue'

					--When [COL Id] is not null and [SLAM Status] = 'Pending' and [COL Status] = 'Pending' then 'No update, no issue'
					--When [COL Id] is not null and [SLAM Stage] not like 'final%' and [SLAM Stage] <> 'Closed' and [COL Status] = 'Pending' then 'No update, no issue'
					
					--When [COL Id] is not null and [SLAM Status] = 'Pending' and [COL Status] = 'Final' then 'Human Intervention (fix this week) - Final in COL but pending in SLAM'
					--When [COL Id] is not null and [SLAM Stage] not like 'final%' and [SLAM Stage] <> 'Closed' and [COL Status] = 'Final' then 'Human Intervention (fix this week) - Final in COL but pending in SLAM'
					--When [COL Id] is not null and [SLAM Status] = 'Pending' and [COL Status] = 'Not Entitled' then 'Human Intervention (fix this week) - Not Entitled in COL but pending in SLAM'
					--When [COL Id] is not null and [SLAM Stage] not like 'final%' and [SLAM Stage] <> 'Closed' and [COL Status] = 'Not Entitled' then 'Human Intervention (fix this week) - Not Entitled in COL but pending in SLAM'
					
					--When [SLAM LienId] is not null and [SLAM OnBenefits] is null and [COL Status] = 'Pending' then 'Not Eligible'
					--When [SLAM Status] = 'Pending' and [COL Status] = 'Pending' then 'Not Eligible'
					--When [COL Id] is Null and [SLAM Status] = 'Pending' then 'Not Eligible'
					--When [COL Id] is Null and [SLAM Stage] not like 'Final%' and [SLAM Stage] <> 'Closed' then 'Not Eligible'
					--When [SLAM Stage] <> 'Closed' and [SLAM Stage] not like 'final%' then 'Not Eligible'

					When [COL Id] is Null and [SLAM Status] = 'Final' then 'Happy Path - Add Lien'
					When [COL Id] is not Null and [SLAM Status] = 'Final' and [COL Status] = 'Pending' then 'Happy Path - Update needed'

					When [ThirdPartyId] is null and [SLAM Stage] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - SLAM data not pulling'

					When [COL Id] is not null then 'No change, no issue'
										
					Else 'Look Into'

					End as [New Liens?],

			--Check Status
				Case
					When [SLAM Status] = 'Look Into' then 'Look Into'
					When [SLAM Status] = 'Pending' and ([SLAM Stage] = 'Closed' or [SLAM Stage] like 'final%') then 'Human Intervention (fix this week) - SLAM stage/status is inconsistent'

					When [COL Question #] > 8 and [SLAM Status] = 'Final' and [COL Amount] = 0 and [COL Status] = 'Final' then 'No change, no issue'

					When [COL Lienholder] is null and [COL LienType] is null and [COL Question #] is null and [COL Status] is null and [COL Amount] is null then 'Human Intervention (fix this week) - delete empty lien from COL'
					When [COL LienId] is null and [Claim Ref #] is not null and [COL LienType] is not null then 'Human Intervention (fix this week) - LienId is NULL in COL'
					When [COL LienId] is null and [COL LienType] is not null and [SLAM LienId] is null then 'Human Intervention (fix this week) - LienId is NULL in COL'
					
					When [SLAM LienId] is not null and [SLAM OnBenefits] is null and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Status] = 'Pending' and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Stage] <> 'Closed' and [SLAM Stage] not like 'final%' and [COL Status] = 'Pending' then 'Not Eligible'
					
					When [SLAM Stage] is null and [SLAM OnBenefits] is null and [COL LienId] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - Lien Id needs update'
					
					When [SLAM Stage] not like 'Final%' and [SLAM Stage] not like 'Closed' and [COL Status] = 'Final' then 'Human Intervention (fix this week) - final in COL but pending in SLAM'
					When [COL Status] is null and [COL Id] is not null then 'Human Intervention (fix this week) - COL status is null'
					When [COL Status] = 'Final' and [SLAM Status] = 'Pending' then 'Human Intervention (fix this week) - final in COL but pending in SLAM'
										
					When ([SLAM Stage] = 'Final No Entitlement' or [SLAM Status] = 'Not Entitled') and [COL Status] <> 'Not Entitled' and [COL Status] <>  'Pending' then 'Human Intervention (fix this week) - not entitled in SLAM but COL mismatch'
					When [SLAM Stage] = 'Closed' and ([SLAM ClosedReason] = 'Resolved - No Entitlement' or [SLAM ClosedReason] like 'Opened in Error' or [SLAM ClosedReason] like 'Per Att%') and [COL Status] <> 'Not Entitled' and [COL Status] <>  'Pending' then 'Human Intervention (fix this week) - not entitled in SLAM but COL mismatch'
					
					When [SLAM Stage] = 'Closed' and [SLAM ClosedReason] is null then 'Human Intervention (Fix this week) - update SLAM closedreason'
					When [COL LienId] = '9999999' then 'Human Intervention (fix this week) - LienId is not valid - delete out of COL?'
					When [COL LienId] is not null and [COL Id] is not null and [SLAM Stage] is null and [SLAM LienType] is null then 'Human Intervention (fix this week) - Check case in SLAM - claimant is probably not in the right case'
					When [COL LienId] is null and [COL Id] is not null and [SLAM Stage] is null and [SLAM LienType] is null then 'Human Intervention (fix this week) - Lien might not be in SLAM'

					When [COL Status] = 'Not Entitled' and [SLAM Status] = 'Final' and [SLAM True FD Amount] = 0 then 'Human Intervention (fix when you can) - not entitled in COL but final in SLAM, $0 FD'
					When [COL Status] = 'Not Entitled' and [SLAM Status] = 'Final' and [SLAM True FD Amount] > 0 then 'Human Intervention (fix this week) - not entitled in COL but final in SLAM'

					When [SLAM Status] <> 'Closed' and ([SLAM ClosedReason] = 'Opened in Error' or [SLAM ClosedReason] = 'Resolved - No Entitlement' or [SLAM ClosedReason] like 'Per Att%') then 'Human Intervention (fix this week) - SLAM stage and closed reason inconsistent'

					When [COL Status] = 'Pending' and ([SLAM Stage] like 'Final%' or [SLAM Status] = 'Final') then 'Happy Path - Update needed'
					When [COL Status] = 'Pending' and ([SLAM ClosedReason] = 'Opened in Error' or [SLAM ClosedReason] = 'Resolved - No Entitlement' or [SLAM ClosedReason] like 'Per Att%') then 'Happy Path - Update needed'
					
					
					When [COL Status] = 'Final' and [SLAM Status] = 'Final' then 'No change, no issue'
					When [SLAM Status] = 'Not Entitled' and [COL Status] = 'Not Entitled' and [COL Amount] = 0 then 'No change, no issue'
					When [SLAM Stage] = 'Closed' and ([SLAM ClosedReason] = 'Opened in Error' or [SLAM ClosedReason] = 'Resolved - No Entitlement' or [SLAM ClosedReason] like 'Per Att%') and [COL Status] = 'Not Entitled' then 'No Change, no issue'
					When [SLAM Stage] = 'Final No Entitlement' and [COL Status] = 'Not Entitled' then 'No Change, no issue'

					When [COL LienType] = 'Attorney' and [COL Question #] > 5 then 'No change, no issue'
					When [COL LienType] = 'Litigation Finance' and [COL Question #] > 5 then 'No change, no issue'
					When [COL LienType] = 'Other' then 'Human Intervention (fix this week) - lientype of other'

					When [ThirdPartyId] is null and [SLAM Stage] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - SLAM data not pulling'

					Else 'Look Into'
					End as [Status_Check],

			
			--Updated SLAM Status
				Case
					When [SLAM LienId] is null and ([COL LienType] = 'Attorney' or [COL LienType] = 'Litigation Finance') then [COL Status]

					When [COL Lienholder] is null and [COL LienType] is null and [COL Question #] is null and [COL Status] is null and [COL Amount] is null then 'Human Intervention (fix this week) - delete empty lien from COL'
					When [COL LienId] is null and [Claim Ref #] is not null and [COL LienType] is not null then 'Human Intervention (fix this week) - LienId is NULL in COL'
					When [COL LienId] is null and [COL LienType] is not null and [SLAM LienId] is null then 'Human Intervention (fix this week) - LienId is NULL in COL'

					When ([COL LienType] like 'Litigation Finance' or [COL LienType] like 'Attorney') and [COL Question #] > 5 then [COL Status]
										
					When [SLAM Status] = 'Pending' and [COL Status] <> 'Pending' then 'Human Intervention (fix this week) - Pending in SLAM but not in COL'
					
					When [SLAM Status] = 'Not Entitled' and [COL Status] <> 'Not Entitled' and [COL Status] <> 'Pending' then 'Human Intervention (fix this week) - Not Entitled in SLAM but COL mismatch'
					When [SLAM Stage] = 'Final No Entitlement' and [COL Status] <> 'Pending' and [COL Status] <> 'Not Entitled' then 'Human Intervention (fix this week) - Not Entitled in SLAM but COL mismatch'
					When [SLAM Stage] = 'Closed' 
							and ([SLAM ClosedReason] = 'Opened in Error' or [SLAM ClosedReason] like 'Per Att%' or [SLAM ClosedReason] = 'Resolved - No Entitlement')
							and [COL Status] <> 'Pending' and [COL Status] <> 'Not Entitled' 
							then 'Human Intervention (fix this week) - Not Entitled in SLAM but COL mismatch'
					When [SLAM Status] = 'Not Entitled' and [COL status] = 'Final' then 'Human Intervention (fix this week) - Not Entitled in SLAM but COL mismatch'

					When [COL Status] = 'Not Entitled' and [SLAM Stage] <> 'Final No Entitlement' and [SLAM Stage] <> 'Closed'
							then 'Human Intervention (fix this week) - Not Entitled in COL but SLAM mismatch'
					
					When [COL Question #] > 5 and [SLAM Status] = 'Final' and [COL Amount] = 0 and [COL Status] = 'Final' then 'Final'
					When [COL Question #] < 6 and [SLAM Status] = 'Final' then 'Final'
													
					When [COL Question #] < 6 and [SLAM Status] = 'Not Entitled' then 'Not Entitled'
					When [COL Question #] < 6 and [SLAM Stage] = 'Final No Entitlement' then 'Not Entitled'
					When [COL Question #] < 6 and [SLAM Stage] = 'Closed' 
							and ([SLAM ClosedReason] = 'Opened in Error' or [SLAM ClosedReason] like 'Per Att%' or [SLAM ClosedReason] = 'Resolved - No Entitlement')  
							then 'Not Entitled'
					
					When [COL Question #] < 6 and [SLAM Status] = 'Pending' then 'Pending'
					When [COL Question #] < 6 and ([SLAM Stage] <> 'Closed' or [SLAM Stage] not like 'Final%') then 'Pending'
									
					When [COL LienType] like 'Other' then 'Human Intervention (fix this week) - lientype of other'

					When [ThirdPartyId] is null and [SLAM Stage] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - SLAM data not pulling'
					
					Else 'Look Into'
					End as 'Updated Status',


			--Check the lien type
				Case 
					When [SLAM LienType (converted)] = [COL LienType] then 'No Change, no issue'
					When [SLAM Stage] = 'Closed' and ([SLAM ClosedReason] = 'Opened in Error' or [SLAM ClosedReason] like 'Per att%') then 'No Change, no issue'
					
					When [COL Lienholder] is null and [COL LienType] is null and [COL Question #] is null and [COL Status] is null and [COL Amount] is null then 'Human Intervention (fix this week) - delete empty lien from COL'
					When [COL LienId] is null and [Claim Ref #] is not null and [COL LienType] is not null then 'Human Intervention (fix this week) - LienId is NULL in COL'
					When [COL LienId] is null and [COL LienType] is not null and [SLAM LienId] is null then 'Human Intervention (fix this week) - LienId is NULL in COL'

					When [SLAM Stage] not like 'Final%' and [SLAM Stage] not like 'Closed' and [COL Status] = 'Final' then 'Human Intervention (fix this week) - final in COL but pending in SLAM'

					When [SLAM LienType (converted)] = [COL LienType] and [SLAM OnBenefits] is null and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Status] = 'Pending' then 'Not Eligible'
					When [SLAM Stage] <> 'Closed' and [SLAM Stage] not like 'final%' and [COL Status] = 'Pending' then 'Not Eligible'

					When [SLAM Stage] is null and [SLAM OnBenefits] is null and [COL LienId] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - Lien Id needs update'
					When [COL LienType] is null then 'Human Intervention (fix this week) - COL lientype is null'
					When [COL LienType]<>[SLAM LienType] then 'Human Intervention (fix this week) - COL lientype <> SLAM lientype'
					When [COL LienType] like 'Other' then 'Human Intervention (fix this week) - lientype of other'
					When [SLAM LienType (converted)] = [COL LienType] and [SLAM OnBenefits] is null and [COL Status] <> 'Pending' and [SLAM LienId] is not null then 'Human Intervention (fix this week) - Pending in SLAM but not in COL'
					When [SLAM LienType (converted)] <> [COL LienType] then 'Human Intervention (fix this week) - lientype mismatch'
					When [ThirdPartyId] is null and [SLAM Stage] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - SLAM data not pulling'

					When [COL LienType] = [SLAM LienType] then 'No change, no issue'
					When [SLAM Status] = 'Not Entitled' then 'No change, no issue'
					When [COL LienType] like 'Attorney' and [COL Question #] > 5 then 'No change, no issue'
					When [COL LienType] like 'Litigation Finance' and [COL Question #] > 5 then 'No change, no issue'
					When [SLAM LienType (converted)] = [COL LienType] and [SLAM LienType] is null and [SLAM Stage] = 'Closed' then 'No Change, no issue'
										
					Else 'Look Into'
					End as [LienType_Check],



			--Check LienId
				Case 
					When [COL Lienholder] is null and [COL LienType] is null and [COL Question #] is null and [COL Status] is null and [COL Amount] is null then 'Human Intervention (fix this week) - delete empty lien from COL'
					When [COL LienId] is null and [Claim Ref #] is not null and [COL LienType] is not null then 'Human Intervention (fix this week) - LienId is NULL in COL'
					When [COL LienId] is null and [COL LienType] is not null and [SLAM LienId] is null then 'Human Intervention (fix this week) - LienId is NULL in COL'

					When [SLAM LienId] is not null and [SLAM OnBenefits] is null and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Status] = 'Pending' and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Stage] <> 'Closed' and [SLAM Stage] not like 'final%' and [COL Status] = 'Pending' then 'Not Eligible'
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

					When [ThirdPartyId] is null and [SLAM Stage] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - SLAM data not pulling'

					Else 'Look Into'
					End as [LienId_Check],



			--Check Amount	
				Case
					When [COL Lienholder] is null and [COL LienType] is null and [COL Question #] is null and [COL Status] is null and [COL Amount] is null then 'Human Intervention (fix this week) - delete empty lien from COL'
				 	When [COL LienId] is null and [Claim Ref #] is not null and [COL LienType] is not null then 'Human Intervention (fix this week) - LienId is NULL in COL'
					When [COL LienId] is null and [COL LienType] is not null and [SLAM LienId] is null then 'Human Intervention (fix this week) - LienId is NULL in COL'
					
					When [COL Question #] = 8 and [SLAM Status] = 'Final' and [COL Amount] = 0 and [COL Status] = 'Final' then 'No change, no issue'
					When [COL Question #] = 8 and [SLAM Status] = 'Final' and [COL Amount] <> 0 and [COL Status] = 'Final' then 'Human Intervention (fix ths week) - Q#8 with amount not $0'
					
					When [SLAM Stage] not like 'Final%' and [SLAM Stage] not like 'Closed' and [COL Status] = 'Final' then 'Human Intervention (fix this week) - final in COL but pending in SLAM'

					When [COL Amount] is null and [SLAM Stage] <> 'Closed' and [SLAM Stage] not like 'final%' and [SLAM Stage] is not null and [COL Status] = 'Pending' then 'Not Eligible'
					When [COL Amount] is null and [COL Status] = 'Pending' and [SLAM Status] = 'Pending' then 'Not Eligible'
					When [COL Amount] is null and [SLAM Onbenefits] is null and [SLAM LienId] is not null and [COL Status] = 'Pending' then 'Not Eligible'
					--When [COL Amount] is null and [COL Question #] > 5 and [COL Status] = 'Pending' then 'Not Eligible'
					
					When [COL Status] = 'Not Entitled' and [COL Amount] <> 0 then 'Human Intervention (fix this week) - not entitled but COL amount not $0'
					When [SLAM Status] = 'Not Entitled' and [COL Status] = 'Not Entitled' and [COL Amount] <> 0 then 'Human Intervention (fix this week) - not entitled but COL amount not $0'
					When [SLAM Stage] = 'Final No Entitlement' and [COL Status] = 'Not Entitled' and [COL Amount] <> 0 then 'Human Intervention (fix this week) - not entitled but COL amount not $0'
					When [SLAM Stage] = 'Closed' and [SLAM ClosedReason] = 'Resolved - No Entitlement' and [COL Status] = 'Not Entitled' and [COL Amount] <> 0 then 'Human Intervention (fix this week) - not entitled but COL amount not $0'
					When [SLAM Stage] = 'Closed' and [SLAM ClosedReason] like 'Opened in Error' and [COL Status] = 'Not Entitled' and [COL Amount] <> 0 then 'Human Intervention (fix this week) - not entitled but COL amount not $0'
					When [SLAM Stage] = 'Closed' and [SLAM ClosedReason] like 'Per Att%' and [COL Status] = 'Not Entitled' and [COL Amount] <> 0 then 'Human Intervention (fix this week) - not entitled but COL amount not $0'
					
					When [SLAM Stage] = 'Closed' and [SLAM ClosedReason] like 'Resolved%' and [COL Status] = 'Pending' then 'Human Intervention (fix this week) - Resolved in SLAM but pending in COL'
					When [SLAM Stage] is null and [SLAM OnBenefits] is null and [COL LienId] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - Lien Id needs update'
					When [COL Status] = 'Pending' and [COL Amount] is not null then 'Human Intervention (fix this week) - Pending in COL but has amount'
					When [COL Amount] <> Round([SLAM True FD Amount],2) and [COL Question #] <= 5 then 'Human Intervention (fix this week) - SLAM and COL lien amounts mismatch'
					When [SLAM True FD Amount] is null and [COL Amount] is not null and [SLAM Stage] <> 'Final No Entitlement' and [SLAM ClosedReason] <> 'Opened in Error' and [SLAM ClosedReason] <> 'Resolved - No Entitlement' and [SLAM ClosedReason] not like 'Per att%' then 'Human Intervention (fix this week) - COL amount is not null but SLAM is null'
					When [COL Amount] is null and ([COL Status] = 'Final' or [COL Status] = 'Not Entitled') then 'Human Intervention (fix this week) - COL lien is final but no amount'
					When [COL Amount] <> 0 and [COL Status] = 'Not Entitled' then 'Human Intervention (fix this week) - COL lien is final but no amount'
					When [COL Status] = 'Pending' and [SLAM OnBenefits] is null and [SLAM LienId] is null then 'Human Intervention (fix this week) - missing Lien Id'
					When [COL LienType] like 'Other' then 'Human Intervention (fix this week) - lientype of other'
					When [ThirdPartyId] is null and [SLAM Stage] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - SLAM data not pulling'
					When [COL Amount] is null and [SLAM True FD Amount] is not null and [COL Question #] > 5 and [COL Status] = 'Pending' and [SLAM Status] = 'Final' then 'Human Intervention (fix this week) - Q#8 amount needs updating'

					When [COL Amount] = Round([SLAM True FD Amount],2) then 'No change, no issue'
					When [COL Amount] = Round([SLAM True FD Amount],2) and [COL Question #] <= 5 and [COL Status] = 'Final' and [SLAM Status] = 'Final' then 'No change, no issue'
					When [COL Amount] = Round([SLAM True FD Amount],2) and [COL Question #] <= 5 and [COL Status] = 'Not Entitled' and [SLAM Onbenefits] = 'No' then 'No change, no issue'
					When [SLAM Status] = 'Not Entitled' and [COL Amount] = 0 then 'No change, no issue'
					When [SLAM Stage] = 'Final No Entitlement' and [COL Amount] = 0 then 'No change, no issue'
					When ([SLAM ClosedReason] = 'Opened in Error' or [SLAM ClosedReason] = 'Resolved - No Entitlement' or [SLAM ClosedReason] like 'Per att%') and [COL Amount] = 0 then 'No change, no issue'
					When [COL Question #] > 5 and ([COL Status] = 'Final' or [COL Status] = 'Not Entitled') and [COL Amount] = 0 then 'No change, no issue'
					When [COL LienType] like 'Attorney' and [COL Question #] > 5 then 'No change, no issue'
					When [COL LienType] like 'Litigation Finance' and [COL Question #] > 5 then 'No change, no issue'
					
					When [COL Amount] is null and [SLAM True FD Amount] is not null and [COL Question #] <= 5 and [COL Status] = 'Pending' and [SLAM Status] = 'Final' then 'Happy Path - update needed'
					When [COL Amount] is null and [SLAM Stage] = 'Final No Entitlement' and [COL Question #] <= 5 and [COL Status] = 'Pending' then 'Happy Path - update needed'
					When [COL Amount] is null and [SLAM Stage] = 'Closed' 
							and ([SLAM ClosedReason] = 'Opened in Error' or [SLAM ClosedReason] = 'Resolved - No Entitlement' or [SLAM ClosedReason] like 'Per att%') 
							and [COL Question #] <= 5 and [COL Status] = 'Pending' then 'Happy Path - update needed'
										
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

					When [COL Question #] <= 5 and [SLAM Status] = 'Final' then cast([SLAM True FD Amount] as varchar)
					When [COL Question #] <= 5 and [SLAM OnBenefits] = 'Yes' then cast([SLAM True FD Amount] as varchar)
					When [COL Question #] <= 5 and [SLAM Stage] like 'Final Demand%' then cast([SLAM True FD Amount] as varchar)
					When [COL Question #] <= 5 and [SLAM Stage] like 'Closed' and [SLAM ClosedReason] = 'Resolved - Final Demand' then cast([SLAM True FD Amount] as varchar)

					When [SLAM Status] = 'Not Entitled' then cast(0 as varchar)
					When [SLAM Stage] = 'Final No Entitlement' then cast(0 as varchar)
					When [SLAM Stage] = 'Closed' and [SLAM ClosedReason] = 'Opened in Error' then cast(0 as varchar)
					When [SLAM Stage] = 'Closed' and [SLAM ClosedReason] like 'Per Att%' then cast(0 as varchar)
					When [SLAM Stage] = 'Closed' and [SLAM ClosedReason] like 'Resolved - No Entitlement' then cast(0 as varchar)

					When [SLAM Status] = 'Pending' then ''
					When [SLAM OnBenefits] is null then ''
					When [SLAM Stage] <> 'Closed' and [SLAM Stage] not like 'Final%' then ''

					When [ThirdPartyId] is null and [SLAM Stage] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - SLAM data not pulling'

					Else 'Look Into'
					End as 'Updated Amount',


			--Check Question number
				Case
					When [COL Lienholder] is null and [COL LienType] is null and [COL Question #] is null and [COL Status] is null and [COL Amount] is null then 'Human Intervention (fix this week) - delete empty lien from COL'
					When [COL LienId] is null and [Claim Ref #] is not null and [COL LienType] is not null then 'Human Intervention (fix this week) - LienId is NULL in COL'
					When [COL LienId] is null and [COL LienType] is not null and [SLAM LienId] is null then 'Human Intervention (fix this week) - LienId is NULL in COL'

					--Q# > 5 Check
						When ([COL Question #] = '8' or [COL Question #] = 8) and [SLAM Status] = 'Final' and ([COL Amount] = '0' or [COL Amount] = 0) and [COL Status] = 'Final' then 'No change, no issue'
						When ([COL Question #] = '7' or [COL Question #] = 7) and [SLAM Status] = 'Final' and ([COL Amount] = '0' or [COL Amount] = 0) and [COL Status] = 'Final' then 'No change, no issue'
						When ([COL Question #] = '6' or [COL Question #] = 6) and [SLAM Status] = 'Final' and ([COL Amount] = '0' or [COL Amount] = 0) and [COL Status] = 'Final' then 'No change, no issue'
						
						When ([COL Question #] = '8' or [COL Question #] = 8) and [COL Status] <> 'Final' and [SLAM Status] = 'Final' then 'Human Intervention (fix this week) - Q# > 5 needs review'
						When ([COL Question #] = '7' or [COL Question #] = 7) and [COL Status] <> 'Final' and [SLAM Status] = 'Final' then 'Human Intervention (fix this week) - Q# > 5 needs review'
						When ([COL Question #] = '6' or [COL Question #] = 6) and [COL Status] <> 'Final' and [SLAM Status] = 'Final' then 'Human Intervention (fix this week) - Q# > 5 needs review'
						
						When ([COL Question #] = '8' or [COL Question #] = 8) and [SLAM Status] = 'Final' and [COL Amount] <> 0 and [COL Status] = 'Final' then 'Human Intervention (fix this week) - Q# > 5 needs review'
						When ([COL Question #] = '7' or [COL Question #] = 7) and [SLAM Status] = 'Final' and [COL Amount] <> 0 and [COL Status] = 'Final' then 'Human Intervention (fix this week) - Q# > 5 needs review'
						When ([COL Question #] = '6' or [COL Question #] = 6) and [SLAM Status] = 'Final' and [COL Amount] <> 0 and [COL Status] = 'Final' then 'Human Intervention (fix this week) - Q# > 5 needs review'
						

					When [SLAM LienId] is not null and [SLAM OnBenefits] is null and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Status] = 'Pending' and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Stage] <> 'Closed' and [SLAM Stage] not like 'final%' and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Stage] is null and [SLAM OnBenefits] is null and [COL LienId] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - Lien Id needs update'
					
					When [COL Question #] <> [SLAM Question #] then 'Human Intervention (fix this week) - Question # mismatch'
						
					When [COL Question #] = [SLAM Question #] then 'No change, no issue'
					When [COL Question #] > 5 then 'No change, no issue'
					When [COL LienType] like 'Attorney' and [COL Question #] > 5 then 'No change, no issue'
					When [COL LienType] like 'Litigation Finance' and [COL Question #] > 5 then 'No change, no issue'
					
					When [COL Status] = 'Pending' and [SLAM OnBenefits] is null and [SLAM LienId] is null then 'Human Intervention (fix this week) - missing Lien Id'

					When [SLAM Question #] is null and [COL Question #] is not null and [SLAM Stage] = 'Final No Entitlement' then 'No change, no issue'
					When [SLAM Question #] is null and [COL Question #] is not null and ([SLAM ClosedReason] = 'Opened in Error' or [SLAM ClosedReason] = 'Resolved - No Entitlement' or [SLAM ClosedReason] like 'Per att%') then 'No change, no issue'
					When [SLAM Question #] is null and [COL Question #] is not null then 'Human Intervention (fix this week) - NULL in SLAM but not COL'

					When [COL Question #] is null then 'Human Intervention (fix this week) - Question # is NULL in COL'

					When [ThirdPartyId] is null and [SLAM Stage] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - SLAM data not pulling'

					Else 'Look Into'
					End as [Question_#_Check],


			--Check Lienholder Name

				Case
					When [COL Lienholder] is null and [COL LienType] is null and [COL Question #] is null and [COL Status] is null and [COL Amount] is null then 'Human Intervention (fix this week) - delete empty lien from COL'
					When [COL LienId] is null and [Claim Ref #] is not null and [COL LienType] is not null then 'Human Intervention (fix this week) - LienId is NULL in COL'
					When [COL LienId] is null and [COL LienType] is not null and [SLAM LienId] is null then 'Human Intervention (fix this week) - LienId is NULL in COL'


					When [SLAM LienId] is not null and [SLAM OnBenefits] is null and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Status] = 'Pending' and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Stage] <> 'Closed' and [SLAM Stage] not like 'final%' and [COL Status] = 'Pending' then 'Not Eligible'
					When [SLAM Stage] is null and [SLAM OnBenefits] is null and [COL LienId] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - Lien Id needs update'
					
					--When len([COL Lienholder]) <= 50 and [COL Lienholder] = [SLAM Lienholder] then 'No change, no issue' 
					--When len([COL Lienholder]) > 50 then 'Human Intervention (fix this week) - COL lienholder name is more than 50 characters'
					When [COL Lienholder] = [SLAM Lienholder] then 'No change, no issue' 
					
					When [Percent Escrow Remaining] < .15 then 'No change, no issue'
					When [Percent Escrow Remaining] = 0 or [Percent Escrow Remaining] = '0' then 'No change, no issue'

					When [COL Lienholder] = 'MO Medicaid' and [SLAM Lienholder] = 'MO Medicaid ' then 'No change, no issue'
					When [COL Lienholder] = 'CO Medicaid' and [SLAM Lienholder] = 'CO Medicaid ' then 'No change, no issue'
					When [COL Lienholder] = 'AL Medicaid' and [SLAM Lienholder] = 'AL Medicaid ' then 'No change, no issue'
					When [COL Lienholder] = 'KS Medicaid' and [SLAM Lienholder] = 'KS Medicaid ' then 'No change, no issue'
					When [COL Lienholder] = 'MS Medicaid' and [SLAM Lienholder] = 'MS Medicaid ' then 'No change, no issue'
					When [COL Lienholder] = 'ME Medicaid' and [SLAM Lienholder] = 'ME Medicaid ' then 'No change, no issue'
					When [COL Lienholder] = '%OK Medicaid%' and [SLAM Lienholder] = '%OK Medicaid%' then 'No change, no issue'
					When [COL Lienholder] = 'GA Medicaid' and [SLAM Lienholder] = 'GA Medicaid ' then 'No change, no issue'
					When [COL Lienholder] = 'BCBS Florida' and [SLAM Lienholder] = 'BCBS FL' then 'No change, no issue'
					When [COL Lienholder] like '%Regence%' and [SLAM Lienholder] like '%Regence%' then 'No change, no issue'
					When [COL Lienholder] = 'MD Medicaid' and [SLAM Lienholder] = 'MD Medicaid ' then 'No change, no issue'
					When [COL Lienholder] = 'NC Medicaid' and [SLAM Lienholder] = 'NC Medicaid ' then 'No change, no issue'
					When [COL Lienholder] = 'KY Medicaid' and [SLAM Lienholder] = 'KY Medicaid ' then 'No change, no issue'
					When [COL Lienholder] = 'KY Spirit (KY MCO)' and [SLAM Lienholder] = 'KY Spirit (KY MCO)/Centene' then 'No change, no issue'
					When [COL Lienholder] = 'Meridian (MI MCO)' and [SLAM Lienholder] = 'Meridian (MI MCO) ' then 'No change, no issue'
					When [COL Lienholder] = 'Keystone' and [SLAM Lienholder] = 'Keystone Health Plan West, Inc/Highmark, Inc.' then 'No change, no issue'
					When [COL Lienholder] = 'IA Medicaid' and [SLAM Lienholder] = 'IA Medicaid ' then 'No change, no issue'
					When [COL Lienholder] = 'Freedom Health' and [SLAM Lienholder] = 'Freedom Health ' then 'No change, no issue'
					When [COL Lienholder] = 'NH Medicaid' and [SLAM Lienholder] = 'NH Medicaid ' then 'No change, no issue'
					When [COL Lienholder] = 'BCBS North Carolina' and [SLAM Lienholder] = 'BCBS NC' then 'No change, no issue'
					When [COL Lienholder] = 'HealthNow' and [SLAM Lienholder] = 'HealthNow New York' then 'No change, no issue'
					When [COL Lienholder] = 'Viva Health' and [SLAM Lienholder] = 'Viva Health (Mass Tort)' then 'No change, no issue'
					When [COL Lienholder] = 'Blue Cross Medicare Advantage' and [SLAM Lienholder] = 'Blue Cross Medicare Advantage/HCSC' then 'No change, no issue'
					When [COL Lienholder] = 'Blue Cross Blue Shield Association' and [SLAM Lienholder] = 'BCBS Association (FEBA)' then 'No change, no issue'
					When [COL Lienholder] = 'MN Medicaid' and [SLAM Lienholder] = 'MN Medicaid ' then 'No change, no issue'
					When [COL Lienholder] = 'Banner Medisun/BCBS AZ' and [SLAM Lienholder] = 'Banner Medisun/BCBS AZ Medicare Advantage' then 'No change, no issue'
					When [COL Lienholder] = 'MT Medicaid' and [SLAM Lienholder] = 'MT Medicaid ' then 'No change, no issue'
					When [COL Lienholder] = 'Priority Health' and [SLAM Lienholder] = 'Priority Health (PLRP)' then 'No change, no issue'
					When [COL Lienholder] = 'AvMed' and [SLAM Lienholder] = 'AvMed (PLRP)' then 'No change, no issue'
					When [COL Lienholder] like '%Wellpoint%' and [SLAM Lienholder] like '%Wellpoint%' then 'No change, no issue'
					When [COL Lienholder] like '%Cigna%' and [SLAM Lienholder] like '%Cigna%' then 'No change, no issue'
					When [COL Lienholder] = 'NY Medicaid' and [SLAM Lienholder] = 'NY Medicaid ' then 'No change, no issue'
					When [COL Lienholder] = 'United Community (MI MCO)' and [SLAM Lienholder] = 'United Community (MI MCO) ' then 'No change, no issue'
					When [COL Lienholder] like '%Air Force%' and [SLAM Lienholder] like '%Air Force%' then 'No change, no issue'
					When [COL Lienholder] = 'SelectCare of Texas' and [SLAM Lienholder] = 'SelectCare of Texas/Universal American' then 'No change, no issue'
					When [COL Lienholder] = 'BCBS AL' and [SLAM Lienholder] = 'Blue Advantage Plus of AL/BCBS AL' then 'No change, no issue'
					When [COL Lienholder] = 'CareMore Health Plan' and [SLAM Lienholder] = 'CareMore Health Plan/Anthem' then 'No change, no issue'
					When [COL Lienholder] like 'Department of VA%' and [SLAM Lienholder] like 'Department of Veterans Affairs%' then 'No change, no issue'
					When [COL Lienholder] = 'MA Medicaid' and [SLAM Lienholder] = 'MA Medicaid ' then 'No change, no issue'
					When [COL Lienholder] = 'BCBS of MN' and [SLAM Lienholder] = 'BCBS MN' then 'No change, no issue'
					When [COL Lienholder] = 'BCBS Massachusetts' and [SLAM Lienholder] = 'BCBS of MA' then 'No change, no issue'
					When [COL Lienholder] = 'Blue Care Network' and [SLAM Lienholder] = 'Blue Care Network ' then 'No change, no issue'
					When [COL Lienholder] = 'Nassau County - NY Medicaid - TA' and [SLAM Lienholder] = 'Nassau County - NY Medicaid - Temporary Assistance' then 'No change, no issue'
					When [COL Lienholder] = 'UnitedHealthcare Community Plan' and [SLAM Lienholder] = 'United Healthcare Community Plan' then 'No change, no issue'
					When [COL Lienholder] = 'BCBS of Michigan' and [SLAM Lienholder] = 'BCBS of Michigan (Direct)' then 'No change, no issue'
					When [COL Lienholder] = 'NY Medicaid - Cayunga County' and [SLAM Lienholder] = 'NY Medicaid - Cayuga County' then 'No change, no issue'
					When [COL Lienholder] = 'BCBS of AR' and [SLAM Lienholder] = 'BCBS AR' then 'No change, no issue'
					When [COL Lienholder] = 'Independent Health Association' and [SLAM Lienholder] = 'Independent Health Association ' then 'No change, no issue'
					When [COL Lienholder] like '%Walmart%' and [SLAM Lienholder] like '%Walmart%' then 'No change, no issue'
					When [COL Lienholder] = 'BCBS OK' and [SLAM Lienholder] = 'BCBS OK/HCSC' then 'No change, no issue'
					When [COL Lienholder] = 'Arizona Physicians IPA Inc.' and [SLAM Lienholder] = 'Arizona Physicians IPA Inc/UHC' then 'No change, no issue'
					When [COL Lienholder] = 'BCBS of Texas' and [SLAM Lienholder] = 'BCBS TX/HCSC' then 'No change, no issue'
					When [COL Lienholder] = 'Health Advantage' and [SLAM Lienholder] = 'Health Advantage/BCBS AR' then 'No change, no issue'
					When [COL Lienholder] = 'BCBS MA' and [SLAM Lienholder] = 'BCBS of MA' then 'No change, no issue'
					When [COL Lienholder] = 'NY Medicaid - NYC County' and [SLAM Lienholder] = 'NY Medicaid - NYC' then 'No change, no issue'
					When [COL Lienholder] = 'IHS - Cherokee Nation' and [SLAM Lienholder] = 'IHS - Cherokee Nation ' then 'No change, no issue'
					When [COL Lienholder] = 'Mercy Health Plans of MO (Part C)' and [SLAM Lienholder] = 'Mercy Health Plans' then 'No change, no issue'
					When [COL Lienholder] = 'Preferred Care Partners' and [SLAM Lienholder] = 'Preferred Care Partners/UHC' then 'No change, no issue'
					When [COL Lienholder] = 'Akamai Advantage' and [SLAM Lienholder] = 'Akamai Advantage/HMSA' then 'No change, no issue'
					When [COL Lienholder] like '%Vista%' and [SLAM Lienholder] like '%Vista%' then 'No change, no issue'
					When [COL Lienholder] like '%Anthem%' and [SLAM Lienholder] like '%Anthem%' then 'No change, no issue'
					When [COL Lienholder] = 'Louisiana Healthcare Connections (LA MCO)' and [SLAM Lienholder] = 'Louisiana Healthcare Connections (LA MCO)/Centene' then 'No change, no issue'
					When [COL Lienholder] = 'BCBS IL' and [SLAM Lienholder] = 'BCBS IL/HCSC' then 'No change, no issue'
					When [COL Lienholder] = 'CareFirst' and [SLAM Lienholder] = 'CareFirst (PLRP)' then 'No change, no issue'
					When [COL Lienholder] like '%Magnolia Health Plan%' and [SLAM Lienholder] like '%Magnolia Health Plan%' then 'No change, no issue'
					When [COL Lienholder] = 'PHP (MI MCO)' and [SLAM Lienholder] = 'Physicians Health Plan Mid MI (MI MCO)' then 'No change, no issue'
					When [COL Lienholder] = 'Meridian (MI MCO)' and [SLAM Lienholder] = 'Meridian Health Plan' then 'No change, no issue'
					When [COL Lienholder] = 'Passport Advantage' and [SLAM Lienholder] = 'Passport' then 'No change, no issue'
					When [COL Lienholder] = 'Kentucky Passport Health Plan' and [SLAM Lienholder] = 'Passport (KY MCO)' then 'No change, no issue'
					When [COL Lienholder] = 'Health Options Inc.' and [SLAM Lienholder] = 'Health Options Inc. ' then 'No change, no issue'
					When [COL Lienholder] = 'SelectHealth Advantage' and [SLAM Lienholder] = 'Select Health Advantage' then 'No change, no issue'
					When [COL Lienholder] = 'NY Medicaid-Schenectady' and [SLAM Lienholder] = 'NY Medicaid - Schenectady ' then 'No change, no issue'
					When [COL Lienholder] = 'NY Medicaid - Schenectady Temp. Assistance' and [SLAM Lienholder] = 'Schenectady County - NY Medicaid - Temporary Assistance' then 'No change, no issue'
					When [COL Lienholder] = 'Michigan Council of Carpenters Health & Welfare' and [SLAM Lienholder] = 'Michigan Regional Council of Carpenters Health & Welfare Fund' then 'No change, no issue'
					When [COL Lienholder] = 'Moda (OR CCO)' and [SLAM Lienholder] = 'Moda/Eastern Oregon (OR CCO)' then 'No change, no issue'
					When [COL Lienholder] = 'Capital District Physicians Health Plan' and [SLAM Lienholder] = 'Capital District Physicians Health Plan ' then 'No change, no issue'
					When [COL Lienholder] = 'Albany County - NY Medicaid - Temp Assistance' and [SLAM Lienholder] = 'Albany County - NY Medicaid - Temporary Assistance' then 'No change, no issue'
					When [COL Lienholder] = 'BCBS South Carolina' and [SLAM Lienholder] = 'BCBS SC' then 'No change, no issue'
					When [COL Lienholder] = 'Military/IHS' and [SLAM Lienholder] = 'Department of the Army' then 'No change, no issue'
					When [COL Lienholder] like 'Central States%' and [SLAM Lienholder] like 'Central States%' then 'No change, no issue'
					When [COL Lienholder] = 'Washington County - NY Medicaid - TA' and [SLAM Lienholder] = 'Washington County - NY Medicaid - Temporary Assistance' then 'No change, no issue'
					When [COL Lienholder] = 'BCBS AZ' and [SLAM Lienholder] = 'BCBS AZ (PLRP)' then 'No change, no issue'
					When [COL Lienholder] = 'BCBS of Alabama' and [SLAM Lienholder] = 'BCBS AL' then 'No change, no issue'
					When [COL Lienholder] like 'Medical Mutual of Ohio%' and [SLAM Lienholder] like 'Medical Mutual of Ohio%' then 'No change, no issue'
					When [COL Lienholder] = 'Chrysler Group LLC' and [SLAM Lienholder] = 'Chrysler Group, LLC' then 'No change, no issue'
					When [COL Lienholder] = 'BCBS Minnesota' and [SLAM Lienholder] = 'BCBS MN' then 'No change, no issue'
					When [COL Lienholder] like 'Trillium Community Health Plan%' and [SLAM Lienholder] like 'Trillium Community Health Plan%' then 'No change, no issue'
					When [COL Lienholder] = 'IHS - Seneca Nation Lionel R. John Health Center' and [SLAM Lienholder] = 'Indian Health Services - Seneca Nation Lionel R. John Health Center' then 'No change, no issue'
					When [COL Lienholder] like 'Department of Veterans Affairs%' and [SLAM Lienholder] like 'Department of Veterans Affairs%' then 'No change, no issue'
					When [COL Lienholder] = 'Humana Caresource (KY MCO)' and [SLAM Lienholder] = 'Caresource (KY MCO)' then 'No change, no issue'
					When [COL Lienholder] = 'Indian Health Services Pascua Yaqui Health Center' and [SLAM Lienholder] = 'Indian Health Services - Pascua Yaqui Health Center' then 'No change, no issue'
					When [COL Lienholder] like '%WellCare%' and [SLAM Lienholder] like '%WellCare%' then 'No change, no issue'
					When [COL Lienholder] = 'Providence Health Plan' and [SLAM Lienholder] = 'Providence Health Assurance' then 'No change, no issue'
					When [COL Lienholder] = 'IHS - Salina A-Mo Community Clinic' and [SLAM Lienholder] = 'IHS - Salina A-Mo Community Clinic ' then 'No change, no issue'
					When [COL Lienholder] = 'BlueCross BlueShield of Tennessee Plan Members' and [SLAM Lienholder] = 'BCBS TN' then 'No change, no issue'
					When [COL Lienholder] = 'Deseret Mutual' and [SLAM Lienholder] = 'Deseret Healthcare' then 'No change, no issue'
					When [COL Lienholder] = 'Select Health' and [SLAM Lienholder] = 'SelectHealth' then 'No change, no issue'
					When [COL Lienholder] = 'BCBS TX' and [SLAM Lienholder] = 'BCBS TX/HCSC' then 'No change, no issue'
					When [COL Lienholder] = 'Health Care Service Corporation' and [SLAM Lienholder] = 'HCSC' then 'No change, no issue'
					When [COL Lienholder] = 'Community Health Plan of Washington' and [SLAM Lienholder] = 'Community Health Plan (WA MCO)' then 'No change, no issue'
					When [COL Lienholder] like '%Coventry%' and [SLAM Lienholder] like '%Coventry%' then 'No change, no issue'
					When [COL Lienholder] = 'Jackson Care Connect' and [SLAM Lienholder] = 'Jackson Care Connect (OR CCO)' then 'No change, no issue'
					When [COL Lienholder] = 'UnitedHealthcare Services' and [SLAM Lienholder] = 'United Healthcare (PLRP)' then 'No change, no issue'
					When [COL Lienholder] = 'Presbyterian Senior Care HMO' and [SLAM Lienholder] = 'Presbyterian Senior Care (HMO)' then 'No change, no issue'
					When [COL Lienholder] = 'United Health Care (LA MCO)' and [SLAM Lienholder] = 'United Healthcare (LA MCO)' then 'No change, no issue'
					When [COL Lienholder] = 'Bayou Health Plan (LA MCO)' and [SLAM Lienholder] = 'United Healthcare (LA MCO)' then 'No change, no issue'
					When [COL Lienholder] = '%USAF%' and [SLAM Lienholder] = 'Department of the Air Force' then 'No change, no issue'
					When [COL Lienholder] = 'Wellmark' and [SLAM Lienholder] = 'Wellmark Health Plan' then 'No change, no issue'
					When [COL Lienholder] = 'Coordinated Care Corporation (WA MCO)' and [SLAM Lienholder] = 'Coordinated Care Corporation/Centene (WA MCO)' then 'No change, no issue'
					When [COL Lienholder] = 'Unicare Life & Health Insurance Company' and [SLAM Lienholder] = 'Unicare/Anthem Wellpoint' then 'No change, no issue'
					When [COL Lienholder] = 'Transamerica - Monumental Life' and [SLAM Lienholder] = 'Transamerica Medicare Supplement Plan' then 'No change, no issue'
					When [COL Lienholder] = 'BCBS of Illinois' and [SLAM Lienholder] = 'BCBS IL/HCSC' then 'No change, no issue'
					When [COL Lienholder] = 'Selectcare Health Plans' and [SLAM Lienholder] = 'Selectcare Health Plans/WellCare' then 'No change, no issue'
					When [COL Lienholder] = 'Monarch HealthCare' and [SLAM Lienholder] = 'Monarch HealthCare ' then 'No change, no issue'
					When [COL Lienholder] like '%Fidelis%' and [SLAM Lienholder] like '%Fidelis%' then 'No change, no issue'
					When [COL Lienholder] = 'BlueCross BlueShield of Tennessee' and [SLAM Lienholder] = 'BCBS TN' then 'No change, no issue'
					When [COL Lienholder] like '%DADS' and [SLAM Lienholder] = 'Texas Department of Aging and Disability Services' then 'No change, no issue'
					When [COL Lienholder] = 'Harris County Hospital District' and [SLAM Lienholder] = 'Harris County Hospital District ' then 'No change, no issue'
					When [COL Lienholder] = 'McLaren Advantage' and [SLAM Lienholder] = 'McLaren Health Care' then 'No change, no issue'
					When [COL Lienholder] = 'Michigan Medicaid' and [SLAM Lienholder] = 'MI Medicaid' then 'No change, no issue'
					When [COL Lienholder] = 'BCBS of MN' and [SLAM Lienholder] = 'BCBS/Blue Plus MN (MN MCO)' then 'No change, no issue'
					When [COL Lienholder] = 'MN-BCBS' and [SLAM Lienholder] = 'BCBS/Blue Plus MN (MN MCO)' then 'No change, no issue'
					When [COL Lienholder] = 'MN-Ucare' and [SLAM Lienholder] = 'Ucare MN (MN MCO)' then 'No change, no issue'
					When [COL Lienholder] = 'Managed Health Services (IN MCO)' and [SLAM Lienholder] = 'Managed Health Services (IN MCO)/Centene' then 'No change, no issue'
					When [COL Lienholder] = 'HCA Inc. Medical Plan' and [SLAM Lienholder] = 'HCA, Inc. Medical Plan' then 'No change, no issue'
					When [COL Lienholder] = 'BCBS Vermont' and [SLAM Lienholder] = 'BCBS VT' then 'No change, no issue'
					When [COL Lienholder] = 'Beau Rivage Resorts, Inc.' and [SLAM Lienholder] = 'Beau Rivage Resorts' then 'No change, no issue'
					When [COL Lienholder] = 'HealthLink' and [SLAM Lienholder] = 'HealthLink/Anthem Wellpoint' then 'No change, no issue'
					When [COL Lienholder] = 'Tricare - Airforce' and [SLAM Lienholder] = 'Department of the Air Force' then 'No change, no issue'
					When [COL Lienholder] = 'Tricare (Navy)%' and [SLAM Lienholder] = 'Department of the Navy' then 'No change, no issue'
					When ([COL Lienholder] = 'Tricare for Life' or [COL Lienholder] = 'Tricare') and [SLAM Lienholder] = 'Tricare (Main)' then 'No change, no issue'
					When [COL Lienholder] = 'Employers & Operating Engineers Local 520 H&W Fund' and [SLAM Lienholder] = 'Employers & Operating Engineers Local 520 Health & Welfare Trust Fund' then 'No change, no issue'
					When [COL Lienholder] = 'WPS Health Insurance' and [SLAM Lienholder] = 'WPS Health Solutions' then 'No change, no issue'
					When [COL Lienholder] = 'BlueCross BlueShield of TN Plan Members-Mesh' and [SLAM Lienholder] = 'BCBS TN' then 'No change, no issue'
					When [COL Lienholder] = 'Buckeye Health Plan' and [SLAM Lienholder] = 'Buckeye Health Plan/Centene' then 'No change, no issue'
					When [COL Lienholder] like 'Geisinger%' and [SLAM Lienholder] like 'Geisinger%' then 'No change, no issue'
					When [COL Lienholder] like '%Windsor%' and [SLAM Lienholder] like '%Windsor%' then 'No change, no issue'
					When [COL Lienholder] = 'Military/IHS' and [SLAM Lienholder] = 'Military/Indian Health Services' then 'No change, no issue'
					When [COL Lienholder] = 'NY Medicaid - Onondaga' and [SLAM Lienholder] = 'NY Medicaid - Onondaga County' then 'No change, no issue'
					When ([COL Lienholder] like 'Onondaga County - NY Mcaid - T%' or [COL Lienholder] = 'NY Medicaid - Onondaga (TA lien)') and [SLAM Lienholder] like 'Onondaga County - NY Medicaid - T%' then 'No change, no issue'
					When [COL Lienholder] = 'QualChoice of Arkansas' and [SLAM Lienholder] = 'QualChoice of Arkansas, Inc.' then 'No change, no issue'
					When [COL Lienholder] = 'Superior Health Plan' and [SLAM Lienholder] = 'Superior Health Plan/Centene' then 'No change, no issue'
					When [COL Lienholder] = 'Sierra Health and Life Insurance Company' and [SLAM Lienholder] = 'Sierra Health and Life Insurance Company/United Healthcare' then 'No change, no issue'
					When [COL Lienholder] = 'BCBS ND' and [SLAM Lienholder] = 'BCBS ND (Noridian)' then 'No change, no issue'
					When [COL Lienholder] = 'HCA' and [SLAM Lienholder] = 'HCA, Inc. Medical Plan' then 'No change, no issue'
					When [COL Lienholder] = 'Blue Cross of Minnesota Plan Members-Mesh' and [SLAM Lienholder] = 'BCBS MN' then 'No change, no issue'
					When [COL Lienholder] = 'BCBS/Blue Plus MN (MN MCO)' and [SLAM Lienholder] = 'BCBS MN' then 'No change, no issue'
					When [COL Lienholder] = 'IHS - Pascua Yaqui Health Center' and [SLAM Lienholder] = 'Indian Health Services - Pascua Yaqui Health Center' then 'No change, no issue'
					When [COL Lienholder] like '%ChampVA%' and [SLAM Lienholder] like '%ChampVA%' then 'No change, no issue'
					When [COL Lienholder] like '%Molina%' and [SLAM Lienholder] like '%Molina%' then 'No change, no issue'
					When [COL Lienholder] = 'BCBS NM' and [SLAM Lienholder] = 'BCBS NM/HCSC' then 'No change, no issue'
					When [COL Lienholder] = 'MGM Resorts International' and [SLAM Lienholder] = 'MGM Resorts International ' then 'No change, no issue'
					When [COL Lienholder] like '%Affairs Region - 22' and [SLAM Lienholder] = 'Department of Veterans Affairs Region - 22' then 'No change, no issue'
					When [COL Lienholder] = 'Jefferson County - NY Medicaid (TA)' and [SLAM Lienholder] = 'Jefferson County - NY Medicaid - Temporary Assistance' then 'No change, no issue'
					When [COL Lienholder] = 'Veterans Affairs - Louisville Regional Office' and [SLAM Lienholder] = 'Department of Veterans Affairs' then 'No change, no issue'
					When [COL Lienholder] like 'Westchester County - NY Medicaid - T%' and [SLAM Lienholder] like 'Westchester County - NY Medicaid - T%' then 'No change, no issue'
					When [COL Lienholder] = 'Health Partners' and [SLAM Lienholder] = 'HealthPartners' then 'No change, no issue'
					When [COL Lienholder] = 'MCS Advantage Inc.' and [SLAM Lienholder] = 'MCS Advantage Inc./Platino' then 'No change, no issue'
					When [COL Lienholder] = 'Phoenix VA Health Care System' and [SLAM Lienholder] = 'Phoenix VA Healthcare System' then 'No change, no issue'
					When [COL Lienholder] = 'BCBS of Oklahoma' and [SLAM Lienholder] = 'BCBS OK/HCSC' then 'No change, no issue'
					When [COL Lienholder] = 'IHS - Phoenix Indian Medical Center' and [SLAM Lienholder] = 'Indian Health Services' then 'No change, no issue'
					When [COL Lienholder] = 'HealthShare (TriCounty CCO)' and [SLAM Lienholder] = 'HealthShare/TriCounty (OR CCO)' then 'No change, no issue'
					When [COL Lienholder] = 'IHS-Three Rivers Health Center-Cherokee Nation' and [SLAM Lienholder] = 'IHS - Three Rivers Health Center - Cherokee Nation' then 'No change, no issue'
					When [COL Lienholder] = 'Tricare (Coast Guard)' and [SLAM Lienholder] = 'United States Coast Guard' then 'No change, no issue'
					When [COL Lienholder] = 'AllCare (OR MCO)' and [SLAM Lienholder] = 'AllCare Health Plan (OR CCO) ' then 'No change, no issue'
					When [COL Lienholder] = 'Secure Horizons' and [SLAM Lienholder] = 'Secure Horizons/UHC' then 'No change, no issue'
					When [COL Lienholder] = 'Military/Indian Health Services' and [SLAM Lienholder] = 'Indian Health Services' then 'No change, no issue'
					When [COL Lienholder] = 'BCBS Rhode Island' and [SLAM Lienholder] = 'BCBS RI' then 'No change, no issue'
					When [COL Lienholder] = 'Arcadian Health' and [SLAM Lienholder] = 'Arcadia Health Solutions' then 'No change, no issue'
					When [COL Lienholder] = 'Medibank' and [SLAM Lienholder] = 'Medibank ' then 'No change, no issue'
					When [COL Lienholder] like 'Suffolk County - NY Medicaid - T%' and [SLAM Lienholder] like 'Suffolk County - NY Medicaid - T%' then 'No change, no issue'
					When [COL Lienholder] = 'iCare' and [SLAM Lienholder] = 'iCare Health Solutions' then 'No change, no issue'
					When [COL Lienholder] = 'Umpua Health Alliance (OR CCO)' and [SLAM Lienholder] = 'Umpqua Health Alliance (OR CCO)' then 'No change, no issue'
					When [COL Lienholder] = 'Citizens Choice Health Plan' and [SLAM Lienholder] = 'Citizens Choice Health Plan/Alignment Health Plan' then 'No change, no issue'
					When [COL Lienholder] = 'Health Alliance Plan' and [SLAM Lienholder] = 'Health Alliance Plan ' then 'No change, no issue'
					When [COL Lienholder] like '%aetna%' and [SLAM Lienholder] like '%aetna%' then 'No change, no issue'
					When [COL Lienholder] like '%humana%' and [SLAM Lienholder] like '%humana%' then 'No change, no issue'
					When [COL Lienholder] like '%BCBS MN%' and [SLAM Lienholder] like '%BCBS Minnesota%' then 'No change, no issue'
					When [COL Lienholder] like '%BCBS Minnesota%' and [SLAM Lienholder] like '%BCBS MN%' then 'No change, no issue'
					When [COL Lienholder] like '%Tufts%' and [SLAM Lienholder] like '%Tufts%' then 'No change, no issue'
					When [COL Lienholder] = 'Community Health Plan' and [SLAM Lienholder] = 'Community Health Plan (WA MCO)' then 'No change, no issue'
					When [COL Lienholder] like 'Medical Health Insuring Corp%' and [SLAM Lienholder] like 'Medical Health Insuring Corp%' then 'No change, no issue'
					When [COL Lienholder] = 'Lifemasters Supported Healthcare/Staywell' and [SLAM Lienholder] = 'Lifemasters Supported Healthcare/Staywell/Wellcare' then 'No change, no issue'
					When [COL Lienholder] = 'Office Management & ENT Services Employees Group' and [SLAM Lienholder] = 'Office of Management and Enterprise Services Employees Group Insurance Department' then 'No change, no issue'
					When [COL Lienholder] = 'Monroe County - Temporary Assistance' and [SLAM Lienholder] = 'Monroe County - NY Medicaid - Temporary Assistance' then 'No change, no issue'
					When [COL Lienholder] like '%Workers of America%' and [SLAM Lienholder] like 'United Mine Workers of America%' then 'No change, no issue'
					When [COL Lienholder] = 'NY Medicaid - Cattaragus County' and [SLAM Lienholder] = 'NY Medicaid - Cattaraugus County' then 'No change, no issue'
					When [COL Lienholder] like 'Chautauqua County - NY Medicaid - T%' and [SLAM Lienholder] like 'Chautauqua County - NY Medicaid - T%' then 'No change, no issue'
					When [COL Lienholder] like '%army%' and [SLAM Lienholder] like '%army%' then 'No change, no issue'
					When [COL Lienholder] = 'General Motors LLC' and [SLAM Lienholder] like 'General Motors%' then 'No change, no issue'
					When [COL Lienholder] = 'Sunshine State Health Plan/Centene' and [SLAM Lienholder] = 'Sunshine Health/Centene' then 'No change, no issue'
					When ([COL Lienholder] like '%United Healthcare%' and [SLAM Lienholder] like '%United Healthcare%') or ([COL Lienholder] like 'United Healthcare' and [SLAM Lienholder] like '%UHC%') or ([COL Lienholder] like '%UHC%' and [SLAM Lienholder] like '%United Healthcare%') or ([COL Lienholder] like '%UHC%' and [SLAM Lienholder] like '%UHC%') then 'No change, no issue'
					When [COL Lienholder] like '%HealthSpring%' and [SLAM Lienholder] like '%HealthSpring%' then 'No change, no issue'
					When [COL Lienholder] like '%Kaiser%' and [SLAM Lienholder] like '%Kaiser%' then 'No change, no issue'


					When ([SLAM Status] is null or [SLAM Status] = 'Not Entitled') and [COL Id] is null then 'No change, no issue'

					When [SLAM Lienholder] like '%placeholder%' then 'Human Intervention (fix this week) - SLAM Lienholder Name is Placeholder'
					When [COL Lienholder] is null or [COL Lienholder] like '' then 'Human Intervention (fix this week) - COL Lienholder Name is blank'

					When [COL LienType] like 'Attorney' and [COL Question #] > 5 then 'No change, no issue'
					When [COL LienType] like 'Litigation Finance' and [COL Question #] > 5 then 'No change, no issue'
					When [COL LienType] like 'Other' then 'Human Intervention (fix this week) - lientype of other'

					When [COL Status] = 'Pending' and [SLAM OnBenefits] is null and [SLAM LienId] is null then 'Human Intervention (fix this week) - missing Lien Id'

					When [COL Lienholder] <> [SLAM Lienholder] then 'Happy Path - Update Needed' 
					
					When [ThirdPartyId] is null and [SLAM Stage] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - SLAM data not pulling'

					When [COL Status] = 'Not Entitled' and [SLAM Status] = 'Final'  then 'Human Intervention (fix this week) - lien is not entitled in COL but mismatch in SLAM'
					When [SLAM Status] = 'Not Entitled' and ([COL Status] <> 'Not Entitled' or [COL Amount] <> 0) then 'Human Intervention (fix this week) - not entitled in SLAM but COL mismatch'
					When [SLAM Stage] = 'Closed' and [SLAM ClosedReason] like 'Resolved - No Entitlement' and ([COL Status] <> 'Not Entitled' or [COL Amount] <> 0) then 'Human Intervention (fix this week) - not entitled in SLAM but COL mismatch'
					When [SLAM Stage] = 'Closed' and [SLAM ClosedReason] like 'Opened in Error' and ([COL Status] <> 'Not Entitled' or [COL Amount] <> 0) then 'Human Intervention (fix this week) - not entitled in SLAM but COL mismatch'
					When [SLAM Stage] = 'Closed' and [SLAM ClosedReason] like 'Per Att%' and ([COL Status] <> 'Not Entitled' or [COL Amount] <> 0) then 'Human Intervention (fix this week) - not entitled in SLAM but COL mismatch'
					When [SLAM Stage] = 'Final No Entitlement' and [SLAM ClosedReason] like 'Per Att%' and ([COL Status] <> 'Not Entitled' or [COL Amount] <> 0) then 'Human Intervention (fix this week) - not entitled in SLAM but COL mismatch'

					Else 'Look Into'
					End as [Lienholder_Check],


		--Liens Not Pulling
			Case
				When [COL Lienholder] is null and [COL LienType] is null and [COL Question #] is null and [COL Status] is null and [COL Amount] is null then 'Human Intervention (fix this week) - delete empty lien from COL'
				When [COL LienId] is null and [Claim Ref #] is not null and [COL LienType] is not null then 'Human Intervention (fix this week) - LienId is NULL in COL'
				When [COL LienId] is null and [COL LienType] is not null and [SLAM LienId] is null then 'Human Intervention (fix this week) - LienId is NULL in COL'

				When [SLAM LienId] is not null and [SLAM OnBenefits] is null and [COL Status] = 'Pending' then 'Not Eligible'
				When [SLAM Status] = 'Pending' and [COL Status] = 'Pending' then 'Not Eligible'
				When [SLAM Stage] <> 'Closed' and [SLAM Stage] not like 'final%' and [COL Status] = 'Pending' then 'Not Eligible'
				When [SLAM Stage] is null and [SLAM OnBenefits] is null and [COL LienId] is null and [SLAM Status] is null then 'Human Intervention (fix this week) - Lien Id needs update'
				
				When [SLAM Status] is null or [SLAM Status] = 'Not Entitled' then 'No change, no issue'
				When [ThirdPartyId] is Null then 'Human Intervention (fix this week) - Lien not pulling in SLAM data'
				When [COL LienType] like 'Attorney' and [COL Question #] > 5 then 'No change, no issue'
				When [COL LienType] like 'Litigation Finance' and [COL Question #] > 5 then 'No change, no issue'
				When [COL LienType] like 'Other' then 'Human Intervention (fix this week) - lientype of other'

				Else 'No change, no issue'
				End as [InSLAM_Check],

						

			--Update Misc. Fields
				[COL LienType] as LienType_Updated,
				[COL LienId] as LienId_Updated,
				[COL Question #] as QuestionNumber_Updated,
				[COL Lienholder] as LienholderName_Updated, 
				[COL Description] as Description_Updated,
				[Imposed on] as ImposedOn_Updated, 
				[Lien doclink] as LienDoclink_Updated, 
				[Max inbound amount] as MaxInboundAmount_Updated, 
				[Max protocol amount] as MaxProtocolAmount_Updated, 
				[Other lien type] as OtherLienType_Updated


				


		From 
			(

				SELECT 
					--COL Data: CMS Tab
							CAST(CMS.[Claim Ref #] as nvarchar) as 'Claim Ref #', CMS.[Lien Id] as 'COL LienId', CMS.[Lien type] as 'COL LienType', CMS.[Question number] as 'COL Question #',CMS.[Status] as 'COL Status', 
							dbo.fixnumerictext(CMS.[Amount]) as 'COL Amount', CMS.[Lien holder] as 'COL Lienholder', CMS.Id as 'COL Id', 
							CMS.Description as 'COL Description', CMS.[Imposed on], CMS.[Lien doclink], CMS.[Max inbound amount], CMS.[Max protocol amount], CMS.[Other lien type],
	
					--COL Data: LF Tab
							LF.[Claim number] as 'COL Claim number',SE.[Firm Name] as 'COL CaseName',

					--SLAM Lien Level Data
							Liens.ClientId, Liens.CaseName as 'CaseName', FPV.CaseName as 'Case Name', FPV.[ThirdPartyId] as 'ThirdPartyId', cast(Liens.[LienId] as char) as 'SLAM LienId', Liens.[COL_LienType] as 'SLAM LienType', Liens.[Question] as 'SLAM Question #', 
							Liens.[Status] as 'SLAM Status', 
							Case
								When len(FPV.[LienHolderName]) > 49 then left(FPV.LienHolderName, 49)
								Else FPV.LienHolderName
								End As 'SLAM Lienholder',

							FPV.FinalDemandAmount as 'SLAM FD Amount', FPV.FinalGlobalAmount as 'SLAM Global Amount', Liens.[True Final Demand] as 'SLAM True FD Amount',


							FPV.[SLAM_LienType], FPV.COL_LienType as 'SLAM LienType (converted)', FPV.Stage as 'SLAM Stage', FPV.ClosedReason as 'SLAM ClosedReason', FPV.OnBenefits as 'SLAM OnBenefits',

					--#Problems
							Prob.Issue as 'Prob_Issue', Prob.[COL Update Notes] as 'Prob_Notes',

					--BUDNSFW
							BUDNSFW_Client.[Issue Detail] as BUDNSFW_ClientIssue_CMS, BUDNSFW_Lien.[Issue Detail] as BUDNSFW_LienIssue,

					--CSR
							CSR.[Resolved Escrow Balance] as 'Current_Escrow',
							Case
								When CSR.[Resolved Escrow Balance] is null then 100
								Else CSR.[Resolved Escrow Balance]/CSR.[Total Claimant Settlement Amount]
								End as 'Percent Escrow Remaining',
							Case
								When CSR.[Claim #] is null then 'Not Eligible - Not on CSR'
								Else 'Good'
								End As 'Claimant on CSR?',

					--SLAM Client Level Data
							Clients.Final as 'SLAM Final', Clients.[Truly Final?] as 'Client Truly Final', Clients.CaseId as 'SLAM CaseId', Clients.QuestionnaireReceived as 'SLAM Quest'
													

				FROM		CMS_Updated as CMS -- update weekly
							LEFT OUTER JOIN JB_GetClientOnBenefitSummary_JAM as Liens ON CMS.[Lien Id] = Liens.[LienId] -- view
							LEFT OUTER JOIN JB_BulkEdit_LF as LF ON CMS.[Claim Ref #] = LF.[Claim Ref #] -- update weekly
							LEFT OUTER JOIN JB_COLSearchExtract as SE on CMS.[Claim Number] = SE.[Claim Number] -- update weekly
							LEFT OUTER JOIN JB_GetClientOnBenefitSummary_FPV as FPV ON CMS.[Lien Id] = FPV.[LienId] -- view
							LEFT OUTER JOIN JB_AMSProblems_Summary as Prob ON LF.[Claim number] = Prob.[Claim #] --update as needed
							LEFT OUTER JOIN JB_CSR_AMS as CSR ON LF.[Claim number] = CSR.[Claim #] -- update weekly
							LEFT OUTER JOIN JB_GetClientSummary as Clients ON LF.[Claim number] = Clients.[ThirdPartyId] -- view
							LEFT OUTER JOIN JB_BUDNSFW_Client as BUDNSFW_Client ON LF.[Claim number] = BUDNSFW_Client.[Claim number] -- update as needed
							LEFT OUTER JOIN JB_BUDNSFW_Lien as BUDNSFW_Lien ON CMS.[Lien Id] = BUDNSFW_Lien.[Lien Id] -- update as needed

			 ) as sub			
	) as sub2
""",
    con = engine
    )
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
