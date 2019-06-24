from __future__ import division

from flask import Flask, render_template, request, jsonify
import numpy as np
from werkzeug.contrib.fixers import ProxyFix
from scipy.stats import pearsonr
from scipy.optimize import linear_sum_assignment
from copy import deepcopy
from collections import defaultdict
import math

import sys
import os
import networkx as nx

app = Flask(__name__)

OPTION = "lower"
MAX_NODES = 999999999999
FLUCT = 0.000001


class Graph: 
      
    # init function to declare class variables 
    def __init__(self,V): 
        self.V = V 
        self.adj = [[] for i in range(V)] 
  
    def DFSUtil(self, temp, v, visited): 
  
        # Mark the current vertex as visited 
        visited[v] = True
  
        # Store the vertex to list 
        temp.append(v) 
  
        # Repeat for all vertices adjacent 
        # to this vertex v 
        for i in self.adj[v]: 
            if visited[i] == False: 
                  
                # Update the list 
                temp = self.DFSUtil(temp, i, visited) 
        return temp 
  
    # method to add an undirected edge 
    def addEdge(self, v, w): 
        self.adj[v].append(w) 
        self.adj[w].append(v) 
  
    # Method to retrieve connected components 
    # in an undirected graph 
    def connectedComponents(self): 
        visited = [] 
        cc = [] 
        for i in range(self.V): 
            visited.append(False) 
        for v in range(self.V): 
            if visited[v] == False: 
                temp = [] 
                cc.append(self.DFSUtil(temp, v, visited)) 
        return cc 

class Tree(): 
  
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
    

def make_dir(new_dir):
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

def initialization(Trees, Tcnt):
    for i in range(0, Tcnt):
        Trees['tree-'+str(i+1)]={}
        Trees['tree-'+str(i+1)]['Nodes']=[]
        Trees['tree-'+str(i+1)]['Edges']=[]
        Trees['tree-'+str(i+1)]['id']=[]
        Trees['tree-'+str(i+1)]['title']=[]
        Trees['tree-'+str(i+1)]['IL-dist'] = []
        Trees['tree-'+str(i+1)]['local-dist'] = []
    return Trees

def initialization_M_for_geodesic_animation(Tcnt, GA_param):
    M = {}
    for i in range(0, Tcnt):
        M['tree-'+str(i+1)]={}
        for j in range(-1, GA_param):
            M['tree-'+str(i+1)]['M_'+str(j+1)]=[]
            M['tree-'+str(i+1)]['l_'+str(j+1)]=[]
            M['tree-'+str(i+1)]['Nodes_'+str(j+1)]=[]
            M['tree-'+str(i+1)]['Edges_'+str(j+1)]=[]
            M['tree-'+str(i+1)]['dist_'+str(j+1)]=[]
            M['tree-'+str(i+1)]['dict_'+str(j+1)]=[]
            M['tree-'+str(i+1)]['IL-dist_'+str(j+1)]=[]
            M['tree-'+str(i+1)]['local-dist_'+str(j+1)]=[]
    return M

def initialization_returned_data(Tcnt, Trlabel, GA_param):
    data = {}
    data['status'] = 'success'
    for i in range(0, Tcnt):
        data["Nodes-"+str(Trlabel[i])] = []
        data["Edges-"+str(Trlabel[i])] = []
        data["IL-dist-"+str(Trlabel[i])] = []
        for j in range(-1, GA_param):
            data["Nodes-"+str(Trlabel[i])+'-'+str(j+1)] = []
            data["Edges-"+str(Trlabel[i])+'-'+str(j+1)] = []
            data["IL-dist-"+str(Trlabel[i])+'-'+str(j+1)] = []
    data["Nodes-AMT"] = []
    data["Edges-AMT"] = []
    data["UNodes-AMT"] = []
    data["UEdges-AMT"] = []
    data["GA_param"] = []
    data["max_ldist"] = []
    return data

def calculate_Ms_for_geodesic_animation(MGs, Ms, M, Tcnt, GA_param):
    for i in range(0, Tcnt):
        for j in range(0, GA_param-1):
            MGs['tree-'+str(i+1)]['M_'+str(j+1)] = calculate_M(M, Ms[i], 1/GA_param*(j+1))
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
            MGs['tree-'+str(i+1)]['M_'+str(j+1)], MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)], MGs['tree-'+str(i+1)]['Edges_'+str(j+1)] = get_links_modified(MGs['tree-'+str(i+1)]['M_'+str(j+1)], MGs['tree-'+str(i+1)]['l_'+str(j+1)])
    return MGs

def updata_internal_x_for_GA(MGs, Tcnt, Trees, nodes, GA_param):
    for i in range(0, Tcnt):
        for j in range(0, GA_param-1):
            param = 1/GA_param*(j+1)
            MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)][:, 0] = param*Trees['tree-'+str(i+1)]['Nodes'][:,0]+(1-param)*nodes[:,0]
    return MGs
    

def load_nodes_data_2_trees(Trees, Tcnt, json, Trlabel, ncnt, svg_h):
    maxn = 0
    for i in range(0, Tcnt):
        # Relabel unlabelled data.
        UK = MAX_NODES
        for j in range(0, int(ncnt[i])):
            Trees['tree-'+str(i+1)]['Nodes'].append([int(json['Nodes-'+str(Trlabel[i])][j]['x']), 1, svg_h - int(json['Nodes-'+str(Trlabel[i])][j]['y'])])
            Trees['tree-'+str(i+1)]['id'].append(int(json['Nodes-'+str(Trlabel[i])][j]['id']))
            if json['Nodes-'+str(Trlabel[i])][j]['title']:
                Trees['tree-'+str(i+1)]['title'].append(int(json['Nodes-'+str(Trlabel[i])][j]['title']))
                if int(json['Nodes-'+str(Trlabel[i])][j]['title']) > maxn:
                    maxn = int(json['Nodes-'+str(Trlabel[i])][j]['title'])
            else:
                Trees['tree-'+str(i+1)]['title'].append(UK)
                UK += 1
    return maxn, Trees

