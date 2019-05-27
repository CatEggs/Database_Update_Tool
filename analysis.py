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
    print(sql_connect)
    engine = create_engine(sql_connect)

    # import S3Reporting MetaData
    metadata = MetaData(bind=engine)

    lf_df = pd.read_sql(
    """
    Select sub2.*, 
        Case
            When [Final (SLAM Summary)] = 'No' and [SLAM Client Funded] = 'Yes' then 'Human Intervention (fix when you can)'
            When [SA Matches?] like 'Human Intervention (high%' then 'Human Intervention (CM)'
            When [SSN Research] like 'Human intervention (high%' then 'Human Intervention (CM)'

            When [Rules for Q2, Q4, Questionnaire, Release] like 'Not Eligible%' then 'Not Eligible'
            When [Claimant on CSR?] like 'Not Eligible%' then 'Not Eligible'
            When [Misc. Issues] like 'Not Eligible%' then 'Not Eligible'
            When [Should we update?] like 'Not Eligible%' then 'Not Eligible'
            When [Claimant in SLAM correctly?] like 'Not Eligible%' then 'Not Eligible'
            When [SA Matches?] like 'Not Eligible%' then 'Not Eligible'
            When [Escrow Analysis] like 'Not Eligible%' then 'Not Eligible'
            When [Update HB?] like 'Not Eligible%' then 'Not Eligible'

            
            When [Escrow Analysis] like 'Human Intervention (high%' then 'Human Intervention (fix this week)'
            When [Update Questions?] like 'Human Intervention (high%' then 'Human Intervention (fix this week)'
            When [Update HB?] like 'Look Into' then 'Human Intervention (fix this week)'
            When [Claimant in SLAM correctly?] like 'Human Intervention (high%' then 'Human Intervention (fix this week)'
            When [Updated SLAM Final] like 'Human Intervention (high%' then 'Human Intervention (fix this week)'
            When [Rules for Q2, Q4, Questionnaire, Release] like 'Human Intervention (high%' then 'Human Intervention (fix this week)'
            When [Updated Mcare] like 'Human Intervention (high%' then 'Human Intervention (fix this week)'
            When [Updated Non PLRP] like 'Human Intervention (high%' then 'Human Intervention (fix this week)'
            When [Updated Mcaid] like 'Human Intervention (high%' then 'Human Intervention (fix this week)'
            When [Updated Third Party] like 'Human Intervention (high%' then 'Human Intervention (fix this week)'
            When [Updated PLRP] like 'Human Intervention (high%' then 'Human Intervention (fix this week)'
            When [Should we update?] like 'Human Intervention (high%' then 'Human Intervention (fix this week)'
            When [Updated SLAM Final] like 'Human intervention (high%' then 'Human Intervention (fix this week)'


            When [Updated SLAM Final] like 'Human Intervention (medium%' then 'Human Intervention (fix this week if time)'
            When [Should we update?] like 'Human Intervention (medium%' then 'Human Intervention (fix this week if time)' 
            

            When [Updated SLAM Final] like 'Human Intervention (low%' then 'Human Intervention (fix when you can)'
            When [Should we update?] like 'Human Intervention (low%' then 'Human Intervention (fix when you can)'
            When [Escrow Analysis] like 'Human Intervention (low%' then 'Human Intervention (fix when you can)'
            When [Update Questions?] like 'Human Intervention (low%' then 'Human Intervention (fix when you can)'


            When [Escrow Analysis] like 'Human Intervention - Close in SLAM' then 'Human Intervention - Close in SLAM'


            When [Update HB?] like 'Happy Path' then 'Happy Path'
            When [Escrow Analysis] like 'Happy Path%' then 'Happy Path'
            --logic for happy path
            --When [Claimant in SLAM correctly?] = 'Good' and [Claimant on CSR?] = 'Good' and [Escrow Analysis] = 'Good' and [Misc. Issues] = 'Good' and [SA matches?] = 'Good' 
                --	and [SSN Research] not like 'human intervention%' and [Rules for Q2, Q4, Questionnaire, Release] like 'normal%' and [Should we update?] like 'ok%' then 'Happy Path'
            
            When [Updated Mcare] like 'No Changes%' then 'No Changes, No Issues'
            When [Updated Non PLRP] like 'No Changes%' then 'No Changes, No Issues'
            When [Updated Mcaid] like 'No Changes%' then 'No Changes, No Issues'
            When [Updated Third Party] like 'No Changes%' then 'No Changes, No Issues'
            When [Updated PLRP] like 'No Changes%' then 'No Changes, No Issues'
            When [Update Questions?] like 'No Changes%' then 'No Changes, No Issues'
            When [Update HB?] like 'No Changes%' then 'No Changes, No Issues'
            When [Escrow Analysis] like 'No Changes%' then 'No Changes, No Issues'
            --When [Claimant in SLAM correctly?] = 'Good' and [Claimant on CSR?] = 'Good' and [Escrow Analysis] = 'Resolved' and [Misc. Issues] = 'Good' and [SA matches?] = 'Good' 
                --	and [SSN Research] not like 'human intervention%' and [Rules for Q2, Q4, Questionnaire, Release] like 'normal%' and [Should we update?] like 'ok%' 
                --	and [Update Questions?] like 'Final%' and [Update HB?] like 'No changes%' then 'No Changes, No Issues'		
            

            Else 'Look Into'
            
            End As 'Initial_LF_Label',
            Case
            When [Final (SLAM Summary)] = 'No' and [SLAM Client Funded] = 'Yes' then 'Human Intervention (fix when you can)'
            When [SA Matches?] like 'Human Intervention (high%' then 'Human Intervention (CM)'
            When [SSN Research] like 'Human intervention (high%' then 'Human Intervention (CM)'

            When [Rules for Q2, Q4, Questionnaire, Release] like 'Not Eligible%' then 'Not Eligible'
            When [Claimant on CSR?] like 'Not Eligible%' then 'Not Eligible'
            When [Misc. Issues] like 'Not Eligible%' then 'Not Eligible'
            When [Should we update?] like 'Not Eligible%' then 'Not Eligible'
            When [Claimant in SLAM correctly?] like 'Not Eligible%' then 'Not Eligible'
            When [SA Matches?] like 'Not Eligible%' then 'Not Eligible'
            When [Escrow Analysis] like 'Not Eligible%' then 'Not Eligible'
            When [Update HB?] like 'Not Eligible%' then 'Not Eligible'

            
            When [Escrow Analysis] like 'Human Intervention (high%' then 'Human Intervention (fix this week)'
            When [Update Questions?] like 'Human Intervention (high%' then 'Human Intervention (fix this week)'
            When [Update HB?] like 'Look Into' then 'Human Intervention (fix this week)'
            When [Claimant in SLAM correctly?] like 'Human Intervention (high%' then 'Human Intervention (fix this week)'
            When [Updated SLAM Final] like 'Human Intervention (high%' then 'Human Intervention (fix this week)'
            When [Rules for Q2, Q4, Questionnaire, Release] like 'Human Intervention (high%' then 'Human Intervention (fix this week)'
            When [Updated Mcare] like 'Human Intervention (high%' then 'Human Intervention (fix this week)'
            When [Updated Non PLRP] like 'Human Intervention (high%' then 'Human Intervention (fix this week)'
            When [Updated Mcaid] like 'Human Intervention (high%' then 'Human Intervention (fix this week)'
            When [Updated Third Party] like 'Human Intervention (high%' then 'Human Intervention (fix this week)'
            When [Updated PLRP] like 'Human Intervention (high%' then 'Human Intervention (fix this week)'
            When [Should we update?] like 'Human Intervention (high%' then 'Human Intervention (fix this week)'
            When [Updated SLAM Final] like 'Human intervention (high%' then 'Human Intervention (fix this week)'


            When [Updated SLAM Final] like 'Human Intervention (medium%' then 'Human Intervention (fix this week if time)'
            When [Should we update?] like 'Human Intervention (medium%' then 'Human Intervention (fix this week if time)' 
            

            When [Updated SLAM Final] like 'Human Intervention (low%' then 'Human Intervention (fix when you can)'
            When [Should we update?] like 'Human Intervention (low%' then 'Human Intervention (fix when you can)'
            When [Escrow Analysis] like 'Human Intervention (low%' then 'Human Intervention (fix when you can)'
            When [Update Questions?] like 'Human Intervention (low%' then 'Human Intervention (fix when you can)'


            When [Escrow Analysis] like 'Human Intervention - Close in SLAM' then 'Human Intervention - Close in SLAM'


            When [Update HB?] like 'Happy Path' then 'Happy Path'
            When [Escrow Analysis] like 'Happy Path%' then 'Happy Path'
            --logic for happy path
            --When [Claimant in SLAM correctly?] = 'Good' and [Claimant on CSR?] = 'Good' and [Escrow Analysis] = 'Good' and [Misc. Issues] = 'Good' and [SA matches?] = 'Good' 
                --	and [SSN Research] not like 'human intervention%' and [Rules for Q2, Q4, Questionnaire, Release] like 'normal%' and [Should we update?] like 'ok%' then 'Happy Path'
            
            When [Updated Mcare] like 'No Changes%' then 'No Changes, No Issues'
            When [Updated Non PLRP] like 'No Changes%' then 'No Changes, No Issues'
            When [Updated Mcaid] like 'No Changes%' then 'No Changes, No Issues'
            When [Updated Third Party] like 'No Changes%' then 'No Changes, No Issues'
            When [Updated PLRP] like 'No Changes%' then 'No Changes, No Issues'
            When [Update Questions?] like 'No Changes%' then 'No Changes, No Issues'
            When [Update HB?] like 'No Changes%' then 'No Changes, No Issues'
            When [Escrow Analysis] like 'No Changes%' then 'No Changes, No Issues'
            --When [Claimant in SLAM correctly?] = 'Good' and [Claimant on CSR?] = 'Good' and [Escrow Analysis] = 'Resolved' and [Misc. Issues] = 'Good' and [SA matches?] = 'Good' 
                --	and [SSN Research] not like 'human intervention%' and [Rules for Q2, Q4, Questionnaire, Release] like 'normal%' and [Should we update?] like 'ok%' 
                --	and [Update Questions?] like 'Final%' and [Update HB?] like 'No changes%' then 'No Changes, No Issues'		
            

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
                    When [SLAM ThirdPartyId] is null then 'Human Intervention (high) - Claimant data not pulling'
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
                    When [SLAM ThirdPartyId] is null then 'Human Intervention (high) - Claimant data not pulling from SLAM'
                    When [SLAM CaseName] like '%EIF%' then 'Not Eligible - EIF'

                    When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]<>[COL HB] and [SLAM Client Funded] = 'No' and [Current Escrow]/[COL SA] > .19 and [SLAM HB]>[Current Escrow] then 'Human Intervention (high) - sum of liens is greater than escrow'
                    When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]=[COL HB] and [COL HB]=[Current Escrow] and [SLAM Client Funded] = 'No' then 'Human Intervention - Close in SLAM'
                    When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]=[COL HB] and [COL HB]<>[Current Escrow] and [SLAM Client Funded] = 'No' then 'Human Intervention (high) - possibly needs update ("Check COL")'

                    When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]=[COL HB] and [COL HB]<>[Current Escrow] and [SLAM Client Funded] = 'No' and [Current Escrow]/[COL SA] < .19 then 'Human Intervention (low) - May need update but not enough escrow'
                    When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]<>[COL HB] and [SLAM Client Funded] = 'No' and [Current Escrow]/[COL SA] < .19 then 'Human Intervention (low) - HB mismatch and not enough escrow'
                    When [Final (SLAM Summary)] = 'Yes' and [COL HB]<>[Current Escrow] and [SLAM Client Funded] = 'Yes' and [current escrow] <> 0 then 'Human Intervention (low) - resolved but escrow mismatch'
                    When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]<>[COL HB] and [SLAM Client Funded] = 'Yes' then 'Human Intervention (low) - resolved but HB mismatch'
                    When [Final (SLAM Summary)] <> 'Yes' and [SLAM Client Funded] = 'Yes' then 'Human Intervention (low) - resolved but not final'
                    When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]<>[COL HB] and [SLAM Client Funded] = 'Yes' and [current escrow] <> 0 then 'Human Intervention (low) - resolved but escrow/HB mismatch'
                    When [Final (SLAM Summary)] = 'Yes' and [Current Escrow]<>[COL HB] and [SLAM Client Funded] = 'Yes' and [current escrow] <> 0 then 'Human Intervention (low) - resolved but escrow/HB mismatch'

                    When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]<>[COL HB] and [SLAM Client Funded] = 'No' and [Current Escrow]/[COL SA] > .19 and [SLAM HB]<=[Current Escrow] then 'Happy Path - update needed'
                    
                    When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]=[COL HB] and [COL HB]=[Current Escrow] and [SLAM Client Funded] = 'Yes' then 'No Changes, No Issues - Resolved'
                    When [Final (SLAM Summary)] = 'Yes' and [SLAM HB]=[COL HB] and [Current Escrow] = 0 and [SLAM Client Funded] = 'Yes' then 'No Changes, No Issues - Resolved'
                    
                    Else 'Look Into'
                    End As 'Escrow Analysis',


            --Problems
                [#Problems], [Bad List Note], [#Prob Notes],
                Case
                    When [COL Case Name] like '%comeback' then 'Not Eligible - EIF'
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
                    When [Truly Final/FinalizedStatusId Issue?] = 'Issue' then 'Human Intervention (medium) - Scope issue'
                    When [SLAM CaseId] IN (862) and [Final (SLAM Summary)] = 'Yes' and [SLAM PreExisting Injuries] not like '%Completed by%' then 'Human Intervention (high) - No (GRG)'
                    When [SLAM CaseId] IN (862) and [SLAM Finalized Status Id] = 2 and [SLAM PreExisting Injuries] not like '%Completed by%' then 'Human Intervention (high) - No (GRG)'
                    When [SLAM CaseId] IN (862) and [SLAM Finalized Status Id] = 3 and [SLAM PreExisting Injuries] not like '%Completed by%' then 'Human Intervention (high) - No (GRG)'
                    When [SLAM CaseId] IN (862) and [Final (SLAM Summary)] = 'Yes' and [SLAM PreExisting Injuries] is null then 'Human Intervention (high) - No (GRG)'
                    When [SLAM CaseId] IN (862) and [SLAM Finalized Status Id] = 2 and [SLAM PreExisting Injuries] is null then 'Human Intervention (high) - No (GRG)'
                    When [SLAM CaseId] IN (862) and [SLAM Finalized Status Id] = 3 and [SLAM PreExisting Injuries] is null then 'Human Intervention (high) - No (GRG)'
                    When [Truly Final/FinalizedStatusId Issue?] = 'Issue' then 'Human Intervention (medium) - Finalized Status Id Issue'
                    When [SLAM Client Funded] = 'Yes' and [Final (SLAM Summary)] = 'No' then 'Human Intervention (low) - Resolved but not final'
                    When [SLAM Client Funded] = 'Yes' and [Final (SLAM Summary)] = 'Yes' then 'Resolved'
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

                    --When [SLAM CaseId] IN (2495, 1326, 1312, 2837, 2187, 2244, 402, 489, 2050, 1166, 653) and ([COL Q4] <> 'No Answer' or [COL HB] < .34) THEN 'Human Intervention (high) - Q4 should be No Answer'
                    --When [SLAM CaseId] IN (1910, 470) and ([COL Q4] <> 'No Answer' or [COL HB] < .34) then 'Human Intervention (high) - Q4 should be No Answer (spreadsheet)'
                    When [SLAM CaseId] IN (2284, 2450) and [SLAM Quest Recd] <> 1 and ([COL Q4] <> 'No Answer' or [COL HB] < .34) then 'Human Intervention (high) - Q4 should No Answer - Quest Recd not true'
                    When [SLAM CaseId] = 2184 and [SLAM Quest Recd] <> 1 and ([COL Q4] <> 'No Answer' or [COL Non PLRP] <> 'No Answer' or [COL HB] <> .4) then 'Human Intervention (high) - Q2 and Q4 should be No Answer - Quest Recd not true'
                    When [SLAM CaseId] IN (483, 862) and [Release Returned?] = 'Within 3 weeks' and ([COL Q4] <> 'No Answer' or [COL HB] < .34) then 'Human Intervention (high) - Q4 should be no answer - BA within 3 weeks'
                    When [SLAM CaseId] IN (483, 862) and [Release Returned?] = 'No release' and ([COL Q4] <> 'No Answer' or [COL HB] < .34) then 'Human Intervention (high) - Q4 should be no answer - BA no release'
                    When [SLAM CaseId] IN (483, 862) and [Release Returned?] = 'Look Into' then 'Human Intervention (high) - Release Date Issue'
                    
                    Else 'Normal Update Process'
                    
                    End as 'Rules for Q2, Q4, Questionnaire, Release',


            --Should we update?
                Case
                    When [SLAM Finalized Status Id] = 1 or [SLAM Finalized Status Id] is null then 'Not Eligible - pending'
                    When [Final (SLAM Summary)] ='No' then 'Not Eligible - pending'
                    
                    When [Truly Final/FinalizedStatusId Issue?] = 'Issue' then 'Human Intervention (medium) - Finalized Status Id Issue'
                    
                    When [SLAM Client Funded] = 'Yes' and [Claim Status] = 'Post Payment Lien Deficient' then 'Human Intervention (low) - resolved but post payment lien deficient'
                    
                    Else 'Ok to Update'
                    End As 'Should we update?',


    -- Bulk Edit
            --Questions Analysis
                [COL Mcare], [COL Non PLRP], [COL Mcaid], [COL Third Party], [COL PLRP], 
                [SLAM Mcare], [SLAM Non PLRP], [SLAM Mcaid], [SLAM Third Party], [SLAM PLRP],
                
                Case
                    When [Final (SLAM Summary)] = 'Yes' and [COL Mcare]=[SLAM Mcare] and [COL Non PLRP]=[SLAM Non PLRP] and [COL Mcaid]=[SLAM Mcaid] and [COL Third Party]=[SLAM Third Party] and [COL PLRP]=[SLAM PLRP] then 'No changes, no issues (final)'
                    WHen [SLAM Client Funded] = 'Yes' and ([COL Mcare]<>[SLAM Mcare] or [COL Non PLRP]<>[SLAM Non PLRP] or [COL Mcaid]<>[SLAM Mcaid] or [COL Third Party]<>[SLAM Third Party] or [COL PLRP]<>[SLAM PLRP]) and [SLAM HB]=[COL HB] then 'No changes, no issues (resolved, Q Mismatch, but HB is good)'
                    When [SLAM Client Funded] = 'Yes' and ([COL Mcare]<>[SLAM Mcare] or [COL Non PLRP]<>[SLAM Non PLRP] or [COL Mcaid]<>[SLAM Mcaid] or [COL Third Party]<>[SLAM Third Party] or [COL PLRP]<>[SLAM PLRP]) then 'Human Intervention (low) - Resolved but question changes'
                    Else 'Questions need update'
                    End as 'Update Questions?',

                Case
                    When [SLAM Client Funded] = 'Yes' and [SLAM HB]=[COL HB] and [COL Mcare] <> [SLAM Mcare] then 'No changes, no issues (Q Mismatch, but resolved and HB is good)'
                    When [COL Mcare] = 'Yes' and [SLAM Mcare] <> 'Yes' then 'Human Intervention (high) - Yes in COL but not in SLAM'
                    Else [SLAM Mcare]
                    End As 'Updated Mcare',
                Case
                    When [SLAM Client Funded] = 'Yes' and [SLAM HB]=[COL HB] and [COL Non PLRP] <> [SLAM Non PLRP] then 'No changes, no issues (Q Mismatch, but resolved and HB is good)'
                    When [COL Non PLRP] = 'Yes' and [SLAM Non PLRP] <> 'Yes' then 'Human Intervention (high) - Yes in COL but not in SLAM'
                    Else [SLAM Non PLRP]
                    End As 'Updated Non PLRP',
                Case
                    When [SLAM Client Funded] = 'Yes' and [SLAM HB]=[COL HB] and [COL Mcaid] <> [SLAM Mcaid] then 'No changes, no issues (Q Mismatch, but resolved and HB is good)'
                    When [COL Mcaid] = 'Yes' and [SLAM Mcaid] <> 'Yes' then 'Human Intervention (high) - Yes in COL but not in SLAM'
                    Else [SLAM Mcaid]
                    End As 'Updated Mcaid',
                Case
                    When [SLAM Client Funded] = 'Yes' and [SLAM HB]=[COL HB] and [COL Third Party] <> [SLAM Third Party] then 'No changes, no issues (Q Mismatch, but resolved and HB is good)'
                    When [COL Third Party] = 'Yes' and [SLAM Third Party] <> 'Yes' then 'Human Intervention (high) - Yes in COL but not in SLAM'
                    Else [SLAM Third Party]
                    End As 'Updated Third Party',
                Case
                    When [SLAM Client Funded] = 'Yes' and [SLAM HB]=[COL HB] and [COL PLRP] <> [SLAM PLRP] then 'No changes, no issues (Q Mismatch, but resolved and HB is good)'
                    When [COL PLRP] = 'Yes' and [SLAM PLRP] <> 'Yes' then 'Human Intervention (high) - Yes in COL but not in SLAM'
                    Else [SLAM PLRP]
                    End As 'Updated PLRP',


            --Updated Holdback
                [COL HB], [SLAM HB],
                Case
                    When [COL HB] = [SLAM HB] then 'No Changes in HB'
                    When [COL HB] <> [SLAM HB] and [Final (SLAM Summary)] = 'Yes' then 'Happy Path'
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
			When [LienType_Check] = 'DNE' then 'Not Eligible'
			When [ThirdPartyId_Match?] = 'Good' and ([Null_Liens] = 'Add Lien') then 'Add Lien'
			When [ThirdPartyId_Match?] = 'Good' and ([InSLAM_Check] = 'Good') and ([Lienholder_Check] = 'Good' or [Lienholder_Check] = 'No Changes, No Issues' ) and ([Null_Liens] = 'Good') and ([LienId_Check] = 'Good') and  ([LienType_Check] =  'Good' or [LienType_Check] =  'DNE') and  ([Status_Check] = 'Good') and ([Amount_Check] =  'Good') then 'No Changes, No Issues'
			When [ThirdPartyId_Match?] = 'Look Into' or([InSLAM_Check] = 'Look Into') or ([Lienholder_Check] = 'Look Into' ) or ([Null_Liens] = 'Look Into') or ([LienId_Check] = 'Look Into') or  ([LienType_Check] =  'Look Into') or  ([Status_Check] = 'Look Into') or ([Amount_Check] =  'Look Into') or ([Lienholder_Check] = 'Look Into' ) then 'Human Intervention (fix this week)'
			When [ThirdPartyId_Match?] = 'Check Query' or([InSLAM_Check] = 'Check Query') or ([Lienholder_Check] = 'Check Query' ) or ([Null_Liens] = 'Check Query') or ([LienId_Check] = 'Check Query') or  ([LienType_Check] =  'Check Query') or  ([Status_Check] = 'Check Query') or ([Amount_Check] =  'Check Query') or ([Lienholder_Check] = 'Check Query' ) then 'Look Into'
			Else 'Happy Path'
				--Case
				--	When [Lienholder_Check] = 'No Changes, No Issues' then 'No Changes, No Issues'
				--	Else 'Happy Path'
				--End
			End as [Initial_CMS_Label],
			Case
			When [LienType_Check] = 'DNE' then 'Not Eligible'
			When [ThirdPartyId_Match?] = 'Good' and ([Null_Liens] = 'Add Lien') then 'Add Lien'
			When [ThirdPartyId_Match?] = 'Good' and ([InSLAM_Check] = 'Good') and ([Lienholder_Check] = 'Good' or [Lienholder_Check] = 'No Changes, No Issues' ) and ([Null_Liens] = 'Good') and ([LienId_Check] = 'Good') and  ([LienType_Check] =  'Good' or [LienType_Check] =  'DNE') and  ([Status_Check] = 'Good') and ([Amount_Check] =  'Good') then 'No Changes, No Issues'
			When [ThirdPartyId_Match?] = 'Look Into' or([InSLAM_Check] = 'Look Into') or ([Lienholder_Check] = 'Look Into' ) or ([Null_Liens] = 'Look Into') or ([LienId_Check] = 'Look Into') or  ([LienType_Check] =  'Look Into') or  ([Status_Check] = 'Look Into') or ([Amount_Check] =  'Look Into') or ([Lienholder_Check] = 'Look Into' ) then 'Human Intervention (fix this week)'
			When [ThirdPartyId_Match?] = 'Check Query' or([InSLAM_Check] = 'Check Query') or ([Lienholder_Check] = 'Check Query' ) or ([Null_Liens] = 'Check Query') or ([LienId_Check] = 'Check Query') or  ([LienType_Check] =  'Check Query') or  ([Status_Check] = 'Check Query') or ([Amount_Check] =  'Check Query') or ([Lienholder_Check] = 'Check Query' ) then 'Look Into'
			Else 'Happy Path'
				--Case
				--	When [Lienholder_Check] = 'No Changes, No Issues' then 'No Changes, No Issues'
				--	Else 'Happy Path'
				--End
			End as [CMS_Label]

From (
		Select	sub.*,
			
---Duplicate Lien Check.
			


				Case
					When [COL Claim number] <> [ThirdPartyId] then 'Look Into'
					When [COL Claim number] = [ThirdPartyId] then 'Good'
					Else 'Check Query'
					End as [ThirdPartyId_Match?],

			--Check for Null liens

				Case
					When [COL Id] is Null and ([COL LienId] = [SLAM LienId]) and ([COL Claim number] = [ThirdPartyId]) and [SLAM Status] = 'Final' and len([COL Lienholder]) <= 50 then 'Add Lien'
					When [COL Id] is Null and ([COL LienId] = [SLAM LienId]) and ([COL Claim number] = [ThirdPartyId]) and [SLAM Status] = 'Final' and len([COL Lienholder]) > 50 then 'Look Into' 
					When [COL Lienholder] is null and [COL LienType] is null and [COL Question #] is null and [COL Status] is null and [COL Amount] is null then 'Look Into'
					When [SLAM Lienholder] is null and [SLAM LienType] is null and [SLAM Question #] is null and [SLAM Status] is null and [SLAM Amount] is null then 'Look Into'
					Else 'Good'
					End as [Null_Liens],

			--Check Status
				Case
					When [COL Status] = 'Payment Confirmed' then 'No Changes, No Issues' 
					When [COL Status] = 'Final' and [SLAM Status] = 'Pending' and ([COL LienId] = [SLAM LienId])  then 'Look Into'
					When [COL Status] = 'Not Entitled' and [SLAM Status] = 'Final' and ([COL LienId] = [SLAM LienId]) and ([COL Claim number] = [ThirdPartyId])  then 'Update'
					When [COL Status] = 'Pending' and [SLAM Status] = 'Final' and ([COL LienId] = [SLAM LienId]) and ([COL Claim number] = [ThirdPartyId])  then 'Update'
					When [COL Status] is null and [SLAM Status] = 'Final' and ([COL LienId] = [SLAM LienId]) and ([COL Claim number] = [ThirdPartyId])  then 'Update'
					When [COL Status] = 'Pending' and [SLAM Status] = 'Pending' and ([COL LienId] = [SLAM LienId]) and ([COL Claim number] = [ThirdPartyId])  then 'Good'
					When [COL Status] = 'Final' and [SLAM Status] = 'Final' and ([COL LienId] = [SLAM LienId]) and ([COL Claim number] = [ThirdPartyId])  then 'Good'
					Else 'Check Query'
					End as [Status_Check],


			--Check the lien type
				Case 
					When [COL LienType] like 'Attorney' then 'DNE'
					When [COL LienType] like 'Litigation Finance' then 'DNE'
					When [COL LienType] like 'Other' then 'Look Into'
					When [COL LienType] is null and ([SLAM LienType] is not null) and ([COL LienId] = [SLAM LienId]) then 'Update'
					When [COL LienType]<>[SLAM LienType] and ([COL LienId] = [SLAM LienId]) then 'Update'
					When [COL LienType] = [SLAM LienType] and ([COL LienId] = [SLAM LienId]) then 'Good'
					Else 'Check Query'
					End as [LienType_Check],

			--Check LienId

				Case 
					When [COL LienId] is Null and ([COL LienType] like 'Attorney' or  [COL LienType] like 'Other') then 'Good'
					When [COL LienId] is Null and [COL Question #] <= 5 and [SLAM Status] = 'Pending'  then 'No Changes, No Issues'
					When [COL LienId] is Null and [COL Question #] <= 5 and [SLAM Status] = 'Final'  then 'Update'
					When [COL LienId]<>[SLAM LienId] or [COL LienId] is Null then 'Update'
					When [COL LienId] = [SLAM LienId] then 'Good'
					When [COL LienId] = [SLAM LienId] and [COL Claim number]<>[ThirdPartyId] then 'Update'
					Else 'Check Query'
					End as [LienId_Check],

			----Check Amount	
				Case 
					When [COL Amount]<>Round([SLAM Amount],2) and ([COL LienId] = [SLAM LienId]) and ([COL Question #] <= 5) and ([COL Status] = 'Final') then 'Look Into'
					When [SLAM Amount] is null and [COL Amount] is not null then 'Look Into'
					When [COL Amount] is null and ([COL Status] = 'Final' or [COL Status] = 'Not Entitled') and ([COL Claim number] = [ThirdPartyId]) then 'Update'
					When ([COL Amount] is null and [SLAM Amount] is not null) and ([COL LienId] = [SLAM LienId]) and ([COL Question #] <= 5) and ([COL Status] = 'Pending' and [SLAM Status] = 'Final') and ([COL Claim number] = [ThirdPartyId]) then 'Update'
					When [COL Amount] = Round([SLAM Amount],2) and ([COL LienId] = [SLAM LienId]) and ([COL Question #] <= 5)  then 'Good'
					When ([COL Amount] is null) and ([COL LienId] = [SLAM LienId]) and ([SLAM Status] = 'Pending' and [COL Status] = 'Pending') then 'Good'
					When [COL Amount] = 0 and ([COL LienId] = [SLAM LienId]) and ([COL Question #] > 5) and ([COL Status] = 'Final' or [COL Status] = 'Not Entitled') then 'Good'
					Else 'Check Query'
					End as [Amount_Check],


			--Check Question number
				Case
					When[COL Question #] > 5 and [COL LienType] <> 'Attorney' and [COL LienType] <> 'Other' and [COL Status] = 'Final' and [COL Amount] = 0 and ([COL Claim number] = [ThirdPartyId])  then 'Good'
					When [COL Question #]<>[SLAM Question #]  and ([COL LienType] <> 'Attorney' or [COL LienType] <> 'Other') and ([COL Claim number] = [ThirdPartyId]) then 'Update'
					When [COL Question #] = [SLAM Question #]  and ([COL LienType] <> 'Attorney' or [COL LienType] <> 'Other') and ([COL Claim number] = [ThirdPartyId])  then 'Good'
					Else 'Check Query'
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
					When len([COL Lienholder]) <= 50 and [COL Lienholder] = [SLAM Lienholder] then 'Good' 
					When len([COL Lienholder]) <= 50 and [COL Lienholder] <> [SLAM Lienholder] then 'Update' 
					Else 'Check Query'
					End as [Lienholder_Check],

			--Liens Not Pulling
			Case
				When [ThirdPartyId] is Null then 'Look Into'
				Else 'Good'
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
							Liens.[Status] as 'SLAM Status', Liens.[True Final Demand] as 'SLAM Amount', Liens.[LienHolderName] as 'SLAM Lienholder'

				--CASE
				--	When isnumeric(CMS.[Lien Id]) = 0 THEN '1' ELSE CMS.[Lien Id]
				--	End as 'COL LienId'

				FROM		CMS_Updated as CMS
							LEFT OUTER JOIN JB_GetClientOnBenefitSummary_JAM as Liens ON CMS.[Lien Id] = Liens.[LienId]  
							LEFT OUTER JOIN JB_BulkEdit_LF as LF ON CMS.[Claim Ref #] = LF.[Claim Ref #]
							LEFT OUTER JOIN JB_COLSearchExtract as SE on CMS.[Claim Number] = SE.[Claim Number]

				--I want to exclude EIF liens from the query, that way analysis is only done on non EIF liens but need to fix JB_GetOnBenefits query first 
				WHERE
						Liens.PersonId NOT IN (Select PersonId from FullProductViews Where (CaseName like '%EIF%') 
			 )) as sub			
	) as sub2

    """,
    con = engine
    )

    # merge dataframes to compare, rename columns
    combined_df = pd.merge(lf_df, cms_df, on = 'Claim Ref #')
    #combined_df = combined_df.rename(columns={"LF_Initial_Label": "LF_Label", "CMS_Initial_Label": "CMS_Label"})

    #Pull Labels from both df into a combined df. Set labels based off matrix
    for index, row in combined_df.iterrows():
        
        if row['LF_Label'] != row['CMS_Label']:
        
            # 1. look Into
            if row['LF_Label'] == 'Look Into':
                combined_df.loc[index, 'CMS_Label'] = row['LF_Label']
            elif row['CMS_Label'] == 'Look Into':
                combined_df.loc[index, 'LF_Label'] = row['CMS_Label']
            
            # 2. Not Eligible
            elif row['LF_Label'] == 'Not Eligible':
                combined_df.loc[index, 'CMS_Label'] = row['LF_Label']
                
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
                combined_df.loc[index, 'LF_Label'] = 'Look Into'
                combined_df.loc[index, 'CMS_Label'] = 'Look Into'
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
    lf_df.to_excel('LF.xlsx')
    cms_df.to_excel('CMS.xlsx')
    happypath = combined_df[combined_df['LF_Label'] == 'Happy Path']
    happypath.to_excel('HappyPath.xlsx')
    addlien = combined_df[combined_df['LF_Label'] == 'Add Lien']
    addlien.to_excel('NewLiens.xlsx')
    combined_df.to_excel('Full_Analysis.xlsx', index = False)
    print('SQL code has completed, on to updates!')