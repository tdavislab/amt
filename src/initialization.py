from functions_util import *

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
            M['tree-'+str(i+1)]['Mx_'+str(j+1)]=[]
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
