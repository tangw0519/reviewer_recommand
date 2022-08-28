import json
import os

import requests
from github import Github

access_token = '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'
access_token1 = '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'
access_token2 = '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'
access_token3 = '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'
number = 0


class DataSet:
    def __init__(self, name):
        self.name = name
        self.counts = self.getProjectPRCounts()
        Name = name.split('/')[1]
        folder = os.path.exists('../../resource/%s' % Name)
        if not folder:
            os.makedirs('../../resource/%s' % Name)
        urlPath = '../../resource/%s/%sPrUrl.json' % (Name, Name)
        if not os.path.exists(urlPath):
            self.prList = self.getAllPrUrl()
        else:
            with open(urlPath, 'r') as load_k:
                self.prList = json.load(load_k)

    def getAllPrUrl(self):
        name = self.name.split('/')[1]
        g = Github(access_token)
        repo = g.get_repo(self.name)
        pulls = repo.get_pulls('all')
        PrUrlList = []
        m = 1
        for s in pulls:
            PrUrlList.append(s.url)
            print('正在获取%s的第%d个pr的url' % (name, m))
            m += 1
        print('获取所有pr的url成功')
        urlPath = '../../resource/%s/%sPrUrl.json' % (name, name)
        with open(urlPath, 'w') as file_obj:
            json.dump(PrUrlList, file_obj, indent=4)
            print('项目Issue url列表保存完成')

        return PrUrlList

    def getProjectPRCounts(self):
        g = Github(access_token)
        repo = g.get_repo(self.name)
        print('项目创建者:%s' % repo.owner.login)
        pulls = repo.get_pulls('all')
        print('项目的pulls数量:%d' % pulls.totalCount)
        return pulls.totalCount

    def getAllPRData(self, path, low, high):
        name = self.name.split('/')[1]
        pullUrlList = []
        pullResList = []
        k = 0
        for c in self.prList[low:high]:
            k += 1
            print('正在获取%s的第%d个pr的url' % (name, (low + k)))
            pullUrlList.append(c)

        headers = {"Authorization": "token " + access_token}
        m = 0
        for u in pullUrlList:
            m += 1
            print('正在获取%s的第%d个pr数据，url为:%s' % (name, (low + m), u))
            res = requests.get(u, headers=headers).json()
            pullResList.append(res)
            filename = path
        with open(filename, 'w') as file_obj:
            json.dump(pullResList, file_obj, indent=4)
            print('项目PR数据保存完成')

    def jsonFileMerge(self, totalPath, toMergedPath1, toMergedPath2):
        with open(toMergedPath1, 'r') as load_f:
            load_dict = json.load(load_f)
        with open(toMergedPath2, 'r') as load_m:
            load_data = load_dict + json.load(load_m)
        with open(totalPath, 'w') as file_obj:
            json.dump(load_data, file_obj, indent=4)
            print('文件合并完成')

    def getJsonFileCounts(self, Path):
        with open(Path, 'r') as load_f:
            load_dict = json.load(load_f)
        print('文件数量:%d' % len(load_dict))
        return len(load_dict)

    def getDataByUrl(self, url, token):
        print(token)
        headers = {"Authorization": "token " + token}
        res = requests.get(url, headers=headers).json()
        return res

    def getPRInfo(self, newPath, low, high):
        names = self.name.split('/')[1]
        oldPath = '../../resource/%s/%sPrData.json' % (names, names)
        with open(oldPath, 'r') as load_file:
            load_dicts = json.load(load_file)
        pullResList = []
        k = 1
        for u in load_dicts[low:high]:
            print('正在处理第%d个pr'
                  '数据————————————————————————————————————————————————————————————————————————————————————————————————' % (
                              low + k))
            new = {}
            new['id'] = u['id']
            new['url'] = u['url']
            new['number'] = u['number']
            new['title'] = u['title']
            new['body'] = u['body']
            new['pr_creator_name'] = u['user']['login']
            new['state'] = u['state']
            new['merge'] = u['merged']
            new['created_at'] = u['created_at']
            new['updated_at'] = u['updated_at']
            new['closed_at'] = u['closed_at']
            if u['merged'] and u['merged_by'] is not None:
                new['merged_at'] = u['merged_at']
                new['pr_mergedBy_user_name'] = u['merged_by']['login']
            if u['assignee'] is not None:
                new['assignee_name'] = u['assignee']['login']
                names = []
                for user in u['assignees']:
                    names.append(user['login'])
                new['assignees'] = names
            if len(u['requested_reviewers']) != 0:
                reviews = []
                for re in u['requested_reviewers']:
                    reviews.append(re['login'])
                new['requested_reviewers'] = reviews
            if u['labels'] is not None:
                labels = []
                for label in u['labels']:
                    labels.append(label['name'])
                new['labels'] = labels
            if u['milestone'] is not None:
                new['milestone'] = u['milestone']
            new['additions_lines'] = u['additions']
            new['deletions_lines'] = u['deletions']
            new['changed_files'] = u['changed_files']
            if u['changed_files'] != 0:
                file_url = u['url'] + '/files'
                changeFilesDetail = []
                details = self.getDataByUrl(file_url, access_token)
                if 'message' not in details:
                    for detail in details:
                        de = {}
                        de['filename'] = detail['filename']
                        de['additions'] = detail['additions']
                        de['deletions'] = detail['deletions']
                        de['changes'] = detail['changes']
                        if 'patch' in detail:
                            de['patch'] = detail['patch']
                        changeFilesDetail.append(de)
                    new['files_detail'] = changeFilesDetail

            commits_url = u['commits_url']
            commitData = self.getDataByUrl(commits_url, access_token1)
            if 'message' not in commitData:
                commitUser = []
                for commit in commitData:
                    com = {}
                    com['commit_author_name'] = commit['commit']['author']['name']
                    com['commit_committer_name'] = commit['commit']['committer']['name']
                    com['message'] = commit['commit']['message']
                    com['commit_author_date'] = commit['commit']['author']['date']
                    com['commit_committer_date'] = commit['commit']['committer']['date']
                    commitUser.append(com)
                new['commitData'] = commitUser

            if u['comments'] != 0:
                comment_url = u['comments_url']
                commentData = self.getDataByUrl(comment_url, access_token2)
                if 'message' not in commentData:
                    commentUser = []
                    for comment in commentData:
                        c = {}
                        c['comment_creator'] = comment['user']['login']
                        c['created_at'] = comment['created_at']
                        c['author_association'] = comment['author_association']
                        c['body'] = comment['body']
                        commentUser.append(c)
                    new['commentData'] = commentUser
            if u['review_comments'] != 0:
                review_comments_url = u['review_comments_url']
                reviewData = self.getDataByUrl(review_comments_url, access_token3)
                if 'message' not in reviewData:
                    reviewUser = []
                    for review in reviewData:
                        r = {}
                        if review['user'] is not None:
                            r['review_comment_creator'] = review['user']['login']
                            r['created_at'] = review['created_at']
                            r['author_association'] = review['author_association']
                            r['body'] = review['body']
                            reviewUser.append(r)
                    new['reviewData'] = reviewUser
            print('已处理第%d个pr数据，url为:%s' % ((k + low), u['url']))
            k += 1
            pullResList.append(new)

        with open(newPath, "w") as dump_f:
            json.dump(pullResList, dump_f, indent=4)
        print('保存了%d到%d的所有pr相关数据' % (low, high))

    def SavePRData(self, start=0):
        name = self.name.split('/')[1]
        folder = os.path.exists('../../resource/%s' % name)
        if not folder:
            os.makedirs('../../resource/%s' % name)
        Num = int(self.counts / 1000)
        for k in range(start, Num + 1, 3):
            self.getAllPRData('../../resource/%s/%sPrData%d.json' % (name, name, (int(k / 3))), 1000 * k,
                              1000 * (k + 3))
            print('保存了%d到%d的pr数据' % ((1000 * k), (1000 * (k + 3))))

    def MergeSavedPRFile(self, num):
        name = self.name.split('/')[1]
        self.jsonFileMerge('../../resource/%s/%sPrData.json' % (name, name),
                           '../../resource/%s/%sPrData0.json' % (name, name),
                           '../../resource/%s/%sPrData1.json' % (name, name))
        self.getJsonFileCounts(
            '../../resource/%s/%sPrData.json' % (name, name))
        for i in range(2, num + 1):
            self.getJsonFileCounts(
                '../../resource/%s/%sPrData.json' % (name, name))
            self.getJsonFileCounts('../../resource/%s/%sPrData%d.json' % (name, name, i))
            self.jsonFileMerge(
                '../../resource/%s/%sPrData.json' % (name, name),
                '../../resource/%s/%sPrData.json' % (name, name),
                '../../resource/%s/%sPrData%d.json' % (name, name, i))
            self.getJsonFileCounts(
                '../../resource/%s/%sPrData.json' % (name, name))

    def SaveFilterPRData(self, start=0):
        Name = self.name.split('/')[1]
        count = int(self.getJsonFileCounts('../../resource/%s/%sPrData.json' % (Name, Name)) / 1000)
        for m in range(start, count + 1):
            print('开始处理%d到%d的pr数据' % ((1000 * m), (1000 * (m + 1))))
            self.getPRInfo('../../resource/%s/%sFilterPrData%d.json' % (Name, Name, m), 1000 * m,
                           1000 * (m + 1))
            print('保存了%d到%d的pr数据' % ((1000 * m), (1000 * (m + 1))))

    def MergeSavedFilterPRFile(self, num):
        name = self.name.split('/')[1]
        self.jsonFileMerge('../../resource/%s/%sFilterPrData.json' % (name, name),
                           '../../resource/%s/%sFilterPrData0.json' % (name, name),
                           '../../resource/%s/%sFilterPrData1.json' % (name, name))
        self.getJsonFileCounts(
            '../../resource/%s/%sFilterPrData.json' % (name, name))
        for i in range(2, num + 1):
            self.getJsonFileCounts(
                '../../resource/%s/%sFilterPrData.json' % (name, name))
            self.getJsonFileCounts('../../resource/%s/%sFilterPrData%d.json' % (name, name, i))
            self.jsonFileMerge(
                '../../resource/%s/%sFilterPrData.json' % (name, name),
                '../../resource/%s/%sFilterPrData.json' % (name, name),
                '../../resource/%s/%sFilterPrData%d.json' % (name, name, i))
            self.getJsonFileCounts(
                '../../resource/%s/%sFilterPrData.json' % (name, name))


# nameList = []
# with open('../../resource/repos/repos.json', 'r') as load_f:
#     load_dict = json.load(load_f)
#     for x in load_dict[0:]:
#         nameList.append(x['full_name'])
# print(nameList)
# for name in nameList[0:1]:
#     print(name)
#     data = DataSet(name)
#     data.MergeSavedFilterPRFile(11)
   # data.SaveFilterPRData(start=41)

