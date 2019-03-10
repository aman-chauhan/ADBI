from sklearn.metrics.pairwise import cosine_similarity
from functools import reduce
import pandas as pd
import numpy as np
import itertools
import igraph
import sys
import os


store = None


def init(attr_path, edge_path):
    attrs = pd.read_csv(attr_path)
    edges = open(edge_path, 'r').readlines()
    edges = [x.strip().split(' ') for x in edges]
    edges = [(int(x[0]), int(x[1])) for x in edges]
    g = igraph.Graph()
    g.add_vertices(attrs.shape[0])
    g.add_edges(edges)
    return g, attrs.values


def attr_q(c, c_list):
    global store
    sum = 0.0
    for i, cluster in enumerate(c):
        if c_list is not None and i not in c_list:
            continue
        for v_i, v_j in itertools.combinations(cluster, 2):
            sum += (store[v_i, v_j] / len(cluster))
    return sum


def iterate(g, base_c, base_q_1, base_q_2, alpha):
    cnt = 0
    # max 15 iterations
    while(cnt < 15):
        q = alpha * base_q_1 + (1 - alpha) * base_q_2 if alpha != 1 else base_q_1
        for v_i in g.vs.indices:
            m = base_c.membership
            max_delta_q = 0
            max_c = None
            for v_j in g.vs.indices:
                if v_i != v_j and m[v_i] != m[v_j]:
                    n = list(m)
                    c1 = n[v_i]
                    c2 = n[v_j]
                    n[v_i] = n[v_j]
                    c = igraph.clustering.VertexClustering(g, n)
                    delta_q_1 = c.recalculate_modularity() - base_q_1
                    delta_q_2 = attr_q(c, [c1, c2]) - attr_q(base_c, [c1, c2]) if alpha != 1 else 0
                    delta_q = alpha * delta_q_1 + (1 - alpha) * delta_q_2 if alpha != 1 else delta_q_1
                    if delta_q > max_delta_q:
                        max_delta_q = delta_q
                        max_c = c
                    del n
            if max_c is not None:
                base_c = max_c
                base_q_1 = max_c.recalculate_modularity()
                base_q_2 = attr_q(max_c, None) if alpha != 1 else 0
        nq = alpha * base_q_1 + (1 - alpha) * base_q_2 if alpha != 1 else base_q_1
        if nq == q:
            break
        cnt += 1
    return base_c


def main(alpha):
    global store
    attr_path = os.path.join('data', 'fb_caltech_small_attrlist.csv')
    edge_path = os.path.join('data', 'fb_caltech_small_edgelist.txt')
    g, attrs = init(attr_path, edge_path)
    store = cosine_similarity(attrs, attrs)

    # phase 1
    # initialize clusters
    base_c = igraph.clustering.VertexClustering(g, [x for x in range(g.vcount())])
    base_q_1 = base_c.recalculate_modularity()
    base_q_2 = attr_q(base_c, None)
    # iterate
    base_c = iterate(g, base_c, base_q_1, base_q_2, alpha)

    cmap = {}
    imap = {}
    for i, x in enumerate(sorted(set(base_c.membership))):
        cmap[x] = i
        imap[i] = x

    g.contract_vertices([cmap[x] for x in base_c.membership])
    g = g.simplify()

    cattrs = []
    for i in range(len(imap)):
        cattrs.append(attrs[base_c[imap[i]]].mean(0).tolist())
    cattrs = np.asarray(cattrs)
    store = cosine_similarity(cattrs, cattrs)

    # phase 2
    # initialize clusters
    base_c2 = igraph.clustering.VertexClustering(g, [x for x in range(g.vcount())])
    base_q_1 = base_c2.recalculate_modularity()
    base_q_2 = attr_q(base_c2, None)
    # iterate
    base_c2 = iterate(g, base_c2, base_q_1, base_q_2, alpha)

    c = list(map(lambda x: reduce(lambda x, y: x + y, map(lambda y: base_c[imap[y]], x)),
                 filter(lambda x: len(x) > 0, base_c2)))
    name_map = {0: 'communities_0.txt',
                0.5: 'communities_5.txt',
                1: 'communities_1.txt'}
    with open(name_map[alpha], 'w') as fp:
        for cluster in c:
            fp.write(','.join([str(x) for x in cluster]) + '\n')


if __name__ == '__main__':
    main(float(sys.argv[1]))
