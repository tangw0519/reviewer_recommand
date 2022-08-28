import json
import os

import numpy as np
import pandas as pd

from dataProcess.personData.getPersonData import PersonData


def getTimeRange(x):
    x = x.replace('[', '').replace(']', '').replace(' ', '')
    arr = x.split(',')
    arr = np.array(arr, dtype=int)
    return arr


class PersonTrans:
    def __init__(self, name):
        self.name = name

    def addReviewInfo(self):
        path = '../../dataset/%s/developer.csv' % self.name
        reviewPath = '../../dataset/%s/%sReviewer.csv' % (self.name, self.name)
        if not os.path.exists(path):
            p = PersonData(self.name)
            p.getAllDeveloper()
        if not os.path.exists(reviewPath):
            p = PersonData(self.name)
            p.getAllReviewData()
        df = pd.read_csv(path)
        df1 = pd.read_csv(reviewPath)
        df['index'] = np.arange(len(df))
        df1['index'] = np.arange(len(df1))
        length = len(getTimeRange(df1['time_range'][0]))
        defaultTime = length * [0]
        isReviewer = []
        reviewActiveTime = []
        author = []
        authorDefault = 'NONE'
        for user in df['name']:
            if len(df1[df1.name == user].index.tolist()) != 0:
                isReviewer.append(1)
                df1Index = df1[df1.name == user].index.tolist()[0]
                reviewActiveTime.append(df1['time_range'][df1Index])
                author.append(df1['author'][df1Index])
            else:
                isReviewer.append(0)
                reviewActiveTime.append(defaultTime)
                author.append(authorDefault)
        df['author'] = author
        df['isReviewer'] = isReviewer
        df['review_time_range'] = reviewActiveTime
        df.to_csv(path, columns=['name', 'author', 'isReviewer', 'review_time_range'], index=False, header=True,
                  sep=',')

    def addMergeInfo(self):
        path = '../../dataset/%s/developer.csv' % self.name
        reviewPath = '../../dataset/%s/%sMerger.csv' % (self.name, self.name)
        if not os.path.exists(path):
            p = PersonData(self.name)
            p.getAllDeveloper()
        if not os.path.exists(reviewPath):
            p = PersonData(self.name)
            p.getAllMergerData()
        df = pd.read_csv(path)
        df1 = pd.read_csv(reviewPath)
        df['index'] = np.arange(len(df))
        df1['index'] = np.arange(len(df1))
        length = len(getTimeRange(df1['time_range'][0]))
        defaultTime = length * [0]
        isMerger = []
        mergerActiveTime = []

        for user in df['name']:
            if len(df1[df1.name == user].index.tolist()) != 0:
                isMerger.append(1)
                df1Index = df1[df1.name == user].index.tolist()[0]
                mergerActiveTime.append(df1['time_range'][df1Index])
            else:
                isMerger.append(0)
                mergerActiveTime.append(defaultTime)
        df['isMerger'] = isMerger
        df['merge_time_range'] = mergerActiveTime
        df.to_csv(path, columns=['name', 'author', 'isReviewer', 'isMerger', 'review_time_range', 'merge_time_range'],
                  index=False, header=True,
                  sep=',')

    def getAuthor(self, developer):
        oldPath = '../../resource/%s/%sPrData.json' % (self.name, self.name)
        path = '../../resource/%s/%sFilterPrData.json' % (self.name, self.name)
        with open(oldPath, 'r') as load_f:
            load_dict = json.load(load_f)
        with open(path, 'r') as load_f:
            load_filter = json.load(load_f)
        author = 'NONE'
        for s in load_dict:
            if s['user']['login'] == developer:
                author = s['author_association']
        if author == 'NONE':
            for s in load_filter:
                if 'commentData' in s:
                    for c in s['commentData']:
                        if developer == c['comment_creator']:
                            author = c['author_association']
        return author

    def changeAuthor(self):
        path = '../../dataset/%s/developer.csv' % self.name
        if not os.path.exists(path):
            p = PersonData(self.name)
            p.getAllDeveloper()
        df = pd.read_csv(path)
        author = []
        for i in range(len(df)):
            if df['author'][i] == 'NONE':
                author.append(self.getAuthor(df['name'][i]))
            else:
                author.append(df['author'][i])
        df['author'] = author
        df.to_csv(path)
        print("修改author数据成功")


def openFile(path):
    with open(path, 'r') as load_f:
        load_dict = json.load(load_f)
    return load_dict


repos = openFile("../../resource/repos/repos.json")
for x in repos[0:]:
    print(x)
    v = PersonTrans(x["name"])
    # v.addReviewInfo()
    # v.addMergeInfo()
    # v.changeAuthor()
