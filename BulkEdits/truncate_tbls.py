import pyodbc
import config

def truncate_tbls():
    connection = pyodbc.connect(
            r'DRIVER={SQL Server Native Client 11.0};'
            r'SERVER=' + config.server + ';'
            r'DATABASE=' + config.database + ';'
            r'UID=' + config.username + ';'
            r'PWD=' + config.password
            )

    cursor = connection.cursor()
    truncate="""
    --TRUNCATE TABLE JB_COLSearchExtract;
    TRUNCATE TABLE JB_BulkEdit_LF;
    TRUNCATE TABLE JB_BulkEdit_IC;
    TRUNCATE TABLE JB_BulkEdit_CMS;
    TRUNCATE TABLE JB_CSR_AMS;
    TRUNCATE TABLE JB_AMSProblems_Summary;
    TRUNCATE TABLE JB_AMSProblems_SSNResearch;
    TRUNCATE TABLE JB_BUDNSFW_Lien;
    TRUNCATE TABLE JB_BUDNSFW_Client;
    """
    cursor.execute(truncate)
    cursor.commit()
truncate_tbls()