def load_edges_data_2_trees(Trees, Tcnt, json, Trlabel, ecnt):
    # Sort nodes based on id, sort title based on node id,
    # and save links to np array, according to sorted node id.
    for i in range(0, Tcnt):
        Trees['tree-'+str(i+1)]['Nodes'] = np.array(Trees['tree-'+str(i+1)]['Nodes'])
        sort_list = np.array(Trees['tree-'+str(i+1)]['id'])
        Trees['tree-'+str(i+1)]['Nodes'] = Trees['tree-'+str(i+1)]['Nodes'][sort_list.argsort()]
        Trees['tree-'+str(i+1)]['title'] = np.array(Trees['tree-'+str(i+1)]['title'])
        Trees['tree-'+str(i+1)]['title'] = update_title(sort_list.argsort(), Trees['tree-'+str(i+1)]['title'])
        sort_list = sorted(sort_list)
        for j in range(0, int(ecnt[i])):
            Trees['tree-'+str(i+1)]['Edges'].append([sort_list.index(int(json['Edges-'+str(Trlabel[i])][j]['source']['id'])), sort_list.index(int(json['Edges-'+str(Trlabel[i])][j]['target']['id']))])
        Trees['tree-'+str(i+1)]['Edges'] = np.array(Trees['tree-'+str(i+1)]['Edges'])
    return Trees

    
def shortest_path(G, source, target):
    path = nx.dijkstra_path(G,source, target)                
    return path

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

def has_intersection(l1, l2):
    return len(list(l1)+list(l2))> len(set(list(l1)+list(l2)))
    

def check_trust_labels(tid, labels):
    pivot = [x for i, x in enumerate(labels[tid]) if x < MAX_NODES]
    for i in range(0, len(labels)):
        if i != tid:
            tmp = [x for i, x in enumerate(labels[i]) if x < MAX_NODES]
            if has_intersection(tmp, pivot)==False:
                return False
    return True
            
    
def find_leaves(links, nodes):
    n,dim = links.shape
    elems = links.reshape((1,n*dim))
    elem, cnt = np.unique(elems, return_counts=True)
    leaves = []
    lnklist = links.tolist()
    lcnt_ = 0
    root = max(nodes[:,2])
    rootcnt = 0
    for i in range(0, len(nodes)):
        if nodes[i, 2]== root:
            rootcnt += 1
    if rootcnt > 1:
        return 'not merge tree'
    
    for i in range(0,len(elem)):
        if cnt[i]==1:
            x = [x for x in lnklist if elem[i] in x]
            end = [y for y in x[0] if y != elem[i]][0]
            lcnt_ += 1
            if nodes[elem[i]][2] < nodes[end][2]:
                leaves.append(elem[i])
            else:
                if nodes[elem[i]][2]<root:
                    return [-1]
                else:
                    continue
    if (lcnt_-len(leaves))>1:
        return [-1]
    return np.array(leaves)

def modify_M(M, l):
    n,dim = M.shape
    for i in range(0, n):
        for j in range(i+1, dim):
            if M[i,j] in l:
                M[i, j] += FLUCT
    return M

def rebulid_connected_set(tmp):
    g = Graph(len(tmp))
    for i in range(0, len(tmp)):
        for j in range(i, len(tmp)):
            if Is_neighbor(tmp[i], tmp[j]):
                g.addEdge(i, j)
    cc = g.connectedComponents()
    tmps = []
    for i in range(0, len(cc)):
        tmp_ = list(tmp[cc[i][0]].flatten())
        for j in range(1, len(cc[i])):
            tmp_ = tmp_+list(tmp[cc[i][j]].flatten())
        tmp_ = set(tmp_)
        tmps.append(list(tmp_))
    return tmps
        
def Is_neighbor(l1, l2):
    return len(set(list(l1.flatten())+list(l2.flatten()))) < len(l1)+len(l2)

def get_links_modified(M, l):
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
        tmps = rebulid_connected_set(tmp)
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
                nn = (x_val_min+x_val_max)/2
                x_val = nn
                new_node = [[x_val, 1., Vallst[i]]]
                new_nodes = np.concatenate((new_nodes, new_node), axis=0)
                M = np.array(M).reshape((n,dim))
            lvalidx +=1
        lvalidx -=1
    return M, new_nodes, np.array(links)


def update_x(x_min, x_max, nodes, pivot, tmp, parent, n):
    for i in range (0, len(parent)):
        if (parent[i] == parent[tmp[pivot]] and (i not in tmp)) or i == tmp[pivot]:
            if nodes[i, 0] < x_min:
                x_min = nodes[i, 0]
            if nodes[i, 0] > x_max:
                x_max = nodes[i, 0]
    return x_min, x_max

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

def update_pivot_labels(l, maxn):
    tmp = maxn+1
    tmps = []
    for i in range(0, len(l)):
        if l[i] > MAX_NODES-1 or l[i] in tmps:
            l[i] = tmp
            tmp += 1
        tmps.append(l[i])
    return l  

def calculate_ultra_M(lcnt, nodes, links):
    aj_matrix = np.zeros((lcnt, lcnt))
    G=nx.Graph()
    G.add_nodes_from([0, len(nodes)])
    for i in range(0, len(links)):
        E_dist = np.linalg.norm(nodes[links[i][0]][[0,2]]-nodes[links[i][1]][[0,2]])
        G.add_edge(links[i][0],links[i][1],weight=E_dist)
    for i in range(0, lcnt):
        for j in range (i, lcnt):
            path = shortest_path(G, i, j)           
            aj_matrix[i,j] = nodes[path[np.argmax(nodes[path,2])],2]
    dist = np.zeros((len(nodes)-lcnt, lcnt))
    for i in range(lcnt, len(nodes)):
        for j in range (0, lcnt):
            dist[i-lcnt,j] = nx.shortest_path_length(G, source=i, target=j, weight='weight')          
    return dist, aj_matrix

def get_dist(MGs, Tcnt, lcnt, GA_param):
    for i in range(0, Tcnt):
        for j in range(0, GA_param-1):
            MGs['tree-'+str(i+1)]['dist_'+str(j+1)] = get_tree_dist(lcnt, MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)], MGs['tree-'+str(i+1)]['Edges_'+str(j+1)])
    return MGs

def get_dict(MGs, dist_AMT, Tcnt, lcnt, GA_param):
    for i in range(0, Tcnt):
        for j in range(0, GA_param-1):
            if j==0:
                MGs['tree-'+str(i+1)]['dict_'+str(j+1)] = map_nodes(MGs['tree-'+str(i+1)]['dist_'+str(j+1)], dist_AMT, lcnt, 'none')
            else:
                MGs['tree-'+str(i+1)]['dict_'+str(j+1)] = map_nodes(MGs['tree-'+str(i+1)]['dist_'+str(j+1)], MGs['tree-'+str(i+1)]['dist_'+str(j)], lcnt, 'none')
    return MGs

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


