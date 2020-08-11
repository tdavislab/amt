from functions_util import *

"""
    Functions used in
"""

class Tree():
    """
        Check if the input is a legel tree:
        1. No cycles
        2. The graph is connected.
    """
    
    def __init__(self, V):
        self.V = V
        self.graph  = defaultdict(list)
    
    def addEdge(self, v, w):
        # Add w to v ist.
        self.graph[v].append(w)
        # Add v to w list.
        self.graph[w].append(v)
    
    # A recursive function that uses visited[]
    # and parent to detect cycle in subgraph
    # reachable from vertex v.
    def isCyclicUtil(self, v, visited, parent):
        
        # Mark current node as visited
        visited[v] = True
        
        # Recur for all the vertices adjacent
        # for this vertex
        for i in self.graph[v]:
            # If an adjacent is not visited,
            # then recur for that adjacent
            if visited[i] == False:
                if self.isCyclicUtil(i, visited, v) == True:
                    return True
        
            # If an adjacent is visited and not
            # parent of current vertex, then there
            # is a cycle.
            elif i != parent:
                return True
    
        return False

    # Returns true if the graph is a tree,
    # else false.
    def isTree(self):
        # Mark all the vertices as not visited
        # and not part of recursion stack
        visited = [False] * self.V
        
        # The call to isCyclicUtil serves multiple
        # purposes. It returns true if graph reachable
        # from vertex 0 is cyclcic. It also marks
        # all vertices reachable from 0.
        if self.isCyclicUtil(0, visited, -1) == True:
            return False
        
        # If we find a vertex which is not reachable
        # from 0 (not marked by isCyclicUtil(),
        # then we return false
        for i in range(self.V):
            if visited[i] == False:
                return False
        
        return True

#-----------------------------------
# Find leaves and save their labels
#-----------------------------------
def find_leaves(links, nodes):
    """
        Check if the input is a merge tree. If yes, return the indexes of leaves in tree.
    """
    n,dim = links.shape
    elems = links.reshape((1,n*dim))
    elem, cnt = np.unique(elems, return_counts=True)
    leaves = []
    lnklist = links.tolist()
    lcnt_ = 0
    root = max(nodes[:,2])
    #Check if input tree has only a root which has the maximum scalar value.
    rootcnt = 0
    for i in range(0, len(nodes)):
        if nodes[i, 2]== root:
            rootcnt += 1
    if rootcnt > 1:
        return 'not merge tree'
    
    for i in range(0,len(elem)):
        if cnt[i]==1:
            # A leaf should be the one which only appear in "links" once and its scalar value should smaller than the scalar value of the other end.
            x = [x for x in lnklist if elem[i] in x]
            end = [y for y in x[0] if y != elem[i]][0]
            lcnt_ += 1
            if nodes[elem[i]][2] < nodes[end][2]:
                leaves.append(elem[i])
            else:
                # If there is a node in a tree which has no parent node and it is not the root, this tree is not a legal merge tree.
                if nodes[elem[i]][2]<root:
                    return [-1]
                else:
                    continue
    if (lcnt_-len(leaves))>1:
        return [-1]
    return np.array(leaves)

def Find_leaves_and_save_labels(Trees, Tcnt):
    """
        The final average tree should inherit the labels of input trees.
        This function will find the original labels of input tree and save them.
    """
    leaves = []
    labels = []
    lcnts = []
    for i in range(0, Tcnt):
        leaf = find_leaves(Trees['tree-'+str(i+1)]['Edges'], Trees['tree-'+str(i+1)]['Nodes'])
        leaves.append(leaf)
        labels.append(list(Trees['tree-'+str(i+1)]['title'][list(leaves[i])]))
        lcnts.append(len(leaves[i]))
        
        # Sort leaves according to the title, and update the label.
        leaves[i] = update_title(np.array(labels[i]).argsort(), leaves[i])
        labels[i] = list(Trees['tree-'+str(i+1)]['title'][list(leaves[i])])
    return leaves, labels, lcnts


#-----------------------------------------------------------------------
# Mapping leaves with pivot tree including when they have different size
#-----------------------------------------------------------------------

