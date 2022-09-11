# fenlei
# labels_raw = np.genfromtxt(data_path + 'features/pr_labels_test.csv', delimiter=',')
# labels = torch.from_numpy(labels_raw[:, -1]).long()
# num_classes = len(list(set(labels)))

# path_edge = np.genfromtxt(data_path + f'metapath/{start_time}-to-{end_time}/pr_path_pr_edge.csv', delimiter=',',
#                           skip_header=True)
# path_edge = path_edge[:, 0:2]
# indices = []
# path_value = []
# pr1_index_count = [0] * labels.shape[0]
# for x in path_edge:
#     pr1_index_count[index_arr.index(int(x[0]))] += 1
#     indices.append(index_arr.index(int(x[1])))
#     path_value.append(1)
# indices = np.array(indices)
# path_value = np.array(path_value, dtype=float)
#
# indptr = [0]
# for x in pr1_index_count:
#     indptr.append(indptr[len(indptr) - 1] + x)
# indptr = np.array(indptr)
# data['path'] = sparse.csr_matrix((path_value, indices, indptr), shape=(labels.shape[0], labels.shape[0]))
#
# commit_edge = np.genfromtxt(data_path + f'metapath/{start_time}-to-{end_time}/pr_commit_pr_edge.csv', delimiter=',',
#                             skip_header=True)
# commit_edge = commit_edge[:, 0:2]
# indices = []
# commit_value = []
# pr1_index_count = [0] * labels.shape[0]
# for x in commit_edge:
#     pr1_index_count[index_arr.index(int(x[0]))] += 1
#     indices.append(index_arr.index(int(x[1])))
#     commit_value.append(1)
# indices = np.array(indices)
# commit_value = np.array(commit_value, dtype=float)
#
# indptr = [0]
# for x in pr1_index_count:
#     indptr.append(indptr[len(indptr) - 1] + x)
# indptr = np.array(indptr)
#
# data['commit'] = sparse.csr_matrix((commit_value, indices, indptr), shape=(labels.shape[0], labels.shape[0]))
#
# review_edge = np.genfromtxt(data_path + f'metapath/{start_time}-to-{end_time}/pr_review_pr_edge.csv', delimiter=',',
#                             skip_header=True)
# review_edge = review_edge[:, 0:2]
# indices = []
# review_value = []
# pr1_index_count = [0] * labels.shape[0]
# for x in review_edge:
#     pr1_index_count[index_arr.index(int(x[0]))] += 1
#     indices.append(index_arr.index(int(x[1])))
#     review_value.append(1)
# indices = np.array(indices)
# review_value = np.array(review_value, dtype=float)
#
# indptr = [0]
# for x in pr1_index_count:
#     indptr.append(indptr[len(indptr) - 1] + x)
# indptr = np.array(indptr)
#
# data['review'] = sparse.csr_matrix((review_value, indices, indptr), shape=(labels.shape[0], labels.shape[0]))


# logits = getBinaryTensor(data_normal(logits)).long().cpu().numpy()
# labels = labels.cpu().numpy()
# count = 0
# for i in range(labels.shape[0]):
#     p = sum(numpy.logical_and(labels[i], logits[i]))
#     q = sum(numpy.logical_or(labels[i], logits[i]))
#     count += p / q
# return count / labels.shape[0]


# if labels[i][prediction[i][0]] == 1 or labels[i][prediction[i][1]] == 1 \
#         or labels[i][prediction[i][2]] == 1 or labels[i][prediction[i][3]] == 1 \
#         or labels[i][prediction[i][4]] == 1:
#     top5_count += 1
# if labels[i][prediction[i][0]] == 1:
#     mrr5_count += 1
# elif labels[i][prediction[i][1]] == 1:
#     mrr5_count += 1 / 2
# elif labels[i][prediction[i][2]] == 1:
#     mrr5_count += 1 / 3
# elif labels[i][prediction[i][3]] == 1:
#     mrr5_count += 1 / 4
# elif labels[i][prediction[i][4]] == 1:
#     mrr5_count += 1 / 5



# def score(logits, labels):
#     _, indices = torch.max(logits, dim=1)
#     prediction = indices.long().cpu().numpy()
#     labels = labels.cpu().numpy()
#     accuracy = (prediction == labels).sum() / len(prediction)
#     micro_f1 = f1_score(labels, prediction, average='micro')
#     macro_f1 = f1_score(labels, prediction, average='macro')
#
#     return accuracy, micro_f1, macro_f1
#
#
# def evaluate(model, g, features, labels, mask, loss_func):
#     model.eval()
#     with torch.no_grad():
#         logits = model(g, features)
#     loss = loss_func(logits[mask], labels[mask])
#     accuracy, micro_f1, macro_f1 = score(logits[mask], labels[mask])
#
#     return loss, accuracy, micro_f1, macro_f1
#


# fenlei
# train_acc, train_micro_f1, train_macro_f1 = score(logits[train_mask], labels[train_mask])
# val_loss, val_acc, val_micro_f1, val_macro_f1 = evaluate(model, g, features, labels, val_mask, loss_fcn)
# early_stop = stopper.step(val_loss.data.item(), val_acc, model)
# print('Epoch {:d} | Train Loss {:.4f} | Train Micro f1 {:.4f} | Train Macro f1 {:.4f} | '
#       'Val Loss {:.4f} | Val Micro f1 {:.4f} | Val Macro f1 {:.4f}'.format(
#     epoch + 1, loss.item(), train_micro_f1, train_macro_f1, val_loss.item(), val_micro_f1, val_macro_f1))

