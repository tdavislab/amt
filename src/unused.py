def modify_matrix(M,nodes, op):
    Val = []
    for i in range (0,len(nodes)):
        Val.append(nodes[i,2])
    idx = sorted(range(len(Val)), key = lambda k:Val[k])
    for i in range(0, len(Val)-1):
        if Val[idx[i]] == Val[idx[i+1]]:
            Val[idx[i+1]] = Val[idx[i]]+0.0001


    for i in range(0, len(M)):
        for j in range (i, len(M)):
            if M[i,j] not in Val:
                #M[i,j] = min(Val, key=lambda x:abs(x-M[i,j]))
                new_Val = map(lambda x: abs(x-M[i,j]),Val)
                min_val= min(new_Val)
                my_keys = []
                for m,val in enumerate(new_Val):
                    if val == min_val:
                        my_keys.append(Val[m])
                if op == "upper":
                    M[i,j]= max(my_keys)
                else:
                    M[i,j]= min(my_keys)
    return M

def add_leaves_and_links(nodes, links, nleaves, nlabel, xlabel, dist_1, dist_2, lcnt):
    tmp = []
    ndict1 = map_nodes_leaves(dist_2[lcnt:len(dist_2)], dist_1[lcnt:len(dist_1)])
    ndict1 = ndict1+lcnt
    nndict1 = np.zeros(len(dist_1)).astype(int)-1
    for i in range(0, lcnt):
        nndict1[i] = i
    for i in range(0,len(ndict1)):
        nndict1[ndict1[i]] = lcnt+i
    for i in range(0, len(nndict1)):
        if nndict1[i]==-1:
            nndict1[i] = map_nodes_leaves([dist_1[i]], dist_2)
    dict1 = nndict1
    
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


def update_idx_old(idx, nidx, pivot):
    for i in range(0, pivot):
        if nidx[i]>idx[pivot]:
            nidx[i] = nidx[i] + 1
    for i in range(pivot, len(idx)):
        if idx[i]>idx[pivot]:
            idx[i] = idx[i] +1
    return idx, nidx

def print_MGs(MGs, Tcnt, GA_param):
    for i in range(0, Tcnt):
        for j in range(0, GA_param-1):
            print MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)]
            print MGs['tree-'+str(i+1)]['Edges_'+str(j+1)]

def rearange_nodes_links_for_GA(MGs, Tcnt, lcnt, GA_param):
    for i in range(0, Tcnt):
        for j in range(0, GA_param-1):
            MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)], MGs['tree-'+str(i+1)]['Edges_'+str(j+1)]=rearange_nodes_links(np.array( MGs['tree-'+str(i+1)]['dict_'+str(j+1)]), MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)], MGs['tree-'+str(i+1)]['Edges_'+str(j+1)])
            MGs['tree-'+str(i+1)]['dist_'+str(j+1)] = get_tree_dist(lcnt, MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)], MGs['tree-'+str(i+1)]['Edges_'+str(j+1)])
    return MGs


def update_links(links, pivot):
    for i in range(0, len(links)-1):
        if links[i][0] >= pivot:
            links[i][0] = links[i][0]+1
        if links[i][1] >= pivot:
            links[i][1] = links[i][1]+1
    return links


def map_leaves(dist1, dist2, lcnt, op):
    tmp = 0
    map_dict = []
    for i in range(0, lcnt):
        map_dict.append(i)
    for i in range(0, len(dist1)):
        idx = find_min_square_dist(dist1[i], dist2, op, map_dict, lcnt)
        map_dict.append(idx)
    return map_dict


def adjust_leaves_dict(ndict, leaves, dist1, dist2, lcnt):
    if len(set(ndict)) < len(leaves):
        exdict = map_leaves(dist1[lcnt:len(dist1)], dist2, lcnt, 'unique')
        for i in range(0, len(leaves)):
            if i not in ndict:
                ndict[exdict[i]]=i
    return ndict


