from sklearn.metrics.pairwise import cosine_similarity
from functools import reduce
import pandas as pd
import numpy as np
import itertools
import igraph
import sys
import os


store = None

# function to initialize the graph and return the attribute data
def init(attr_path, edge_path):
    attrs = pd.read_csv(attr_path)
    edges = open(edge_path, 'r').readlines()
    edges = [x.strip().split(' ') for x in edges]
    edges = [(int(x[0]), int(x[1])) for x in edges]
    g = igraph.Graph()
    g.add_vertices(attrs.shape[0])
    g.add_edges(edges)
    return g, attrs.values

# given list of clusters c, cluster clstr, and vertex x
# 1. Calculate overall Qattr when clstr is None
# 2. Calculate delta_Qattr when clstr is not None and a vertex x is given
def attr_q(c, clstr = None, x = None):
    global store
    sum = 0.0
    if clstr is not None:
        for i in c[clstr]:
            sum += store[x, i]
        sum /= len(c[clstr])
    else:
        for i, cluster in enumerate(c):
            for v_i, v_j in itertools.combinations(cluster, 2):
                sum += (store[v_i, v_j] / len(cluster))
    return sum


# function to iterate for 15 iterations unless converged
# takes as input the graph g, original clustering base_c,
# newman modularity of clustering base_q_1,
# attribute modularity of clustering base_q_2, and alpha
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
                    # move the vertex in a copy of member list and calculate delta
                    n = list(m)
                    n[v_i] = n[v_j]
                    c = igraph.clustering.VertexClustering(g, n)
                    # delta Q newman
                    delta_q_1 = c.recalculate_modularity() - base_q_1
                    # delta Q attribute, ignoring the change in attribute modularity of m[v_i]
                    delta_q_2 = attr_q(base_c, m[v_j], v_i) if alpha != 1 else 0
                    # composite delta
                    delta_q = alpha * delta_q_1 + (1 - alpha) * delta_q_2 if alpha != 1 else delta_q_1
                    if delta_q > max_delta_q:
                        max_delta_q = delta_q
                        max_c = c
                    # deleting copy member list for memory cleanup
                    del n
            # replace base clustering if an improvement was found
            if max_c is not None:
                base_c = max_c
                base_q_1 = max_c.recalculate_modularity()
                base_q_2 = attr_q(max_c) if alpha != 1 else 0
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
    base_q_2 = attr_q(base_c)
    # iterate
    base_c = iterate(g, base_c, base_q_1, base_q_2, alpha)

    # maintaining mapping between old and new clusters
    cmap = {}
    imap = {}
    for i, x in enumerate(sorted(set(base_c.membership))):
        cmap[x] = i
        imap[i] = x

    # reducing the communities to single vertices
    g.contract_vertices([cmap[x] for x in base_c.membership])
    g = g.simplify()

    # reducing the attributes based on the original clusters
    # we add the attribute values for each vertex in the cluster
    cattrs = []
    for i in range(len(imap)):
        cattrs.append(attrs[base_c[imap[i]]].sum(0).tolist())
    cattrs = np.asarray(cattrs)
    store = cosine_similarity(cattrs, cattrs)

    # phase 2
    # initialize clusters
    base_c2 = igraph.clustering.VertexClustering(g, [x for x in range(g.vcount())])
    base_q_1 = base_c2.recalculate_modularity()
    base_q_2 = attr_q(base_c2)
    # iterate
    base_c2 = iterate(g, base_c2, base_q_1, base_q_2, alpha)

    # map-reduce function to retrieve the original clusters
    c = list(map(lambda x: reduce(lambda a, b: a + b, map(lambda y: base_c[imap[y]], x)),
                 filter(lambda x: len(x) > 0, base_c2)))
    # write the clusters to file
    with open('communities.txt', 'w') as fp:
        for cluster in c:
            fp.write(','.join([str(x) for x in cluster]) + '\n')


if __name__ == '__main__':
    main(float(sys.argv[1]))
