import json
import requests
from github import Github

access_token = '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'
counts = 3000


class SourceData:
    def __init__(self):
        pass

    def openFile(self, path):
        with open(path, 'r') as load_f:
            load_dict = json.load(load_f)
        return load_dict

    def saveFile(self, path, data):
        with open(path, 'w') as file_obj:
            json.dump(data, file_obj, indent=4)
            print('文件保存完成')

    def getProjectPRCounts(self, name):
        g = Github(access_token)
        repo = g.get_repo(name)
        pulls = repo.get_pulls('all')
        return pulls.totalCount

    def getProjectIssueCounts(self, name):
        g = Github(access_token)
        repo = g.get_repo(name)
        issues = repo.get_issues(state='all')
        return issues.totalCount

    def getDataByUrl(self, url):
        headers = {"Authorization": "token " + access_token}
        res = requests.get(url, headers=headers).json()
        print(res)
        return res

    def getRepoInfo(self, language, date, num, pr_counts, issue_counts, star_counts, path):
        datalist = []
        for i in range(num):
            # url = f'https://api.github.com/search/repositories?q=language:{language}+created:>{date}&sort=forks&per_page=100&page={i + 1} '
            url = f'https://api.github.com/search/repositories?q=language:{language}+created:>{date}&sort=forks&per_page=30 '
            r = requests.get(url).json()
            items = r['items']
            for item in items:
                prs = self.getProjectPRCounts(item['full_name'])
                issues = self.getProjectIssueCounts(item['full_name'])
                print('名称:%s=====issues:%d=====prs:%d=====forks:%d=====stars:%d' % (
                    item['full_name'], issues, prs, item['forks'], item['stargazers_count']))
                # if prs > pr_counts and issues > issue_counts and item['forks'] > fork_counts and item[
                #     'stargazers_count'] > star_counts:
                if prs > pr_counts and issues > issue_counts and item['stargazers_count'] > star_counts:
                    print('****' * 20)
                    new = {}
                    new['name'] = item['name']
                    new['created_at'] = item['created_at']
                    new['full_name'] = item['full_name']
                    new['url'] = item['url']
                    new['description'] = item['description']
                    new['pr_counts'] = prs
                    new['issue_counts'] = issues
                    new['forks'] = item['forks']
                    new['stars'] = item['stargazers_count']
                    datalist.append(new)
        print(len(datalist))
        with open(path, 'w') as file_obj:
            json.dump(datalist, file_obj, indent=4)
            print('文件保存完成')


data = SourceData()
# data.getRepoInfo('javascript', '2013-01-01', 1, 10000, 20000, 50000, '../../resource/repos/reposJavascript.json')
# data.getRepoInfo('python', '2010-01-01', 1, 10000, 20000, 30000, '../../resource/repos/reposPython.json')
# data.getRepoInfo('Java', '2010-01-01', 1, 10000, 10000, 10000, '../../resource/repos/reposJava.json')
# data.getRepoInfo("Cpp", '2010-01-01', 1, 10000, 20000, 50000, '../../resource/repos/reposC++.json')