def map_and_extend_leaves(label1, leaves1, nodes1, links1, label2, leaves2,  nodes2,  links2, mode, ED):
    """
        PARTIAL AGREEMENT-Refer to Section 4.2 in the paper.
        This function aims to:
        1. Make the input tree has the same number of leaves with the pivot tree.
        2. Sort the index of leaves of input tree to map the index of leaves of pivot tree.
        
        Parameters
        ----------
        label1, leaves1, nodes1, links1: information about input tree.
        label2, leaves2, nodes2, links2: information about pivot tree.
        mode: "Tree distance", "Euclidean distance", or "Tree&Euclidean distance"
        ED: paramter for "Tree&Euclidean distance"
        
        Returns
        -------
        nlabel1, nleaves1, nodes1, links1: Updated input tree, whose leaves have fully match with pivot tree.
        nnlabel: original label of input tree. Used in "coloring nodes by label" in the interface. Green for "newly labeled ones" and red for "original labeled ones."
        
    """
    nl1 = len(leaves1)
    nl2 = len(leaves2)
    tmplabel = []
    nleaves1 = []
    nleaves2 = []
    nlabel1 = []
    nlabel2 = []
    nnodes2 = deepcopy(nodes2)
    nlinks2 = deepcopy(links2)
    # Mapping leaves whose labels can find in pivot tree.
    for i in range(0, nl2):
        if label2[i] in label1:
            tmplabel.append(label2[i])
    
    for i in range(0, len(tmplabel)):
        nleaves1.append(leaves1[list(label1).index(tmplabel[i])])
        nleaves2.append(leaves2[list(label2).index(tmplabel[i])])
    lcnt = len(tmplabel)
    nleaves1 = move_the_labelled_to_the_front(nleaves1, leaves1)
    nleaves2 = move_the_labelled_to_the_front(nleaves2, leaves2)
    nlabel1 = move_the_labelled_to_the_front(tmplabel, label1)
    nlabel2 = move_the_labelled_to_the_front(tmplabel, label2)

    # Recording the index of mapped leaves.
    idx1 = compute_sorted_index(nleaves1, len(nodes1), nodes1)
    idx2 = compute_sorted_index(nleaves2, len(nnodes2), nnodes2)

    # Resort the nodes and links according to mapped leaves.
    nodes1, links1 = rearange_nodes_links_old(idx1, nodes1, links1)
    nnodes2, nlinks2 = rearange_nodes_links_old(idx2, nnodes2, nlinks2)
    
    nleaves1 = list(range(0, nl1))
    nleaves2 = list(range(0, nl2))

    # Calculated the distance matrix from unmatched leaves to matched leaves
    dist_1 = get_leaves_dist(lcnt, len(leaves1), nodes1, links1, mode, ED)
    dist_2 = get_leaves_dist(lcnt, len(leaves2), nnodes2, nlinks2, mode, ED)
    nnlabel = nlabel1[:]

    # Add dummy leaves and links to input tree to make it has the same number of leaves with the pivot tree.
    # For unmatched leaves, we update their labeling with minimum weight matching of distance matrices. For detail, please refer to the paper.
    nodes1, links1, nleaves1, nlabel1 = add_leaves_and_links(nodes1, links1, nleaves1, nlabel1, nlabel2, dist_2, dist_1, lcnt)
    for i in range(len(nnlabel), len(nlabel1)):
        nnlabel.append(MAX_NODES)
    return nlabel1, nleaves1, nodes1, links1, nnlabel


