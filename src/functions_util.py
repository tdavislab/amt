import os
from PKG import *
""" Functions used accross *util.py
"""

def make_dir(new_dir):
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

# Calculate shortest path using dijkstra on tree
def shortest_path(G, source, target):
    path = nx.dijkstra_path(G,source, target)
    return path


def update_title(idx, title):
    ntitle = []
    for i in range(0, len(title)):
        ntitle.append(title[idx[i]])
    return np.array(ntitle)

# Copy array without reference
def copy_array(l):
    tmp = []
    for i in range(0, len(l)):
        tmp.append(l[i])
    return np.array(tmp)

# Find the index of tree with maximum valid labels
def find_max_labelled_leaves_tree(m):
    tmp = []
    for i in range(0, len(m)):
        tmp.append(count_labelled_leaves(m[i]))
    tmp = np.array(tmp)
    return np.where(tmp==tmp.max())[0][0]

# Count the number of valid labels of a tree
def count_labelled_leaves(l):
    tmp = 0
    for i in range(0, len(l)):
        if l[i]<MAX_NODES:
            tmp += 1
    return tmp

def square_dist(a, b):
    tmp = 0
    for i in range(0, len(a)):
        tmp = (a[i]-b[i])**2+tmp
    return tmp

def find_min_square_dist(l, M, op, map_dict, lcnt):
    idx = MAX_NODES
    pivot = MAX_NODES
    for i in range(0, len(M)):
        tmp = square_dist(l, M[i])
        if (op=='unique'):
            if tmp < pivot and (i+lcnt not in map_dict):
                pivot = tmp
                idx = i
        else:
            if tmp < pivot:
                pivot = tmp
                idx = i
    return idx
