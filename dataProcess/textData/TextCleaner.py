import json

import pandas as pd
import re
from keras.preprocessing.text import Tokenizer
from keras_preprocessing.sequence import pad_sequences
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords


def openFile(path):
    with open(path, 'r') as load_f:
        load_dict = json.load(load_f)
    return load_dict


# 英文缩写替换
def replace_abbreviations(text):
    pattern = r"[^\s]*\.(com|org|net)\S*"
    text = re.sub(pattern, '', text)
    text = text.lower().replace("it's", "it is").replace("i'm", "i am").replace("he's", "he is").replace(
        "she's",
        "she is") \
        .replace("we're", "we are").replace("they're", "they are").replace("you're", "you are").replace(
        "that's",
        "that is") \
        .replace("this's", "this is").replace("can't", "can not").replace("don't", "do not").replace("doesn't",
                                                                                                     "does not") \
        .replace("we've", "we have").replace("i've", " i have").replace("isn't", "is not").replace("won't",
                                                                                                   "will not") \
        .replace("hasn't", "has not").replace("wasn't", "was not").replace("weren't", "were not").replace(
        "let's",
        "let us") \
        .replace("didn't", "did not").replace("hadn't", "had not").replace("waht's", "what is").replace(
        "couldn't",
        "could not") \
        .replace("you'll", "you will").replace("you've", "you have")

    text = text.replace("'s", "").replace("\n", "").replace("\t", "").replace("<br /><br />", "").replace("- x ",
                                                                                                          "").replace(
        'num', "").replace(
        "- ", "").replace(" xxxx ", "").replace("--", "")
    return text


# 删除标点符号及其它字符
def clear_review(text):
    text = re.sub('([a-zA-Z])\\.([a-zA-Z])\\.*', '\\1\\2', text)
    text = re.sub('\\d+', '', text)
    text = re.sub('[^a-zA-Z0-9\\s_-]', ' ', text)
    return text


# 删除停用词　＋　词形还原
def stemed_words(text):
    stop_words = set(stopwords.words('english'))
    filtered_sentence = []
    text = word_tokenize(text)
    for w in text:
        if w not in stop_words:
            filtered_sentence.append(w)
    lemma = WordNetLemmatizer()
    texts = []
    for item in filtered_sentence:
        word1 = lemma.lemmatize(item, pos="n")
        word2 = lemma.lemmatize(word1, pos="v")
        word3 = lemma.lemmatize(word2, pos="a")
        if word3 != '':
            texts.append(word3)
    return texts


# 文本预处理
def preprocess(text):
    text1 = replace_abbreviations(text)
    text2 = clear_review(text1)
    text3 = stemed_words(text2)
    line = ""
    for word in text3:
        line += word + " "
    line = line.strip()
    if line == '':
        line = 'none'
    return line



class TextCleaner:
    def __init__(self, name, relation):
        self.name = name
        self.relation = relation

    def getAllData(self):
        path = '../../dataset/%s/%s/%s%s.csv' % (self.name, self.relation, self.name, self.relation.capitalize())
        dt = pd.read_csv(path)
        return dt

    # 获取某段时间内数据
    def getDataBetweenTime(self, startTime, endTime):
        Data = self.getAllData()
        if self.relation == 'merge':
            Data = Data[(startTime <= Data['create_time']) & (Data['create_time'] <= endTime)]
        else:
            Data = Data[(startTime <= Data['review_created_time']) & (Data['review_created_time'] <= endTime)]
        print(len(Data))
        return Data

    def developerToIndex(self, name):
        path = '../../dataset/%s/developer.csv' % self.name
        developer = pd.read_csv(path)['name']
        dev = []
        for d in developer:
            dev.append(d)
        return dev.index(name)

    def cleanMessage(self):
        print(self.name,'-------------strat----------------')
        df = self.getAllData()
        path = '../../dataset/%s/%s/afterTextClean.csv' % (self.name, self.relation)
        df['title'] = df['title'].apply(preprocess)
        df['body'] = df['body'].apply(preprocess)
        df['commit_message'] = df['commit_message'].apply(preprocess)
        df.to_csv(path, header=True, index=False)
        print(self.name, '-------------end----------------')


# repos = openFile("../../resource/repos/repos.json")
# for x in repos[0:]:
#     data = TextCleaner(x["name"], 'merge')
#     data.cleanMessage()
#     data = TextCleaner(x["name"], 'review')
#     data.cleanMessage()

# JSON->toCSV->reactReview
# TextCleaner->
# afterTextClean->LabelTrans
# afterLabelClean->timeTrans
# afterTimeClean->removeMerger
# afterRemoveClean->pathCharge