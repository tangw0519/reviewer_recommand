import os

import numpy as np
import pandas as pd

from utils import *
from keras.preprocessing.text import Tokenizer


class Features:
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
        self.new_path = f'../{self.name}/features/{self.filename_prefix}-to-{self.filename_suffix}/'
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

    def get_text_dict(self, MAX_TITLE_WORDS=10000):
        with open(self.path, 'r') as f:
            prs = json.load(f)
        df = pd.DataFrame()
        title = []
        for pr in prs:
            if self.is_range(pr['created_at']) and 'reviewData' in pr and len(pr['reviewData']) != 0:
                pr['body'] = pr['body'] if pr['body'] is not None else ''
                if 'commitData' in pr and len(pr['commitData']) != 0:
                    commit_message = ''
                    for commit in pr['commitData']:
                        commit_message += commit['message']
                    text = preprocess(pr['title'] + ' ' + pr['body'] + ' ' + commit_message)
                else:
                    text = preprocess(pr['title'] + ' ' + pr['body'])
                # text = preprocess(pr['title'] + ' ' + pr['body'])
                title.append(text)
        df['title'] = title
        df['title'] = df['title'].fillna("")
        title_tokenizer = Tokenizer(num_words=MAX_TITLE_WORDS, filters='!"#$%&()*+,-./:;<=>?@[\]^_`{|}~', split=" ",
                                    lower=True)
        title_tokenizer.fit_on_texts(df['title'].values)
        word_index = title_tokenizer.word_index
        print('所选特征共有 %s 个不相同的词语.' % len(word_index))
        return title_tokenizer

    def get_pr_features(self, MAX_TITLE_LENGTH=500):
        print(f'当前操作：获取{self.name}的features')
        with open(self.path, 'r') as f:
            prs = json.load(f)
        features_path = self.new_path + 'pr_features.csv'
        if os.path.exists(features_path):
            os.remove(features_path)
        dicts = self.get_text_dict()
        contents = []
        for pr in prs:
            if self.is_range(pr['created_at']) and 'reviewData' in pr and len(pr['reviewData']) != 0:
                head = [pr['number']]
                pr['body'] = pr['body'] if pr['body'] is not None else ''
                # if 'commitData' in pr and len(pr['commitData']) != 0:
                #     commit_message = ''
                #     for commit in pr['commitData']:
                #         commit_message += commit['message']
                #     title = dicts.texts_to_sequences(pr['title'] + ' ' + commit_message)
                #     title = dicts.texts_to_sequences(commit_message)
                # else:
                #     title = dicts.texts_to_sequences(pr['title'])
                title = dicts.texts_to_sequences(pr['title'] + ' ' + pr['body'])

                title = [x[0] for x in title if len(x) != 0]
                if len(title) < MAX_TITLE_LENGTH:
                    title = title + [0] * (MAX_TITLE_LENGTH - len(title))
                else:
                    title = title[0:MAX_TITLE_LENGTH]
                head = head + title
                contents.append(head)
        df = pd.DataFrame(contents)
        df.to_csv(features_path, index=False, header=False,
                  sep=',')

    def get_num_classes(self):
        path = f'../{self.name}/loss/{self.filename_prefix}-to-{self.filename_suffix}/reviewer_index.csv'
        if os.path.exists(path):
            df = pd.read_csv(path,header=None)
            res = [x[0] for x in df.values.tolist()]
            return res
        else:
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

    def get_pr_labels(self):
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


