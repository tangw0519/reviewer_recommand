import os

import pandas as pd

from utils import *
from keras.preprocessing.text import Tokenizer


class Features:
    def __init__(self, name, start='', end=''):
        self.name = name
        default_start, default_end = get_default_time(self.name)
        self.start = start or default_start
        self.end = end or default_end
        self.path = '../../resource/%s/%sFilterPrData.json' % (self.name, self.name)
        self.new_path = '../%s/features/' % self.name
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

    def get_text_dict(self, MAX_TITLE_WORDS=5000):
        with open(self.path, 'r') as f:
            prs = json.load(f)
        df = pd.DataFrame()
        title = []
        for pr in prs:
            if self.is_range(pr['created_at']) and 'reviewData' in pr and len(pr['reviewData']) !=0:
                text = preprocess(pr['title']+' '+pr['body'])
                title.append(text)
        df['title'] = title
        df['title'] = df['title'].fillna("")
        title_tokenizer = Tokenizer(num_words=MAX_TITLE_WORDS, filters='!"#$%&()*+,-./:;<=>?@[\]^_`{|}~', split=" ",
                                    lower=True)
        title_tokenizer.fit_on_texts(df['title'].values)
        word_index = title_tokenizer.word_index
        print('title共有 %s 个不相同的词语.' % len(word_index))
        return title_tokenizer

    def get_num_classes(self):
        with open(self.path, 'r') as f:
            prs = json.load(f)
        reviewer = []
        for pr in prs:
            if self.is_range(pr['created_at']) and 'reviewData' in pr and len(pr['reviewData']) !=0:
                for review in pr['reviewData']:
                    if review['review_comment_creator'] not in reviewer:
                        reviewer.append(review['review_comment_creator'])
        print(len(set(reviewer)))
        return reviewer

    def get_pr_features(self, MAX_TITLE_LENGTH=500):
        with open(self.path, 'r') as f:
            prs = json.load(f)
        features_path = self.new_path + 'pr_features.csv'
        if os.path.exists(features_path):
            os.remove(features_path)
        dicts = self.get_text_dict()
        contents = []
        for pr in prs:
            if self.is_range(pr['created_at']) and 'reviewData' in pr and len(pr['reviewData']) !=0:
                head = [pr['number']]
                title = dicts.texts_to_sequences(pr['title']+' '+pr['body'])
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

    def get_pr_labels(self):
        classes = self.get_num_classes()
        with open(self.path, 'r') as f:
            prs = json.load(f)
        features_path = self.new_path + 'pr_labels.csv'
        if os.path.exists(features_path):
            os.remove(features_path)
        contents = []
        for pr in prs:
            if self.is_range(pr['created_at']) and 'reviewData' in pr and len(pr['reviewData']) !=0:
                temp_arr = []
                for review in pr['reviewData']:
                    temp_arr.append(classes.index(review['review_comment_creator']))
                temp_arr = list(set(temp_arr))
                for label in temp_arr:
                    line = [pr['number']] + [label]
                    contents.append(line)
        df = pd.DataFrame(contents)
        df.to_csv(features_path, index=False, header=False,
                  sep=',')

    def get_num_classes_test(self):
        reviewer = []
        df = pd.read_csv('../../data/bitcoin/edge/pr_reviewer_edge.csv')
        for i in range(-1, len(df) - 1):
            if i + 1 == 0 or df['pr'][i] != df['pr'][i + 1]:
                reviewer.append(df['reviewer'][i + 1])
        reviewer = list(set(reviewer))
        return reviewer

    def get_pr_labels_test(self):
        classes = self.get_num_classes_test()
        labels_path=self.new_path + 'pr_labels_test.csv'
        df=pd.read_csv('../../data/bitcoin/edge/pr_reviewer_edge.csv')
        contents=[]
        for i in range(-1,len(df)-1):
            if i+1==0 or df['pr'][i]!=df['pr'][i+1]:
                contents.append([df['pr'][i+1],classes.index(df['reviewer'][i+1])])
        df = pd.DataFrame(contents)
        df.to_csv(labels_path, index=False, header=False,
                  sep=',')

    def get_nodes(self):
        df = pd.read_csv('../../data/bitcoin/edge/pr_reviewer_edge.csv')
        arr =[]
        for i in range(len(df)):
            arr.append(df['pr'][i])
        print(len(list(set(arr))))