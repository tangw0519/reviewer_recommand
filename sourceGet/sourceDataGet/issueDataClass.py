import json
import os

import requests
from github import Github

access_token = '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'
# access_token = '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'
# access_token = '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'
# access_token = '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'

class IssueDataSet:
    def __init__(self, name):
        self.name = name
        Name = name.split('/')[1]
        self.counts = self.getProjectIssueCounts()
        # urlPath = '../../resource/%s/%sIssueUrl.json' % (Name, Name)
        # if not os.path.exists(urlPath):
        #     self.issueList = self.getAllIssueUrl()
        # else:
        #     with open(urlPath, 'r') as load_f:
        #         self.issueList = json.load(load_f)

    def getProjectIssueCounts(self):
        g = Github(access_token)
        repo = g.get_repo(self.name)
        print('项目创建者:%s' % repo.owner.login)
        issues = repo.get_issues(state='all')
        print('项目的issues数量:%d' % issues.totalCount)
        return issues.totalCount

    def getAllIssueUrl(self):
        name = self.name.split('/')[1]
        g = Github(access_token)
        repo = g.get_repo(self.name)
        issues = repo.get_issues(state='all')
        IssueUrlList = []
        m = 1
        for x in issues:
            IssueUrlList.append(x.url)
            print('正在获取%s的第%d个issue的url' % (name, m))
            m += 1
        print('获取所有issue的url成功')
        urlPath = '../../resource/%s/%sIssueUrl.json' % (name, name)
        with open(urlPath, 'w') as file_obj:
            json.dump(IssueUrlList, file_obj, indent=4)
            print('项目Issue url列表保存完成')

        return IssueUrlList

    def getAllIssueData(self, path, low, high):
        IssueUrlListLowToHigh = []
        IssueResList = []
        m = 1
        for x in self.issueList[low:high]:
            IssueUrlListLowToHigh.append(x)
            print('正在获取第%d个issue的url' % (low + m))
            m += 1
        print('获取%d到%d的issue的url成功', (low, high))
        k = 1
        headers = {"Authorization": "token " + access_token}
        for s in IssueUrlListLowToHigh:
            res = requests.get(s, headers=headers).json()
            IssueResList.append(res)
            print('正在获取第%d个issue的数据，url为:%s' % (low + k, s))
            k += 1
            filename = path
        with open(filename, 'w') as file_obj:
            json.dump(IssueResList, file_obj, indent=4)
            print('项目Issue数据保存完成')

    def getJsonFileCounts(self, Path):
        with open(Path, 'r') as load_f:
            load_dict = json.load(load_f)
        print('文件数量:%d' % len(load_dict))
        return len(load_dict)

    def jsonFileMerge(self, totalPath, toMergedPath1, toMergedPath2):
        with open(toMergedPath1, 'r') as load_f:
            load_dict = json.load(load_f)
        with open(toMergedPath2, 'r') as load_m:
            load_data = load_dict + json.load(load_m)
        with open(totalPath, 'w') as file_obj:
            json.dump(load_data, file_obj, indent=4)
            print('文件合并完成')

    def getDataByUrl(self, url):
        headers = {"Authorization": "token " + access_token}
        res = requests.get(url, headers=headers).json()
        return res

    def FilterData(self, newPath, low, high):
        Name = self.name.split('/')[1]
        oldPath = '../../resource/%s/%sIssue.json' % (Name, Name)
        with open(oldPath, 'r') as load_f:
            load_dict = json.load(load_f)
        newList = []
        k = 1
        print('开始处理%d到%d的issue数据' % (low, high))
        for issue in load_dict[low:high]:
            if 'pull_request' not in issue and 'message' not in issue:
                new = {}
                new['id'] = issue['id']
                new['url'] = issue['url']
                new['number'] = issue['number']
                new['title'] = issue['title']
                new['body'] = issue['body']
                new['issue_creator_name'] = issue['user']['login']
                new['author_association'] = issue['author_association']
                new['state'] = issue['state']
                new['created_at'] = issue['created_at']
                new['updated_at'] = issue['updated_at']
                if issue['state'] == 'closed' and issue['closed_by'] is not None:
                    new['closed_at'] = issue['closed_at']
                    new['issue_closedBy_user_name'] = issue['closed_by']['login']
                if issue['assignee'] is not None:
                    new['assignee_name'] = issue['assignee']['login']
                    names = []
                    for user in issue['assignees']:
                        names.append(user['login'])
                    new['assignees'] = names
                if issue['labels'] is not None:
                    labels = []
                    for label in issue['labels']:
                        labels.append(label['name'])
                    new['labels'] = labels
                if issue['milestone'] is not None:
                    new['milestone'] = issue['milestone']
                comment = []
                if issue['comments'] != 0:
                    comments_url = issue['comments_url']
                    commentData = self.getDataByUrl(comments_url)
                    if 'message' not in commentData:
                        for c in commentData:
                            x = {}
                            x['comment_creator'] = c['user']['login']
                            x['created_at'] = c['created_at']
                            x['author_association'] = c['author_association']
                            x['body'] = c['body']
                            comment.append(x)
                        new['commentData'] = comment
                newList.append(new)
            print('已处理第%d个issue数据，url为:%s' % ((k + low), issue['url']))
            k += 1

        with open(newPath, "w") as dump_f:
            json.dump(newList, dump_f, indent=4)
        print('保存了%d到%d的所有issue相关数据' % (low, high))

    def SaveIssueData(self, start=0):
        name = self.name.split('/')[1]
        number = int(self.counts / 1000 + 1)
        for j in range(start, number, 3):
            print('开始处理 %d 到 %d 的issue数据' % (j * 1000, 1000 * (j + 3)))
            data.getAllIssueData('../../resource/%s/%sIssue%d.json' % (name, name, int(j / 3)), 1000 * j,
                                 1000 * (j + 3))
            print('保存了 %d 到 %d 的isuue数据' % (j * 1000, 1000 * (j + 3)))

    def MergeSavedIssueFile(self, num):
        name = self.name.split('/')[1]
        self.jsonFileMerge('../../resource/%s/%sIssue.json' % (name, name),
                           '../../resource/%s/%sIssue0.json' % (name, name),
                           '../../resource/%s/%sIssue1.json' % (name, name))
        self.getJsonFileCounts(
            '../../resource/%s/%sIssue.json' % (name, name))
        for i in range(2, num + 1):
            self.getJsonFileCounts(
                '../../resource/%s/%sIssue.json' % (name, name))
            self.getJsonFileCounts('../../resource/%s/%sIssue%d.json' % (name, name, i))
            self.jsonFileMerge(
                '../../resource/%s/%sIssue.json' % (name, name),
                '../../resource/%s/%sIssue.json' % (name, name),
                '../../resource/%s/%sIssue%d.json' % (name, name, i))
            self.getJsonFileCounts(
                '../../resource/%s/%sIssue.json' % (name, name))

    def SaveFilterIssueData(self, start=0):
        Name = self.name.split('/')[1]
        count = int(self.getJsonFileCounts('../../resource/%s/%sIssue.json' % (Name, Name)) / 1000)
        for m in range(start, count + 1):
            print('开始处理%d到%d的issue数据' % ((1000 * m), (1000 * (m + 1))))
            self.FilterData('../../resource/%s/%sFilterIssue%d.json' % (Name, Name, m), 1000 * m,
                            1000 * (m + 1))
            print('保存了%d到%d的issue数据' % ((1000 * m), (1000 * (m + 1))))

    def MergeSavedFilterIssueFile(self, num):
        names = self.name.split('/')[1]
        self.jsonFileMerge('../../resource/%s/%sFilterIssue.json' % (names, names),
                           '../../resource/%s/%sFilterIssue0.json' % (names, names),
                           '../../resource/%s/%sFilterIssue1.json' % (names, names))
        self.getJsonFileCounts(
            '../../resource/%s/%sFilterIssue.json' % (names, names))
        for i in range(2, num + 1):
            self.getJsonFileCounts(
                '../../resource/%s/%sFilterIssue.json' % (names, names))
            self.getJsonFileCounts('../../resource/%s/%sFilterIssue%d.json' % (names, names, i))
            self.jsonFileMerge(
                '../../resource/%s/%sFilterIssue.json' % (names, names),
                '../../resource/%s/%sFilterIssue.json' % (names, names),
                '../../resource/%s/%sFilterIssue%d.json' % (names, names, i))
            self.getJsonFileCounts(
                '../../resource/%s/%sFilterIssue.json' % (names, names))


nameList = []
with open('../../resource/repos/repos.json', 'r') as load_f:
    load_dict = json.load(load_f)
    for x in load_dict:
        nameList.append(x['full_name'])
print(nameList)
for name in nameList:
    print(name)
    data = IssueDataSet(name)
    # data.SaveFilterIssueData(0)
    # data.MergeSavedFilterIssueFile(45)
