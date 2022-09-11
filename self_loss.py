import math

import torch
import torch.nn as nn
import torch.nn.functional as func


class WeightCroLoss(nn.Module):
    def __init__(self):
        super(WeightCroLoss, self).__init__()

    def forward(self, pred, labels, weight=1):
        # _, indices = torch.max(pred, dim=1)
        prediction = pred.long().cpu().numpy()
        labels = labels.cpu().numpy()
        result_loss = 0
        for i in range(labels.shape[0]):
            c_pred = prediction[i]
            c_label = labels[i]
            temp_loss = 0
            for j in range(len(c_label)):
                temp_loss -= c_pred[j] * math.log(math.exp(c_label[j]) / (1 + math.exp(c_label[j]))) + (
                            1 - c_pred[j]) * math.log(1 / (1 + math.exp(c_label[j])))
            result_loss += temp_loss
        return result_loss
        # weight_xy = torch.zeros(size=(pred.shape[0], pred.shape[1]))
        # # weight_xy = weight_xy.__deepcopy__(weight)
        # log = func.log_softmax(pred, dim=1)
        # log = log * weight_xy
        #
        # labels = labels.reshape(-1, 1)
        # log = log.gather(1, labels)
        # result_loss = -1 * log
        # result_loss = result_loss.mean()
        # return result_loss
