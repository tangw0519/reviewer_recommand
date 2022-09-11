import os

import numpy as np
import pandas as pd

from utils import *


class Loss:
    def __init__(self, name, start='', end=''):
        self.name = name
        default_start, default_end = get_default_time(self.name)
        self.start = start or default_start
        self.end = end or default_end
        print(f'当前项目：{self.name}')
        print(f'当前时间范围：{self.start} ~ {self.end}')
        self.filename_prefix = start.split('T')[0]
        self.filename_suffix = end.split('T')[0]
        self.path = '../../resource/%s/%sFilterPrData.json' % (self.name, self.name)
        self.new_path = f'../{self.name}/loss/{self.filename_prefix}-to-{self.filename_suffix}/'
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

    def get_num_classes(self):
        with open(self.path, 'r') as f:
            prs = json.load(f)
        reviewer = []
        for pr in prs:
            if self.is_range(pr['created_at']) and 'reviewData' in pr and len(pr['reviewData']) != 0:
                for review in pr['reviewData']:
                    if review['review_comment_creator'] not in reviewer:
                        reviewer.append(review['review_comment_creator'])
        print(f'{self.name}共有{len(set(reviewer))}个reviewer')
        return reviewer

    def get_all_reviewer_active_counts(self, month=3):
        print(f'当前操作：获取{self.name}的reviewer活跃时间及次数')
        time_path = self.new_path + f'reviewer_time_count_{month}.csv'
        reviewers = self.get_num_classes()
        time_ranges = get_time_split(month)
        reviewer_time_count = {}
        for review in reviewers:
            reviewer_time_count[review] = [0] * len(time_ranges)

        with open(self.path, 'r') as f:
            prs = json.load(f)

        for k in range(len(time_ranges)):
            for pr in prs:
                if is_range_self(time_ranges[k][0], pr['created_at'], time_ranges[k][1]) and 'reviewData' in pr and len(
                        pr['reviewData']) != 0:
                    for reviews in pr['reviewData']:
                        reviewer_time_count[reviews['review_comment_creator']][k] += 1
        if os.path.exists(time_path):
            os.remove(time_path)
        df = pd.DataFrame(reviewer_time_count)
        df.to_csv(time_path, index=False, sep=',')
        return reviewer_time_count

    def get_loss(self, month=1):
        path = self.new_path + f'reviewer_time_count_{month}.csv'
        if not os.path.exists(path):
            self.get_all_reviewer_active_counts(month)
        time_ranges = get_time_split(month)
        df = pd.read_csv(path)
        reviewers = np.array(df.columns)
        content = np.array(df)
        for i in range(1, len(content)):
            content[i] = content[i] + content[i - 1]

        print(f'当前操作：获取{self.name}的time_active')
        with open(self.path, 'r') as f:
            prs = json.load(f)
        features_path = self.new_path + f'pr_active_{month}.csv'

        contents = []
        for pr in prs:
            if self.is_range(pr['created_at']) and 'reviewData' in pr and len(pr['reviewData']) != 0:
                for i in range(len(time_ranges)):
                    if is_range_self(time_ranges[i][0], pr['created_at'], time_ranges[i][1]):
                        row = [pr['number']]
                        row.extend(content[i])
                        contents.append(row)
        if os.path.exists(features_path):
            os.remove(features_path)
        df = pd.DataFrame(contents)
        df.to_csv(features_path, index=False, header=False,
                  sep=',')

        reviewer_index_path = self.new_path + 'reviewer_index.csv'
        if os.path.exists(reviewer_index_path):
            os.remove(reviewer_index_path)
        df = pd.DataFrame(reviewers)
        df.to_csv(reviewer_index_path, index=False, header=False,
                  sep=',')

        return time_ranges, reviewers, content


# m = Loss('bitcoin', '2017-01-01T00:00:00Z', '2020-06-30T00:00:00Z')
# m.get_loss(month=1)
