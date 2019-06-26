from functions_util import *
from tree_util import *

def MAPPING_AND_EXTEND_LEAVES(Trees, Tcnt, lcnts, label_mode, labels, leaves, mapping_mode, ED_param, maxn):
    nnlabel = labels[:]
    if len(set(lcnts)) > 1:
        # find the tree with the maximum number of labelled leaves as pivot.
        lcnts = np.array(lcnts)
        maxidx = np.where(lcnts==lcnts.max())[0]
        if label_mode == 'trust-labels':
            pivot = maxidx[find_max_labelled_leaves_tree(np.array(labels)[maxidx])]
        else:
            pivot = maxidx[0]
        
        # Make the number of leaves of all trees the same.
        for i in range(0, Tcnt):
            if i!= pivot:
                if label_mode == 'trust-labels':
                    labels[i], leaves[i], Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges'], nnlabel[i] = map_and_extend_leaves(labels[i], leaves[i], Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges'], labels[pivot], leaves[pivot], Trees['tree-'+str(pivot+1)]['Nodes'], Trees['tree-'+str(pivot+1)]['Edges'], mapping_mode, ED_param)
                else:
                    labels[pivot] = update_pivot_labels(labels[pivot], maxn)
                    labels[i], leaves[i], Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges'] = map_and_extend_leaves_unlabelled(labels[i], leaves[i], Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges'], labels[pivot], leaves[pivot], Trees['tree-'+str(pivot+1)]['Nodes'], Trees['tree-'+str(pivot+1)]['Edges'], mapping_mode, ED_param)
                    print labels
                    nnlabel[i] = labels[i]


    else:
        pivot = find_max_labelled_leaves_tree(labels)
        if label_mode == 'not-trust-labels':
            labels[pivot] = update_pivot_labels(labels[pivot], maxn)
            for i in range(0, Tcnt):
                labels[i], leaves[i], Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges'] = map_and_extend_leaves_unlabelled(labels[i], leaves[i], Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges'], labels[pivot], leaves[pivot], Trees['tree-'+str(pivot+1)]['Nodes'], Trees['tree-'+str(pivot+1)]['Edges'], mapping_mode, ED_param)
    for i in range(0, Tcnt):
        if i != pivot:
            leaves[i], nnlabel[i] = mapping_leaves(leaves[i], leaves[pivot], labels[i], labels[pivot], Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges'], Trees['tree-'+str(pivot+1)]['Nodes'], Trees['tree-'+str(pivot+1)]['Edges'], mapping_mode, ED_param, nnlabel[i])

    idx = Trees['tree-'+str(pivot+1)]['Nodes'][leaves[pivot]][:,0].argsort()
    for i in range(0, Tcnt):
        leaves[i] = leaves[i][idx]
    
    
    label = labels[pivot]
    
    return leaves, label, Trees, nnlabel

def MAPPING_ITERNAL_NODES_FOR_GA(MGs, Tcnt, lcnt, dist_AMT, GA_param):
    for i in range(0, Tcnt):
        for j in range(0, GA_param-1):
            MGs['tree-'+str(i+1)]['dist_'+str(j+1)] = get_tree_dist(lcnt, MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)], MGs['tree-'+str(i+1)]['Edges_'+str(j+1)])
            if j==0:
                MGs['tree-'+str(i+1)]['dict_'+str(j+1)] = map_nodes(MGs['tree-'+str(i+1)]['dist_'+str(j+1)], dist_AMT, lcnt, 'none')
            else:
                MGs['tree-'+str(i+1)]['dict_'+str(j+1)] = map_nodes(MGs['tree-'+str(i+1)]['dist_'+str(j+1)], MGs['tree-'+str(i+1)]['dist_'+str(j)], lcnt, 'none')
            MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)], MGs['tree-'+str(i+1)]['Edges_'+str(j+1)]=rearange_nodes_links(np.array( MGs['tree-'+str(i+1)]['dict_'+str(j+1)]), MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)], MGs['tree-'+str(i+1)]['Edges_'+str(j+1)])
            MGs['tree-'+str(i+1)]['dist_'+str(j+1)] = get_tree_dist(lcnt, MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)], MGs['tree-'+str(i+1)]['Edges_'+str(j+1)])
    return MGs


def MAKE_AMT_LARGEST(ncnt, nodes, links, MGs, dist_AMT, lcnt):
    ncnt = list(ncnt)
    if int(max(ncnt)) <= len(nodes):
        Unodes = copy_array(nodes)
        Ulinks = copy_array(links)
    else:
        tid = ncnt.index(max(ncnt))
        dictU = adjust_dict(MGs['tree-'+str(tid+1)]['dict_1'], nodes, dist_AMT, MGs['tree-'+str(tid+1)]['dist_1'], lcnt)
        Unodes, Ulinks = extend_nodes_links(dictU, nodes, links)
    dist_U = get_tree_dist(lcnt, Unodes, Ulinks)
    return Unodes, Ulinks, dist_U


def ADD_EXTRA_NODES_LINKS_FOR_GA(MGs, Tcnt, dist_U, lcnt, Unodes, GA_param):
    for i in range(0, Tcnt):
        for j in range(0, GA_param-1):
            if len(Unodes) > len(MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)]):
                sdictU = map_nodes(dist_U, MGs['tree-'+str(i+1)]['dist_'+str(j+1)], lcnt, 'none')
                sdictU = adjust_dict(sdictU, MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)], MGs['tree-'+str(i+1)]['dist_'+str(j+1)], dist_U, lcnt)
                MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)], MGs['tree-'+str(i+1)]['Edges_'+str(j+1)] = extend_nodes_links(sdictU, MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)], MGs['tree-'+str(i+1)]['Edges_'+str(j+1)])
    return MGs



def ADD_EXTRA_NODES_LINKS(Trees, Tcnt, MGs, GA_param, dists, lcnt, ncnt, Unodes):
    for i in range(0, Tcnt):
        dist_U = MGs['tree-'+str(i+1)]['dist_'+str(GA_param-1)]
        if len(Unodes) > ncnt[i]:
            sdictU = map_nodes(dist_U, dists[i], lcnt, 'none', 'internal')
            # Ensure each nodes in smaller tree and be mapped to the nodes in larger tree.
            sdictU = adjust_dict(sdictU, Trees['tree-'+str(i+1)]['Nodes'], dists[i], dist_U, lcnt)
            Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges'] = extend_nodes_links(sdictU, Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges'])
    return Trees

def REARANGE_LINKS(Trees, Tcnt, MGs, GA_param):
    for i in range(0, Tcnt):
        Trees['tree-'+str(i+1)]['Edges'] = rearange_links(Trees['tree-'+str(i+1)]['Edges'],  MGs['tree-'+str(i+1)]['Edges_'+str(GA_param-1)])
    return Trees

def REARANGE_LINKS_for_GA(MGs, Tcnt, Ulinks, GA_param):
    for i in range(0, Tcnt):
        MGs['tree-'+str(i+1)]['Edges_1'] =  rearange_links(MGs['tree-'+str(i+1)]['Edges_1'], Ulinks)
        for j in range(1, GA_param-1):
            MGs['tree-'+str(i+1)]['Edges_'+str(j+1)] = rearange_links(MGs['tree-'+str(i+1)]['Edges_'+str(j+1)], MGs['tree-'+str(i+1)]['Edges_'+str(j)])
    return MGs
