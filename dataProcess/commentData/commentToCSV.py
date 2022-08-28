# coding=utf-8
import csv
import json
import os
import re

import pandas as pd


def openFile(path):
    with open(path, 'r') as load_f:
        load_dict = json.load(load_f)
    return load_dict


def code_preprocess(text):
    arr = text.split("\n")
    arr = [x for x in arr if x.startswith('+') or x.startswith('-')]
    arr = [x.lstrip("+").lstrip("-").lstrip() for x in arr]
    arr = [x for x in arr if x and x.startswith('//') == False]
    text = " ".join(arr)
    pattern = r"[^\s]*\.(com|org|net)\S*"
    text = re.sub(pattern, '', text)
    text = re.sub('[\\d+]', '', text)
    text = re.sub('\\-([^a-zA-Z0-9\\s_])', '', text)
    text = re.sub('\\.([^a-zA-Z0-9\\s_])', '', text)
    text = re.sub('[^a-zA-Z0-9\\s_\\-\\.]', '', text)
    arr = text.split(" ")
    arr = [x.strip() for x in arr if x.strip() != '']
    newArr = []
    for x in arr:
        if x.startswith('sha-'):
            newArr.append('sha')
        else:
            newArr.append(x)
    text = " ".join(newArr)
    return text


class DataComment:
    def __init__(self, name):
        self.name = name
        print('当前处理项目:%s' % name)

    def csvCommentSave(self):
        print(self.name, 'comment')
        path = '../../resource/%s/%sFilterPrData.json' % (self.name, self.name)
        folder = os.path.exists('../../dataset/%s/%s' % (self.name, 'comment'))
        newPath = '../../dataset/%s/%s/%sComment.csv' % (self.name, 'comment', self.name)
        if not folder:
            os.makedirs('../../dataset/%s/%s' % (self.name, 'comment'))

        files = openFile(path)
        row = []
        for entity in files:
            if 'commentData' in entity:
                id = entity['id']
                title = str(entity['title'])
                creator = entity['pr_creator_name']
                pr_create_time = entity['created_at']

                additions_lines = entity['additions_lines']
                deletions_lines = entity['deletions_lines']
                changed_files = entity['changed_files']

                if entity['body'] == '':
                    body = "none"
                else:
                    body = str(entity['body'])

                label = ''
                if not entity['labels']:
                    label = ",none"
                else:
                    for text in entity['labels']:
                        label += ',' + text
                label = label[1:]

                commit_message = ''
                commit_creator = []
                if 'commitData' in entity and len(entity['commitData']) != 0:
                    for com in entity['commitData']:
                        commit_creator.append(com['commit_author_name'])
                        commit_message += str(com['message'])
                else:
                    commit_message = "none"

                commit_creator = list(set(commit_creator))
                path_name = []
                code = ''
                if 'files_detail' in entity:
                    for s in entity['files_detail']:
                        path_name.append(s['filename'])
                        if 'patch' in s:
                            code += code_preprocess(s["patch"])

                for re in entity['commentData']:
                    commenter = re['comment_creator']
                    row.append(
                        [id, pr_create_time, creator, title, body, label,
                         commit_creator, commit_message, path_name, code,
                         additions_lines, deletions_lines, changed_files, commenter])

        if os.path.exists(newPath):
            os.remove(newPath)
        with open(newPath, "a", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(
                ["id", "create_time", "creator", "title", "body", "label",
                 "commit_creator", "commit_message", "path_name", "code",
                 "additions_lines", "deletions_lines", "changed_files", "commenter",
                 ])
            for r in row:
                writer.writerow(r)
        print("保存所有的comment数据到csv文件")


# d=DataComment('react')
# newPath = '../../dataset/react/comment/reactComment.csv'
# df=pd.read_csv(newPath)
# print(len(df))
