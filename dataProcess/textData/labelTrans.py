import json
import os

import numpy as np
import pandas as pd
from pandas import DataFrame

from dataProcess.textData.TextCleaner import TextCleaner


class LabelTrans:
    def __init__(self, name, relation):
        self.name = name
        self.relation = relation

    def labelToIndex(self, label):
        df = pd.read_csv("../../dataset/%s/label.csv" % self.name)
        a = df[df.labelName == label].index.tolist()
        return a[0]

    def cleanLabel(self):
        print(self.name,'-------------start-----------------')
        if not os.path.exists("../../dataset/%s/%s/afterTextClean.csv" % (self.name, self.relation)):
            text = TextCleaner(self.name, self.relation)
            text.cleanMessage()
        df1 = pd.read_csv("../../dataset/%s/%s/afterTextClean.csv" % (self.name, self.relation))
        length = 0
        for i in range(len(df1)):
            if length < len(df1["label"][i].split(",")):
                length = len(df1["label"][i].split(","))
        arrayLabel = []
        for i in range(len(df1)):
            arr = [0] * length
            k = 0
            for text in df1["label"][i].split(","):
                arr[k] = self.labelToIndex(text)
                k += 1
            arrayLabel.append(arr)
        df1["label"] = arrayLabel
        df1.to_csv("../../dataset/%s/%s/afterLabelClean.csv" % (self.name, self.relation), header=True, index=False)
        print(self.name, '-------------end-----------------')


# print("当前操作：将标签字符串转变为数字")
# with open("../../resource/repos/repos.json", 'r') as load_f:
#     repos = json.load(load_f)
# for x in repos[0:]:
#     data = LabelTrans(x["name"], 'merge')
#     data.cleanLabel()
#     data = LabelTrans(x["name"], 'review')
#     data.cleanLabel()

# JSON->toCSV->reactReview
# TextCleaner->
# afterTextClean->LabelTrans
# afterLabelClean->timeTrans
# afterTimeClean->removeMerger
# afterRemoveClean->pathCharge
