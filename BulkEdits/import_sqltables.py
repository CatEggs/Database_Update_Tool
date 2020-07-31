from sqlalchemy import create_engine, event
from sqlalchemy.exc import ProgrammingError
from truncate_tbls import truncate_tbls 
import pandas as pd
import config
import time
import os

### Connect ot SQL ###
sql_connect = "mssql+pyodbc://" + config.username + ":" + config.password + "@" + config.local + "?driver=SQL+Server+Native+Client+11.0"
engine = create_engine(sql_connect)

### Put tables in dataframe ###
csr = pd.read_excel("CSR.xlsx", index=False)
bud_clients = pd.read_excel("BUDNSFW_Claimant.xlsx", index=False)
bud_liens = pd.read_excel("BUDNSFW_Lien.xlsx", index=False)
lf = pd.read_excel("Combined.xlsx", sheet_name='LF',index=False)
# cms = pd.read_excel("Combined.xlsx", sheet_name='CMS', index=False)
ic = pd.read_excel("Combined.xlsx", sheet_name='IC', index=False)
prob_ssn = pd.read_excel("Problem_SSN.xlsx", index=False)
prob_sum = pd.read_excel("Problem_Summary.xlsx", index=False)
# se = pd.read_excel("SE.xlsx", index=False)

### Run truncate tables script ###
truncate_tbls()

t0 = time.time()
### Insert tables into SQL ###
@event.listens_for(engine, 'before_cursor_execute')
def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
    if executemany:
        cursor.fast_executemany = True

csr.to_sql("JB_CSR_AMS", engine, if_exists='append', index=False)
bud_clients.to_sql("JB_BUDNSFW_Client", engine, if_exists='append', index=False)
bud_liens.to_sql("JB_BUDNSFW_Lien", engine, if_exists='append', index=False)
lf.to_sql("JB_BulkEdit_LF", engine, if_exists='append', index=False)
# cms.to_sql("JB_BulkEdit_CMS", engine, if_exists='append', index=False)
ic.to_sql("JB_BulkEdit_IC", engine, if_exists='append', index=False)
prob_sum.to_sql("JB_AMSProblems_Summary", engine, if_exists='append', index=False)
prob_ssn.to_sql("JB_AMSProblems_SSNResearch", engine, if_exists='append', index=False)
# se.to_sql("JB_COLSearchExtract", engine, if_exists='append', index=False)

print(f"All rows written in {(time.time() - t0):.1f} seconds")