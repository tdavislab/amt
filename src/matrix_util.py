from __future__ import division
from functions_util import *
from graph_util import rebulid_connected_set

def calculate_ultra_M(lcnt, nodes, links):
    aj_matrix = np.zeros((lcnt, lcnt))
    x_matrix = np.zeros((lcnt, lcnt))
    G=nx.Graph()
    G.add_nodes_from([0, len(nodes)])
    for i in range(0, len(links)):
        E_dist = np.linalg.norm(nodes[links[i][0]][[0,2]]-nodes[links[i][1]][[0,2]])
        G.add_edge(links[i][0],links[i][1],weight=E_dist)
    for i in range(0, lcnt):
        for j in range (i, lcnt):
            path = shortest_path(G, i, j)
            aj_matrix[i,j] = nodes[path[np.argmax(nodes[path,2])],2]
            x_matrix[i,j] = nodes[path[np.argmax(nodes[path,2])],0]

    dist = np.zeros((len(nodes)-lcnt, lcnt))
    for i in range(lcnt, len(nodes)):
        for j in range (0, lcnt):
            dist[i-lcnt,j] = nx.shortest_path_length(G, source=i, target=j, weight='weight')
    return dist, aj_matrix, x_matrix


def elementwise_1_center(Ms, i, j):
    tmp = []
    for tid in range(0, len(Ms)):
        tmp.append(Ms[tid][i, j])
    return (max(tmp)+min(tmp))/2


def modify_M(M, l):
    n,dim = M.shape
    for i in range(0, n):
        for j in range(i+1, dim):
            if M[i,j] in l:
                M[i, j] += FLUCT
    return M

def update_x(x_min, x_max, nodes, pivot, tmp, parent, n):
    for i in range (0, len(parent)):
        if (parent[i] == parent[tmp[pivot]] and (i not in tmp)) or i == tmp[pivot]:
            if nodes[i, 0] < x_min:
                x_min = nodes[i, 0]
            if nodes[i, 0] > x_max:
                x_max = nodes[i, 0]
    return x_min, x_max

def update_parent(l, i, j, x_min, x_max, leaves, n):
    tmp = l[i]
    for idx in range(0, len(l)):
        if l[idx] == tmp and idx != i:
            l[idx] = j
            if leaves[idx, 0] < x_min:
                x_min = leaves[idx, 0]
            if leaves[idx, 0] > x_max:
                x_max = leaves[idx, 0]
    return l, x_min, x_max

def get_links_modified(M, l,M_x):
    n,dim = M.shape
    l_val = []
    
    # Scalar field values of leave nodes.
    for i in range (0, len(M)):
        l_val.append(M[i,i])
    
    M = modify_M(M, l_val)

    # Scalar field valuse of internal nodes.
    M_val = set(M.reshape((1, n*dim))[0])-set([0])-set(l_val)
    Vallst = sorted(list(M_val))
    # Create a vector to store current ancestor of each leaf.
    new_nodes = l
    links = []
    parent = range(0, len(new_nodes))
    lidx = 0
    lvalidx = 0
    # Update M from the smallest internal node.
    for i in range(0, len(Vallst)):
        tmp = np.argwhere(M==Vallst[i])
        tmp_cnt = 0
        for j in range(0, len(tmp)):
            # if target nodes already have the same parent with small value, update M with this value.
            if parent[tmp[j-tmp_cnt][0]]== parent[tmp[j-tmp_cnt][1]]:
                M[tmp[j-tmp_cnt][0]][tmp[j-tmp_cnt][1]] = new_nodes[parent[tmp[j-tmp_cnt][0]]][2]
                tmp = tmp.tolist()
                tmp.remove(tmp[j-tmp_cnt])
                tmp = np.array(tmp)
                if len(tmp):
                    tmp_cnt = tmp_cnt+1
                else:
                    lidx += 1
        
        tmps, xs = rebulid_connected_set(tmp, M_x)
        if len(tmps)==0:
            lvalidx +=1
        for k in range(0, len(tmps)):
            tmp = tmps[k]
            
            x_val_min = 9999999
            x_val_max = -999999
            nn = 0
            for j in range(0, len(tmp)):
                if parent[tmp[j]] != i+len(l_val)-lidx+lvalidx:
                    # Add a new nodes whose x axis is the average of its children. So we need to calculate the number of children of each nodes as well as the sum of x value.
                    x_val_min, x_val_max = update_x(x_val_min, x_val_max, l, j, tmp, parent, nn)
                    links.append([parent[tmp[j]], i+len(l_val)-lidx+lvalidx])
                    parent, x_val_min, x_val_max = update_parent(parent, tmp[j], i+len(l_val)-lidx+lvalidx, x_val_min, x_val_max, l, nn)
                    parent[tmp[j]] = i+len(l_val)-lidx+lvalidx
            if len(tmp):
                #nn = (x_val_min+x_val_max)/2
                nn = xs[k]
                x_val = nn
                new_node = [[x_val, 1., Vallst[i]]]
                new_nodes = np.concatenate((new_nodes, new_node), axis=0)
                M = np.array(M).reshape((n,dim))
            lvalidx +=1
        lvalidx -=1
    return M, new_nodes, np.array(links)

def calculate_Ms_for_geodesic_animation(MGs, Ms, M, Tcnt, GA_param, Ms_X, M_x):
    for i in range(0, Tcnt):
        for j in range(0, GA_param-1):
            MGs['tree-'+str(i+1)]['M_'+str(j+1)] = calculate_M(M, Ms[i], 1/GA_param*(j+1))
            MGs['tree-'+str(i+1)]['Mx_'+str(j+1)] = calculate_M(M_x, Ms_X[i], 1/GA_param*(j+1))
    return MGs

def calculate_M(M1, M2, param):
    return param*M2+(1-param)*M1

def calculate_ls_for_geodesic_animation(MGs, Trees, nodes, Tcnt, lcnt, GA_param):
    for i in range(0, Tcnt):
        for j in range(0, GA_param-1):
            MGs['tree-'+str(i+1)]['l_'+str(j+1)]=calculate_pos_leaves(Trees['tree-'+str(i+1)]['Nodes'][0:lcnt, :], nodes[0:lcnt, :], 1/GA_param*(j+1))
    return MGs

def calculate_pos_leaves(l1, l2, param):
    return param*l1+(1-param)*l2


def rebuild_GA_trees(MGs, Tcnt, GA_param):
    for i in range(0, Tcnt):
        for j in range(0, GA_param-1):
            MGs['tree-'+str(i+1)]['M_'+str(j+1)], MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)], MGs['tree-'+str(i+1)]['Edges_'+str(j+1)] = get_links_modified(MGs['tree-'+str(i+1)]['M_'+str(j+1)], MGs['tree-'+str(i+1)]['l_'+str(j+1)], MGs['tree-'+str(i+1)]['Mx_'+str(j+1)])
    return MGs

# Previous Version-discarded.
def updata_internal_x_for_GA(MGs, Tcnt, Trees, nodes, GA_param):
    for i in range(0, Tcnt):
        for j in range(0, GA_param-1):
            param = 1/GA_param*(j+1)
            MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)][:, 0] = param*Trees['tree-'+str(i+1)]['Nodes'][:,0]+(1-param)*nodes[:,0]
    return MGs

