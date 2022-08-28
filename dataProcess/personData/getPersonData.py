import csv
import os
from datetime import datetime
import json
import pandas as pd
import time
import datetime
from dateutil.relativedelta import relativedelta


def openFile(path):
    with open(path, 'r') as load_f:
        load_dict = json.load(load_f)
    return load_dict


def saveFile(path, data):
    with open(path, 'w') as file_obj:
        json.dump(data, file_obj, indent=4)
        print('文件保存完成')


def trans_format(time_string, from_format, to_format='%Y.%m.%d %H:%M:%S'):
    time_struct = time.strptime(time_string, from_format)
    times = time.strftime(to_format, time_struct)
    return times


def date_range(start, end, m):
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


def times_count(data_list, month_list):
    ret = []
    # 初始化每月的次数为0
    for index in range(len(month_list)):
        ret.append(0)

    # 2021-09-30T15:08:28Z
    for item in data_list:
        cur = datetime.datetime.strptime(item, "%Y-%m-%dT%H:%M:%SZ").date()
        for i in range(len(month_list)):
            current_month = datetime.datetime.strptime(month_list[i], "%Y-%m").date()
            if cur < current_month:
                ret[i - 1] += 1
                break
            elif cur == current_month:
                ret[i] += 1
                break
    return ret


