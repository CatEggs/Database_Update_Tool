import analysis
import update
import hi_results
import updatelib as ud

def main():
    hi_path = r'F:\Mass Tort Cases\TVM\Claims Online\Updates\2019\Bulk Edit - Test -2019_05_20\Human Intervention\\'
    path = r'F:\Mass Tort Cases\TVM\Claims Online\Updates\2019\Bulk Edit - Test -2019_05_20\\'
    bj_filename = 'Burnett.xlsx'
    #ba_filename = 'BA.xlsx'
    # ud.make_copy(path, bj_filename)
    # ud.make_copy(path, ba_filename)
    analysis.col_1()
    update.col_2(path, bj_filename)
    #update.col_2(path, ba_filename)
    hi_results.col_3(hi_path)
 
main()