def mapping_leaves(leaves1, leaves2, label1, label2, nodes1, links1, nodes2, links2, mode, ED, nnlabel):
    """ FULL AGREEMENT--Refer to Section 4.1 in the paper.
        Map leaves when the tree has the same number of leaves with pivot tree.
        """
    
    # Varibles for labeled leaves
    nleaves1 = []
    nleaves2 = []
    nlabel = []
    
    # Variables for unlabeled leaves
    UKleaves1 = []
    UKleaves2 = []
    UKlabel1 = []
    UKlabel2 = []
    
    nleaves = np.zeros(len(leaves1))
    label = np.zeros(len(leaves1))
    UK1idx = []
    UK2idx = []
    for i in range(0, len(leaves1)):
        if label1[i] in label2 and label1[i] < MAX_NODES:
            nleaves1.append(leaves1[i])
            nlabel.append(label1[i])
            idx = label2.index(label1[i])
            nleaves[idx] = leaves1[i]
            label[idx] = nnlabel[i]
        else:
            UKleaves1.append(leaves1[i])
            UKlabel1.append(label1[i])
            UK1idx.append(i)
        if label2[i] in label1 and label2[i] < MAX_NODES:
            nleaves2.append(leaves2[i])
        else:
            UKleaves2.append(leaves2[i])
            UKlabel2.append(label2[i])
            UK2idx.append(i)
    if len(UK1idx)>0:
        # Calculated the distance matrix from unmatched leaves to matched leaves
        dist1 = get_tree_dist_between_leaves(UKleaves1, nleaves1, nodes1, links1, mode, ED)
        dist2 = get_tree_dist_between_leaves(UKleaves2, nleaves2, nodes2, links2, mode, ED)
        # Calculate resorting rule with minimum weight matching of distance matrices
        dict1 = map_nodes_leaves(dist2, dist1)
        for i in range(0, len(dict1)):
            # Update labels using resorting rule.
            nleaves[UK2idx[i]] = leaves1[UK1idx[dict1[i]]]
            label[UK2idx[i]] = nnlabel[UK1idx[dict1[i]]]
    return nleaves, label


def map_and_extend_leaves_unlabelled(label1, leaves1, nodes1, links1, label2, leaves2,  nodes2,  links2, mode, ED):
    """ DISAGREEMENT-Refer to Section 4.2 in the paper.
        Mapping and extend leaves for tree under "Ignore label" mode, when the input tree has the different size of leaves with pivot tree.
        """
    nl1 = len(leaves1)
    nl2 = len(leaves2)
    dist_M = np.zeros((nl1, nl2))
    for i in range(0, nl1):
        for j in range(0, nl2):
            dist_M[i,j] = np.linalg.norm(nodes1[leaves1[i]][[0,2]]-nodes2[leaves2[j]][[0,2]])
    # Mapping the leaves with minimum weight matching of euclidean distance matrices
    row_ind, col_ind = linear_sum_assignment(dist_M)
    label1 = update_label(label1, label2, col_ind)
    # Since we already have some matched labeled leaves, we can turn to partial agreement case.
    nlabel1, nleaves1, nodes1, links1, nnlabel  = map_and_extend_leaves(label1, leaves1, nodes1, links1, label2, leaves2,  nodes2,  links2, mode, ED)

    return nlabel1, nleaves1, nodes1, links1


#-------------------------------
# Distance matrix on Trees
#-------------------------------

## TODO: all distance matrices on tree are calculated in similar format, we can combine them to one function.

def get_leaves_dist(llcnt, lcnt, nodes, links, mode, ED):
    """ Calculate distance matrix between labeled leaves with leaves.
        
        Parameters
        ----------
        llcnt: number of labeled leaves
        lcnt: number of leaves
        nodes, links: nodes and links of tree
        mode: "Tree distance", "Euclidean distance", or "Tree&Euclidean distance"
        ED: paramter for "Tree&Euclidean distance"
        
        Returns
        -------
        distance matrix in the size of lcnt * llcnt as Numpy array
        
    """
        # TODO: this function is quite similar as "get_leaves_dist". Because I rewrite mapping_leaves without move labeled leaves to the front first. So UK and l just record the position of labeled leaves and unlabeled leaves without change their order.
    
    G=nx.Graph()
    G.add_nodes_from([0, len(nodes)])
    for i in range(0, len(links)):
        E_dist = np.linalg.norm(nodes[links[i][0]][2]-nodes[links[i][1]][2])
        G.add_edge(links[i][0],links[i][1],weight=E_dist)
    dist = np.zeros((lcnt, llcnt))
    for i in range(0, lcnt):
        for j in range (0, llcnt):
            if mode == "td-mapping":
                dist[i,j] = nx.shortest_path_length(G, source=i, target=j, weight='weight')
            if mode == "ed-mapping":
                dist[i,j] =  np.linalg.norm(nodes[i][[0,2]]-nodes[j][[0,2]])
            if mode == "et-mapping":
                dist[i,j] = (1-ED)*nx.shortest_path_length(G, source=i, target=j, weight='weight')+ED*np.linalg.norm(nodes[i][[0,2]]-nodes[j][[0,2]])
    return dist