def rearange_nodes_links_for_GA(MGs, Tcnt, lcnt, GA_param):
    for i in range(0, Tcnt):
        for j in range(0, GA_param-1):
            MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)], MGs['tree-'+str(i+1)]['Edges_'+str(j+1)]=rearange_nodes_links(np.array( MGs['tree-'+str(i+1)]['dict_'+str(j+1)]), MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)], MGs['tree-'+str(i+1)]['Edges_'+str(j+1)])
            MGs['tree-'+str(i+1)]['dist_'+str(j+1)] = get_tree_dist(lcnt, MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)], MGs['tree-'+str(i+1)]['Edges_'+str(j+1)])
    return MGs


def get_tree_dist(lcnt, nodes, links):
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

def get_tree_dist_whole(lcnt, nodes, links):
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

def get_leaves_dist(llcnt, lcnt, nodes, links, mode, ED):
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

def compute_sorted_index(leaves, ncnt, nodes):
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
    
def update_links(links, pivot):
    for i in range(0, len(links)-1):
        if links[i][0] >= pivot:
            links[i][0] = links[i][0]+1
        if links[i][1] >= pivot:
            links[i][1] = links[i][1]+1
    return links

def add_links(links, pivot, newn):
    idx = np.argwhere(links == pivot)
    links = links.tolist()
    links.append([links[idx[0,0]][0], newn])
    return np.array(links)

def update_idx_old(idx, nidx, pivot):
    for i in range(0, pivot):
        if nidx[i]>idx[pivot]:
            nidx[i] = nidx[i] + 1
    for i in range(pivot, len(idx)):
        if idx[i]>idx[pivot]:
            idx[i] = idx[i] +1
    return idx, nidx

def rearange_nodes_links_old(idx, nodes, links):
    nodes = nodes[idx,:]
    for i in range(0, len(links)):
        links[i, 0] = idx.index(links[i, 0])
        links[i, 1] = idx.index(links[i, 1])
    for i in range (0, len(links)):
        links[i] = sorted(links[i])
        
    links = links[links[:,0].argsort()]
    idx = update_idx_links(links[:,0], links[:,1])
    links = links[idx]
    return nodes, links

def update_idx_links(l1, l2):
    nidx = np.array(range(0, len(l1)))
    for i in set(list(l1)):
        if list(l1).count(i)>1:
            idx = [index for index, value in enumerate(l1) if value == i]
            new = np.array(l2[idx]).argsort()
            nidx[idx] = nidx[np.array(idx)[new]]
    return nidx
    
def update_idx(tmp, array):
    for i in range(0, len(array)):
        if list(tmp).count(i)>1:
            idx = [index for index, value in enumerate(tmp) if value == i]
            new = np.array(tmp)[idx]+np.array(array[idx]).argsort()*0.1
            for j in range(0, len(idx)):
                tmp[idx[j]]=new[j]
    sort_list = sorted(tmp)
    idx = []
    for i in range(0, len(tmp)):
        idx.append(sort_list.index(tmp[i]))
    return idx

def rearange_nodes_links(idx, nodes, links):
    idx = update_idx(list(idx), nodes[:, 2])
    idx = list(np.array(idx).argsort())
    nodes = nodes[idx,:]
    for i in range(0, len(links)):
        links[i, 0] = idx.index(links[i, 0])
        links[i, 1] = idx.index(links[i, 1])
    for i in range (0, len(links)):
        links[i] = sorted(links[i])
    links = links[links[:,0].argsort()]
    idx = update_idx_links(links[:,0], links[:,1])
    links = links[idx]
    return nodes, links

def get_tree_dist_between_leaves(UK, l, nodes, links, mode, ED):
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

def mapping_leaves(leaves1, leaves2, label1, label2, nodes1, links1, nodes2, links2, mode, ED):
    nleaves1 = []
    nleaves2 = []
    nlabel = []
    
    UKleaves1 = []
    UKleaves2 = []
    UKlabel1 = []
    UKlabel2 = []

    nleaves = np.zeros(len(leaves1))
    UK1idx = []
    UK2idx = []
    for i in range(0, len(leaves1)):
        if label1[i] in label2 and label1[i] < MAX_NODES:
            nleaves1.append(leaves1[i])
            nlabel.append(label1[i])
            idx = label2.index(label1[i])
            nleaves[idx] = leaves1[i]
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
        dist1 = get_tree_dist_between_leaves(UKleaves1, nleaves1, nodes1, links1, mode, ED)
        dist2 = get_tree_dist_between_leaves(UKleaves2, nleaves2, nodes2, links2, mode, ED)
        dict1 = map_nodes_leaves(dist2, dist1)

        for i in range(0, len(dict1)):
            nleaves[UK2idx[i]] = leaves1[UK1idx[dict1[i]]]
    return nleaves

def map_and_extend_leaves(label1, leaves1, nodes1, links1, label2, leaves2,  nodes2,  links2, mode, ED):
   
    nl1 = len(leaves1)
    nl2 = len(leaves2)
    tmplabel = []
    nleaves1 = []
    nleaves2 = []
    nlabel1 = []
    nlabel2 = []
    nnodes2 = deepcopy(nodes2)
    nlinks2 = deepcopy(links2)
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

    idx1 = compute_sorted_index(nleaves1, len(nodes1), nodes1)
    idx2 = compute_sorted_index(nleaves2, len(nnodes2), nnodes2)
    
    nodes1, links1 = rearange_nodes_links_old(idx1, nodes1, links1)
    nnodes2, nlinks2 = rearange_nodes_links_old(idx2, nnodes2, nlinks2)

    nleaves1 = list(range(0, nl1))
    nleaves2 = list(range(0, nl2))
    
    dist_1 = get_leaves_dist(lcnt, len(leaves1), nodes1, links1, mode, ED)
    dist_2 = get_leaves_dist(lcnt, len(leaves2), nnodes2, nlinks2, mode, ED)

    nodes1, links1, nleaves1, nlabel1 = add_leaves_and_links(nodes1, links1, nleaves1, nlabel1, nlabel2, dist_2, dist_1, lcnt)

    return nlabel1, nleaves1, nodes1, links1

