import csv
import json
import os

import pandas as pd


class getFileCounts:
    def __init__(self):
        self.nameList = []
        with open('../../resource/repos/repos.json', 'r') as load_f:
            load_dict = json.load(load_f)
            for x in load_dict:
                self.nameList.append(x['full_name'])
        self.path = '../../dataset/statics.csv'

    def getJsonFileCounts(self):
        row = []
        for name in self.nameList:
            Name = name.split("/")[1]
            print('当前处理项目%s' % Name)
            AllIssuePath = '../../resource/%s/%sIssue.json' % (Name, Name)
            AllPrPath = '../../resource/%s/%sPrData.json' % (Name, Name)
            FilterIssuePath = '../../resource/%s/%sFilterIssue.json' % (Name, Name)
            path = '../../resource/%s/%sFilterPrData.json' % (Name, Name)
            with open(AllIssuePath, 'r') as load_a:
                allIssues = len(json.load(load_a))
            with open(AllPrPath, 'r') as load_b:
                allPrs = len(json.load(load_b))
            with open(FilterIssuePath, 'r') as load_c:
                allFilterIssues = len(json.load(load_c))
            with open(path, 'r') as load_d:
                allFilterPrs = len(json.load(load_d))

            with open(path, 'r') as load_a:
                load_dicts = json.load(load_a)
            # print('项目%s总pr数量：%s' % (self.name, str(len(load_dicts))))
            creator = []
            a = 0
            # 合并
            b = 0
            c = 0
            merger = []
            # commit
            d = 0
            e = 0
            committer = []
            # 评论
            f = 0
            g = 0
            commenter = []
            # 审查
            h = 0
            i = 0
            reviewer = []

            for s in load_dicts:
                # pr
                creator.append(s['pr_creator_name'])
                if s['state'] != 'open':
                    a += 1
                # merge
                if s['merge']:
                    b += 1
                    if "pr_mergedBy_user_name" in s and s["pr_creator_name"] == s["pr_mergedBy_user_name"]:
                        c += 1
                    if 'pr_mergedBy_user_name' in s:
                        merger.append(s['pr_mergedBy_user_name'])
                # commit
                if 'commitData' in s and len(s['commitData']) != 0:
                    d += 1
                    e += len(s['commitData'])
                    for commit in s['commitData']:
                        if 'commit_author_login' in commit:
                            committer.append(commit['commit_author_login'])
                        else:
                            committer.append(commit['commit_author_name'])
                # comment
                if 'commentData' in s and len(s['commentData']) != 0:
                    f += 1
                    g += len(s['commentData'])
                    for comment in s['commentData']:
                        commenter.append(comment['comment_creator'])
                # review
                if 'reviewData' in s and len(s['reviewData']) != 0:
                    h += 1
                    i += len(s['reviewData'])
                    for review in s['reviewData']:
                        reviewer.append(review['review_comment_creator'])
            user = commenter + committer + reviewer + merger + creator
            user = list(set(user))

            row.append([Name, allIssues, allPrs, allFilterIssues, allFilterPrs,
                        len(list(set(creator))), a, b, c, len(list(set(merger))),
                        d, e, len(list(set(committer))), f, g,
                        len(list(set(commenter))), h, i, len(list(set(reviewer))), len(user)])
        if os.path.exists(self.path):
            os.remove(self.path)
        with open(self.path, "a", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(
                ["Name", "allIssues", "allPrs", "allFilterIssues", "allFilterPrs",
                 "prCreators", "closedPr", "mergedPr", "selfMergedPr", "mergers",
                 "hasCommitPr", "commits", "committers", "hasCommentPr", "comments",
                 "commenters", "hasReviewPr", "reviews", "reviewers", "users"])
            for r in row:
                writer.writerow(r)

    def add_self_operation_info(self):
        df = pd.read_csv('../../dataset/statics.csv')
        forks = []
        stars = []
        project_created_at = []
        with open('../../resource/repos/repos.json', 'r') as load_f:
            load_dict = json.load(load_f)
            for x in load_dict:
                forks.append(x['forks'])
                stars.append(x['stars'])
                project_created_at.append(x['created_at'])
        df['forks'] = forks
        df['stars'] = stars
        df['project_created_at'] = project_created_at

        selfReview = []
        for name in self.nameList:
            name = name.split("/")[1]
            data = pd.read_csv('../../dataset/%s/review/filter.csv' % name)
            data = data[data['reviewer'] == data['creator']]
            selfReview.append(len(data))
        df['selfReview'] = selfReview
        df.to_csv('../../dataset/statics.csv',
                  index=False, header=True,
                  sep=',')

        print('over')


# data = getFileCounts()
# data.getJsonFileCounts()
# data.add_self_operation_info()

path = '../../dataset/statics.csv'
if os.path.isfile(path):
    content = pd.read_csv(path)
    print(content)
else:
    data = getFileCounts()
    data.getJsonFileCounts()
    data.add_self_operation_info()
    content = pd.read_csv(path)
    print(content)