def get_tree_dist_between_leaves(UK, l, nodes, links, mode, ED):
    """ Calculate distance matrix between labeled leaves with leaves.
        
        Parameters
        ----------
        UK: indexes of unlabeled leaves as Numpy array
        l: indexes of labeled leaves as Numpy array
        nodes, links: nodes and links of tree
        mode: "Tree distance", "Euclidean distance", or "Tree&Euclidean distance"
        ED: paramter for "Tree&Euclidean distance"
        
        Returns
        -------
        distance matrix in the size of len(UK) and len(l) as Numpy array
        
    """
    G=nx.Graph()
    G.add_nodes_from([0, len(nodes)])
    for i in range(0, len(links)):
        E_dist = np.linalg.norm(nodes[links[i][0]][2]-nodes[links[i][1]][2])
        G.add_edge(links[i][0],links[i][1],weight=E_dist)
    dist = np.zeros((len(UK), len(l)))
    for i in range(0, len(UK)):
        for j in range (0, len(l)):
            if mode == "td-mapping":
                dist[i,j] = nx.shortest_path_length(G, source=UK[i], target=l[j], weight='weight')
            if mode == "ed-mapping":
                dist[i,j] =  np.linalg.norm(nodes[UK[i]][[0,2]]-nodes[l[j]][[0,2]])
            if mode == "et-mapping":
                dist[i,j] = (1-ED)*nx.shortest_path_length(G, source=UK[i], target=l[j], weight='weight')+ED*np.linalg.norm(nodes[UK[i]][[0,2]]-nodes[l[j]][[0,2]])

    return dist


def get_tree_dist(lcnt, nodes, links):
    """ Calculate tree distance matrix between not-leaf nodes and leaves
        
        Parameters
        ----------
        lcnt: number of leaves
        nodes, links: nodes and links of tree
        
        Returns
        -------
        distance matrix in the size of len(not-leaf nodes) and lcnt as Numpy array
        
        """
    G=nx.Graph()
    G.add_nodes_from([0, len(nodes)])
    for i in range(0, len(links)):
        E_dist = abs(nodes[links[i][0]][2]-nodes[links[i][1]][2])
        #E_dist = np.linalg.norm(nodes[links[i][0]][[0,2]]-nodes[links[i][1]][[0,2]])
        G.add_edge(links[i][0],links[i][1],weight=E_dist)
    #G.add_edge(links[i][0],links[i][1],weight=1)
    dist = np.zeros((len(nodes)-lcnt, lcnt))
    for i in range(lcnt, len(nodes)):
        for j in range (0, lcnt):
            dist[i-lcnt,j] =nx.shortest_path_length(G, source=i, target=j, weight='weight')+1*np.linalg.norm(nodes[i][[0,2]]-nodes[j][[0,2]])
    return dist

def get_dist(MGs, Tcnt, lcnt, GA_param):
    """ Calculate tree distance matrix between not-leaf nodes and leaves for geodesic trees
        """
    for i in range(0, Tcnt):
        for j in range(0, GA_param-1):
            MGs['tree-'+str(i+1)]['dist_'+str(j+1)] = get_tree_dist(lcnt, MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)], MGs['tree-'+str(i+1)]['Edges_'+str(j+1)])
    return MGs


def get_tree_dist_whole(lcnt, nodes, links):
    """ Calculate tree distance matrix between all nodes and leaves
        
        Parameters
        ----------
        lcnt: number of leaves
        nodes, links: nodes and links of tree
        
        Returns
        -------
        distance matrix in the size of len(nodes) and lcnt as Numpy array
        
        """
    G=nx.Graph()
    G.add_nodes_from([0, len(nodes)])
    for i in range(0, len(links)):
        E_dist = abs(nodes[links[i][0]][2]-nodes[links[i][1]][2])
        #E_dist = np.linalg.norm(nodes[links[i][0]][[0,2]]-nodes[links[i][1]][[0,2]])
        G.add_edge(links[i][0],links[i][1],weight=E_dist)
    #G.add_edge(links[i][0],links[i][1],weight=1)
    dist = np.zeros((len(nodes), lcnt))
    for i in range(0, len(nodes)):
        for j in range (0, lcnt):
            dist[i,j] =nx.shortest_path_length(G, source=i, target=j, weight='weight')+1*np.linalg.norm(nodes[i][[0,2]]-nodes[j][[0,2]])
    return dist


