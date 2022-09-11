import numpy
import torch
from sklearn.metrics import f1_score

from self_loss import WeightCroLoss
from utils import load_data, EarlyStopping


def multi_label_score(logits, labels):
    _, indices = torch.max(logits, dim=1)
    prediction = indices.long().cpu().numpy()
    labels = labels.cpu().numpy()
    top1_count = 0
    for i in range(labels.shape[0]):
        if labels[i][prediction[i]] == 1:
            top1_count += 1
    top1 = top1_count / labels.shape[0]
    mrr1 = top1

    _, indices = logits.topk(k=3, dim=1)
    prediction = indices.long().cpu().numpy()
    top3_count = 0
    mrr3_count = 0
    for i in range(labels.shape[0]):
        for j in range(3):
            if labels[i][prediction[i][j]] == 1:
                top3_count += 1
                mrr3_count += 1 / (j + 1)
                break

    top3 = top3_count / labels.shape[0]
    mrr3 = mrr3_count / labels.shape[0]

    _, indices = logits.topk(k=5, dim=1)
    prediction = indices.long().cpu().numpy()
    top5_count = 0
    mrr5_count = 0
    for i in range(labels.shape[0]):
        for j in range(5):
            if labels[i][prediction[i][j]] == 1:
                top5_count += 1
                mrr5_count += 1 / (j + 1)
                break

    top5 = top5_count / labels.shape[0]
    mrr5 = mrr5_count / labels.shape[0]

    return top1, top3, top5, mrr1, mrr3, mrr5


def multi_label_evaluate(model, g, features, labels, mask, loss_func):
    model.eval()
    with torch.no_grad():
        logits = model(g, features)
    loss = loss_func(logits[mask], labels[mask])
    top1, top3, top5, mrr1, mrr3, mrr5 = multi_label_score(logits[mask], labels[mask])
    return loss, top1, top3, top5, mrr1, mrr3, mrr5


def main(args):
    # If args['hetero'] is True, g would be a heterogeneous graph.
    # Otherwise, it will be a list of homogeneous graphs.
    g, features, labels, losses, num_classes, train_idx, val_idx, test_idx, train_mask, \
    val_mask, test_mask = load_data(args['dataset'], start_time=args['start_time'], end_time=args['end_time'])

    if hasattr(torch, 'BoolTensor'):
        train_mask = train_mask.bool()
        val_mask = val_mask.bool()
        test_mask = test_mask.bool()

    features = features.to(args['device'])
    labels = labels.to(args['device'])
    losses = losses.to(args['device'])
    train_mask = train_mask.to(args['device'])
    val_mask = val_mask.to(args['device'])
    test_mask = test_mask.to(args['device'])
    # 数据集是异构图，并没有给出邻接矩阵，需要再构造
    if args['hetero']:
        from model_hetero import HAN
        model = HAN(meta_paths=[['pa', 'ap'], ['pf', 'fp']],
                    in_size=features.shape[1],
                    hidden_size=args['hidden_units'],
                    out_size=num_classes,
                    num_heads=args['num_heads'],
                    dropout=args['dropout']).to(args['device'])
        g = g.to(args['device'])
    else:
        from model import HAN
        model = HAN(num_meta_paths=len(g),
                    in_size=features.shape[1],
                    hidden_size=args['hidden_units'],
                    out_size=num_classes,
                    num_heads=args['num_heads'],
                    dropout=args['dropout']).to(args['device'])
        g = [graph.to(args['device']) for graph in g]

    stopper = EarlyStopping(patience=args['patience'])
    loss_fcn = torch.nn.MultiLabelSoftMarginLoss(reduction='mean')
    # loss_fcn = WeightCroLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args['lr'],
                                 weight_decay=args['weight_decay'])

    for epoch in range(args['num_epochs']):
        model.train()
        logits = model(g, features)
        loss = loss_fcn(logits[train_mask], labels[train_mask])
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # duo fen lei
        top1_train_acc, top3_train_acc, top5_train_acc, mrr1_train, mrr3_train, mrr5_train = multi_label_score(
            logits[train_mask], labels[train_mask])
        val_loss, top1_val_acc, top3_val_acc, top5_val_acc, mrr1_val, mrr3_val, mrr5_val = multi_label_evaluate(model,
                                                                                                                g,
                                                                                                                features,
                                                                                                                labels,
                                                                                                                val_mask,
                                                                                                                loss_fcn)
        early_stop = stopper.step(val_loss.data.item(), top1_val_acc, model)
        print('--------------------------------------------------- Epoch {:d} '
              '---------------------------------------------------'.format(epoch + 1))
        print('Train Loss {:.4f} | Top1 Train Acc {:.4f} | Top3 Train Acc {:.4f} | Top5 Train Acc {:.4f} | MRR1 Train '
              'Acc {:.4f} | MRR3 Train '
              'Acc {:.4f} | MRR5 Train '
              'Acc {:.4f}'.format(
            loss.item(), top1_train_acc, top3_train_acc, top5_train_acc, mrr1_train, mrr3_train, mrr5_train))
        print(
            'Val Loss {:.4f} | Top1 Val Acc {:.4f} | Top3 Val Acc {:.4f} | Top5 Val Acc {:.4f} | MRR1 Val Acc {:.4f} '
            '| MRR3 Val Acc {:.4f} | MRR5 Val Acc {:.4f}'.format(
                val_loss, top1_val_acc, top3_val_acc, top5_val_acc, mrr1_val, mrr3_val, mrr5_val))

        if early_stop:
            break

    stopper.load_checkpoint(model)

    # zi ding yi
    test_loss, top1_test_acc, top3_test_acc, top5_test_acc, mrr1_test, mrr3_test, mrr5_test = multi_label_evaluate(
        model, g, features, labels,
        test_mask,
        loss_fcn)
    print(
        'Test loss {:.4f} | Top1 Test Acc {:.4f} | Top3 Test Acc {:.4f} | Top5 Test Acc {:.4f} | MRR1 Test Acc {:.4f} '
        '| MRR3 Test Acc {:.4f} | MRR5 Test Acc {:.4f}'.format(
            test_loss.item(), top1_test_acc, top3_test_acc, top5_test_acc, mrr1_test, mrr3_test, mrr5_test))


if __name__ == '__main__':
    import argparse

    from utils import setup

    parser = argparse.ArgumentParser('HAN')
    parser.add_argument('-s', '--seed', type=int, default=1,
                        help='Random seed')
    parser.add_argument('-ld', '--log-dir', type=str, default='results',
                        help='Dir for saving training results')
    parser.add_argument('--hetero', action='store_true', default=False,
                        help='Use metapath coalescing with DGL\'s own dataset')
    args = parser.parse_args().__dict__

    args = setup(args)

    main(args)
