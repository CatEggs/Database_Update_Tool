import analysis
import update
import hi_results
import updatelib as ud
import time
import concurrent.futures
from os import listdir


start = time.perf_counter()


def main():
    # define the file path
    hi_path = r'F:\Mass Tort Cases\TVM\Claims Online\Updates\2019\2019_11_04\Human_Intervention\\'
    path = r'F:\Mass Tort Cases\TVM\Claims Online\Updates\2019\2019_11_04\OBE\\'

    # put .xlsx files found in path to list
    file_list = []
    for f in listdir(path):
        if f.endswith('.xlsx'):
            file_list.append(f)
    # run SQL analysis
    analysis.col_1()
    print('Analysis is done, now for human intervention results!')
    
    # create the human intervention spreadsheets
    hi_results.col_3(hi_path)

    # run update script to update the OBE's with info from analysis
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for f in file_list:
            executor.submit(update.col_2, path, f)

if __name__ == '__main__':
    main()

finish = time.perf_counter()
print(f'Finished in {round(finish-start, 2)} seconds')