def map_and_extend_leaves_unlabelled(label1, leaves1, nodes1, links1, label2, leaves2,  nodes2,  links2, mode, ED):
   
    nl1 = len(leaves1)
    nl2 = len(leaves2)
    dist_M = np.zeros((nl1, nl2))
    for i in range(0, nl1):
        for j in range(0, nl2):
            dist_M[i,j] = np.linalg.norm(nodes1[leaves1[i]][[0,2]]-nodes2[leaves2[j]][[0,2]])
    row_ind, col_ind = linear_sum_assignment(dist_M)
    label1 = update_label(label1, label2, col_ind)
    nlabel1, nleaves1, nodes1, links1  = map_and_extend_leaves(label1, leaves1, nodes1, links1, label2, leaves2,  nodes2,  links2, mode, ED)
    
    return nlabel1, nleaves1, nodes1, links1

def update_label(label1, label2, idx):
    for i in range(0, len(idx)):
        label1[i] = label2[idx[i]]
    return label1
    

def move_the_labelled_to_the_front(nl, l):
    nnl = list(copy_array(nl))
    for i in range(0, len(l)):
        if l[i] not in nnl:
            nnl.append(l[i])
    return nnl

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


def map_nodes(dist1, dist2, lcnt, op, mode=None):
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


def map_nodes_leaves(dist1, dist2):
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
    
def map_leaves(dist1, dist2, lcnt, op):
    tmp = 0
    map_dict = []
    for i in range(0, lcnt):
        map_dict.append(i)
    for i in range(0, len(dist1)):
        idx = find_min_square_dist(dist1[i], dist2, op, map_dict, lcnt)
        map_dict.append(idx)
    return map_dict


def update_title(idx, title):
    ntitle = []
    for i in range(0, len(title)):
        ntitle.append(title[idx[i]])
    return np.array(ntitle)

def calculate_cls_label(n, l, L, maxn, mode):
    cls = []
    label = []
    tmp = maxn+1
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
            label.append("")
    return cls, label

def update_nodes(nodes, svg_h):
    for i in range(0, len(nodes)):
        nodes[i,2] = svg_h-nodes[i,2]
    return nodes

def copy_array(l):
    tmp = []
    for i in range(0, len(l)):
        tmp.append(l[i])
    return np.array(tmp)

def extend_nodes_links(sd, nodes, links):
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


def adjust_sd(idx, nodes, links):
    nnodes = nodes[:, [0,2]].tolist()
    tmp = [i for i, e in enumerate(nnodes) if e == nnodes[idx]]
    if len(tmp)>1:
        for i in range(0, len(tmp)):
            if nodes[tmp[i], 1]>0:
                idx = tmp[i]
    return idx


def adjust_dict(ndict, nodes, dist1, dist2, lcnt):
    if len(set(ndict)) < len(nodes):
            exdict = map_nodes(dist1, dist2, lcnt, 'unique')
            for i in range(0, len(nodes)):
                if i not in ndict:
                    ndict[exdict[i]]=i
    return ndict

def adjust_leaves_dict(ndict, leaves, dist1, dist2, lcnt):
    if len(set(ndict)) < len(leaves):
            exdict = map_leaves(dist1[lcnt:len(dist1)], dist2, lcnt, 'unique')
            for i in range(0, len(leaves)):
                if i not in ndict:
                    ndict[exdict[i]]=i
    return ndict

def count_labelled_leaves(l):
    tmp = 0
    for i in range(0, len(l)):
        if l[i]<MAX_NODES:
            tmp += 1
    return tmp

def find_max_labelled_leaves_tree(m):
    tmp = []
    for i in range(0, len(m)):
        tmp.append(count_labelled_leaves(m[i]))
    tmp = np.array(tmp)
    return np.where(tmp==tmp.max())[0][0]

def elementwise_1_center(Ms, i, j):
    tmp = []
    for tid in range(0, len(Ms)):
        tmp.append(Ms[tid][i, j])
    return (max(tmp)+min(tmp))/2

def failure_status(err):
    if err == 'not tree':
        data = {'status': 'failure', 'error-type':"not tree"}
    elif err == 'wrong labelling':
        data = {'status': 'failure', 'error-type':"wrong labelling mode"}
    elif err == 'not merge tree':
        data = {'status': 'failure', 'error-type':"not merge tree"}
    elif err == "Not Unique labelling":
        data = {'status': 'failure', 'error-type':"not unique"}
    else:
        data = {'status': 'failure', 'error-type':"Unknown Error"}
    return data


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
    
def Find_leaves_and_save_labels(Trees, Tcnt):
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

def calculate_IL_dist_for_Trees(Trees, Tcnt, Ms, M):
    for i in range(0, Tcnt):
        Trees['tree-'+str(i+1)]['IL-dist'] = infinity_norm(Ms[i], M)
    return Trees

def infinity_norm(M1, M2):
    M1 = fill_sym_matrix(M1)
    M2 = fill_sym_matrix(M2)    
    return  np.linalg.norm(M1-M2, np.inf)

def calculate_IL_dist_for_GA(MGs, Tcnt, M, GA_param):
    for i in range(0, Tcnt):
        for j in range(0, GA_param-1):
            MGs['tree-'+str(i+1)]['IL-dist_'+str(j+1)]= infinity_norm(MGs['tree-'+str(i+1)]['M_'+str(j+1)], M)
    return MGs

def calculate_local_dist_for_Trees(Trees, Tcnt, Udist, DELTA, mapping_mode, ED_param):
    ldist = np.zeros(len(Udist))
    #print "--------"
    #print Udist
    #print "start"
    for i in range(0, Tcnt):
        Trees['tree-'+str(i+1)]['local-dist'] = calculate_local_dist(Trees['tree-'+str(i+1)]["Nodes"], Trees['tree-'+str(i+1)]["Edges"], Udist, DELTA, mapping_mode, ED_param)
        #print Trees['tree-'+str(i+1)]['local-dist']
        ldist += Trees['tree-'+str(i+1)]['local-dist']
    #print "--------------"
    ldist = ldist/Tcnt
    Uldist = []
    for i in range(0, Tcnt):
        tmp = abs(Trees['tree-'+str(i+1)]['local-dist']-ldist)
        Uldist.append(tmp)
    max_ldist = np.amax(Uldist)
    Uldist = np.array(Uldist).T.tolist()
    for i in range(0, len(Uldist)):
        Uldist[i] = sorted(Uldist[i])
    gUldist = []
    for i in range(0, len(Uldist)):
        gUldist.append([])
        for j in range(0, Tcnt):
            gUldist[i].append({"tree-"+str(j+1): Uldist[i][j]})

    stmp = []
    for i in range(0, Tcnt):
        stmp.append(Trees['tree-'+str(i+1)]['local-dist'])
    stmp = np.array(stmp).T

    sldist=[]
    for i in range(0, len(stmp)):
        sldist.append({"min": min(stmp[i]), "1st-q": np.percentile(stmp[i], 25), "median":  np.median(stmp[i]), "3rd-q":  np.percentile(stmp[i], 75), "max":  max(stmp[i])})
            
    return Trees, ldist, gUldist, max_ldist, sldist