def calculate_whole_dist_matrix(nodes, links, mode, ED):
    """ Calculate tree distance matrix between nodes and nodes
        
        Parameters
        ----------
        nodes, links: nodes and links of tree
        mode: "Tree distance", "Euclidean distance", or "Tree&Euclidean distance"
        ED: paramter for "Tree&Euclidean distance"
        
        Returns
        -------
        distance matrix in the size of len(nodes) and len(nodes) as Numpy array
        
        """
    # Used in uncertainty calculation. Only consider tree distance mode.
    mode = 'td-mapping'
    G=nx.Graph()
    G.add_nodes_from([0, len(nodes)])
    for i in range(0, len(links)):
        E_dist = np.linalg.norm(nodes[links[i][0]][2]-nodes[links[i][1]][2])
        G.add_edge(links[i][0],links[i][1],weight=E_dist)
    dist = np.zeros((len(nodes), len(nodes)))
    for i in range(0, len(nodes)):
        for j in range(0, len(nodes)):
            if mode == "td-mapping":
                dist[i,j] = nx.shortest_path_length(G, source=i, target=j, weight='weight')
            if mode == "ed-mapping":
                dist[i,j] =  np.linalg.norm(nodes[i][[0,2]]-nodes[j][[0,2]])
            if mode == "et-mapping":
                dist[i,j] = (1-ED)*nx.shortest_path_length(G, source=i, target=j, weight='weight')+ED*np.linalg.norm(nodes[i][[0,2]]-nodes[j][[0,2]])
    return dist


#------------------------
# Modification on Tree
#------------------------


def add_leaves_and_links(nodes, links, nleaves, nlabel, xlabel, dist_1, dist_2, lcnt):
    """ Add dummy leaves to Tree to make the size of leaves be the same with the size of leaves of pivot tree.
        
        Parameters
        ----------
        lcnt: number of matched leaves
        nodes, links: nodes and links of tree
        nleaves: index of leaves with the matched labeled leaves in the front.
        nlabels: corresponding labels of the leaves.
        xlabels: correspongding labels of leaves in pivot tree.
        dist_1, dist_2: distance matrics from umatched leaves to matched leaves.
        
        Returns
        -------
        nodes, links, nleaves, nlabel: nodes, links, index of leaves and corresponding labels after ading dummy leaves and links.
        
        """
    tmp = []
    # Mapping unmatched leaves with minimum weight matching of distance matrices.
    ndict1 = map_nodes_leaves(dist_2[lcnt:len(dist_2)], dist_1[lcnt:len(dist_1)])
    ndict1 = ndict1+lcnt
    nndict1 = np.zeros(len(dist_1)).astype(int)-1
    # The indexes of matched leaves do not need to be changed.
    for i in range(0, lcnt):
        nndict1[i] = i
    # Record resorting rule of unmatch leaves of input tree.
    for i in range(0,len(ndict1)):
        nndict1[ndict1[i]] = lcnt+i

    # Because the size of leaves in pivot tree is larger than that of input tree. There are some leaves in pivot tree are unmatched. We should create dummy node to input tree.
    for i in range(0, len(nndict1)):
        if nndict1[i]==-1:
            # Still use minimum weight matching of distance matrices to find the position of dummy node.
            nndict1[i] = map_nodes_leaves([dist_1[i]], dist_2)
    dict1 = nndict1

    # Add dummy nodes and links.
    ntmp = len(nodes)
    nodes = nodes.tolist()
    for i in range(0, len(dict1)):
        if dict1[i] not in tmp:
            tmp.append(dict1[i])
        else:
            tmp.append(ntmp)
            nleaves.append(ntmp)
            nlabel.append(xlabel[i])
            new_node = nodes[dict1[i]][:]
            new_node[1] = 0
            nodes.append(new_node)
            links = add_links(links, dict1[i], ntmp)
            ntmp = ntmp + 1
    nodes = np.array(nodes)
    return nodes, links, nleaves, nlabel

