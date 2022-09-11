dataset = 'bitcoin'
start_time = '2017-01-01T00:00:00Z'
end_time = '2020-06-30T00:00:00Z'
top_m = 5
namuda = 0.5
features_len = 500


# from data.process.get_edge import Edge
# d = Edge(dataset, start_time, end_time)
# d.get_pr_reviewer_edges(namuda=namuda)
# d.get_pr_committer_edges()
# d.get_pr_commenter_edges(namuda=namuda)
# d.get_pr_pr_edges(top_m=top_m)

from data.process.get_features import Features
f = Features(dataset, start_time, end_time)
# f.get_pr_features(MAX_TITLE_LENGTH=features_len)
f.get_pr_labels()

# from data.process.get_metapath import MetaPath
# m = MetaPath(dataset, start_time, end_time)
# m.get_pr_review_pr(top_m=top_m)
# m.get_pr_commit_pr(top_m=top_m)
# m.get_pr_path_pr()
# m.get_pr_label_pr(top_m=top_m)