class PersonData:
    def __init__(self, name):
        self.name = name

    # project
    def getAllDeveloper(self):
        path = '../../resource/%s/%sFilterPrData.json' % (self.name, self.name)
        folder = os.path.exists('../../dataset/%s/%s' % (self.name, 'merge'))
        newPath = '../../dataset/%s/developer.csv' % self.name
        if not folder:
            os.makedirs('../../dataset/%s/%s' % (self.name, 'merge'))

        creator = []
        merger = []
        committer = []
        commenter = []
        reviewer = []
        files = openFile(path)
        for s in files:
            # pr
            creator.append(s['pr_creator_name'])
            # merge
            if s['merge']:
                if 'pr_mergedBy_user_name' in s:
                    merger.append(s['pr_mergedBy_user_name'])
            # commit
            if 'commitData' in s and len(s['commitData']) != 0:
                for commit in s['commitData']:
                    committer.append(commit['commit_author_name'])
            # comment
            if 'commentData' in s and len(s['commentData']) != 0:
                for comment in s['commentData']:
                    commenter.append(comment['comment_creator'])
            # review
            if 'reviewData' in s and len(s['reviewData']) != 0:
                for review in s['reviewData']:
                    reviewer.append(review['review_comment_creator'])

        # print('创建pr的开发者数量：' + str(len(list(set(creator)))))
        user = commenter + committer + reviewer + merger + creator
        user = list(set(user))
        print('参与到项目pr的开发者数量：' + str(len(user)))
        row = []
        for u in user:
            row.append([u])
        if os.path.exists(newPath):
            os.remove(newPath)
        with open(newPath, "a", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(
                ["name"])
            for r in row:
                writer.writerow(r)

    def getProjectActiveTime(self):
        print("当前操作：获取项目%s的时间信息" % self.name)
        path = '../../resource/repos/repos.json'
        load_dict = openFile(path)
        for p in load_dict:
            if p["name"] == self.name:
                firstTime = p["created_at"]
                lastTime = "2021-12-31T23:59:59Z"
        return firstTime.split("T")[0], lastTime.split("T")[0]

    # review
    def getReviewerActiveTime(self, developer):
        print("当前操作：获取项目%s的reviewer：%s审查时间信息" % (self.name, developer))
        path = '../../resource/%s/%sFilterPrData.json' % (self.name, self.name)
        load_dict = openFile(path)
        times = []
        for s in load_dict:
            if 'reviewData' in s and len(s['reviewData']) != 0:
                for review in s['reviewData']:
                    if review['review_comment_creator'] == developer:
                        times.append(review['created_at'])
        return times

    def JsonReviewerTimes(self):
        print("当前操作：获取项目%s的所有reviewer审查信息（审查次数，时间），将保存为json文件" % self.name)
        path = '../../resource/%s/%sFilterPrData.json' % (self.name, self.name)
        load_dict = openFile(path)
        reviewer = []
        count = []
        for s in load_dict:
            if 'reviewData' in s and len(s['reviewData']) != 0:
                for review in s['reviewData']:
                    if review['review_comment_creator'] not in reviewer:
                        reviewer.append(review['review_comment_creator'])
                        count.append(1)
                    else:
                        count[reviewer.index(review['review_comment_creator'])] += 1

        newPath = '../../dataset/%s/%sReviewer.json' % (self.name, self.name)
        row = []
        for i in range(len(reviewer)):
            new = {}
            new["name"] = reviewer[i]
            new["counts"] = count[i]
            new["times"] = self.getReviewerActiveTime(reviewer[i])
            row.append(new)
        with open(newPath, 'w') as file_obj:
            json.dump(row, file_obj, indent=4)
            print('数据保存完成')

    def review_times_count_all(self, m=3):
        print("当前操作：获取项目%s的所有reviewer时间信息" % self.name)
        start, end = self.getProjectActiveTime()
        if not os.path.exists('../../dataset/%s/%sReviewer.json' % (self.name, self.name)):
            self.JsonReviewerTimes()
        json_data = json.load(open('../../dataset/%s/%sReviewer.json' % (self.name, self.name), 'r'))
        ret = []
        months = date_range(start, end, m)
        for index in range(len(json_data)):
            user_count = {"name": json_data[index]["name"], "counts": json_data[index]["counts"], "xAxis": months,
                          "yAxis": times_count(json_data[index]["times"], months)}

            ret.append(user_count)
        newPath = '../../dataset/%s/%sReviewerGraphData.json' % (self.name, self.name)
        with open(newPath, 'w') as file_obj:
            json.dump(ret, file_obj, indent=4)
            print('数据保存完成')

    def getAllReviewData(self, timeGap=3):
        print("当前操作：获取项目%s的所有reviewer信息，包括时间信息" % self.name)
        path = '../../resource/%s/%sFilterPrData.json' % (self.name, self.name)
        load_dict = openFile(path)
        reviewer = []
        count = []
        author = []
        for s in load_dict:
            if 'reviewData' in s and len(s['reviewData']) != 0:
                for review in s['reviewData']:
                    if review['review_comment_creator'] not in reviewer:
                        reviewer.append(review['review_comment_creator'])
                        author.append(review['author_association'])
                        count.append(1)
                    else:
                        count[reviewer.index(review['review_comment_creator'])] += 1

        newPath = '../../dataset/%s/%sReviewer.csv' % (self.name, self.name)
        row = []
        for u in reviewer:
            row.append([u])
        if os.path.exists(newPath):
            os.remove(newPath)
        with open(newPath, "a", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["name"])
            for r in row:
                writer.writerow(r)
        df = pd.read_csv(newPath)
        df['count'] = count
        df['author'] = author
        df.to_csv(newPath, header=True, index=False, sep=',')
        df = pd.read_csv(newPath)

        if not os.path.exists('../../dataset/%s/%sReviewerGraphData.json' % (self.name, self.name)):
            self.review_times_count_all(timeGap)
        with open('../../dataset/%s/%sReviewerGraphData.json' % (self.name, self.name), 'r') as load_f:
            result = json.load(load_f)
        time_range = []
        for i in range(len(df)):
            for user in result:
                if user["name"] == df["name"][i]:
                    time_range.append(user['yAxis'])
        df['time_range'] = time_range
        df = df.sort_values(by="count", ascending=True)
        df.to_csv(newPath, header=True, index=False, sep=',')
        print('over')

    # merge
    def getMergerActiveTime(self, developer):
        print("当前操作：获取项目%s的Merger：%s合并时间信息" % (self.name, developer))
        path = '../../resource/%s/%sFilterPrData.json' % (self.name, self.name)
        load_dict = openFile(path)
        times = []
        for s in load_dict:
            if 'pr_mergedBy_user_name' in s and 'merged_at' in s:
                if s['pr_mergedBy_user_name'] == developer:
                    times.append(s['merged_at'])
        return times

    def JsonMergerTimes(self):
        print("当前操作：获取项目%s的所有Merger合并信息（审查次数，时间），将保存为json文件" % self.name)
        path = '../../resource/%s/%sFilterPrData.json' % (self.name, self.name)
        load_dict = openFile(path)
        merger = []
        count = []
        for s in load_dict:
            if 'pr_mergedBy_user_name' in s:
                if s['pr_mergedBy_user_name'] not in merger:
                    merger.append(s['pr_mergedBy_user_name'])
                    count.append(1)
                else:
                    count[merger.index(s['pr_mergedBy_user_name'])] += 1

        newPath = '../../dataset/%s/%sMerger.json' % (self.name, self.name)
        row = []
        for i in range(len(merger)):
            new = {}
            new["name"] = merger[i]
            new["counts"] = count[i]
            new["times"] = self.getMergerActiveTime(merger[i])
            row.append(new)
        with open(newPath, 'w') as file_obj:
            json.dump(row, file_obj, indent=4)
            print('数据保存完成')

    def merge_times_count_all(self, m=3):
        print("当前操作：获取项目%s的所有merger时间信息" % self.name)
        start, end = self.getProjectActiveTime()
        if not os.path.exists('../../dataset/%s/%sMerger.json' % (self.name, self.name)):
            self.JsonMergerTimes()
        json_data = json.load(open('../../dataset/%s/%sMerger.json' % (self.name, self.name), 'r'))
        ret = []
        months = date_range(start, end, m)
        for index in range(len(json_data)):
            user_count = {"name": json_data[index]["name"], "counts": json_data[index]["counts"], "xAxis": months,
                          "yAxis": times_count(json_data[index]["times"], months)}

            ret.append(user_count)
        newPath = '../../dataset/%s/%sMergerGraphData.json' % (self.name, self.name)
        with open(newPath, 'w') as file_obj:
            json.dump(ret, file_obj, indent=4)
            print('数据保存完成')

    def getAllMergerData(self, timeGap=3):
        path = '../../resource/%s/%sFilterPrData.json' % (self.name, self.name)
        load_dict = openFile(path)
        merger = []
        count = []
        for s in load_dict:
            if 'pr_mergedBy_user_name' in s:
                if s['pr_mergedBy_user_name'] not in merger:
                    merger.append(s['pr_mergedBy_user_name'])
                    count.append(1)
                else:
                    count[merger.index(s['pr_mergedBy_user_name'])] += 1
        row = []
        newPath = '../../dataset/%s/%sMerger.csv' % (self.name, self.name)

        for u in merger:
            row.append([u])
        if os.path.exists(newPath):
            os.remove(newPath)
        with open(newPath, "a", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["name"])
            for r in row:
                writer.writerow(r)

        df = pd.read_csv(newPath)
        df['count'] = count
        df = df.sort_values(by="count", ascending=True)
        df.to_csv(newPath, header=True, index=False, sep=',')

        df = pd.read_csv(newPath)
        df = df.sort_values(by="count", ascending=True)
        if not os.path.exists('../../dataset/%s/%sMergerGraphData.json' % (self.name, self.name)):
            self.merge_times_count_all(timeGap)
        with open('../../dataset/%s/%sMergerGraphData.json' % (self.name, self.name), 'r') as load_f:
            result = json.load(load_f)
        time_range = []
        for i in range(len(df)):
            for user in result:
                if user["name"] == df["name"][i]:
                    time_range.append(user['yAxis'])
        df['time_range'] = time_range
        df.to_csv(newPath, header=True, index=False, sep=',')


# arr = openFile('../../resource/repos/repos.json')
# for x in arr[0:]:
#     print(x["name"])
#     v = PersonData(x["name"])
#     v.getAllReviewData()

# v = PersonData('pandas')
# v.getAllReviewData()
