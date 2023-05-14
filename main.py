from pathlib import Path
import pandas as pd

def search_word_receipt(disease_str):
    with open('target_word.csv', encoding='cp932') as f:
        rows = f.readlines()
    words = [row.replace('\n', '') for row in rows]
    hit_words = []
    for word in words:
        if word in disease_str:
            hit_words.append(word)
    return hit_words

def read_disease_master():
    with open('disease.csv', encoding='cp932') as f:
        rows = f.readlines()
    disease_master = {}
    for row in rows:
        row = row.replace('\n', '')
        row_list = row.split(',')
        disease_master[row_list[0]] = row_list[1]
    return disease_master

def read_receipts(input_path, disease_master):
    df = pd.read_csv('./data/karte/カルテ_全結合.csv', engine='python', encoding='cp932', dtype='object')
    for file in input_path.glob('**/*.UKE'):
        with open(file, encoding='cp932') as f:
            rows = f.readlines()
        patient_id = ''
        nanbyo = False
        InFlag = False
        disease_list = []
        output_rows = []

        for row in rows:
            row_list = row.split(',')
            if row_list[0] == 'RE':
                if InFlag and not nanbyo and patient_id:
                    disease_str = ' '.join(disease_list)
                    receipt_hit_words = ' '.join(search_word_receipt(disease_str))
                    patient_df = df[df['カルテ番号等'] == patient_id]
                    karte_txt = ''
                    for i, v in patient_df.iterrows():
                        karte_txt += f"{v['体位']} {v['カルテ内容']}"
                    karte_hit_words = ' '.join(search_word_receipt(karte_txt))
                    row = [patient_id, receipt_hit_words, karte_hit_words]
                    if receipt_hit_words or karte_hit_words:
                        output_rows.append(row)
                disease_list = []
                InFlag = False
                if int(row_list[2]) % 2 == 1:
                    InFlag = True
                    patient_id = row_list[13][:8]
            if InFlag and row_list[0] == 'SB':
                if disease_master[row_list[1]] == '＊＊　未コード化傷病名　＊＊':
                    disease_name = row_list[3]
                else:
                    disease_name = disease_master[row_list[1]]
                disease_list.append(disease_name)
            if InFlag and row_list[0] == 'SY':
                if disease_master[row_list[1]] == '＊＊　未コード化傷病名　＊＊':
                    disease_name = row_list[5]
                else:
                    disease_name = disease_master[row_list[1]]
                disease_list.append(disease_name)

            if InFlag and row_list[0] == 'SI':
                if row_list[3] == '190101770':
                    nanbyo = True
    df = pd.DataFrame(output_rows, columns=['患者ID', 'レセプトヒットワード', 'カルテヒットワード'])
    df.to_csv('out.csv', index=False, encoding='cp932')

if __name__ == '__main__':
    input_path = Path.cwd()/'data/receipt'
    disease_master = read_disease_master()
    read_receipts(input_path, disease_master)
