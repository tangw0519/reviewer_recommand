import json
import math
import os
import shutil
from data.process.get_edge import Edge
from utils import *


class MetaPath:
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
        self.new_path = f'../{self.name}/metapath/{self.filename_prefix}-to-{self.filename_suffix}/'
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

    def is_time_before_pr1(self, t, t_end):
        t = get_unix(t)
        start = get_unix(self.start)
        end = get_unix(t_end)
        if start <= t <= end:
            return True
        else:
            return False

    def get_pr_commit_pr_weight(self, pr1, pr2):
        committer1 = []
        committer2 = []
        for commit in pr1['commitData']:
            committer1.append(commit['commit_author_name'])
        for commit in pr2['commitData']:
            committer2.append(commit['commit_author_name'])
        t1 = pr1['created_at']
        t2 = pr2['created_at']
        zi = abs(get_unix_distance(t2, t1))
        mu = get_unix_distance(self.start, self.end)
        weight = get_similarity_user(committer1, committer2) * math.exp(-(zi / mu))
        return weight

    def get_pr_commit_pr(self, top_m):
        print(f'当前操作：获取在commit方面相关的前{top_m}条pr连边')
        with open(self.path, 'r') as f:
            prs = json.load(f)
        edge_path = self.new_path + 'pr_commit_pr_edge.csv'
        if os.path.exists(edge_path):
            os.remove(edge_path)
        df = pd.DataFrame()
        pr1_csv = []
        pr2_csv = []
        weight_csv = []
        for pr1 in prs:
            if self.is_range(pr1['created_at']) and 'reviewData' in pr1 and 'commitData' in pr1 and len(
                    pr1['reviewData']) != 0:
                print(pr1['created_at'])
                neighbour = []
                for pr2 in prs:
                    if pr2['number'] != pr1['number'] and self.is_time_before_pr1(
                            pr2['created_at'],
                            pr1['created_at']) and 'commitData' in pr2 and 'reviewData' in pr2 and len(
                        pr2['reviewData']) != 0:
                        weight = self.get_pr_commit_pr_weight(pr1, pr2)
                        neighbour.append({'pr1': pr1['number'], 'pr2': pr2['number'], 'weight': weight})
                neighbour = sorted(neighbour, key=lambda pr: pr['weight'], reverse=True)[0:top_m]
                for edge in neighbour:
                    if edge['weight'] > 0:
                        pr1_csv.append(edge['pr1'])
                        pr2_csv.append(edge['pr2'])
                        weight_csv.append(edge['weight'])
        df['pr1'] = pr1_csv
        df['pr2'] = pr2_csv
        df['weight'] = weight_csv
        df.to_csv(edge_path, columns=['pr1', 'pr2', 'weight'], index=False, header=True,
                  sep=',')

    def get_pr_path_pr(self):
        edge_path = self.new_path + 'pr_path_pr_edge.csv'
        if os.path.exists(edge_path):
            os.remove(edge_path)
        old_path = f'../{self.name}/edge/{self.filename_prefix}-to-{self.filename_suffix}/pr_pr_edge.csv'
        if os.path.exists(old_path):
            shutil.copyfile(old_path, edge_path)
        else:
            d = Edge(self.name, self.start, self.end)
            d.get_pr_pr_edges()
            shutil.copyfile(old_path, edge_path)

    def get_pr_review_pr_weight(self, pr1, pr2):
        reviewer1 = []
        reviewer2 = []
        for review in pr1['reviewData']:
            reviewer1.append(review['review_comment_creator'])
        for review in pr2['reviewData']:
            reviewer2.append(review['review_comment_creator'])
        t1 = pr1['created_at']
        t2 = pr2['created_at']
        zi = abs(get_unix_distance(t2, t1))
        mu = get_unix_distance(self.start, self.end)
        weight = get_similarity_user(reviewer1, reviewer2) * math.exp(-(zi / mu))
        return weight

    def get_pr_review_pr(self, top_m):
        print(f'当前操作：获取在review方面相关的前{top_m}条pr连边')
        with open(self.path, 'r') as f:
            prs = json.load(f)
        edge_path = self.new_path + 'pr_review_pr_edge.csv'
        if os.path.exists(edge_path):
            os.remove(edge_path)
        df = pd.DataFrame()
        pr1_csv = []
        pr2_csv = []
        weight_csv = []
        for pr1 in prs:
            if self.is_range(pr1['created_at']) and 'reviewData' in pr1 and len(pr1['reviewData']) != 0:
                print(pr1['created_at'])
                neighbour = []
                for pr2 in prs:
                    if pr2['number'] != pr1['number'] and self.is_time_before_pr1(
                            pr2['created_at'], pr1['created_at']) and 'reviewData' in pr2 and len(
                        pr2['reviewData']) != 0:
                        weight = self.get_pr_review_pr_weight(pr1, pr2)
                        neighbour.append({'pr1': pr1['number'], 'pr2': pr2['number'], 'weight': weight})
                neighbour = sorted(neighbour, key=lambda pr: pr['weight'], reverse=True)[0:top_m]
                for edge in neighbour:
                    if edge['weight'] > 0:
                        pr1_csv.append(edge['pr1'])
                        pr2_csv.append(edge['pr2'])
                        weight_csv.append(edge['weight'])
        df['pr1'] = pr1_csv
        df['pr2'] = pr2_csv
        df['weight'] = weight_csv
        df.to_csv(edge_path, columns=['pr1', 'pr2', 'weight'], index=False, header=True,
                  sep=',')

    def get_pr_label_pr_weight(self, pr1, pr2):
        if len(pr1['labels']) > 0 and len(pr2['labels']) > 0:
            labels1 = pr1['labels']
            labels2 = pr2['labels']
            t1 = pr1['created_at']
            t2 = pr2['created_at']
            zi = abs(get_unix_distance(t2, t1))
            mu = get_unix_distance(self.start, self.end)
            weight = get_similarity_user(labels1, labels2) * math.exp(-(zi / mu))
            return weight
        else:
            return 0

    def get_pr_label_pr(self, top_m):
        print(f'当前操作：获取在label方面相关的前{top_m}条pr连边')
        with open(self.path, 'r') as f:
            prs = json.load(f)
        edge_path = self.new_path + 'pr_label_pr_edge.csv'
        if os.path.exists(edge_path):
            os.remove(edge_path)
        df = pd.DataFrame()
        pr1_csv = []
        pr2_csv = []
        weight_csv = []
        for pr1 in prs:
            if self.is_range(pr1['created_at']) and 'reviewData' in pr1 and len(pr1['reviewData']) != 0:
                print(pr1['created_at'])
                neighbour = []
                for pr2 in prs:
                    if pr2['number'] != pr1['number'] and self.is_time_before_pr1(pr2['created_at'], pr1['created_at']) \
                            and 'reviewData' in pr2 and len(pr2['reviewData']) != 0:
                        weight = self.get_pr_label_pr_weight(pr1, pr2)
                        neighbour.append({'pr1': pr1['number'], 'pr2': pr2['number'], 'weight': weight})
                neighbour = sorted(neighbour, key=lambda pr: pr['weight'], reverse=True)[0:top_m]
                for edge in neighbour:
                    if edge['weight'] > 0:
                        pr1_csv.append(edge['pr1'])
                        pr2_csv.append(edge['pr2'])
                        weight_csv.append(edge['weight'])
        df['pr1'] = pr1_csv
        df['pr2'] = pr2_csv
        df['weight'] = weight_csv
        df.to_csv(edge_path, columns=['pr1', 'pr2', 'weight'], index=False, header=True,
                  sep=',')

    def get_pr_comment_pr_weight(self, pr1, pr2):
        commenter1 = []
        commenter2 = []
        for comment in pr1['commentData']:
            commenter1.append(comment['comment_creator'])
        for comment in pr2['commentData']:
            commenter2.append(comment['comment_creator'])
        t1 = pr1['created_at']
        t2 = pr2['created_at']
        zi = abs(get_unix_distance(t2, t1))
        mu = get_unix_distance(self.start, self.end)
        weight = get_similarity_user(commenter1, commenter2) * math.exp(-(zi / mu))
        return weight

    def get_pr_comment_pr(self, top_m):
        print(f'当前操作：获取在comment方面相关的前{top_m}条pr连边')
        with open(self.path, 'r') as f:
            prs = json.load(f)
        edge_path = self.new_path + 'pr_comment_pr_edge.csv'
        if os.path.exists(edge_path):
            os.remove(edge_path)
        df = pd.DataFrame()
        pr1_csv = []
        pr2_csv = []
        weight_csv = []
        for pr1 in prs:
            if self.is_range(pr1['created_at']) and 'reviewData' in pr1 and len(pr1['reviewData']) != 0 and \
                    'commentData' in pr1 and len(pr1['commentData']) != 0:
                print(pr1['created_at'])
                neighbour = []
                for pr2 in prs:
                    if pr2['number'] != pr1['number'] and self.is_time_before_pr1(pr2['created_at'], pr1['created_at']) \
                            and 'reviewData' in pr2 and len(pr2['reviewData']) != 0 and 'commentData' in pr1 and len(pr1['commentData']) != 0:
                        weight = self.get_pr_comment_pr_weight(pr1, pr2)
                        neighbour.append({'pr1': pr1['number'], 'pr2': pr2['number'], 'weight': weight})
                neighbour = sorted(neighbour, key=lambda pr: pr['weight'], reverse=True)[0:top_m]
                for edge in neighbour:
                    if edge['weight'] > 0:
                        pr1_csv.append(edge['pr1'])
                        pr2_csv.append(edge['pr2'])
                        weight_csv.append(edge['weight'])
        df['pr1'] = pr1_csv
        df['pr2'] = pr2_csv
        df['weight'] = weight_csv
        df.to_csv(edge_path, columns=['pr1', 'pr2', 'weight'], index=False, header=True,
                  sep=',')
