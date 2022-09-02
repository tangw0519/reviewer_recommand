import os
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

    def get_text_dict(self, MAX_TITLE_WORDS=3000):
        with open(self.path, 'r') as f:
            prs = json.load(f)
        df = pd.DataFrame()
        title = []
        for pr in prs:
            if self.is_range(pr['created_at']) and 'reviewData' in pr:
                text = preprocess(pr['title'])
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
            if self.is_range(pr['created_at']) and 'reviewData' in pr:
                for review in pr['reviewData']:
                    if review['review_comment_creator'] not in reviewer:
                        reviewer.append(review['review_comment_creator'])
        return reviewer

    def get_pr_features(self, MAX_TITLE_LENGTH=50):
        with open(self.path, 'r') as f:
            prs = json.load(f)
        features_path = self.new_path + 'pr_features.csv'
        if os.path.exists(features_path):
            os.remove(features_path)
        dicts = self.get_text_dict()
        classes = self.get_num_classes()
        contents = []
        for pr in prs:
            if self.is_range(pr['created_at']) and 'reviewData' in pr:
                head = [pr['number']]
                title = dicts.texts_to_sequences(pr['title'])
                title = [x[0] for x in title if len(x) != 0]
                if len(title) < MAX_TITLE_LENGTH:
                    title = title + [0] * (MAX_TITLE_LENGTH - len(title))
                else:
                    title = title[0:MAX_TITLE_LENGTH]
                head = head + title
                temp_arr = []
                for review in pr['reviewData']:
                    temp_arr.append(classes.index(review['review_comment_creator']))
                temp_arr = list(set(temp_arr))
                for label in temp_arr:
                    line = head + [label]
                    contents.append(line)
        df = pd.DataFrame(contents)
        df.to_csv(features_path, index=False, header=False,
                  sep=',')