def add_links(links, pivot, newn):
    # add link from newly added dummy node to the node in the same position.
    idx = np.argwhere(links == pivot)
    links = links.tolist()
    links.append([links[idx[0,0]][0], newn])
    return np.array(links)

def rearange_nodes_links_old(idx, nodes, links):
    """ Update the order of nodes and revise the index recording in links according to updating rules.
        """
    nodes = nodes[idx,:]
    for i in range(0, len(links)):
        links[i, 0] = idx.index(links[i, 0])
        links[i, 1] = idx.index(links[i, 1])
    for i in range (0, len(links)):
        links[i] = sorted(links[i])
    
    # Sort links according to the source.
    links = links[links[:,0].argsort()]
    idx = update_idx_links(links[:,0], links[:,1])
    links = links[idx]
    return nodes, links

def rearange_nodes_links(idx, nodes, links):
    """ Update the order of nodes and revise the index recording in links according to updating rules.
        Difference with the former one. Recalculate updating rules in this function.
        """
    # TODO: Modify functions citing this function, so that we can combine this version with the former one.
    idx = update_idx(list(idx), nodes[:, 2])
    idx = list(np.array(idx).argsort())
    nodes = nodes[idx,:]
    for i in range(0, len(links)):
        links[i, 0] = idx.index(links[i, 0])
        links[i, 1] = idx.index(links[i, 1])
    for i in range (0, len(links)):
        links[i] = sorted(links[i])

    # Sort links according to the source.
    links = links[links[:,0].argsort()]
    idx = update_idx_links(links[:,0], links[:,1])
    links = links[idx]
    return nodes, links


def rearange_links(links1, links2):
    """ Mapping links for animation.
        """
    l1 = links1[:].tolist()
    l2 = links2[:].tolist()
    idx = np.zeros(len(l1)).astype(int)-1
    Uidx1 = []
    Uidx2 = []
    for i in range(0, len(l1)):
        if l1[i] in l2:
            # Link is fully matched if it appear both in links1 and links2
            idx[l2.index(l1[i])]=i
        else:
            Uidx1.append(i)
    for i in range(0, len(idx)):
        if idx[i] <0:
            Uidx2.append(i)
    for i in range(0, len(Uidx1)):
        for j in range(0, len(Uidx2)):
            if links1[Uidx1[i], 0] == links2[Uidx2[j], 0]:
                # Matching links when they have the same one source.
                idx[Uidx2[j]]=Uidx1[i]
    Uidx1 = []
    for i in range(0, len(l1)):
        if i not in idx:
            Uidx1.append(i)
    
    j = 0
    for i in range(0, len(idx)):
        if idx[i]<0:
            # Matching links if one's source is the same with the other's target. And change switch one's source with its target.
            if links1[Uidx1[j]][1]==links2[i][0]:
                tmp = links1[Uidx1[j]][1]
                links1[Uidx1[j]][1] =  links1[Uidx1[j]][0]
                links1[Uidx1[j]][0] = tmp
            idx[i]=Uidx1[j]
            j += 1
    links1 = links1[idx]
    return links1


#-------------------------------------------------------------------------------
# Mapping non-leaf nodes with pivot tree including when they have different size
#-------------------------------------------------------------------------------

