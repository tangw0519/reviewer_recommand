import pandas as pd

from data.process.get_edge import Edge
from data.process.get_features import Features
from data.process.get_metapath import MetaPath

# d = Edge('bitcoin', '2017-01-01T00:00:00Z', '2020-06-30T00:00:00Z')
# d.get_pr_reviewer_edges(0.5)
# d.get_pr_committer_edges()
# d.get_pr_commenter_edges(0.5)
# d.get_pr_pr_edges(5)
#
f = Features('bitcoin', '2017-01-01T00:00:00Z', '2020-06-30T00:00:00Z')
f.get_pr_features(500)
# f.get_pr_labels()


# m = MetaPath('bitcoin', '2017-01-01T00:00:00Z', '2020-06-30T00:00:00Z')
# m.get_pr_commit_pr(5)
# m.get_pr_path_pr()