def calculate_local_dist_for_GA(MGs, Tcnt, GA_param, Udist, DELTA, mapping_mode, ED_param):
    for i in range(0, Tcnt):
        for j in range(0, GA_param-1):
            MGs['tree-'+str(i+1)]['local-dist_'+str(j+1)]=  calculate_local_dist(MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)], MGs['tree-'+str(i+1)]['Edges_'+str(j+1)], Udist, DELTA, mapping_mode, ED_param)
    return MGs

def calculate_local_dist(nodes, links, dist2, DELTA, mapping_mode, ED_param):
    dist1 = calculate_whole_dist_matrix(nodes, links, mapping_mode, ED_param)
    #print dist1
    dist = np.zeros(len(nodes))
    for i in range(0, len(nodes)):
        dist[i] = calculate_weighted_cosine_similarity(dist1[i], dist2[i], DELTA)
    return dist

def calculate_weighted_cosine_similarity(A, B, DELTA):
    C = 0
    D = 0
    E = 0
    for i in range(0, len(A)):
        C += math.exp(-(A[i]**2+B[i]**2)/DELTA**2)*A[i]*B[i]
        D += math.exp(-2*(A[i]**2)/(DELTA**2))*(A[i]**2)
        E += math.exp(-2*(B[i]**2)/(DELTA**2))*(B[i]**2)
    return C/math.sqrt(D)/math.sqrt(E)

def calculate_whole_dist_matrix(nodes, links, mode, ED):
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


def fill_sym_matrix(M):
    for i in range(0, len(M)):
        for j in range(0, i):
            M[i][j] = M[j][i]
    return M

def MAPPING_AND_EXTEND_LEAVES(Trees, Tcnt, lcnts, label_mode, labels, leaves, mapping_mode, ED_param, maxn):
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
            if lcnts[i] < lcnts[pivot]:
                if label_mode == 'trust-labels':
                    labels[i], leaves[i], Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges'] = map_and_extend_leaves(labels[i], leaves[i], Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges'], labels[pivot], leaves[pivot], Trees['tree-'+str(pivot+1)]['Nodes'], Trees['tree-'+str(pivot+1)]['Edges'], mapping_mode, ED_param)
                else:
                    labels[pivot] = update_pivot_labels(labels[pivot], maxn)
                    labels[i], leaves[i], Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges'] = map_and_extend_leaves_unlabelled(labels[i], leaves[i], Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges'], labels[pivot], leaves[pivot], Trees['tree-'+str(pivot+1)]['Nodes'], Trees['tree-'+str(pivot+1)]['Edges'], mapping_mode, ED_param)

                    
    else:
        pivot = find_max_labelled_leaves_tree(labels)        
        if label_mode == 'not-trust-labels':
            labels[pivot] = update_pivot_labels(labels[pivot], maxn)
            for i in range(0, Tcnt):
                labels[i], leaves[i], Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges'] = map_and_extend_leaves_unlabelled(labels[i], leaves[i], Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges'], labels[pivot], leaves[pivot], Trees['tree-'+str(pivot+1)]['Nodes'], Trees['tree-'+str(pivot+1)]['Edges'], mapping_mode, ED_param)

    for i in range(0, Tcnt):
        if i != pivot:
            leaves[i] = mapping_leaves(leaves[i], leaves[pivot], labels[i], labels[pivot], Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges'], Trees['tree-'+str(pivot+1)]['Nodes'], Trees['tree-'+str(pivot+1)]['Edges'], mapping_mode, ED_param)


    idx = Trees['tree-'+str(pivot+1)]['Nodes'][leaves[pivot]][:,0].argsort()
    for i in range(0, Tcnt):
        leaves[i] = leaves[i][idx]
    
        
    label = labels[pivot]
    
    return leaves, label, Trees

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

def ADD_EXTRA_NODES_LINKS(Trees, Tcnt, MGs, GA_param, dists, lcnt, ncnt, Unodes):
    for i in range(0, Tcnt):
        dist_U = MGs['tree-'+str(i+1)]['dist_'+str(GA_param-1)]
        if len(Unodes) > ncnt[i]:
            sdictU = map_nodes(dist_U, dists[i], lcnt, 'none', 'internal')
            # Ensure each nodes in smaller tree and be mapped to the nodes in larger tree.
            sdictU = adjust_dict(sdictU, Trees['tree-'+str(i+1)]['Nodes'], dists[i], dist_U, lcnt)
            Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges'] = extend_nodes_links(sdictU, Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges'])
    return Trees

def ADD_EXTRA_NODES_LINKS_FOR_GA(MGs, Tcnt, dist_U, lcnt, Unodes, GA_param):
    for i in range(0, Tcnt):
        for j in range(0, GA_param-1):
            if len(Unodes) > len(MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)]):
                sdictU = map_nodes(dist_U, MGs['tree-'+str(i+1)]['dist_'+str(j+1)], lcnt, 'none')
                sdictU = adjust_dict(sdictU, MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)], MGs['tree-'+str(i+1)]['dist_'+str(j+1)], dist_U, lcnt)
                MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)], MGs['tree-'+str(i+1)]['Edges_'+str(j+1)] = extend_nodes_links(sdictU, MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)], MGs['tree-'+str(i+1)]['Edges_'+str(j+1)])
    return MGs

