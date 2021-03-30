#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A graph generator based on the PC algorithm [Kalisch2007].

[Kalisch2007] Markus Kalisch and Peter Bhlmann. Estimating
high-dimensional directed acyclic graphs with the pc-algorithm. In The
Journal of Machine Learning Research, Vol. 8, pp. 613-636, 2007.
"""
from __future__ import print_function

import logging
import math
from itertools import combinations, permutations
import pandas as pd
import networkx as nx
import numpy as np
from gsq.ci_tests import ci_test_bin, ci_test_dis
from gsq.gsq_testdata import bin_data, dis_data
# from networkx.drawing.tests.test_pylab import plt
from scipy.stats import norm
import matplotlib.pyplot as plt

from utils.pageRank import PRIterator

_logger = logging.getLogger(__name__)


# 条件独立性检验
def gaussCItest(suffstat, x, y, S):
    S = list(S)
    C = pd.DataFrame(suffstat).astype(float).corr().values
    n = pd.DataFrame(suffstat).values.shape[0]

    cut_at = 0.9999999

    # 偏相关系数
    # S中没有点
    if len(S) == 0:
        r = C[x, y]

    # S中只有一个点 一阶偏相关系数
    elif len(S) == 1:
        a = (C[x, y] - C[x, S] * C[y, S])
        try:
            b = math.sqrt((1 - math.pow(C[y, S], 2)) * (1 - math.pow(C[x, S], 2)))
            r = a / b
        except:
            r = C[x, y]
    # 其实我没太明白这里是怎么求的，但R语言的pcalg包就是这样写的
    else:
        m = C[np.ix_([x] + [y] + S, [x] + [y] + S)]
        PM = np.linalg.pinv(m)
        r = -1 * PM[0, 1] / math.sqrt(abs(PM[0, 0] * PM[1, 1]))

    r = min(cut_at, max(-1 * cut_at, r))
    # Fisher’s z-transform
    res = math.sqrt(n - len(S) - 3) * .5 * math.log1p((2 * r) / (1 - r))
    # Φ^{-1}(1-α/2)
    return 2 * (1 - norm.cdf(abs(res)))


def _create_complete_graph(node_ids):
    """
    根据「节点列表」创建「图结构」
    Create a complete graph from the list of node ids.

    Args:
        node_ids: a list of node ids

    Returns:
        An undirected graph (as a networkx.Graph)
    """
    g = nx.Graph()
    g.add_nodes_from(node_ids)
    for (i, j) in combinations(node_ids, 2):
        g.add_edge(i, j)
    return g


def estimate_skeleton(indep_test_func, data_matrix, alpha, **kwargs):
    """
    根据统计信息预估骨架图，
    1. 根据原始数据转换成无方向的的图
    2. 遍历所有的有向边，进行独立性检测，当独立性检测结果大于 alpha 时，删除边
    Estimate a skeleton graph from the statistical information.

    Args:
        indep_test_func: 独立性检测方法
        the function name for a conditional independency test.
        data_matrix: data (as a numpy array).
        alpha: the significance level.
        kwargs:
            'max_reach': maximum value of l (see the code).  The
                value depends on the underlying distribution.
            'method': if 'stable' given, use stable-PC algorithm
                (see [Colombo2014]).
            'init_graph': initial structure of skeleton graph
                (as a networkx.Graph). If not specified,
                a complete graph is used.
            other parameters may be passed depending on the
                indep_test_func()s.
    Returns:
        g: a skeleton graph (as a networkx.Graph).
        sep_set: a separation set (as an 2D-array of set()).

    [Colombo2014] Diego Colombo and Marloes H Maathuis. Order-independent
    constraint-based causal structure learning. In The Journal of Machine
    Learning Research, Vol. 15, pp. 3741-3782, 2014.
    """

    def method_stable(kwargs):
        return ('method' in kwargs) and kwargs['method'] == "stable"

    node_ids = range(data_matrix.shape[1])
    node_size = data_matrix.shape[1]
    sep_set = [[set() for i in range(node_size)] for j in range(node_size)]
    if 'init_graph' in kwargs:
        g = kwargs['init_graph']
        if not isinstance(g, nx.Graph):
            raise ValueError
        elif not g.number_of_nodes() == len(node_ids):
            raise ValueError('init_graph not matching data_matrix shape')
        for (i, j) in combinations(node_ids, 2):
            if not g.has_edge(i, j):
                sep_set[i][j] = None
                sep_set[j][i] = None
    else:
        # 构造无向边的图
        g = _create_complete_graph(node_ids)

    l = 0
    while True:
        cont = False
        remove_edges = []
        # 遍历 node_ids 的全排列，去遍历所有可能存在的边（因为是有向边，所以是排列）
        for (i, j) in permutations(node_ids, 2):
            # 即其相邻节点
            adj_i = list(g.neighbors(i))
            # 如果 j 是 i 的相邻节点，则删除；否则继续下一次遍历
            if j not in adj_i:
                continue
            else:
                adj_i.remove(j)
            # The process stops if all neighborhoods in the current graph are smaller than the size of the conditional set.
            if len(adj_i) >= l:
                # _logger.debug('testing %s and %s' % (i, j))
                _logger.debug('测试 %s 节点和 %s 节点' % (i, j))
                # _logger.debug('neighbors of %s are %s' % (i, str(adj_i)))
                _logger.debug('%s 的相邻节点有 %s' % (i, str(adj_i)))
                if len(adj_i) < l:
                    continue
                # 存在任意节点 k（其实不是节点 k，也可能是节点集合 k），使 i-j 满足条件独立性，那么需要删除 i-j
                for k in combinations(adj_i, l):
                    _logger.debug('indep prob of %s and %s with subset %s'
                                  % (i, j, str(k)))
                    # 求独立性检测概率
                    # p_val = indep_test_func(data_matrix, i, j, set(k), **kwargs)
                    p_val = gaussCItest(data_matrix, i, j, set(k))
                    _logger.debug('独立性检测概率为 %s' % str(p_val))
                    # 如果概率值大于 alpha 超参数，则移除 i->j 的边
                    if p_val > alpha:
                        if g.has_edge(i, j):
                            _logger.debug('p: 移除边 (%s, %s)' % (i, j))
                            if method_stable(kwargs):
                                remove_edges.append((i, j))
                            else:
                                g.remove_edge(i, j)
                        # 求并集，即将集合 k 加入到 sep_set 中，由于本步骤不考虑方向，因此 i->j j->i 都采取这种策略
                        sep_set[i][j] |= set(k)
                        sep_set[j][i] |= set(k)
                        break
                cont = True
        l += 1
        if method_stable(kwargs):
            g.remove_edges_from(remove_edges)
        if cont is False:
            break
        if ('max_reach' in kwargs) and (l > kwargs['max_reach']):
            break

    return (g, sep_set)


def estimate_cpdag(skel_graph, sep_set):
    """

    Estimate a CPDAG from the skeleton graph and separation sets
    returned by the estimate_skeleton() function.

    Args:
        skel_graph: A skeleton graph (an undirected networkx.Graph).
        sep_set: An 2D-array of separation set.
            The contents look like something like below.
                sep_set[i][j] = set([k, l, m])

    Returns:
        An estimated DAG.
    """
    # 将骨架图变成有方向的
    dag = skel_graph.to_directed()
    node_ids = skel_graph.nodes()
    # 提取所有的 i,j 组合
    for (i, j) in combinations(node_ids, 2):
        # 寻找满足关系的 k，i → k ← j
        adj_i = set(dag.successors(i))
        if j in adj_i:
            continue
        adj_j = set(dag.successors(j))
        if i in adj_j:
            continue
        # 程序稳定的验证，无实际意义
        if sep_set[i][j] is None:
            continue
        # 叮！ 找到了 K 可能的集合
        common_k = adj_i & adj_j
        for k in common_k:
            # k 不能存在于 sep_set，由于上一步中无方向，因此只需要判断一个即可
            if k not in sep_set[i][j]:
                # 如果 k->i，那么j->i，这是不合理的
                if dag.has_edge(k, i):
                    _logger.debug('S: 移除边 (%s, %s)' % (k, i))
                    dag.remove_edge(k, i)
                # 同上
                if dag.has_edge(k, j):
                    _logger.debug('S: remove edge (%s, %s)' % (k, j))
                    dag.remove_edge(k, j)

    def _has_both_edges(dag, i, j):
        return dag.has_edge(i, j) and dag.has_edge(j, i)

    def _has_any_edge(dag, i, j):
        return dag.has_edge(i, j) or dag.has_edge(j, i)

    def _has_one_edge(dag, i, j):
        return ((dag.has_edge(i, j) and (not dag.has_edge(j, i))) or
                (not dag.has_edge(i, j)) and dag.has_edge(j, i))

    def _has_no_edge(dag, i, j):
        return (not dag.has_edge(i, j)) and (not dag.has_edge(j, i))

    # For all the combination of nodes i and j, apply the following
    # rules.
    # 开始使用三种规则了
    old_dag = dag.copy()
    while True:
        # 提取所有的 i,j 组合
        for (i, j) in combinations(node_ids, 2):
            # Rule 1: Orient i-j into i->j whenever there is an arrow k->i
            # such that k and j are nonadjacent.
            #
            # Check if i-j.
            # 检验是否存在 i-j 无向边
            if _has_both_edges(dag, i, j):
                # Look all the predecessors of i.
                for k in dag.predecessors(i):
                    # Skip if there is an arrow i->k.
                    if dag.has_edge(i, k):
                        continue
                    # Skip if k and j are adjacent.
                    if _has_any_edge(dag, k, j):
                        continue
                    # Make i-j into i->j
                    _logger.debug('R1: remove edge (%s, %s)' % (j, i))
                    dag.remove_edge(j, i)
                    break

            # Rule 2: Orient i-j into i->j whenever there is a chain
            # i->k->j.
            #
            # Check if i-j.
            if _has_both_edges(dag, i, j):
                # Find nodes k where k is i->k.
                succs_i = set()
                for k in dag.successors(i):
                    if not dag.has_edge(k, i):
                        succs_i.add(k)
                # Find nodes j where j is k->j.
                preds_j = set()
                for k in dag.predecessors(j):
                    if not dag.has_edge(j, k):
                        preds_j.add(k)
                # Check if there is any node k where i->k->j.
                if len(succs_i & preds_j) > 0:
                    # Make i-j into i->j
                    _logger.debug('R2: remove edge (%s, %s)' % (j, i))
                    dag.remove_edge(j, i)

            # Rule 3: Orient i-j into i->j whenever there are two chains
            # i-k->j and i-l->j such that k and l are nonadjacent.
            #
            # Check if i-j.
            if _has_both_edges(dag, i, j):
                # Find nodes k where i-k.
                adj_i = set()
                for k in dag.successors(i):
                    if dag.has_edge(k, i):
                        adj_i.add(k)
                # For all the pairs of nodes in adj_i,
                for (k, l) in combinations(adj_i, 2):
                    # Skip if k and l are adjacent.
                    if _has_any_edge(dag, k, l):
                        continue
                    # Skip if not k->j.
                    if dag.has_edge(j, k) or (not dag.has_edge(k, j)):
                        continue
                    # Skip if not l->j.
                    if dag.has_edge(j, l) or (not dag.has_edge(l, j)):
                        continue
                    # Make i-j into i->j.
                    _logger.debug('R3: remove edge (%s, %s)' % (j, i))
                    dag.remove_edge(j, i)
                    break

            # Rule 4: Orient i-j into i->j whenever there are two chains
            # i-k->l and k->l->j such that k and j are nonadjacent.
            #
            # However, this rule is not necessary when the PC-algorithm
            # is used to estimate a DAG.

        if nx.is_isomorphic(dag, old_dag):
            break
        old_dag = dag.copy()

    return dag


def construct_service_dependency_diagram(b):
    data = np.array(b.iloc[:, :])[:, :]
    columns = list(b.columns)[:]
    columns_mapping = {i: str(column) for i, column in enumerate(columns)}

    (g, sep_set) = estimate_skeleton(indep_test_func=ci_test_dis,
                                     data_matrix=data,
                                     alpha=0.05)
    g = estimate_cpdag(skel_graph=g, sep_set=sep_set)
    return g, columns_mapping


def get_root_cause(g):
    """
    通过关系图获取根因列表
    Args:
        g: 关系图

    Returns: 根因列表

    """
    result = list()
    node_ids = g.nodes()
    # 获取原因最多的节点
    max_pre_node, max_pre_size = None, 0
    for node_id in node_ids:
        if len(list(g.predecessors(node_id))) > max_pre_size:
            max_pre_node = node_id
            max_pre_size = len(list(g.predecessors(node_id)))
    # 层次遍历
    node_filter, node_queue = {max_pre_node}, list([max_pre_node])
    while node_queue:
        node_now = node_queue.pop(0)
        if not g.predecessors(node_now):
            result.append(node_now)
            continue
        is_pre_not_filter = False
        for k in g.predecessors(node_now):
            if k not in node_filter:
                is_pre_not_filter = True
                node_filter.add(k)
                node_queue.append(k)
        # 如果所有的上游节点都在 filter 中，将当前节点加入 result，避免 result 为空的情况
        if not is_pre_not_filter:
            result.append(node_now)
    return result


if __name__ == '__main__':

    # 打印日志，不要注释掉
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    _logger.setLevel(logging.DEBUG)
    _logger.addHandler(ch)

    # mock 原始数据
    dm = np.array(bin_data).reshape((5000, 5))
    (g, sep_set) = estimate_skeleton(indep_test_func=ci_test_bin,
                                     data_matrix=dm,
                                     alpha=0.01)
    #
    g = estimate_cpdag(skel_graph=g, sep_set=sep_set)
    g_answer = nx.DiGraph()
    g_answer.add_nodes_from([0, 1, 2, 3, 4])
    g_answer.add_edges_from([(0, 1), (2, 3), (3, 2), (3, 1),
                             (2, 4), (4, 2), (4, 1)])
    print('Edges are:', g.edges(), end='')
    if nx.is_isomorphic(g, g_answer):
        print(' => GOOD')
    else:
        print(' => WRONG')
        print('True edges should be:', g_answer.edges())

    # 又 mock 了多点的数据进行测试
    dm = np.array(dis_data).reshape((10000, 5))
    (g, sep_set) = estimate_skeleton(indep_test_func=ci_test_dis,
                                     data_matrix=dm,
                                     alpha=0.01,
                                     levels=[3, 2, 3, 4, 2])
    g = estimate_cpdag(skel_graph=g, sep_set=sep_set)
    nx.draw(g,pos=spring_layout(g, prog='dot'),  # pos 指的是布局,主要有spring_layout,random_layout,circle_layout,shell_layout
            node_color='g',  # node_color指节点颜色,有rbykw,同理edge_color
            edge_color='r',
            with_labels=True)
    plt.show()

    pr = PRIterator(g)
    page_ranks = pr.page_rank()
    print("The final page rank is\n", page_ranks)

    g_answer = nx.DiGraph()
    g_answer.add_nodes_from([0, 1, 2, 3, 4])
    g_answer.add_edges_from([(0, 2), (1, 2), (1, 3), (4, 3)])
    print('Edges are:', g.edges(), end='')
    if nx.is_isomorphic(g, g_answer):
        print(' => GOOD')
    else:
        print(' => WRONG')
        print('True edges should be:', g_answer.edges())
