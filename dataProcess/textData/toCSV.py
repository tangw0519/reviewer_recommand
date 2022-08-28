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


class DataSetTrans:
    def __init__(self, name):
        self.name = name
        print('当前处理项目:%s' % name)

    def getDataCount(self):
        newPath = '../../dataset/%s/%s/%sMerge.csv' % (self.name, 'merge', self.name)
        df = pd.read_csv(newPath)
        print("数据量：%d条" % len(df))
        return len(df)

    def getAllLabel(self):
        path = '../../resource/%s/%sFilterPrData.json' % (self.name, self.name)
        folder = os.path.exists('../../dataset/%s/%s' % (self.name, 'merge'))
        newPath = '../../dataset/%s/label.csv' % self.name
        if not folder:
            os.makedirs('../../dataset/%s/%s' % (self.name, 'merge'))
        labels = []
        files = openFile(path)
        for s in files:
            if s['labels']:
                for label in s['labels']:
                    labels.append(label)
            else:
                labels.append("none")
        labels = list(set(labels))
        print(len(labels))
        row = []
        for u in labels:
            row.append([u])
        if os.path.exists(newPath):
            os.remove(newPath)
        with open(newPath, "a", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(
                ["labelName"])
            for r in row:
                writer.writerow(r)

    def csvMergeSave(self):
        print(self.name, 'merge')
        path = '../../resource/%s/%sFilterPrData.json' % (self.name, self.name)
        folder = os.path.exists('../../dataset/%s/%s' % (self.name, 'merge'))
        newPath = '../../dataset/%s/%s/%sMerge.csv' % (self.name, 'merge', self.name)
        if not folder:
            os.makedirs('../../dataset/%s/%s' % (self.name, 'merge'))

        files = openFile(path)
        row = []
        for entity in files:
            if entity['merge'] and 'pr_mergedBy_user_name' in entity:
                id = entity['id']
                title = str(entity['title'])
                merger = entity['pr_mergedBy_user_name']
                creator = entity['pr_creator_name']
                create_time = entity['created_at']

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
                        if 'commit_author_login' in com:
                            commit_creator.append(com['commit_author_login'])
                        else:
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
                row.append(
                    [id, create_time, creator, title, body, label, commit_creator, commit_message, path_name, code,
                     additions_lines, deletions_lines, changed_files, merger])
        if os.path.exists(newPath):
            os.remove(newPath)
        with open(newPath, "a", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(
                ["id", "create_time", "creator", "title", "body", "label", "commit_creator", "commit_message",
                 "path_name", "code",
                 "additions_lines", "deletions_lines", "changed_files", "merger"])
            for r in row:
                writer.writerow(r)

    def csvReviewSave(self):
        print(self.name, 'review')
        path = '../../resource/%s/%sFilterPrData.json' % (self.name, self.name)
        folder = os.path.exists('../../dataset/%s/%s' % (self.name, 'review'))
        newPath = '../../dataset/%s/%s/%sReview.csv' % (self.name, 'review', self.name)
        if not folder:
            os.makedirs('../../dataset/%s/%s' % (self.name, 'review'))

        files = openFile(path)
        row = []
        for entity in files:
            if 'reviewData' in entity:
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
                        if 'commit_author_login' in com:
                            commit_creator.append(com['commit_author_login'])
                        else:
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

                for re in entity['reviewData']:
                    reviewer = re['review_comment_creator']
                    # review_created_time = re['created_at']
                    # reviewer_type = re['author_association']
                    # review_body = re['body']
                    row.append(
                        [id, pr_create_time, creator, title, body, label,
                         commit_creator, commit_message, path_name, code,
                         additions_lines, deletions_lines, changed_files, reviewer])

        if os.path.exists(newPath):
            os.remove(newPath)
        with open(newPath, "a", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(
                ["id", "create_time", "creator", "title", "body", "label",
                 "commit_creator", "commit_message", "path_name", "code",
                 "additions_lines", "deletions_lines", "changed_files", "reviewer",
                 ])
            for r in row:
                writer.writerow(r)
        print("保存所有的review数据到csv文件")


# repos = openFile("../../resource/repos/repos.json")
# for x in repos[0:]:
#     print(x)
#     data = DataSetTrans(x["name"])
#     data.csvMergeSave()
#     data.csvReviewSave()

# JSON->toCSV->reactReview
# TextCleaner->
# afterTextClean->LabelTrans
# afterLabelClean->timeTrans
# afterTimeClean->removeMerger
# afterRemoveClean->pathCharge