def load_Trees(data, Trees, Tcnt, Trlabel, label, cls, ncnt, ecnt, nodes, links, Unodes, Ulinks, GA_param, Uldist, gUldist, max_ldist, sldist):
    data["max_ldist"] = max_ldist
    for i in range (0, Tcnt):
        data["IL-dist-"+str(Trlabel[i])] = Trees['tree-'+str(i+1)]['IL-dist']
        data["IL-dist-"+str(Trlabel[i])+"-0"] = 0
        data["IL-dist-"+str(Trlabel[i])+"-"+str(GA_param)] =  Trees['tree-'+str(i+1)]['IL-dist']
        for j in range(0, ncnt[i]):
            data["Nodes-"+str(Trlabel[i])].append({"id": j, "x": Trees['tree-'+str(i+1)]['Nodes'][j, 0], "y":  Trees['tree-'+str(i+1)]['Nodes'][j, 2], "title":label[j], "cls": cls[j],'local-dist': Trees['tree-'+str(i+1)]['local-dist'][j]})
            data["Nodes-"+str(Trlabel[i])+"-"+str(GA_param)].append({"id": j, "x": Trees['tree-'+str(i+1)]['Nodes'][j, 0], "y":  Trees['tree-'+str(i+1)]['Nodes'][j, 2], "title":label[j], "cls": cls[j],'local-dist': Trees['tree-'+str(i+1)]['local-dist'][j]})
        for j in range(0, ecnt[i]):
            data["Edges-"+str(Trlabel[i])].append({"id": j, "source":{"id": Trees['tree-'+str(i+1)]['Edges'][j, 0], "title": Trees['tree-'+str(i+1)]['Edges'][j,0], "x": Trees['tree-'+str(i+1)]['Nodes'][Trees['tree-'+str(i+1)]['Edges'][j, 0],0], "y": Trees['tree-'+str(i+1)]['Nodes'][Trees['tree-'+str(i+1)]['Edges'][j, 0],2], "local-dist": Trees['tree-'+str(i+1)]['local-dist'][Trees['tree-'+str(i+1)]['Edges'][j, 0]]} , "target": {"id": Trees['tree-'+str(i+1)]['Edges'][j, 1], "title": Trees['tree-'+str(i+1)]['Edges'][j,1], "x": Trees['tree-'+str(i+1)]['Nodes'][Trees['tree-'+str(i+1)]['Edges'][j,1],0], "y": Trees['tree-'+str(i+1)]['Nodes'][Trees['tree-'+str(i+1)]['Edges'][j, 1],2], "local-dist": Trees['tree-'+str(i+1)]['local-dist'][Trees['tree-'+str(i+1)]['Edges'][j, 1]]}})
            data["Edges-"+str(Trlabel[i])+"-"+str(GA_param)].append({"id": j, "source":{"id": Trees['tree-'+str(i+1)]['Edges'][j, 0], "title": Trees['tree-'+str(i+1)]['Edges'][j,0], "x": Trees['tree-'+str(i+1)]['Nodes'][Trees['tree-'+str(i+1)]['Edges'][j, 0],0], "y": Trees['tree-'+str(i+1)]['Nodes'][Trees['tree-'+str(i+1)]['Edges'][j, 0],2], "local-dist": Trees['tree-'+str(i+1)]['local-dist'][Trees['tree-'+str(i+1)]['Edges'][j, 0]]} , "target": {"id": Trees['tree-'+str(i+1)]['Edges'][j, 1], "title": Trees['tree-'+str(i+1)]['Edges'][j,1], "x": Trees['tree-'+str(i+1)]['Nodes'][Trees['tree-'+str(i+1)]['Edges'][j,1],0], "y": Trees['tree-'+str(i+1)]['Nodes'][Trees['tree-'+str(i+1)]['Edges'][j, 1],2], "local-dist": Trees['tree-'+str(i+1)]['local-dist'][Trees['tree-'+str(i+1)]['Edges'][j, 1]]}})
        for j in range(0, len(Unodes)):
            data["Nodes-"+str(Trlabel[i])+"-0"].append({"id": j, "x":Unodes[j,0], "y": Unodes[j,2], "title":label[j], "cls": cls[j], 'local-dist': Uldist[j]})
        for j in range(0, len(Ulinks)):
            data["Edges-"+str(Trlabel[i])+"-0"].append({"id": j, "source":{"id": label[Ulinks[j, 0]], "title": label[Ulinks[j,0]], "x": Unodes[Ulinks[j,0],0], "y": Unodes[Ulinks[j, 0],2], 'local-dist': Uldist[Ulinks[j, 0]] } , "target": {"id": label[Ulinks[j, 1]], "title": label[Ulinks[j,1]], "x": Unodes[Ulinks[j,1],0], "y":  Unodes[Ulinks[j, 1],2], 'local-dist': Uldist[Ulinks[j, 1]]}}) 
    for i in range(0, len(nodes)):
        data["Nodes-AMT"].append({"id": i, "x":nodes[i,0], "y": nodes[i,2], "title":label[i], "cls": cls[i]})
    for i in range(0, len(links)):
        data["Edges-AMT"].append({"id": i, "source":{"id": label[links[i, 0]], "title": label[links[i,0]], "x": nodes[links[i,0],0], "y": nodes[links[i, 0],2]} , "target": {"id": label[links[i, 1]], "title": label[links[i,1]], "x": nodes[links[i,1],0], "y":  nodes[links[i, 1],2]}})

    for i in range(0, len(Unodes)):
        data["UNodes-AMT"].append({"id": i, "x":Unodes[i,0], "y": Unodes[i,2], "title":label[i], "cls": cls[i], 'local-dist': Uldist[i], 'glocal-dist': gUldist[i], 'sldist': sldist[i]})
    for i in range(0, len(Ulinks)):
        data["UEdges-AMT"].append({"id": i, "source":{"id": label[Ulinks[i, 0]], "title": label[Ulinks[i,0]], "x": Unodes[Ulinks[i,0],0], "y": Unodes[Ulinks[i, 0],2], 'local-dist': Uldist[Ulinks[i, 0]], 'glocal-dist':  gUldist[Ulinks[i, 0]], 'sldist': sldist[Ulinks[i, 0]]} , "target": {"id": label[Ulinks[i, 1]], "title": label[Ulinks[i,1]], "x": Unodes[Ulinks[i,1],0], "y":  Unodes[Ulinks[i, 1],2], 'local-dist': Uldist[Ulinks[i, 1]], 'glocal-dist':  gUldist[Ulinks[i, 1]], 'sldist': sldist[Ulinks[i, 1]]}}) 
    return data

