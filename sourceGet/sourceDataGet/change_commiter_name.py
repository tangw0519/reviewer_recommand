import json
import os.path

import requests

access_token0 = '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'
access_token1 = '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'
access_token2 = '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'
access_token3 = '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'


def open_file(path):
    with open(path, 'r') as load_f:
        load_dict = json.load(load_f)
    return load_dict


def getDataByUrl(url, count, low):
    if count % 3 == 0:
        access_token = access_token0
    if count % 3 == 1:
        access_token = access_token1
    if count % 3 == 2:
        access_token = access_token2
    # if count % 4 == 3:
    #     access_token = access_token3
    print(f'当前url:{url} 当前token是第{(count % 3) + 1}个 已处理{low + count}个')
    headers = {"Authorization": "token " + access_token}
    res = requests.get(url, headers=headers).json()
    return res


def change_name(name, low, high):
    oldPath = '../../resource/%s/%sFilterPrData.json' % (name, name)
    with open(oldPath, 'r') as load_file:
        load_dicts = json.load(load_file)
    pr_list = []
    count = 0
    print(f'开始{name}处理第{low}-{high}的数据')
    fail_url = []
    for pr in load_dicts[low:high]:
        commits_url = pr['url'] + '/commits'
        commitData = getDataByUrl(commits_url, count, low)
        count += 1
        if 'message' in commitData:
            print(commits_url)
            fail_url.append(commits_url)
        else:
            com_data = []
            for commit in commitData:
                com = {}
                com['message'] = commit['commit']['message']
                if commit['author']:
                    com['commit_author_login'] = commit['author']['login']
                if commit['committer']:
                    com['commit_committer_login'] = commit['committer']['login']
                com['commit_author_name'] = commit['commit']['author']['name']
                com['commit_committer_name'] = commit['commit']['committer']['name']
                com['commit_author_email'] = commit['commit']['author']['email']
                com['commit_committer_email'] = commit['commit']['committer']['email']
                com['commit_author_date'] = commit['commit']['author']['date']
                com['commit_committer_date'] = commit['commit']['committer']['date']
                com_data.append(com)
            pr['commitData'] = com_data
        pr_list.append(pr)
    newPath = f'../../resource/%s/%sFilterPrData{low}_{high}.json' % (name, name)
    with open(newPath, "w") as dump_f:
        json.dump(pr_list, dump_f, indent=4)
    print(f'保存了{low}到{high}所有pr相关数据')

    if len(fail_url) != 0:
        fail_path = f'../../resource/%s/%sFailedCommitUrl{low}_{high}.json' % (name, name)
        with open(fail_path, "w") as dump_f:
            json.dump(fail_url, dump_f, indent=4)


def get_len(name):
    oldPath = '../../resource/%s/%sFilterPrData.json' % (name, name)
    with open(oldPath, 'r') as load_file:
        load_dicts = json.load(load_file)
    return len(load_dicts)


def batch_change(name):
    length = get_len(name)
    times = int(length / 2000)
    # for i in range(0, 4):
    for i in range(17, times + 1):
        change_name(name, 2000 * i, 2000 * (i + 1))


def jsonFileMerge(totalPath, toMergedPath1, toMergedPath2):
    with open(toMergedPath1, 'r') as load_f:
        load_dict = json.load(load_f)
    with open(toMergedPath2, 'r') as load_m:
        load_data = load_dict + json.load(load_m)
    with open(totalPath, 'w') as file_obj:
        json.dump(load_data, file_obj, indent=4)
        print('文件合并完成')


def MergeSavedFilterPRFile(name):
    jsonFileMerge('../../resource/%s/%sFilterPrData_all.json' % (name, name),
                  '../../resource/%s/%sFilterPrData0_2000.json' % (name, name),
                  '../../resource/%s/%sFilterPrData2000_4000.json' % (name, name))
    length = get_len(name)
    times = int(length / 2000)
    for i in range(2, times + 1, 1):
        jsonFileMerge('../../resource/%s/%sFilterPrData_all.json' % (name, name),
                      '../../resource/%s/%sFilterPrData_all.json' % (name, name),
                      f'../../resource/%s/%sFilterPrData{2000 * i}_{2000 * (i + 1)}.json' % (name, name))


