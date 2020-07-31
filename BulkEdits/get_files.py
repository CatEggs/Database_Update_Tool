import pandas as pd
import glob

path = r'C:\\Users\\cegboh\\Desktop\\PythonProjects\\COLProject\\BulkEdits\\'
csr_path = glob.glob(r'F:\\Mass Tort Cases\\TVM\\Claims Online\\Reports\Astora Cross-Settlement Payment List for Shapiro*.xlsx')
prob_path = glob.glob(r'F:\\Mass Tort Cases\\TVM\\Claims Online\\#Problems - AMS - Data Checks -*.xlsx')
bud_path = glob.glob(r'F:\\Mass Tort Cases\\TVM\\Claims Online\\#BUDNSFW - AMS - Data Checks - *.xlsx')

csr = pd.read_excel(csr_path[0], header = 1 )
prob_sum = pd.read_excel(prob_path[0], sheet_name = 'Summary' )
prob_ssn = pd.read_excel(prob_path[0], sheet_name = 'SSN Bad Matches')
bud_client = pd.read_excel(bud_path[0], sheet_name = 'Claimant Level')
bud_lien = pd.read_excel(bud_path[0], sheet_name = 'Lien Level')

csr.to_excel(path +'CSR.xlsx', index = False)
prob_sum.to_excel(path +'Problem_Summary.xlsx', index = False)
prob_ssn.to_excel(path +'Problem_SSN.xlsx', index = False)
bud_client.to_excel(path +'BUDNSFW_Claimant.xlsx', index = False)
bud_lien.to_excel(path +'BUDNSFW_Lien.xlsx', index = False)