def load_GA_Trees(data, MGs, Tcnt, Trlabel, label, cls, GA_param):
    data["GA_param"] = GA_param
    for i in range(0, Tcnt):
        for j in range(0, GA_param-1):
            data["IL-dist-"+str(Trlabel[i])+'-'+str(j+1)] = MGs['tree-'+str(i+1)]['IL-dist_'+str(j+1)]
            ncnt = len(MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)])
            for k in range(0, ncnt):
                data["Nodes-"+str(Trlabel[i])+'-'+str(j+1)].append({"id": k, "x": MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)][k, 0], "y":  MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)][k, 2], "title":label[k], "cls": cls[k], 'local-dist': MGs['tree-'+str(i+1)]['local-dist_'+str(j+1)][k]})
            ecnt = len(MGs['tree-'+str(i+1)]['Edges_'+str(j+1)])
            for k in range(0, ecnt):
                data["Edges-"+str(Trlabel[i])+'-'+str(j+1)].append({"id": k, "source":{"id": MGs['tree-'+str(i+1)]['Edges_'+str(j+1)][k, 0],  "x": MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)][MGs['tree-'+str(i+1)]['Edges_'+str(j+1)][k, 0],0], "y": MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)][MGs['tree-'+str(i+1)]['Edges_'+str(j+1)][k, 0],2]}, "target": {"id": MGs['tree-'+str(i+1)]['Edges_'+str(j+1)][k, 1], "x": MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)][MGs['tree-'+str(i+1)]['Edges_'+str(j+1)][k, 1],0], "y": MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)][MGs['tree-'+str(i+1)]['Edges_'+str(j+1)][k, 1],2]}})
    return data

def rearange_links(links1, links2):
    l1 = links1[:].tolist()
    l2 = links2[:].tolist()
    idx = np.zeros(len(l1)).astype(int)-1
    Uidx1 = []
    Uidx2 = []
    for i in range(0, len(l1)):
        if l1[i] in l2:
            idx[l2.index(l1[i])]=i
        else:
            Uidx1.append(i)
    for i in range(0, len(idx)):
        if idx[i] <0:
            Uidx2.append(i)
    for i in range(0, len(Uidx1)):
        for j in range(0, len(Uidx2)):
            if links1[Uidx1[i], 0] == links2[Uidx2[j], 0]:
                idx[Uidx2[j]]=Uidx1[i]
    Uidx1 = []
    for i in range(0, len(l1)):
        if i not in idx:
            Uidx1.append(i)
    
    j = 0
    for i in range(0, len(idx)):
        if idx[i]<0:
            if links1[Uidx1[j]][1]==links2[i][0]:
                tmp = links1[Uidx1[j]][1]
                links1[Uidx1[j]][1] =  links1[Uidx1[j]][0]
                links1[Uidx1[j]][0] = tmp        
            idx[i]=Uidx1[j]
            j += 1
    links1 = links1[idx]
    return links1