def charge_fail(name, low, high):
    urls = open_file(f'../../resource/{name}/{name}FailedCommitUrl{low}_{high}.json')
    prs = open_file(f'../../resource/{name}/{name}FilterPrData{low}_{high}.json')
    count = 0
    urls = [x.replace('/commits', '') for x in urls]

    pr_list = []
    for pr in prs:
        if pr['url'] in urls:
            commitData = getDataByUrl(pr['url'] + '/commits', count, 0)
            print(commitData)
            count += 1
            com_data = []
            for commit in commitData:
                com = {}
                com['message'] = commit['commit']['message']
                if commit['author']:
                    com['commit_author_login'] = commit['author']['login']
                if commit['committer']:
                    com['commit_committer_login'] = commit['committer']['login']
                com['commit_author_name'] = commit['commit']['author']['name']
                com['commit_committer_name'] = commit['commit']['committer']['name']
                com['commit_author_email'] = commit['commit']['author']['email']
                com['commit_committer_email'] = commit['commit']['committer']['email']
                com['commit_author_date'] = commit['commit']['author']['date']
                com['commit_committer_date'] = commit['commit']['committer']['date']
                com_data.append(com)
            pr['commitData'] = com_data
            print(com_data)
            pr_list.append(pr)
        else:
            pr_list.append(pr)

    newPath = f'../../resource/{name}/{name}FilterPrData{low}_{high}.json'
    with open(newPath, "w") as dump_f:
        json.dump(pr_list, dump_f, indent=4)
    print(f'保存了相关数据')


# oldPath = '../../resource/repos/repos.json'
# with open(oldPath, 'r') as load_file:
#     load_dicts = json.load(load_file)
#     for x in load_dicts[8:9]:
#         print(x['name'])
#         batch_change(x['name'])

def get_all_commit_data(name, low, high):
    oldPath = '../../resource/%s/%sFilterPrData.json' % (name, name)
    with open(oldPath, 'r') as load_file:
        load_dicts = json.load(load_file)
    commit_list = []
    fail_url = []
    print(f'开始{name}处理第{low}-{high}的数据')
    count = 0
    for pr in load_dicts[low:high]:
        new = {}
        new['number'] = pr['number']
        commits_url = pr['url'] + '/commits'
        commitData = getDataByUrl(commits_url, count, low)
        if 'message' in commitData:
            print(commits_url)
            fail_url.append(commits_url)
            count += 1
        else:
            count += 1
            com_data = []
            for commit in commitData:
                com = {}
                com['message'] = commit['commit']['message']
                if commit['author']:
                    com['commit_author_login'] = commit['author']['login']
                if commit['committer']:
                    com['commit_committer_login'] = commit['committer']['login']
                com['commit_author_name'] = commit['commit']['author']['name']
                com['commit_committer_name'] = commit['commit']['committer']['name']
                com['commit_author_email'] = commit['commit']['author']['email']
                com['commit_committer_email'] = commit['commit']['committer']['email']
                com['commit_author_date'] = commit['commit']['author']['date']
                com['commit_committer_date'] = commit['commit']['committer']['date']
                com_data.append(com)
            new['commitData'] = com_data
            commit_list.append(new)
    newPath = f'../../resource/%s/%sCommitData{low}_{high}.json' % (name, name)
    with open(newPath, "w") as dump_f:
        json.dump(commit_list, dump_f, indent=4)
    print(f'保存了{low}到{high}所有commit相关数据')

    fail_path = '../../resource/%s/%sFailedCommitUrl.json' % (name, name)
    if os.path.exists(fail_path):
        with open(fail_path, 'r') as load_file:
            load_dicts = json.load(load_file)
            load_dicts = load_dicts + fail_url
        with open(fail_path, "w") as dump_f:
            json.dump(load_dicts, dump_f, indent=4)
    else:
        with open(fail_path, "w") as dump_f:
            json.dump(fail_url, dump_f, indent=4)
