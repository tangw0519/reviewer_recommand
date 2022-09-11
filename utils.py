import datetime
import dgl
import errno
import numpy as np
import os
import pickle
import random

import pandas as pd
import torch

from dgl.data.utils import download, get_download_dir, _get_dgl_url
from pprint import pprint
from scipy import sparse
from scipy import io as sio

# The configuration below is from the paper.
default_configure = {
    'lr': 0.005,  # Learning rate
    'num_heads': [8],  # Number of attention heads for node-level attention
    # 'hidden_units': 8,
    'hidden_units': 512,
    'dropout': 0.6,
    'weight_decay': 0.001,
    'num_epochs': 200,
    'patience': 100
}


def setup(args):
    args.update(default_configure)
    set_random_seed(args['seed'])
    args['dataset'] = 'bitcoin'
    args['start_time'] = '2017-01-01'
    args['end_time'] = '2020-06-30'
    args['device'] = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    args['log_dir'] = setup_log_dir(args)
    return args


sampling_configure = {
    'batch_size': 20
}
datasets = ['bitcoin',
            'scikit-learn',
            'react',
            'node',
            'tensorflow'
            ]


def set_random_seed(seed=0):
    """Set random seed.
    Parameters
    ----------
    seed : int
        Random seed to use
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)


def mkdir_p(path, log=True):
    """Create a directory for the specified path.
    Parameters
    ----------
    path : str
        Path name
    log : bool
        Whether to print result for directory creation
    """
    try:
        os.makedirs(path)
        if log:
            print('Created directory {}'.format(path))
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path) and log:
            print('Directory {} already exists.'.format(path))
        else:
            raise


def get_date_postfix():
    """Get a date based postfix for directory name.
    Returns
    -------
    post_fix : str
    """
    dt = datetime.datetime.now()
    post_fix = '{}_{:02d}-{:02d}-{:02d}'.format(
        dt.date(), dt.hour, dt.minute, dt.second)

    return post_fix


def setup_log_dir(args, sampling=False):
    """Name and create directory for logging.
    Parameters
    ----------
    args : dict
        Configuration
    Returns
    -------
    log_dir : str
        Path for logging directory
    sampling : bool
        Whether we are using sampling based training
    """
    date_postfix = get_date_postfix()
    log_dir = os.path.join(
        args['log_dir'],
        '{}_{}'.format(args['dataset'], date_postfix))

    if sampling:
        log_dir = log_dir + '_sampling'

    # mkdir_p(log_dir)
    return log_dir


def setup_for_sampling(args):
    args.update(default_configure)
    args.update(sampling_configure)
    set_random_seed()
    args['device'] = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    args['log_dir'] = setup_log_dir(args, sampling=True)
    return args


def get_binary_mask(total_size, indices):
    mask = torch.zeros(total_size)
    mask[indices] = 1
    return mask.byte()


def get_metapath(dataset, index_arr, path_name, node_num, start_time, end_time):
    data_path = f'data/{dataset}/'
    path_edge = np.genfromtxt(data_path + f'metapath/{start_time}-to-{end_time}/pr_{path_name}_pr_edge.csv',
                              delimiter=',',
                              skip_header=True)
    path_weight = path_edge[:, -1]
    path_edge = path_edge[:, 0:2]

    indices = []
    path_value = []
    pr1_index_count = [0] * node_num
    k = 0
    for x in path_edge:
        pr1_index_count[index_arr.index(int(x[0]))] += 1
        indices.append(index_arr.index(int(x[1])))
        path_value.append(path_weight[k])
        k += 1
    indices = np.array(indices)
    path_value = np.array(path_value, dtype=float)

    indptr = [0]
    for x in pr1_index_count:
        indptr.append(indptr[len(indptr) - 1] + x)
    indptr = np.array(indptr)
    return sparse.csr_matrix((path_value, indices, indptr), shape=(node_num, node_num))


def get_train_all_metapath(arr, remove_self_loop, dataset, index_arr, node_num, start_time, end_time):
    data = {}
    gs = []
    for name in arr:
        data[name] = get_metapath(dataset, index_arr, name, node_num, start_time, end_time)
        if not remove_self_loop:
            data[name] = sparse.csr_matrix(data[name] + np.eye(node_num))
        gs.append(dgl.from_scipy(data[name]))
    return gs, data


def load_self_data(dataset, remove_self_loop, start_time, end_time):
    data_path = f'data/{dataset}/'
    if not os.path.exists(data_path + f'features/{start_time}-to-{end_time}') or not os.path.exists(
            data_path + f'metapath/{start_time}-to-{end_time}'):
        print('当前数据集尚未process')
        return

    features_raw = np.genfromtxt(data_path + f'features/{start_time}-to-{end_time}/pr_features.csv', delimiter=',')
    features = torch.from_numpy(features_raw[:, 1:]).float()
    index_arr = list(np.array(features_raw[:, 0], dtype=int))
    # duo biao qian
    labels_raw = np.genfromtxt(data_path + f'features/{start_time}-to-{end_time}/pr_labels.csv', delimiter=',')
    labels = torch.from_numpy(labels_raw[:, 1:]).long()
    num_classes = len(labels_raw[0]) - 1

    loss_self = np.genfromtxt(data_path + f'loss/{start_time}-to-{end_time}/pr_active_1.csv', delimiter=',')
    loss = torch.from_numpy(loss_self[:, 1:]).float()

    metapath = ['path', 'commit']
    gs, data = get_train_all_metapath(metapath, remove_self_loop, dataset, index_arr, labels.shape[0], start_time,
                                      end_time)

    rate1 = int(labels.shape[0] * 0.8)
    rate2 = int(labels.shape[0] * 0.9)
    # 打乱，不按时间顺序
    shuffled_index = np.random.permutation(labels.shape[0])
    data['train_idx'] = shuffled_index[:rate1]
    data['val_idx'] = shuffled_index[rate1:rate2]
    data['test_idx'] = shuffled_index[rate2:]
    # 不打乱 按时间来分割
    # data_index = np.array(list(range(0, labels.shape[0])))
    # data['train_idx'] = data_index[:rate1]
    # data['val_idx'] = data_index[rate1:rate2]
    # data['test_idx'] = data_index[rate2:]

    train_idx = torch.from_numpy(data['train_idx']).long().squeeze(0)
    val_idx = torch.from_numpy(data['val_idx']).long().squeeze(0)
    test_idx = torch.from_numpy(data['test_idx']).long().squeeze(0)

    num_nodes = gs[0].number_of_nodes()
    train_mask = get_binary_mask(num_nodes, train_idx)
    val_mask = get_binary_mask(num_nodes, val_idx)
    test_mask = get_binary_mask(num_nodes, test_idx)

    print('dataset loaded')
    pprint({
        'dataset': dataset,
        'time_range': start_time + '~' + end_time,
        'train': train_mask.sum().item() / num_nodes,
        'val': val_mask.sum().item() / num_nodes,
        'test': test_mask.sum().item() / num_nodes,
        'classes': num_classes,
        'pr nodes': labels.shape[0],
        'pr features': features.shape[1],
        'metapath': ','.join(metapath)
    })

    return gs, features, labels,loss, num_classes, train_idx, val_idx, test_idx, \
           train_mask, val_mask, test_mask


def load_data(dataset, remove_self_loop=False, start_time='', end_time=''):
    # if dataset == 'ACM':
    #     return load_acm(remove_self_loop)
    # elif dataset == 'ACMRaw':
    #     return load_acm_raw(remove_self_loop)
    # el
    if dataset in datasets:
        return load_self_data(dataset, remove_self_loop, start_time, end_time)
    else:
        return NotImplementedError('Unsupported dataset {}'.format(dataset))


class EarlyStopping(object):
    def __init__(self, patience=10):
        dt = datetime.datetime.now()
        self.filename = 'result/early_stop_{}_{:02d}-{:02d}-{:02d}.pth'.format(
            dt.date(), dt.hour, dt.minute, dt.second)
        self.patience = patience
        self.counter = 0
        self.best_acc = None
        self.best_loss = None
        self.early_stop = False

    def step(self, loss, acc, model):
        if self.best_loss is None:
            self.best_acc = acc
            self.best_loss = loss
            self.save_checkpoint(model)
        elif (loss > self.best_loss) and (acc < self.best_acc):
            self.counter += 1
            print(f'EarlyStopping counter: {self.counter} out of {self.patience}')
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            if (loss <= self.best_loss) and (acc >= self.best_acc):
                self.save_checkpoint(model)
            self.best_loss = np.min((loss, self.best_loss))
            self.best_acc = np.max((acc, self.best_acc))
            self.counter = 0
        return self.early_stop

    def save_checkpoint(self, model):
        """Saves model when validation loss decreases."""
        torch.save(model.state_dict(), self.filename)

    def load_checkpoint(self, model):
        """Load the latest checkpoint."""
        model.load_state_dict(torch.load(self.filename))
