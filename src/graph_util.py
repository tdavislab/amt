from __future__ import division
from functions_util import *

"""
    Functions used in rebuilding merge tree from ultra matrix.
"""


class Graph:
    
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

def Is_neighbor(l1, l2):
    return len(set(list(l1.flatten())+list(l2.flatten()))) < len(l1)+len(l2)


def calculate_1_center(l):
    return (max(l)+min(l))/2

def rebulid_connected_set(tmp, M_x):
    """Classify the braches of tree into different connected set according to the graph.
    """
    g = Graph(len(tmp))
    for i in range(0, len(tmp)):
        for j in range(i, len(tmp)):
            if Is_neighbor(tmp[i], tmp[j]):
                g.addEdge(i, j)
    cc = g.connectedComponents()
    tmps = []
    x = []
    for i in range(0, len(cc)):
        x_=[]
        tmp_ = list(tmp[cc[i][0]].flatten())
        x_.append(M_x[tmp[cc[i][0]][0]][tmp[cc[i][0]][1]])
        for j in range(1, len(cc[i])):
            tmp_ = tmp_+list(tmp[cc[i][j]].flatten())
            x_.append(M_x[tmp[cc[i][j]][0]][tmp[cc[i][j]][1]])
        x.append(calculate_1_center(x_))
        tmp_ = set(tmp_)
        tmps.append(list(tmp_))
    return tmps, x
