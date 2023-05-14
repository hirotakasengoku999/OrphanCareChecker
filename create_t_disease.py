import pandas as pd
from pathlib import Path

with open('unique_patient_list.csv', encoding='cp932') as f:
    rows = f.readlines()
    f.close()
patient_list = [row.replace('\n', '') for row in rows]

filepath = Path.cwd()/'data/receipt'

for file in filepath.glob('**/*.UKE'):
    with open(file, encoding='cp932') as f:
        rows = f.readlines()

    for row in rows:
        row_list = row.split(',')
        if row_list[0] == 'RE':
            if row_list[13][:8] in patient_list:
                print(row_list)