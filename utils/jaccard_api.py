import re
from copy import deepcopy

import jieba
import jieba.analyse


def log_preprocess(log, paramregex, eraseRex):
    for currentRex in eraseRex:
        log = re.sub(currentRex, '', log)
    for currentRex in paramregex:
        log = re.sub(currentRex, '<*>', log)
    return log


def generate_cidian_jaccard(exception_window_log_, stopkeyword):
    log_dic = []
    fenci = jieba.cut_for_search(exception_window_log_)
    for fc in fenci:
        if fc not in log_dic and fc not in stopkeyword and not re.search(' +', fc):
            log_dic.append(fc)
    return log_dic
