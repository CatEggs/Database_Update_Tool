import pathlib
import glob
import pandas
import openpyxl as op

currentdirectory = pathlib.Path('.')
pattern = "*.xlsx"
files =[f for f in currentdirectory.glob(pattern)]
print(files)

xx = pandas.DataFrame()
yy = pandas.DataFrame()
zz = pandas.DataFrame()

# create an xlsx file name "Combined" 
writer = pandas.ExcelWriter('Combined.xlsx', engine = 'xlsxwriter')

# grabs all files in the folder with a specific sheet name and puts in its own datafram
for f in files:
  data = pandas.read_excel(f, sheet_name = 'Law Firm Representation')
  data2 = pandas.read_excel(f, sheet_name = 'CMS_Third Party Liens', converters={'Lien Id': str}).rename(columns = {'Lien Id': 'Lien Id_Old'})
  data2['Lien Id'] = data2['Lien Id_Old'].apply(lambda s: int(s) if str(s).isdigit() else s)
  data3 = pandas.read_excel(f, sheet_name = 'Implant Claimant')
  xx = xx.append(data)
  yy = yy.append(data2.drop(columns = ['Lien Id_Old']), sort=False)
  zz = zz.append(data3)

# prints each datafram into its own tab in the Combined.xlsx file
xx.to_excel(writer, sheet_name ='LF', index=False)
yy.to_excel(writer, sheet_name ='CMS', index=False)
zz.to_excel(writer, sheet_name ='IC', index=False)

writer.save()