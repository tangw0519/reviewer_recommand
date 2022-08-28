import csv
import datetime
import json
import math
import os
import re

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords


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
        .replace("you'll", "you will").replace("you've", "you have").replace("- x ", "").replace('num', "").replace(
        "- ", "").replace(" xxxx ", "")

    text = text.replace("'s", "").replace("\n", "").replace("\t", "").replace("<br /><br />", "")
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


def code_preprocess(text):
    arr = text.split("\n")
    arr = [x for x in arr if x.startswith('+') or x.startswith('-')]
    arr = [x.lstrip("+").lstrip("-").lstrip() for x in arr]
    arr = [x for x in arr if x and x.startswith('//') == False]
    text = " ".join(arr)
    pattern = r"[^\s]*\.(com|org|net)\S*"
    text = re.sub(pattern, '', text)
    text = re.sub('[\\d+]', '', text)
    text = re.sub('\\-([^a-zA-Z0-9\\s_])', '', text)
    text = re.sub('\\.([^a-zA-Z0-9\\s_])', '', text)
    text = re.sub('[^a-zA-Z0-9\\s_\\-\\.]', '', text)
    arr = text.split(" ")
    arr = [x.strip() for x in arr if x.strip() != '']
    newArr = []
    for x in arr:
        if x.startswith('sha-'):
            newArr.append('sha')
        else:
            newArr.append(x)
    text = " ".join(newArr)
    return text


class Test:
    def __init__(self, name):
        self.name = name
        print('当前处理项目:%s' % name)

    def test(self):
        path = '../../model/ReactResultModel.csv'
        df = pd.read_csv(path)
        plt.figure(figsize=(10, 5))
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        plt.subplot(1, 2, 1)
        plt.plot(df["train_losses"], label="trainning loss")
        plt.plot(df["test_losses"], label="validation loss")
        plt.legend()
        plt.title("项目react review关系loss")
        plt.subplot(1, 2, 2)
        plt.plot(df["precision1"], label="precision top1")
        plt.plot(df["precision2"], label="precision top2")
        plt.plot(df["precision3"], label="precision top3")
        plt.plot(df["precision4"], label="precision top4")
        plt.plot(df["precision5"], label="precision top5")
        plt.legend()
        plt.title("项目react review关系precision")
        plt.show()

    def test_path_name(self):
        path = '../../dataset/%s/merge/filter.csv' % self.name
        df = pd.read_csv(path)
        first = df['path_name'][0]
        second = df['path_name'][1]

        first = first.replace("[", "").replace("]", "").replace("'", "").replace(",", "").replace(".", "").replace("/",
                                                                                                                   " ").split(
            " ")
        second = second.replace("[", "").replace("]", "").replace("'", "").replace(",", "").replace(".", "").replace(
            "/", " ").split(" ")

        print(first)
        print(second)

        words1_dict = {}
        words2_dict = {}
        for word in first:
            # word = word.strip(",.?!;")
            word = re.sub('[^a-zA-Z]', '', word)
            word = word.lower()
            # print(word)
            if word != '' and word in words1_dict:  # 这里改动了
                num = words1_dict[word]
                words1_dict[word] = num + 1
            elif word != '':
                words1_dict[word] = 1
            else:
                continue
        for word in second:
            # word = word.strip(",.?!;")
            word = re.sub('[^a-zA-Z]', '', word)
            word = word.lower()
            if word != '' and word in words2_dict:
                num = words2_dict[word]
                words2_dict[word] = num + 1
            elif word != '':
                words2_dict[word] = 1
            else:
                continue

        print(words1_dict)
        print(words2_dict)

        dic1 = sorted(words1_dict.items(), key=lambda asd: asd[1], reverse=True)
        dic2 = sorted(words2_dict.items(), key=lambda asd: asd[1], reverse=True)
        print(dic1)
        print(dic2)
        words_key = []
        for i in range(len(dic1)):
            words_key.append(dic1[i][0])  # 向数组中添加元素
        for i in range(len(dic2)):
            if dic2[i][0] in words_key:
                # print 'has_key', dic2[i][0]
                pass
            else:  # 合并
                words_key.append(dic2[i][0])
        # print(words_key)
        vect1 = []
        vect2 = []
        for word in words_key:
            if word in words1_dict:
                vect1.append(words1_dict[word])
            else:
                vect1.append(0)
            if word in words2_dict:
                vect2.append(words2_dict[word])
            else:
                vect2.append(0)
        print(vect1)
        print(vect2)

        # 计算余弦相似度
        sum = 0
        sq1 = 0
        sq2 = 0
        for i in range(len(vect1)):
            sum += vect1[i] * vect2[i]
            sq1 += pow(vect1[i], 2)
            sq2 += pow(vect2[i], 2)
        try:
            result = round(float(sum) / (math.sqrt(sq1) * math.sqrt(sq2)), 2)
        except ZeroDivisionError:
            result = 0.0
        print(result)

    def test2(self):
        path = '../../resource/pytorch/pytorchFilterPrData.json'
        with open(path, 'r') as load_f:
            load_dict = json.load(load_f)
        for pr in load_dict[2:3]:
            if 'files_detail' in pr:
                for path in pr['files_detail'][0:1]:
                    if 'patch' in path:
                        print(path['patch'])
                        print('*' * 200)
                        print(code_preprocess(path['patch']))

    def test3(self):
        path = '../../dataset/%s/merge/filter.csv' % self.name
        df = pd.read_csv(path)
        additions_lines = []
        deletions_lines = []
        changed_files = []
        jsonPath = '../../resource/%s/%sFilterPrData.json' % (self.name, self.name)
        with open(jsonPath, 'r') as load_f:
            load_dict = json.load(load_f)
        idList = df['id'].values.tolist()
        print(datetime.datetime.now())
        print(len(idList))
        for Id in idList:
            count = 0
            for entity in load_dict:
                if entity['id'] == Id:
                    count += 1
                    additions_lines.append(entity['additions_lines'])
                    deletions_lines.append(entity['deletions_lines'])
                    changed_files.append(entity['changed_files'])
                if count == 1:
                    break
        print(additions_lines)
        print(len(deletions_lines))
        print(len(changed_files))
        print(len(df))
        df['additions_lines'] = additions_lines
        df['deletions_lines'] = deletions_lines
        df['changed_files'] = changed_files
        print(df)
        print(datetime.datetime.now())


t = Test('react')
# t.test2()


