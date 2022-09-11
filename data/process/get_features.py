import os

import numpy as np

from utils import *
from keras.preprocessing.text import Tokenizer


class Features:
    def __init__(self, name, start='', end='', month=1):
        self.name = name
        default_start, default_end = get_default_time(self.name)
        self.start = start or default_start
        self.end = end or default_end
        self.path = '../../resource/%s/%sFilterPrData.json' % (self.name, self.name)
        self.new_path = '../%s/features/' % self.name
        self.month = month
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

    def get_pr_features(self):
        print(f'当前操作：获取{self.name}的features')
        with open(self.path, 'r') as f:
            prs = json.load(f)
        features_path = self.new_path + f'pr_features_{self.month}.csv'
        time_ranges = get_time_split(self.month)
        contents = []
        for pr in prs:
            if self.is_range(pr['created_at']) and 'reviewData' in pr and len(pr['reviewData']) != 0:
                row = [pr['number']]
                row.extend([0] * len(time_ranges))
                for i in range(len(time_ranges)):
                    if is_range_self(time_ranges[i][0], pr['created_at'], time_ranges[i][1]):
                        row[i] = 1
                if 'commitData' in pr and len(pr['commitData']) != 0:
                    row.append(len(pr['commitData']))
                else:
                    row.append(0)
                if 'changed_files' in pr:
                    row.append(pr['changed_files'])
                else:
                    row.append(0)
                if 'additions_lines' in pr:
                    row.append(pr['additions_lines'])
                else:
                    row.append(0)
                if 'deletions_lines' in pr:
                    row.append(pr['deletions_lines'])
                else:
                    row.append(0)
                contents.append(row)

        if os.path.exists(features_path):
            os.remove(features_path)
        df = pd.DataFrame(contents)
        df.to_csv(features_path, index=False, header=False,
                  sep=',')

    def get_num_classes(self):
        with open(self.path, 'r') as f:
            prs = json.load(f)
        reviewer = []
        for pr in prs:
            if self.is_range(pr['created_at']) and 'reviewData' in pr:
                for review in pr['reviewData']:
                    if review['review_comment_creator'] not in reviewer:
                        reviewer.append(review['review_comment_creator'])
        return reviewer

    def get_labels(self):
        print(f'当前操作：获取{self.name}的labels')
        classes = self.get_num_classes()
        with open(self.path, 'r') as f:
            prs = json.load(f)
        features_path = self.new_path + 'pr_labels.csv'
        contents = []
        for pr in prs:
            if self.is_range(pr['created_at']) and 'reviewData' in pr and len(pr['reviewData']) != 0:
                temp_arr = []
                for review in pr['reviewData']:
                    temp_arr.append(classes.index(review['review_comment_creator']))
                temp_arr = list(set(temp_arr))
                labels = [0] * len(classes)
                for index in temp_arr:
                    labels[index] = 1
                line = [pr['number']] + labels
                contents.append(line)
        if os.path.exists(features_path):
            os.remove(features_path)
        df = pd.DataFrame(contents)
        df.to_csv(features_path, index=False, header=False,
                  sep=',')

    def get_reviewer_features(self):
        print(f'当前操作：获取{self.name}的reviewer活跃时间及次数')
        time_path = self.new_path + f'reviewer_features_{self.month}.csv'
        reviewers = self.get_num_classes()
        time_ranges = get_time_split(self.month)
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

        committer_count = {}
        additions_lines = {}
        deletions_lines = {}
        changed_files = {}
        for pr in prs:
            if self.is_range(pr['created_at']) and 'reviewData' in pr and len(pr['reviewData']) != 0:
                if 'commitData' in pr['commitData']:
                    for commit in pr['commitData']:
                        committer_count[commit['commit_author_date']] += 1
                        deletions_lines[commit['commit_author_date']] += pr['deletions_lines']
                        additions_lines[commit['commit_author_date']] += pr['additions_lines']
                        changed_files[commit['commit_author_date']] += pr['changed_files']

        contents = []
        for name in reviewer_time_count:
            row = [reviewers.index(name)]
            row.extend(reviewer_time_count[name])
            if name in committer_count:
                row.append(committer_count[name])
            else:
                row.append(0)
            if name in changed_files:
                row.append(changed_files[name])
            else:
                row.append(0)
            if name in additions_lines:
                row.append(additions_lines[name])
            else:
                row.append(0)
            if name in deletions_lines:
                row.append(deletions_lines[name])
            else:
                row.append(0)
            contents.append(row)
        df = pd.DataFrame(contents)
        df.to_csv(time_path, index=False, sep=',', header=None)
        return reviewer_time_count


f = Features('bitcoin', '2017-01-01T00:00:00Z', '2020-06-30T00:00:00Z')
f.get_reviewer_features()
