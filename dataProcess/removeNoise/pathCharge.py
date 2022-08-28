import json

import pandas as pd
import re


# 文本预处理
def preprocess(text):
    text = str(text)
    length = len(text)
    text = text[1:length - 1].replace(",", " ").replace("'", "").replace("/", " ")
    line = str(text)
    return line


class PathCharge:
    def __init__(self, relation):
        path = '../../dataset/statics.csv'
        self.nameList = pd.read_csv(path)['Name'].values.tolist()
        self.relation = relation

    def charge_path(self):
        for name in self.nameList:
            print(name,'------------start-------------------')
            path = '../../dataset/%s/%s/filter.csv' % (name, self.relation)
            df = pd.read_csv(path)
            df['path_name'] = df['path_name'].apply(preprocess)
            df.to_csv(path, header=True, index=False)
            print(name, '------------over-------------------')
        print('------------------------------all over-------------------------------------')

    def change_path_counts(self):
        for name in self.nameList:
            print(name)
            path = '../../dataset/%s/%s/filter.csv' % (name, self.relation)
            df = pd.read_csv(path)
            additions_lines = []
            deletions_lines = []
            changed_files = []
            jsonPath = '../../resource/%s/%sFilterPrData.json' % (name, name)
            with open(jsonPath, 'r') as load_f:
                load_dict = json.load(load_f)
            idList = df['id'].values.tolist()

            for Id in idList:
                count = 0
                for entity in load_dict:
                    if entity['id'] == Id:
                        count += 1
                        additions_lines.append(entity['additions_lines'])
                        deletions_lines.append(entity['deletions_lines'])
                        changed_files.append(entity['changed_files'])
                    if count == 1:
                        break
            df['additions_lines'] = additions_lines
            df['deletions_lines'] = deletions_lines
            df['changed_files'] = changed_files

            if self.relation == 'merge':
                df.to_csv(path,
                          columns=["id", "merger", "create_time", "create_time_range","creator", "title",
                                   "label", "commit_creator", "commit_message",
                                   "path_name", "code", "body", 'merger_id', 'merger_time_range',
                                   'person_probably', "additions_lines", "deletions_lines", "changed_files"],
                          index=False, header=True,
                          sep=',')
            else:
                df.to_csv(path,
                          columns=["id", "reviewer", "create_time", "create_time_range","creator", "title",
                                   "label", "commit_creator", "commit_message",
                                   "path_name", "code", "body", 'reviewer_id', 'reviewer_time_range', 'person_probably',
                                   "additions_lines", "deletions_lines", "changed_files"],
                          index=False, header=True,
                          sep=',')
            print(name, '------------over-------------------')
        print('------------------------------all over-------------------------------------')


# p = PathCharge('merge')
# p.charge_path()
# p = PathCharge('review')
# p.charge_path()
