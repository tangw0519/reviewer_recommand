import time
from datetime import datetime
import json
import pandas as pd
import re
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords


def get_default_time(name):
    df = pd.read_csv('../statics.csv')
    df = df[df['Name'] == name]
    start = df.project_created_at.values[0]
    end = '2022-01-02T10:22:15Z'
    return start, end


def get_unix(t):
    time_strip = datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ')
    get_time = time_strip.strftime('%Y-%m-%d %H:%M:%S')
    get_unix_time = int(time.mktime(time.strptime(get_time, "%Y-%m-%d %H:%M:%S")))
    return get_unix_time


def get_unix_distance(t1, t2):
    t1 = get_unix(t1)
    t2 = get_unix(t2)
    return t2 - t1


def get_similarity(f1, f2):
    '''
    求两个文件的相似度
    :param f1: 文件1路径
    :param f2: 文件2路径
    :return:
    '''
    arr1 = f1.split("/")
    arr2 = f2.split("/")
    len1 = len(arr1)
    len2 = len(arr2)
    len_max = max(len1, len2)
    lcp = 0
    for i in range(len_max):
        if arr1[i] == arr2[i]:
            lcp += 1
        else:
            break
    return lcp / len_max


def delete_same_commit(arr):
    '''
    删除相同的committer——pr信息只保留一个
    :param arr:
    :return:
    '''
    commit_arr = []
    for edge in arr:
        temp = [x for x in arr if x['committer'] == edge['committer']]
        arr = [x for x in arr if x['committer'] != edge['committer']]
        weight = 0
        for x in temp:
            weight += x['weight']
        if len(temp) != 0:
            commit_arr.append({'pr': edge['pr'], 'committer': edge['committer'], 'weight': weight / len(temp)})
    return commit_arr


def Txt2Csv(Txt_path, Csv_path):
    '''
    由txt文件转变为csv文件
    :param Txt_path: txt路径
    :param Csv_path: csv路径
    :return:
    '''
    with open(Txt_path, encoding='utf-8') as f:
        contents = []
        lines = f.readlines()  # lines是一个列表
        for i in lines:
            line = i.strip().split(",")  # 去掉前后的换行符，之后按逗号分割开
            contents.append(line)  # contents二维列表
    df = pd.DataFrame(contents)
    df.to_csv(Csv_path, header=False)  # 不添加表头
    print("数据写入成功")


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


def get_similarity_user(arr1, arr2):
    """
    求两个文件的相似度
    :param arr2:
    :param arr1:
    :return:
    """
    len1 = len(arr1)
    len2 = len(arr2)
    len_max = max(len1, len2)
    len_min = min(len1, len2)
    arr = list(set(arr1 + arr2))
    lcp = len(arr) - len_min
    return lcp / len_max
