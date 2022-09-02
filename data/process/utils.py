import time
from datetime import datetime
import pandas as pd


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
