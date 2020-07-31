@echo on

REM REM run this code on the command prompt to run code
REM REM .\runfulltool.bat 

REM Get date to add to filepath
for /f "delims=" %%a in ('wmic OS Get localdatetime  ^| find "."') do set dt=%%a
set YYYY=%dt:~0,4%
set MM=%dt:~4,2%
set DD=%dt:~6,2%
set stamp=%YYYY%_%MM%_%DD%

REM Create filepath variables
set obe_filepath="\\atx-fs-1\Files\Mass Tort Cases\TVM\Claims Online\Updates\2020\%stamp%\OBE"
set tbu_filepath="\\atx-fs-1\Files\Mass Tort Cases\TVM\Claims Online\Updates\2020\%stamp%\TBU"
set bulkedits_filepath="\\atx-fs-1\Files\Mass Tort Cases\TVM\Claims Online\Updates\PythonDocs\BulkEdits\BulkEdits"
set my_bulkedits="C:\Users\cegboh\Desktop\PythonProjects\COLProject\BulkEdits\"
set col_main= "C:\Users\cegboh\Desktop\PythonProjects\COLProject"

REM Create Folders
python create_folders.py

REM casperjs .\cot_ce.js COL_USERNAME(email) COL_Password filename.xlsx

REM move "SE.xlsx" to 1st BulkEdits folder --RUN if you can fix ^^
REM move SE.xlsx  %my_bulkedits%


REM copy all files to Updates drive 
copy *.xlsx  %obe_filepath%
copy *.xlsx  %tbu_filepath%
copy *.xlsx %bulkedits_filepath%

REM REM merge all the excel files in this folder into one file called Combined.xlsx
python merge_xlsx.py 

REM move "Combined.xlsx" to 1st BulkEdits folder 
move Combined.xlsx  %my_bulkedits%

REM change directories since all the other files will be in this folder
cd  %my_bulkedits%

REM get all files needed for SQL table import
python get_files.py

REM REM import tables into SQL
python import_sqltables.py

REM change directories since all the other files will be in this folder
cd  %col_main%

REM Run main COL Script 
REM python main.py %stamp%