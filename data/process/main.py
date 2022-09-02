import json
import math
import os

import pandas as pd

from utils import *


class Dataset:
    def __init__(self, name, start='', end=''):
        self.name = name
        default_start, default_end = get_default_time(self.name)
        self.start = start or default_start
        self.end = end or default_end
        self.path = '../../resource/%s/%sFilterPrData.json' % (self.name, self.name)
        self.new_path = '../%s/' % self.name
        if not os.path.exists(self.new_path):
            os.makedirs(self.new_path)

    def is_range(self, t):
        t = get_unix(t)
        start = get_unix(self.start)
        end = get_unix(self.end)
        if start <= t <= end:
            return True
        else:
            return False

    # pr-review
    def get_pr_reviewer_weight(self, namuda, review_arr):
        mu = get_unix_distance(self.start, self.end)
        arr = []
        for review in review_arr:
            reviewer = review['reviewer']
            this_reviewer_arr = [x for x in review_arr if x['reviewer'] == reviewer]  # 找出当前
            review_arr = [x for x in review_arr if x['reviewer'] != reviewer]  # 去除当前
            j = len(this_reviewer_arr)
            weight = 0
            for reviewer in this_reviewer_arr:
                zi = abs(get_unix_distance(self.end, reviewer['review_time']))
                weight += math.pow(namuda, j - 1) * math.exp(zi / mu)
            arr.append({'pr': review['pr'], 'reviewer': review['reviewer'], 'weight': weight})
        arr = [x for x in arr if x['weight'] != 0]
        return arr

    def get_pr_reviewer_edges(self, namuda):
        with open(self.path, 'r') as f:
            prs = json.load(f)
        edge_path = self.new_path + 'pr_reviewer_edge.csv'
        if os.path.exists(edge_path):
            os.remove(edge_path)
        df = pd.DataFrame()
        pr_csv = []
        user_csv = []
        weight_csv = []
        for pr in prs:
            if self.is_range(pr['created_at']) and 'reviewData' in pr:
                review_arr = []
                for review in pr['reviewData']:
                    review_arr.append({'pr': pr['number'], 'reviewer': review['review_comment_creator'],
                                       'review_time': review['created_at']})
                review_arr = self.get_pr_reviewer_weight(namuda, review_arr)
                for edge in review_arr:
                    pr_csv.append(edge['pr'])
                    user_csv.append(edge['reviewer'])
                    weight_csv.append(edge['weight'])
        df['pr'] = pr_csv
        df['reviewer'] = user_csv
        df['weight'] = weight_csv
        df.to_csv(edge_path, columns=['pr', 'reviewer', 'weight'], index=False, header=True,
                  sep=',')

    # pr-commit
    def get_pr_committer_weight(self, r_time):
        dis1 = get_unix_distance(self.start, self.end)
        dis2 = get_unix_distance(self.start, r_time)
        return dis2 / dis1

    def get_pr_committer_edges(self):
        with open(self.path, 'r') as f:
            prs = json.load(f)
        edge_path = self.new_path + 'pr_committer_edge.csv'
        if os.path.exists(edge_path):
            os.remove(edge_path)
        df = pd.DataFrame()
        pr_csv = []
        user_csv = []
        weight_csv = []
        for pr in prs:
            if self.is_range(pr['created_at']) and 'commitData' in pr:
                arr = []
                for commit in pr['commitData']:
                    weight = self.get_pr_committer_weight(commit['commit_author_date'])
                    arr.append({'pr': pr['number'], 'committer': commit['commit_author_name'], 'weight': weight})
                arr = delete_same_commit(arr)
                for edge in arr:
                    pr_csv.append(edge['pr'])
                    user_csv.append(edge['committer'])
                    weight_csv.append(edge['weight'])
        df['pr'] = pr_csv
        df['committer'] = user_csv
        df['weight'] = weight_csv
        df.to_csv(edge_path, columns=['pr', 'committer', 'weight'], index=False, header=True,
                          sep=',')

    # pr-comment
    def get_pr_commenter_weight(self, namuda, comment_arr):
        mu = get_unix_distance(self.start, self.end)
        arr = []
        for comment in comment_arr:
            commenter = comment['commenter']
            this_commenter_arr = [x for x in comment_arr if x['commenter'] == commenter]  # 找出当前
            comment_arr = [x for x in comment_arr if x['commenter'] != commenter]  # 去除当前
            j = len(this_commenter_arr)
            weight = 0
            for commenter in this_commenter_arr:
                zi = abs(get_unix_distance(self.end, commenter['comment_time']))
                weight += math.pow(namuda, j - 1) * math.exp(zi / mu)
            arr.append({'pr': comment['pr'], 'commenter': comment['commenter'], 'weight': weight})
        arr = [x for x in arr if x['weight'] != 0]
        return arr

    def get_pr_commenter_edges(self, namuda):
        with open(self.path, 'r') as f:
            prs = json.load(f)
        edge_path = self.new_path + 'pr_commenter_edge.csv'
        if os.path.exists(edge_path):
            os.remove(edge_path)
        df = pd.DataFrame()
        pr_csv = []
        user_csv = []
        weight_csv = []

        for pr in prs:
            if self.is_range(pr['created_at']) and 'commentData' in pr:
                comment_arr = []
                for comment in pr['commentData']:
                    comment_arr.append({'pr': pr['number'], 'commenter': comment['comment_creator'],
                                        'comment_time': comment['created_at']})
                comment_arr = self.get_pr_commenter_weight(namuda, comment_arr)
                for edge in comment_arr:
                    pr_csv.append(edge['pr'])
                    user_csv.append(edge['commenter'])
                    weight_csv.append(edge['weight'])
        df['pr'] = pr_csv
        df['commenter'] = user_csv
        df['weight'] = weight_csv
        df.to_csv(edge_path, columns=['pr', 'commenter', 'weight'], index=False, header=True,
                          sep=',')

    # pr-pr
    def get_pr_pr_weight(self, pr1, pr2):
        if 'files_detail' in pr1 and 'files_detail' in pr2:
            path1 = []
            path2 = []
            for f in pr1['files_detail']:
                path1.append(f['filename'])
            for f in pr2['files_detail']:
                path2.append(f['filename'])
            weight = 0
            t1 = pr1['created_at']
            t2 = pr2['created_at']
            zi = abs(get_unix_distance(t1, t2))
            mu = get_unix_distance(self.start, self.end)
            for f1 in path1:
                for f2 in path2:
                    weight += (get_similarity(f1, f2) / (len(path1) * len(path2))) * math.exp(-(zi / mu))
            return weight
        else:
            return 0

    def get_pr_pr_edges(self, top_m):
        with open(self.path, 'r') as f:
            prs = json.load(f)
        edge_path = self.new_path + 'pr_pr_edge.csv'
        if os.path.exists(edge_path):
            os.remove(edge_path)
        df = pd.DataFrame()
        pr1_csv = []
        pr2_csv = []
        weight_csv = []
        for pr1 in prs:
            if self.is_range(pr1['created_at']) and 'files_detail' in pr1:
                print(pr1['created_at'])
                neighbour = []
                for pr2 in prs:
                    if pr2['number'] != pr1['number'] and self.is_range(pr2['created_at']) and 'files_detail' in pr2:
                        weight = self.get_pr_pr_weight(pr1, pr2)
                        neighbour.append({'pr1': pr1['number'], 'pr2': pr2['number'], 'weight': weight})
                neighbour = sorted(neighbour, key=lambda pr: pr['weight'], reverse=True)[0:top_m]
                for edge in neighbour:
                    pr1_csv.append(edge['pr1'])
                    pr2_csv.append(edge['pr2'])
                    weight_csv.append(edge['weight'])
        df['pr1'] = pr1_csv
        df['pr2'] = pr2_csv
        df['weight'] = weight_csv
        df.to_csv(edge_path, columns=['pr1', 'pr2', 'weight'], index=False, header=True,
                          sep=',')


d = Dataset('bitcoin', '2017-01-01T00:00:00Z', '2020-06-30T00:00:00Z')
d.get_pr_reviewer_edges(0.5)
d.get_pr_committer_edges()
d.get_pr_commenter_edges(0.5)
# d.get_pr_pr_edges(5)
