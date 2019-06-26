from __future__ import division

"""Interactive Visualization Tools for A Structural Average of Labeled Merge Trees"""
# Author: Lin Yan <lynne.h.yan@gmail.com>

import sys
import os
sys.path.append(os.path.abspath('./src'))
from flask import Flask, render_template, request, jsonify
from werkzeug.contrib.fixers import ProxyFix

from files_util import *

app = Flask(__name__)

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
    ED_param = 1.-float(json['ED_param'])
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
    leaves, label, Trees, nlabels = MAPPING_AND_EXTEND_LEAVES(Trees, Tcnt, lcnts, label_mode, labels, leaves, mapping_mode, ED_param, maxn)

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
    Ms_X = []
    for i in range(0, Tcnt):
        dist, M, M_X = calculate_ultra_M(lcnt, Trees['tree-'+str(i+1)]['Nodes'], Trees['tree-'+str(i+1)]['Edges'])
        dists.append(dist)
        Ms.append(M)
        Ms_X.append(M_X)

    # Compute the average position of leaves for further use.
    l = Trees['tree-1']['Nodes'][0:len(leaves[0]),:]
    for i in range(1, Tcnt):
        l = l + Trees['tree-'+str(i+1)]['Nodes'][0:len(leaves[i]),:]
    l = l/Tcnt
        
    # Calculate the 1-center ultra matrix
    M = np.zeros((lcnt, lcnt))
    M_x = np.zeros((lcnt, lcnt))
    for i in range(0, lcnt):
        for j in range(i, lcnt):
            M[i, j] = elementwise_1_center(Ms, i, j)
            M_x[i, j] = elementwise_1_center(Ms_X, i, j)

    # Modified the ultra matrix to represent a reasonable merge tree,
    # and create nodes and links based on this matrix. 
    M, nodes, links = get_links_modified(M, l, M_x)
    idx = compute_sorted_index(range(0, lcnt), len(nodes), nodes)
    nodes, links = rearange_nodes_links_old(idx, nodes, links)

    # Get M_x
    dist, M, M_x = calculate_ultra_M(lcnt,nodes, links)
    
    # Calculate ultra matrix and position of leaves for geodesic_animation.
    MGs = initialization_M_for_geodesic_animation(Tcnt, GA_param)
    MGs = calculate_Ms_for_geodesic_animation(MGs, Ms, M, Tcnt, GA_param, Ms_X, M_x)
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
    #MGs = updata_internal_x_for_GA(MGs, Tcnt, Trees, Unodes, GA_param)

    # Calculate local Uncertainty for each node - Weighted-Cosine Similarity
    Udist = calculate_whole_dist_matrix(Unodes, Ulinks, mapping_mode, ED_param)
    Trees, Uldist, gUldist, max_ldist, sldist = calculate_local_dist_for_Trees(Trees, Tcnt, Udist, DELTA, mapping_mode, ED_param)


    
    MGs = calculate_local_dist_for_GA(MGs, Tcnt, GA_param, Udist, DELTA, mapping_mode, ED_param)

    # Rearange the links for visualization
    MGs = REARANGE_LINKS_for_GA(MGs, Tcnt,  Ulinks, GA_param)

    Trees = REARANGE_LINKS(Trees, Tcnt, MGs, GA_param)
    
    for i in range(0, Tcnt):
        ncnt[i] = len(Trees['tree-'+str(i+1)]['Nodes']) 
        ecnt[i] = len(Trees['tree-'+str(i+1)]['Edges'])
        
    # Generate class and label properties for each nodes.
    cls, label, clss = calculate_cls_label(len(Unodes), lcnt, label, maxn, label_mode, nlabels)
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
    data = load_Trees(data, Trees, Tcnt, Trlabel, label, cls, ncnt, ecnt, nodes, links, Unodes, Ulinks, GA_param, Uldist, gUldist, max_ldist, sldist, clss)
    data = load_GA_Trees(data, MGs, Tcnt, Trlabel, label, cls, GA_param, clss)

    return jsonify(data)

app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':

    app.run(debug=True)
  
  
   
