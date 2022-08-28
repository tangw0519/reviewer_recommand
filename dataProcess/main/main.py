import pandas as pd

# JSON->toCSV->reactReview
# TextCleaner->
# afterTextClean->LabelTrans
# afterLabelClean->timeTrans
# afterTimeClean->removeMerger
# afterRemoveClean->pathCharge
from dataProcess.removeNoise.pathCharge import PathCharge
from dataProcess.removeNoise.removeNoise import RemoveNoise
from dataProcess.textData.TextCleaner import TextCleaner
from dataProcess.textData.labelTrans import LabelTrans
from dataProcess.textData.timeTrans import TimeTrans
from dataProcess.textData.toCSV import DataSetTrans

nameList = pd.read_csv('../../dataset/statics.csv')['Name'].values.tolist()


def tocsv():
    print("当前操作：将json数据转换成csv（其中code已经被处理）")
    for name in nameList:
        print(name)
        data = DataSetTrans(name)
        data.csvMergeSave()
        data.csvReviewSave()


def text():
    print("当前操作：处理title，commit_message,body")
    for name in nameList:
        data = TextCleaner(name, 'merge')
        data.cleanMessage()
        data = TextCleaner(name, 'review')
        data.cleanMessage()


def label():
    print("当前操作：将标签字符串转变为数字")
    for name in nameList:
        data = LabelTrans(name, 'merge')
        data.cleanLabel()
        data = LabelTrans(name, 'review')
        data.cleanLabel()


def time():
    print("当前操作：将时间按照时间窗格变成01表示")
    for name in nameList:
        print(name, '----------------time clean strat----------------------')
        v = TimeTrans(name, "merge")
        v.timeClean()
        v = TimeTrans(name, "review")
        v.timeClean()
        print(name, '----------------time clean over----------------------')


def remove():
    print("当前操作：去除操作次数过少的开发者及其操作记录，将数据集合并")
    for name in nameList:
        re = RemoveNoise(name)
        re.remove_merger_low_counts()
        re.remove_noise_of_merge_memory()
        re.merge_merger_and_memory()
        re.remove_reviewer_low_counts()
        re.remove_noise_of_review_memory()
        re.merge_reviewer_and_memory()


def path():
    print("当前操作：处理path_name")
    p = PathCharge('merge')
    p.charge_path()
    p = PathCharge('review')
    p.charge_path()


# tocsv()
# text()
# label()
# time()
# remove()
# path()
