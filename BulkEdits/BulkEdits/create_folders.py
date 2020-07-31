from pathlib import Path
from datetime import date

def create_folders():
    today = date.today().strftime('%Y_%m_%d')
    filepath = r"\\atx-fs-1\Files\Mass Tort Cases\TVM\Claims Online\Updates\2020\\"+ today
    Path(filepath+"\\Human_Intervention").mkdir(parents=True, exist_ok=True)
    Path(filepath+"\\TBU").mkdir(parents=True, exist_ok=True)
    Path(filepath+"\\OBE").mkdir(parents=True, exist_ok=True)

create_folders()
