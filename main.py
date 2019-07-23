import analysis
import update
import hi_results
import updatelib as ud

def main():
    hi_path = r'F:\Mass Tort Cases\TVM\Claims Online\Updates\2019\Bulk Edit - Test - 2019_07_15\Human Intervention\\'
    # path = r'F:\Mass Tort Cases\TVM\Claims Online\Updates\2019\Bulk Edit - Test - 2019_07_15\\'

    # bj_filename = 'Burnett.xlsx'
    # ba_filename = 'BA.xlsx'
    # ak18_filename = 'AWKO2018.xlsx'
    # bbga_filename = 'BBGA1.xlsx'
    # bbgac_filename = 'BBGAComeback.xlsx'
    # bliz2_filename = 'Bliz2.xlsx'
    # clh2_filename = 'CLH2.xlsx'
    # clh3_filename = 'CLH3.xlsx'
    # goza_filename = 'Goza.xlsx'
    # indset_filename = 'IndividuallySettled.xlsx'
    # ls2_filename = 'LevinSims2.xlsx'
    # ls3_filename = 'LevinSims3.xlsx'
    # lpm_filename = 'LPM.xlsx'
    # ## lpm2_filename = 'LPM2.xlsx'
    # mos_filename = 'MostynLaw.xlsx'
    # mos17_filename = 'Mostyn2017.xlsx'
    # mos50_filename = 'Mostyn50.xlsx'

    # mr17_filename = 'MR17.xlsx'
    # mrc_filename = 'MRComeback.xlsx'
    # mrfeb_filename = 'MRFeb.xlsx'
    # mrs_filename = 'MRSettlement.xlsx'
    # muel1_filename = 'Mueller1.xlsx'
    # muel2_filename = 'Mueller2.xlsx'
    # pk_filename = 'PerdueKidd.xlsx'
    # rob_filename = 'Robinson.xlsx'
    # tf29_filename = 'TF29.xlsx'
    # tf_filename = 'TraceyFox.xlsx'

    analysis.col_1()

    # try:
    #     update.col_2(path, bj_filename)
    # except FileNotFoundError:
    #     print('Burnett file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('Burnett updates done!')
    # try:
    #     update.col_2(path, ba_filename)
    # except FileNotFoundError:
    #     print('BaileyAylstock file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('BA updates done!')
    # try:
    #     update.col_2(path, ak18_filename)
    # except FileNotFoundError:
    #     print('AWKO2018 file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('AWKO18 updates done!')
    # try:
    #     update.col_2(path, bbga_filename)
    # except FileNotFoundError:
    #     print('BBGA file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('BBGA updates done!')
    # try:
    #     update.col_2(path, bbgac_filename)
    # except FileNotFoundError:
    #     print('BBGAComeback file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('BBGAComeback updates done!')
    # try:
    #     update.col_2(path, bliz2_filename)
    # except FileNotFoundError:
    #     print('Blizzard2 file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('Bliz2 updates done!')
    # try:
    #     update.col_2(path, clh2_filename)
    # except FileNotFoundError:
    #     print('CLH2 file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('CLH2 updates done!')
    # try:
    #     update.col_2(path, clh3_filename)
    # except FileNotFoundError:
    #     print('CLH3 file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('CLH3 updates done!')
    # try:
    #     update.col_2(path, goza_filename)
    # except FileNotFoundError:
    #     print('Goza file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('Goza updates done!')
    # try:
    #     update.col_2(path, indset_filename)
    # except FileNotFoundError:
    #     print('IndividuallySettled file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('IndividSet updates done!')
    # try:
    #     update.col_2(path, ls2_filename)
    # except FileNotFoundError:
    #     print('LevinSims2 file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('ls2 updates done!')
    # try:
    #     update.col_2(path, ls3_filename)
    # except FileNotFoundError:
    #     print('LevinSims3 file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('ls3 updates done!')
    # try:
    #     update.col_2(path, lpm_filename)
    # except FileNotFoundError:
    #     print('LPM file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('lpm updates done!')
    # # try:
    # #     update.col_2(path, lpm2_filename)
    # # except FileNotFoundError:
    # #     print('LPM2 file not found. Check to see if the excel name matches the one on python script')
    # #     pass
    # try:
    #     update.col_2(path, mos_filename)
    # except FileNotFoundError:
    #     print('MostynLaw file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('mostyn updates done!')
    # try:
    #     update.col_2(path, mos17_filename)
    # except FileNotFoundError:
    #     print('Mostyn2017 file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('mostyn17 updates done!')
    # print('updates are half way done!')
    # try:
    #     update.col_2(path, mos50_filename)
    # except FileNotFoundError:
    #     print('Mostyn50 file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('most50 updates done!')
    # try:
    #     update.col_2(path, mr17_filename)
    # except FileNotFoundError:
    #     print('MR2017 file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('mr17 updates done!')
    # try:
    #     update.col_2(path, mrc_filename)
    # except FileNotFoundError:
    #     print('MRComeback file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('mrcomeback updates done!')
    # try:
    #     update.col_2(path, mrfeb_filename)
    # except FileNotFoundError:
    #     print('MRFeb file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('mrfeb updates done!')
    # try:
    #     update.col_2(path, mrs_filename)
    # except FileNotFoundError:
    #     print('MRSettlement file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('mrsettlement updates done!')
    # try:
    #     update.col_2(path, muel1_filename)
    # except FileNotFoundError:
    #     print('Mueller1 file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('mueller1 updates done!')
    # try:
    #     update.col_2(path, muel2_filename)
    # except FileNotFoundError:
    #     print('Mueller2 file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('mueller2 updates done!')
    # try:
    #     update.col_2(path, pk_filename)
    # except FileNotFoundError:
    #     print('PerdueKidd file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('perduekidd updates done!')
    # try:
    #     update.col_2(path, rob_filename)
    # except FileNotFoundError:
    #     print('Robinson file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('rob updates done!')
    # try:
    #     update.col_2(path, tf29_filename)
    # except FileNotFoundError:
    #     print('TraceyFox229 file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('tf29 updates done!')
    # try:
    #     update.col_2(path, tf_filename)
    # except FileNotFoundError:
    #     print('TraceyFox file not found. Check to see if the excel name matches the one on python script')
    #     pass
    # print('tf updates done!')
    print('Updates are complete, now for human intervention results!')

    hi_results.col_3(hi_path)
 
main()