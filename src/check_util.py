from tree_util import Tree
from functions_util import *

def check_is_tree(Trees, Tcnt):
    for i in range(0, Tcnt):
        Istree = check_tree(Trees['tree-'+str(i+1)]['Edges'],
                            Trees['tree-'+str(i+1)]['Nodes'])
        if Istree==False:
            return False
    return True

def check_is_merge_tree(leaves, Trees, Tcnt):
    for i in range(0, Tcnt):
        if len(leaves[i])<2:
            return False
        IsMergeTree = check_merge_tree(leaves[i], Trees['tree-'+str(i+1)]['Edges'],Trees['tree-'+str(i+1)]['Nodes'])
        if (IsMergeTree==False):
            return False
    return True

def check_unique_label(labels):
    for i in range(0, len(labels)):
        if len(list(labels[i]))>len(set(list(labels[i]))):
            return False
    return True

def check_can_EF(lcnts, labels):
    if len(set(lcnts)) > 1:
        lcnts = np.array(lcnts)
        maxidx = np.where(lcnts==lcnts.max())[0]
        pivot = maxidx[find_max_labelled_leaves_tree(np.array(labels)[maxidx])]
    else:
        pivot = find_max_labelled_leaves_tree(labels)
    return check_trust_labels(pivot, labels)

def check_tree(links, nodes):
    tree = Tree(len(nodes))
    if len(links)<2:
        return False
    for i in range(0, len(links)):
        tree.addEdge(links[i][0], links[i][1])
    return tree.isTree()

def check_merge_tree(leaves, links, nodes):
    root = list(nodes[:,2]).index(max(nodes[:,2]))
    G=nx.Graph()
    G.add_nodes_from([0, len(nodes)])
    for i in range(0, len(links)):
        G.add_edge(links[i][0],links[i][1],weight=1)
    for i in range(0, len(leaves)):
        tmp = nodes[leaves[i],2]
        path = shortest_path(G, leaves[i], root)
        for j in range(1, len(path)):
            if nodes[path[j], 2]<= tmp:
                return False
            else:
                tmp = nodes[path[j],2]
    return True

def check_trust_labels(tid, labels):
    pivot = [x for i, x in enumerate(labels[tid]) if x < MAX_NODES]
    for i in range(0, len(labels)):
        if i != tid:
            tmp = [x for i, x in enumerate(labels[i]) if x < MAX_NODES]
            if has_intersection(tmp, pivot)==False:
                return False
    return True


def has_intersection(l1, l2):
    return len(list(l1)+list(l2))> len(set(list(l1)+list(l2)))


