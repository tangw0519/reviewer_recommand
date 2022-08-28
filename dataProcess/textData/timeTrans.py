import json
import os
from datetime import datetime
import json
import pandas as pd
import time
import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd

from dataProcess.textData.labelTrans import LabelTrans


def openFile(path):
    with open(path, 'r') as load_f:
        load_dict = json.load(load_f)
    return load_dict


def trans_format(time_string, from_format, to_format='%Y.%m.%d %H:%M:%S'):
    time_struct = time.strptime(time_string, from_format)
    times = time.strftime(to_format, time_struct)
    return times


class TimeTrans:
    def __init__(self, name, relation):
        self.name = name
        self.relation = relation

    def getProjectActiveTime(self):
        path = '../../resource/repos/repos.json'
        load_dict = openFile(path)
        for p in load_dict:
            if p["name"] == self.name:
                firstTime = p["created_at"]
                lastTime = "2021-12-31T23:59:59Z"
        return firstTime.split("T")[0], lastTime.split("T")[0]

    def date_range(self, m=3):
        start, end = self.getProjectActiveTime()
        ret = []
        right = datetime.datetime.strptime(end, "%Y-%m-%d").date()
        left = trans_format(start, '%Y-%m-%d', '%Y-%m')

        left = datetime.datetime.strptime(left, "%Y-%m").date()
        # right = datetime.datetime.strptime(right, "%Y-%m").date()
        while left < right:
            ret.append(left.strftime("%Y-%m"))
            left = left + relativedelta(months=m)
        ret.append(left.strftime("%Y-%m"))
        return ret

    def times_count(self, data, m=3):
        month_list = self.date_range(m)
        # ret = np.zeros(len(month_list), dtype=int)
        ret = [0] * len(month_list)

        cur = datetime.datetime.strptime(data, "%Y-%m-%dT%H:%M:%SZ").date()
        for i in range(len(month_list)):
            current_month = datetime.datetime.strptime(month_list[i], "%Y-%m").date()
            if cur < current_month:
                ret[i - 1] += 1
                break
            elif cur == current_month:
                ret[i] += 1
                break
        return ret

    def timeClean(self, m=3):
        if not os.path.exists('../../dataset/%s/%s/afterLabelClean.csv' % (self.name, self.relation)):
            label = LabelTrans(self.name, self.relation)
            label.cleanLabel()
        df = pd.read_csv('../../dataset/%s/%s/afterLabelClean.csv' % (self.name, self.relation))
        arrayTime = []
        for s in df['create_time']:
            arrayTime.append(self.times_count(s, m))
        df['create_time_range'] = arrayTime
        if self.relation == 'review':
            name = 'reviewer'
        else:
            name = 'merger'
        df.to_csv("../../dataset/%s/%s/afterTimeClean.csv" % (self.name, self.relation),
                  columns=["id", name, "create_time", 'create_time_range', "creator", "title",
                           "label", "commit_creator", "commit_message",
                           "path_name", "code", "body",
                           "additions_lines", "deletions_lines", "changed_files"],
                  header=True, index=False)

# print("当前操作：将时间按照时间窗格变成01表示")
# repos = openFile("../../resource/repos/repos.json")
# for x in repos:
#     print(x['name'])
#     v = TimeTrans(x["name"], "merge")
#     v.timeClean()
#     v = TimeTrans(x["name"], "review")
#     v.timeClean()

# JSON->toCSV->reactReview
# TextCleaner->
# afterTextClean->LabelTrans
# afterLabelClean->timeTrans
# afterTimeClean->removeMerger
# afterRemoveClean->pathCharge
