# coding=utf-8
import csv
import json
import os

import numpy as np
import pandas as pd


def listToArray(dataAll):
    array = []
    for x in dataAll:
        x = x.replace('[', '').replace(']', '').replace(' ', '')
        arr = x.split(',')
        listArr = np.zeros(len(arr), dtype=int)
        for i in range(len(arr)):
            listArr[i] = arr[i]
        array.append(listArr)
    array = np.array(array)
    return array


# df = pd.read_csv('dataset/pandas/pandasMerger.csv')
# num_class = pd.get_dummies(df['name']).values.shape[1]
#
# personTime = listToArray(df['time_range'])


def getRecommandPerson(time, personTime, num_class):
    index = np.where(time == 1)[0][0]
    current = [0] * num_class
    for i in range(len(personTime)):
        flag1 = False  # 是否一直不活跃
        recent_active_gap = 0  # 是否长期不活跃
        active_times = 0  # 是否活跃度不高
        for j in range(index):
            if personTime[i][j] != 0:
                flag1 = True
                recent_active_gap = j
                active_times += personTime[i][j]
        if not flag1:
            current[i] -= 5  # pr所在时刻之前该角色不曾活跃过
        else:
            if index - recent_active_gap > 6:  # 是否长期不活跃，一两年不活跃
                current[i] -= 2
            # if active_times < 20:
            #     current[i] = -2
            else:
                if active_times < 20:
                    current[i] += 2
                else:
                    current[i] += 5
    return current


class RemoveNoise:
    def __init__(self, name):
        self.name = name
        print('当前处理项目:%s' % name)

    def remove_merger_low_counts(self, counts=10):
        print("当前操作：去除项目%s合并次数少于%d的merger" % (self.name, counts))
        newPath = '../../dataset/%s/%sMerger.csv' % (self.name, self.name)
        df = pd.read_csv(newPath)
        df = df[counts <= df['count']]
        df.to_csv('../../dataset/%s/%sRemoveMerger.csv' % (self.name, self.name), header=True, index=False)

    def remove_noise_of_merge_memory(self):
        print("当前操作：去除项目%s合并次数少于10的merger进行的合并操作记录" % self.name)
        newPath = '../../dataset/%s/%sRemoveMerger.csv' % (self.name, self.name)
        nameList = pd.read_csv(newPath)['name'].values.tolist()
        path = '../../dataset/%s/merge/afterTimeClean.csv' % self.name
        df = pd.read_csv(path)
        df = df[df['merger'].isin(nameList)]
        df.to_csv('../../dataset/%s/merge/afterRemoveClean.csv' % self.name, header=True, index=False)

    def merge_merger_and_memory(self):
        print("当前操作：合并项目%s的merger以及操作记录，生成filter数据集" % self.name)
        newPath = '../../dataset/%s/%sRemoveMerger.csv' % (self.name, self.name)
        df = pd.read_csv(newPath)
        personTime = listToArray(df['time_range'])

        path = '../../dataset/%s/merge/afterRemoveClean.csv' % self.name
        data = pd.read_csv(path)
        nameList = df['name'].values.tolist()
        merger_id = []
        merger_time_range = []

        for i in range(len(data)):
            index = nameList.index(data['merger'][i])
            merger_id.append(index)
            merger_time_range.append(df['time_range'][index])
        data['merger_id'] = merger_id
        data['merger_time_range'] = merger_time_range

        arrayTime = []
        createTimes = listToArray(data['create_time_range'])
        for time in createTimes:
            person_time = getRecommandPerson(time, personTime, len(nameList))
            arrayTime.append(person_time)

        data['person_probably'] = arrayTime

        data.to_csv('../../dataset/%s/merge/filter.csv' % self.name,
                    columns=["id", "create_time", "create_time_range","creator", "title", "body", "label", "commit_creator",
                             "commit_message",
                             "path_name", "code",
                             "additions_lines", "deletions_lines", "changed_files", "merger" ,'merger_id',
                             'merger_time_range', 'person_probably'],
                    index=False, header=True,
                    sep=',')

    # review
    def remove_reviewer_low_counts(self, counts=10):
        print("当前操作：去除项目%s审查次数少于%d的reviewer" % (self.name, counts))
        newPath = '../../dataset/%s/%sReviewer.csv' % (self.name, self.name)
        df = pd.read_csv(newPath)
        df = df[counts <= df['count']]
        df.to_csv('../../dataset/%s/%sRemoveReviewer.csv' % (self.name, self.name), header=True, index=False)

    def remove_noise_of_review_memory(self):
        print("当前操作：去除项目%s审查次数少于阈值的reviewer进行的审查操作记录" % self.name)
        newPath = '../../dataset/%s/%sRemoveReviewer.csv' % (self.name, self.name)
        nameList = pd.read_csv(newPath)['name'].values.tolist()
        path = '../../dataset/%s/review/afterTimeClean.csv' % self.name
        df = pd.read_csv(path)
        df = df[df['reviewer'].isin(nameList)]
        df.to_csv('../../dataset/%s/review/afterRemoveClean.csv' % self.name, header=True, index=False)

    def merge_reviewer_and_memory(self):
        print("当前操作：合并项目%s的reviewer以及操作记录，生成filter数据集" % self.name)
        newPath = '../../dataset/%s/%sRemoveReviewer.csv' % (self.name, self.name)
        df = pd.read_csv(newPath)
        personTime = listToArray(df['time_range'])

        path = '../../dataset/%s/review/afterRemoveClean.csv' % self.name
        data = pd.read_csv(path)
        nameList = df['name'].values.tolist()
        reviewer_id = []
        reviewer_time_range = []

        for i in range(len(data)):
            index = nameList.index(data['reviewer'][i])
            reviewer_id.append(index)
            reviewer_time_range.append(df['time_range'][index])
        data['reviewer_id'] = reviewer_id
        data['reviewer_time_range'] = reviewer_time_range

        arrayTime = []
        createTimes = listToArray(data['create_time_range'])
        for time in createTimes:
            person_time = getRecommandPerson(time, personTime, len(nameList))
            arrayTime.append(person_time)

        data['person_probably'] = arrayTime

        data.to_csv('../../dataset/%s/review/filter.csv' % self.name,
                    columns=["id", "create_time", "create_time_range", "creator", "title", "body", "label",
                             "commit_creator", "commit_message", "path_name", "code",
                             "additions_lines", "deletions_lines", "changed_files", "reviewer", 'reviewer_id',
                             'reviewer_time_range', 'person_probably'],
                    index=False, header=True,
                    sep=',')


# print("当前操作：去除操作次数过少的开发者及其操作记录，将数据集合并")
# nameList = pd.read_csv('../../dataset/statics.csv')['Name'].values.tolist()
# for name in nameList:
#     re = RemoveNoise(name)
#     re.remove_merger_low_counts()
#     re.remove_noise_of_merge_memory()
#     re.merge_merger_and_memory()
#     re.remove_reviewer_low_counts()
#     re.remove_noise_of_review_memory()
#     re.merge_reviewer_and_memory()

# JSON->toCSV->reactReview
# TextCleaner->
# afterTextClean->LabelTrans
# afterLabelClean->timeTrans
# afterTimeClean->removeMerger
# afterRemoveClean->pathCharge
