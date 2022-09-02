from data.process.get_edge import Edge
from data.process.get_features import Features

d = Edge('bitcoin', '2017-01-01T00:00:00Z', '2020-06-30T00:00:00Z')
d.get_pr_reviewer_edges(0.5)
d.get_pr_committer_edges()
d.get_pr_commenter_edges(0.5)
d.get_pr_pr_edges(5)

# f = Features('bitcoin', '2017-01-01T00:00:00Z', '2020-06-30T00:00:00Z')
# f.get_pr_features()