def map_nodes(dist1, dist2, lcnt, op, mode=None):
    """ Mapping non-leaf nodes in input tree with that in pivot tree.
        
        Parameters
        ----------
        dist1, dist2: distance matrices between non-leaf nodes with leaves
        lcnt: number of leaves
        op: "None" | "Unique"
        mode: "Node" | "Anything"
        """
    # TODO: Modify the functions citing this function, so that we can avoid use "mode" in this function.
    # The only difference is the format of dist2
    
    tmp = 0
    map_dict = []
    for i in range(0, lcnt):
        map_dict.append(i)
    
    if mode == None:
        if len(dist1)==len(dist2):
            dist_M = np.zeros((len(dist1), len(dist2)))
            for i in range(0, len(dist1)):
                for j in range(0, len(dist2)):
                    dist_M[i,j] = np.linalg.norm(dist1[i]-dist2[j])
            row_ind, col_ind = linear_sum_assignment(dist_M)
            for i in range(0, len(col_ind)):
                map_dict.append(col_ind[i]+lcnt)
        else:
            for i in range(0, len(dist1)):
                idx = find_min_square_dist(dist1[i], dist2, op, map_dict, lcnt)
                map_dict.append(idx+lcnt)
    else:
        if len(dist1)==len(dist2)-lcnt:
            dist1 = dist1[lcnt:len(dist1),:]
            dist_M = np.zeros((len(dist1), len(dist2)))
            for i in range(0, len(dist1)):
                for j in range(0, len(dist2)):
                    dist_M[i,j] = np.linalg.norm(dist1[i]-dist2[j])
            row_ind, col_ind = linear_sum_assignment(dist_M)
            for i in range(0, len(col_ind)):
                map_dict.append(col_ind[i]+lcnt)
        else:
            for i in range(0, len(dist1)):
                idx = find_min_square_dist(dist1[i], dist2, op, map_dict, lcnt)
                map_dict.append(idx)

    return map_dict


def get_dict(MGs, dist_AMT, Tcnt, lcnt, GA_param):
    """ Mapping non-leaf nodes in input tree with that in pivot tree for geodesic trees.
        """
    for i in range(0, Tcnt):
        for j in range(0, GA_param-1):
            if j==0:
                MGs['tree-'+str(i+1)]['dict_'+str(j+1)] = map_nodes(MGs['tree-'+str(i+1)]['dist_'+str(j+1)], dist_AMT, lcnt, 'none')
            else:
                MGs['tree-'+str(i+1)]['dict_'+str(j+1)] = map_nodes(MGs['tree-'+str(i+1)]['dist_'+str(j+1)], MGs['tree-'+str(i+1)]['dist_'+str(j)], lcnt, 'none')
    return MGs



def extend_nodes_links(sd, nodes, links):
    """ Add dummy non-leaf nodes to the position of "sd" for geodesic animation.
        """
    nnodes = nodes.tolist()
    nlinks = links.tolist()
    tmp = []
    nid = len(nodes)
    for i in range(0, len(sd)):
        if sd[i] not in tmp:
            tmp.append(sd[i])
        else:
            nnodes.append(nodes[sd[i]]+[0,0,FLUCT])
            tmp.append(nid)
            # make sure not add links to dummy leaf.
            sd[i] = adjust_sd(sd[i], nodes, links)
            nlinks.append([sd[i],nid])
            nid = nid + 1
    nnodes, nlinks = rearange_nodes_links_old(tmp, np.array(nnodes), np.array(nlinks))
    return np.array(nnodes), np.array(nlinks)


#-----------------------------------------
# Detail info of tree needed in JSON files
#-----------------------------------------

def calculate_cls_label(n, l, L, maxn, mode, nlabels):
    """ Classify the nodes, from 1-center tree and ensembles, into: labeled leaf, Newly labeled leaf, and non-leaf node.
        Also return the final label for 1-center tree.
        """
    cls = []
    label = []
    tmp = maxn+1
    clss = []
    for i in range(0, n):
        if i < l:
            if mode == 'trust-labels':
                if L[i] < MAX_NODES:
                    cls.append("IsLeaf")
                    label.append(L[i])
                else:
                    cls.append("IsULLeaf")
                    label.append(tmp)
                    tmp += 1
            else:
                cls.append("IsULLeaf")
                label.append(L[i])
        else:
            cls.append("NotLeaf")
            # Inplementing algorithm based on Leaf-Labeled Merge Trees. So the labels of non-leaf nodes make no sense in this algorithm. Put "" on non-leaf nodes of 1-center tree.
            label.append("")
    for i in range(0, len(nlabels)):
        cls_=[]
        for j in range(0, n):
            if j < l:
                if mode == 'trust-labels':
                    if nlabels[i][j]==L[j]:
                        cls_.append("IsLeaf")
                    else:
                        cls_.append("IsULLeaf")
                else:
                    cls_.append("IsULLeaf")
            else:
                cls_.append("NotLeaf")
        clss.append(cls_)
    return cls, label, clss