# fen lei
# test_loss, test_acc, test_micro_f1, test_macro_f1 = evaluate(model, g, features, labels, test_mask, loss_fcn)
# print('Test loss {:.4f} | Test Acc {:.4f} | Test Micro f1 {:.4f} | Test Macro f1 {:.4f}'.format(
#     test_loss.item(), test_acc, test_micro_f1, test_macro_f1))

def load_acm(remove_self_loop):
    url = 'dataset/ACM3025.pkl'
    data_path = get_download_dir() + '/ACM3025.pkl'
    # download(_get_dgl_url(url), path=data_path)

    with open(data_path, 'rb') as f:
        data = pickle.load(f)

    labels, features = torch.from_numpy(data['label'].todense()).long(), \
                       torch.from_numpy(data['feature'].todense()).float()
    num_classes = labels.shape[1]
    labels = labels.nonzero()[:, 1]

    if remove_self_loop:
        num_nodes = data['label'].shape[0]
        data['PAP'] = sparse.csr_matrix(data['PAP'] - np.eye(num_nodes))
        data['PLP'] = sparse.csr_matrix(data['PLP'] - np.eye(num_nodes))

    # Adjacency matrices for meta path based neighbors
    # (Mufei): I verified both of them are binary adjacency matrices with self loops
    author_g = dgl.from_scipy(data['PAP'])
    subject_g = dgl.from_scipy(data['PLP'])
    gs = [author_g, subject_g]

    train_idx = torch.from_numpy(data['train_idx']).long().squeeze(0)
    val_idx = torch.from_numpy(data['val_idx']).long().squeeze(0)
    test_idx = torch.from_numpy(data['test_idx']).long().squeeze(0)

    num_nodes = author_g.number_of_nodes()
    train_mask = get_binary_mask(num_nodes, train_idx)
    val_mask = get_binary_mask(num_nodes, val_idx)
    test_mask = get_binary_mask(num_nodes, test_idx)

    print('dataset loaded')
    pprint({
        'dataset': 'ACM',
        'train': train_mask.sum().item() / num_nodes,
        'val': val_mask.sum().item() / num_nodes,
        'test': test_mask.sum().item() / num_nodes
    })

    return gs, features, labels, num_classes, train_idx, val_idx, test_idx, \
           train_mask, val_mask, test_mask


def load_acm_raw(remove_self_loop):
    assert not remove_self_loop
    url = 'dataset/ACM.mat'
    data_path = get_download_dir() + '/ACM.mat'
    download(_get_dgl_url(url), path=data_path)

    data = sio.loadmat(data_path)
    p_vs_l = data['PvsL']  # paper-field?
    p_vs_a = data['PvsA']  # paper-author
    p_vs_t = data['PvsT']  # paper-term, bag of words
    p_vs_c = data['PvsC']  # paper-conference, labels come from that

    # We assign
    # (1) KDD papers as class 0 (data mining),
    # (2) SIGMOD and VLDB papers as class 1 (database),
    # (3) SIGCOMM and MOBICOMM papers as class 2 (communication)
    conf_ids = [0, 1, 9, 10, 13]
    label_ids = [0, 1, 2, 2, 1]

    p_vs_c_filter = p_vs_c[:, conf_ids]
    p_selected = (p_vs_c_filter.sum(1) != 0).A1.nonzero()[0]
    p_vs_l = p_vs_l[p_selected]
    p_vs_a = p_vs_a[p_selected]
    p_vs_t = p_vs_t[p_selected]
    p_vs_c = p_vs_c[p_selected]

    hg = dgl.heterograph({
        ('paper', 'pa', 'author'): p_vs_a.nonzero(),
        ('author', 'ap', 'paper'): p_vs_a.transpose().nonzero(),
        ('paper', 'pf', 'field'): p_vs_l.nonzero(),
        ('field', 'fp', 'paper'): p_vs_l.transpose().nonzero()
    })

    features = torch.FloatTensor(p_vs_t.toarray())

    pc_p, pc_c = p_vs_c.nonzero()
    labels = np.zeros(len(p_selected), dtype=np.int64)
    for conf_id, label_id in zip(conf_ids, label_ids):
        labels[pc_p[pc_c == conf_id]] = label_id
    labels = torch.LongTensor(labels)

    num_classes = 3

    float_mask = np.zeros(len(pc_p))
    for conf_id in conf_ids:
        pc_c_mask = (pc_c == conf_id)
        float_mask[pc_c_mask] = np.random.permutation(np.linspace(0, 1, pc_c_mask.sum()))
    train_idx = np.where(float_mask <= 0.2)[0]
    val_idx = np.where((float_mask > 0.2) & (float_mask <= 0.3))[0]
    test_idx = np.where(float_mask > 0.3)[0]

    num_nodes = hg.number_of_nodes('paper')
    train_mask = get_binary_mask(num_nodes, train_idx)
    val_mask = get_binary_mask(num_nodes, val_idx)
    test_mask = get_binary_mask(num_nodes, test_idx)

    return hg, features, labels, num_classes, train_idx, val_idx, test_idx, \
           train_mask, val_mask, test_mask


def data_normal(origin_data):
    d_min = origin_data.min()
    if d_min < 0:
        origin_data += torch.abs(d_min)
        d_min = origin_data.min()
    d_max = origin_data.max()
    dst = d_max - d_min
    norm_data = (origin_data - d_min).true_divide(dst)
    return norm_data


def getBinaryTensor(imgTensor, boundary=0.5):
    one = torch.ones_like(imgTensor)
    zero = torch.zeros_like(imgTensor)
    return torch.where(imgTensor > boundary, one, zero)