def print_MGs(MGs, Tcnt, GA_param):
    for i in range(0, Tcnt):
        for j in range(0, GA_param-1):
            print MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)]
            print MGs['tree-'+str(i+1)]['Edges_'+str(j+1)]
                                        

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
            
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/say_name', methods=['POST'])
def say_name():
    json = request.get_json()
    Trlabel = json['tids']
    Tcnt = len(Trlabel)
    svg_w = json['width']
    svg_h = float(json['height'])
    label_mode = json['label-mode']
    mapping_mode = json['mapping-mode']
    ED_param = json['ED_param']
    GA_param = json['GA_param']
    sigma = float(json['sigma'])
    DELTA = sigma*svg_h
    #print DELTA
    #DELTA = 20
    
    # Record the number of nodes and edges in each trees.
    ncnt = np.zeros(Tcnt).astype(int)
    ecnt = np.zeros(Tcnt).astype(int)
    for i in range(0, Tcnt):
        ncnt[i] = len(json['Nodes-'+str(Trlabel[i])]) 
        ecnt[i] = len(json['Edges-'+str(Trlabel[i])])

    # Initialize and load data to trees.
    Trees = {}
    Trees = initialization(Trees, Tcnt)
    maxn, Trees = load_nodes_data_2_trees(Trees, Tcnt, json, Trlabel, ncnt, svg_h)
    Trees = load_edges_data_2_trees(Trees, Tcnt, json, Trlabel, ecnt)

    # Check data structure: is or is not a tree.
    Istree = check_is_tree(Trees, Tcnt)
    if (Istree==False):
        return jsonify(failure_status("not tree"))
    
    # Find leaves from trees.
    # Save the title of leaves.
    leaves, labels, lcnts = Find_leaves_and_save_labels(Trees, Tcnt)

    # Check data structure: is or is not a merge tree.
    Ismergetree = check_is_merge_tree(leaves, Trees, Tcnt)
    if (Ismergetree==False):
        return jsonify(failure_status("not merge tree"))
    
    # Check data structure: can or cannot use "Enforce Labels" mode.
    if label_mode == 'trust-labels':
        CanUseEL = check_can_EF(lcnts, labels)
        if (CanUseEL==False):
            return jsonify(failure_status("wrong labelling"))
        UniqueL = check_unique_label(labels)
        if  (UniqueL==False):
            return jsonify(failure_status("Not Unique labelling"))

    # Matching the leaves and arrange them in corresponding order.
    # If the number of leaves are not the same. Make them the same by adding additional leaves.
    # Update labels, leaves, nodes, and links according to the change above.
    leaves, label, Trees = MAPPING_AND_EXTEND_LEAVES(Trees, Tcnt, lcnts, label_mode, labels, leaves, mapping_mode, ED_param, maxn)

    # Compute the index of nodes, putting the leaves in the front.
    # Rearrange the order of nodes according to the index, and update the links.    
    for i in range(0, Tcnt):
        ncnt[i] = len(json['Nodes-'+str(Trlabel[i])])
        ecnt[i] = len(json['Edges-'+str(Trlabel[i])])
    for i in range(0, Tcnt):
        idx = compute_sorted_index(leaves[i], int(ncnt[i]), Trees['tree-'+str(i+1)]['Nodes'])
        Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges']= rearange_nodes_links_old(idx, Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges'])
    lcnt = len(leaves[0])

    # Calculate the ultra matrix for trees
    Ms = []
    dists = []
    for i in range(0, Tcnt):
        dist, M = calculate_ultra_M(lcnt, Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges'])
        dists.append(dist)
        Ms.append(M)

    # Compute the average position of leaves for further use.
    l = Trees['tree-1']['Nodes'][0:len(leaves[0]),:]
    for i in range(1, Tcnt):
        l = l + Trees['tree-'+str(i+1)]['Nodes'][0:len(leaves[i]),:]
    l = l/Tcnt
        
    # Calculate the 1-center ultra matrix
    M = np.zeros((lcnt, lcnt))
    for i in range(0, lcnt):
        for j in range(i, lcnt):
            M[i, j] = elementwise_1_center(Ms, i, j)

    # Modified the ultra matrix to represent a reasonable merge tree,
    # and create nodes and links based on this matrix. 
    M, nodes, links = get_links_modified(M, l)
    idx = compute_sorted_index(range(0, lcnt), len(nodes), nodes)
    nodes, links = rearange_nodes_links_old(idx, nodes, links)
    
    # Calculate ultra matrix and position of leaves for geodesic_animation.
    MGs = initialization_M_for_geodesic_animation(Tcnt, GA_param)
    MGs = calculate_Ms_for_geodesic_animation(MGs, Ms, M, Tcnt, GA_param)
    MGs = calculate_ls_for_geodesic_animation(MGs, Trees, nodes, Tcnt, len(leaves[0]), GA_param)

    # Rebuild trees from MGs
    MGs = rebuild_GA_trees(MGs, Tcnt, GA_param)


    #print_MGs(MGs, Tcnt, GA_param)


    # Compute pairwise tree distance matrix.
    dist_AMT = get_tree_dist(lcnt, nodes, links)

    # Mapping nodes between trees according to tree distance matrices for GA Matrix
    MGs = MAPPING_ITERNAL_NODES_FOR_GA(MGs, Tcnt, lcnt, dist_AMT, GA_param)

    
    # Mapping nodes between trees according to tree distance matrices.
    dicts = []
    for i in range(0, Tcnt):
        dicts.append(map_nodes(dists[i], MGs['tree-'+str(i+1)]['dist_'+str(GA_param-1)], lcnt, 'none'))
    
    # Rearange the nodes and links according to the mapping strategy.
    nodes, links = rearange_nodes_links_old(range(0,len(nodes)), nodes, links)
    for i in range(0, Tcnt):
        Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges']=rearange_nodes_links(dicts[i], Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges'])



    # Calculate Global Uncertainty - Interleaving distance
    Trees = calculate_IL_dist_for_Trees(Trees, Tcnt, Ms, M)
    MGs = calculate_IL_dist_for_GA(MGs, Tcnt, M, GA_param)
    
    # Recalculate the pairwise tree distance.
    dists = []
    for i in range(0, Tcnt):
        dists.append(get_tree_dist_whole(lcnt, Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges']))
        dicts[i] = sorted(dicts[i])


    # If numbers of trees' nodes are not the same.
    # We need to add extra nodes and links for animation.
    Unodes, Ulinks, dist_U = MAKE_AMT_LARGEST(ncnt, nodes, links, MGs, dist_AMT, lcnt)
    MGs = get_dict(MGs, dist_U, Tcnt, lcnt, GA_param)
    MGs = ADD_EXTRA_NODES_LINKS_FOR_GA(MGs, Tcnt, dist_U, lcnt, Unodes, GA_param)
    MGs = get_dist(MGs, Tcnt, len(leaves[0]), GA_param)
    Trees = ADD_EXTRA_NODES_LINKS(Trees, Tcnt, MGs, GA_param, dists, lcnt, ncnt, Unodes)
    # Edit Internal nodes for geodesic animation.
    MGs = updata_internal_x_for_GA(MGs, Tcnt, Trees, Unodes, GA_param)

    # Calculate local Uncertainty for each node - Weighted-Cosine Similarity
    Udist = calculate_whole_dist_matrix(Unodes, Ulinks, mapping_mode, ED_param)
    Trees, Uldist, gUldist, max_ldist, sldist = calculate_local_dist_for_Trees(Trees, Tcnt, Udist, DELTA, mapping_mode, ED_param)


    
    MGs = calculate_local_dist_for_GA(MGs, Tcnt, GA_param, Udist, DELTA, mapping_mode, ED_param)

    # Rearange the links for visualization.
    MGs = REARANGE_LINKS_for_GA(MGs, Tcnt,  Ulinks, GA_param)

    Trees = REARANGE_LINKS(Trees, Tcnt, MGs, GA_param)
    
    for i in range(0, Tcnt):
        ncnt[i] = len(Trees['tree-'+str(i+1)]['Nodes']) 
        ecnt[i] = len(Trees['tree-'+str(i+1)]['Edges'])
        
    # Generate class and label properties for each nodes.
    cls, label = calculate_cls_label(len(Unodes), lcnt, label, maxn, label_mode)
    # Update nodes according to height of svg
    nodes = update_nodes(nodes, svg_h)
    Unodes = update_nodes(Unodes, svg_h)
    for i in range(0, Tcnt):
        Trees['tree-'+str(i+1)]['Nodes'] = update_nodes(Trees['tree-'+str(i+1)]['Nodes'], svg_h)
    
    for i in range(0, Tcnt):
        MGs['tree-'+str(i+1)]['Nodes_0']=Trees['tree-'+str(i+1)]['Nodes']
        MGs['tree-'+str(i+1)]['Edges_0']=Trees['tree-'+str(i+1)]['Edges']
        MGs['tree-'+str(i+1)]['Nodes_'+str(GA_param)] = Unodes
        MGs['tree-'+str(i+1)]['Edges_'+str(GA_param)] = Ulinks
        for j in range(0, GA_param-1):
            MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)] = update_nodes(MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)], svg_h)
        
    # Convert np array data to json data, and send it to website.
    data = initialization_returned_data(Tcnt, Trlabel, GA_param)
    data = load_Trees(data, Trees, Tcnt, Trlabel, label, cls, ncnt, ecnt, nodes, links, Unodes, Ulinks, GA_param, Uldist, gUldist, max_ldist, sldist)
    data = load_GA_Trees(data, MGs, Tcnt, Trlabel, label, cls, GA_param)

    return jsonify(data)

app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':

    app.run(debug=True)
  
  
   
