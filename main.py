import analysis
import update
import hi_results
import time
import concurrent.futures
from os import listdir

def main(user_input):
    start = time.perf_counter()
    hi_path = r'F:\Mass Tort Cases\TVM\Claims Online\Updates\2020\\'+ user_input +'\Human_Intervention\\'
    path = r'F:\Mass Tort Cases\TVM\Claims Online\Updates\2020\\'+ user_input +'\TBU\\'

    # # put .xlsx files found in path to list
    file_list = []
    for f in listdir(path):
        if f.endswith('.xlsx'):
            file_list.append(f)

    # # run SQL analysisCOL
    analysis.col_1()
    print('Analysis is done, now for human intervention results!')
    
    # # create the human intervention spreadsheets
    hi_results.col_3(hi_path)

    # # run update script to update the OBE's with info from analysis
    print(file_list)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for f in file_list:
            executor.submit(update.col_2, path, f)

    finish = time.perf_counter()
    print(f'Finished in {round(finish-start, 2)} seconds')

if __name__ == '__main__':
    user_input = input('Tell me the folder date (yyyy-mm-dd):')
    main(user_input)