def update_nodes(nodes, svg_h):
    """ Update the position of nodes for presentation on SVG.
        """
    for i in range(0, len(nodes)):
        nodes[i,2] = svg_h-nodes[i,2]
    return nodes

#----------------
# Sub-functions
#----------------

def move_the_labelled_to_the_front(nl, l):
    """ Put the matched leaves, which have the same labels across input tree and pivot tree, into front.
        The others will implement the partial agreement strategy.
        """
    nnl = list(copy_array(nl))
    for i in range(0, len(l)):
        if l[i] not in nnl:
            nnl.append(l[i])
    return nnl

def compute_sorted_index(leaves, ncnt, nodes):
    """ Record the updating rule for leaves. This rule should be implemented on nodes and links of the tree.
        """
    leaves= np.array(leaves).astype(int)
    idx = []
    for i in range(0, len(leaves)):
        idx.append(int(leaves[i]))
    nidx = []
    for i in range(0, len(nodes)):
        if i not in leaves:
            nidx.append(i)

    nidx = np.array(nidx)[nodes[nidx][:,0].argsort()]
    j = 0
    for i in range(0, ncnt):
        if i not in leaves:
            idx.append(nidx[j])
            j+=1
    return idx



def update_idx_links(l1, l2):
    # Sort links according to target, without change the order of source.
    nidx = np.array(range(0, len(l1)))
    for i in set(list(l1)):
        if list(l1).count(i)>1:
            idx = [index for index, value in enumerate(l1) if value == i]
            new = np.array(l2[idx]).argsort()
            nidx[idx] = nidx[np.array(idx)[new]]
    return nidx


def map_nodes_leaves(dist1, dist2):
    """ Mapping nodes or leaves with minimum weight matching of distance matrices.
        """
    tmp = np.zeros((len(dist1), len(dist2)))
    for i in range(0, len(dist1)):
        for j in range(0, len(dist2)):
            if len(dist1[i])>1:
                pcc = np.linalg.norm(dist1[i]-dist2[j])
                tmp[i,j] = pcc
            else:
                tmp[i,j] = (dist1[i]-dist2[j])**2
    row_ind, col_ind = linear_sum_assignment(tmp)
    return col_ind


def update_idx(tmp, array):
    """ Recalculate idx to make sure that there is a fully match between idx and leaves.
        """
    for i in range(0, len(array)):
        if list(tmp).count(i)>1:
            # Some index in idx may be duplicated because some leaves have the same scalar value.
            idx = [index for index, value in enumerate(tmp) if value == i]
            new = np.array(tmp)[idx]+np.array(array[idx]).argsort()*0.1
            for j in range(0, len(idx)):
                tmp[idx[j]]=new[j]
    sort_list = sorted(tmp)
    idx = []
    for i in range(0, len(tmp)):
        idx.append(sort_list.index(tmp[i]))
    return idx


def adjust_sd(idx, nodes, links):
    """ Update idx to make sure not include dummy leaf.
        """
    nnodes = nodes[:, [0,2]].tolist()
    tmp = [i for i, e in enumerate(nnodes) if e == nnodes[idx]]
    if len(tmp)>1:
        for i in range(0, len(tmp)):
            # All the second element of dummy leaves are setted to be 0.
            if nodes[tmp[i], 1]>0:
                idx = tmp[i]
    return idx

def adjust_dict(ndict, nodes, dist1, dist2, lcnt):
    """ Ensure each nodes in smaller tree and be mapped to the nodes in larger tree.
        """
    if len(set(ndict)) < len(nodes):
        exdict = map_nodes(dist1, dist2, lcnt, 'unique')
        for i in range(0, len(nodes)):
            if i not in ndict:
                ndict[exdict[i]]=i
    return ndict

def update_label(label1, label2, idx):
    """ Update the labels of input tree according to pivot tree.
        """
    for i in range(0, len(idx)):
        label1[i] = label2[idx[i]]
    return label1


def update_pivot_labels(l, maxn):
    """ Record the smallest unused label for relabeling 1-center
        """
    tmp = maxn+1
    tmps = []
    for i in range(0, len(l)):
        if l[i] > MAX_NODES-1 or l[i] in tmps:
            l[i] = tmp
            tmp += 1
        tmps.append(l[i])
    return l




