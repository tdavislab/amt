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


def load_Trees(data, Trees, Tcnt, Trlabel, label, cls, ncnt, ecnt, nodes, links, Unodes, Ulinks, GA_param, Uldist, gUldist, max_ldist, sldist, clss):
    data["max_ldist"] = max_ldist
    for i in range (0, Tcnt):
        data["IL-dist-"+str(Trlabel[i])] = Trees['tree-'+str(i+1)]['IL-dist']
        data["IL-dist-"+str(Trlabel[i])+"-0"] = 0
        data["IL-dist-"+str(Trlabel[i])+"-"+str(GA_param)] =  Trees['tree-'+str(i+1)]['IL-dist']
        for j in range(0, ncnt[i]):
            data["Nodes-"+str(Trlabel[i])].append({"id": j, "x": Trees['tree-'+str(i+1)]['Nodes'][j, 0], "y":  Trees['tree-'+str(i+1)]['Nodes'][j, 2], "title":label[j], "cls": clss[i][j],'local-dist': Trees['tree-'+str(i+1)]['local-dist'][j]})
            data["Nodes-"+str(Trlabel[i])+"-"+str(GA_param)].append({"id": j, "x": Trees['tree-'+str(i+1)]['Nodes'][j, 0], "y":  Trees['tree-'+str(i+1)]['Nodes'][j, 2], "title":label[j], "cls": clss[i][j],'local-dist': Trees['tree-'+str(i+1)]['local-dist'][j]})
        for j in range(0, ecnt[i]):
            data["Edges-"+str(Trlabel[i])].append({"id": j, "source":{"id": Trees['tree-'+str(i+1)]['Edges'][j, 0], "title": Trees['tree-'+str(i+1)]['Edges'][j,0], "x": Trees['tree-'+str(i+1)]['Nodes'][Trees['tree-'+str(i+1)]['Edges'][j, 0],0], "y": Trees['tree-'+str(i+1)]['Nodes'][Trees['tree-'+str(i+1)]['Edges'][j, 0],2], "local-dist": Trees['tree-'+str(i+1)]['local-dist'][Trees['tree-'+str(i+1)]['Edges'][j, 0]]} , "target": {"id": Trees['tree-'+str(i+1)]['Edges'][j, 1], "title": Trees['tree-'+str(i+1)]['Edges'][j,1], "x": Trees['tree-'+str(i+1)]['Nodes'][Trees['tree-'+str(i+1)]['Edges'][j,1],0], "y": Trees['tree-'+str(i+1)]['Nodes'][Trees['tree-'+str(i+1)]['Edges'][j, 1],2], "local-dist": Trees['tree-'+str(i+1)]['local-dist'][Trees['tree-'+str(i+1)]['Edges'][j, 1]]}})
            data["Edges-"+str(Trlabel[i])+"-"+str(GA_param)].append({"id": j, "source":{"id": Trees['tree-'+str(i+1)]['Edges'][j, 0], "title": Trees['tree-'+str(i+1)]['Edges'][j,0], "x": Trees['tree-'+str(i+1)]['Nodes'][Trees['tree-'+str(i+1)]['Edges'][j, 0],0], "y": Trees['tree-'+str(i+1)]['Nodes'][Trees['tree-'+str(i+1)]['Edges'][j, 0],2], "local-dist": Trees['tree-'+str(i+1)]['local-dist'][Trees['tree-'+str(i+1)]['Edges'][j, 0]]} , "target": {"id": Trees['tree-'+str(i+1)]['Edges'][j, 1], "title": Trees['tree-'+str(i+1)]['Edges'][j,1], "x": Trees['tree-'+str(i+1)]['Nodes'][Trees['tree-'+str(i+1)]['Edges'][j,1],0], "y": Trees['tree-'+str(i+1)]['Nodes'][Trees['tree-'+str(i+1)]['Edges'][j, 1],2], "local-dist": Trees['tree-'+str(i+1)]['local-dist'][Trees['tree-'+str(i+1)]['Edges'][j, 1]]}})
        for j in range(0, len(Unodes)):
            data["Nodes-"+str(Trlabel[i])+"-0"].append({"id": j, "x":Unodes[j,0], "y": Unodes[j,2], "title":label[j], "cls": cls[j], 'local-dist': 1})
        for j in range(0, len(Ulinks)):
            data["Edges-"+str(Trlabel[i])+"-0"].append({"id": j, "source":{"id": label[Ulinks[j, 0]], "title": label[Ulinks[j,0]], "x": Unodes[Ulinks[j,0],0], "y": Unodes[Ulinks[j, 0],2], 'local-dist': Uldist[Ulinks[j, 0]] } , "target": {"id": label[Ulinks[j, 1]], "title": label[Ulinks[j,1]], "x": Unodes[Ulinks[j,1],0], "y":  Unodes[Ulinks[j, 1],2], 'local-dist': Uldist[Ulinks[j, 1]]}})
    for i in range(0, len(nodes)):
        data["Nodes-AMT"].append({"id": i, "x":nodes[i,0], "y": nodes[i,2], "title":label[i], "cls": cls[i]})
    for i in range(0, len(links)):
        data["Edges-AMT"].append({"id": i, "source":{"id": label[links[i, 0]], "title": label[links[i,0]], "x": nodes[links[i,0],0], "y": nodes[links[i, 0],2]} , "target": {"id": label[links[i, 1]], "title": label[links[i,1]], "x": nodes[links[i,1],0], "y":  nodes[links[i, 1],2]}})

    for i in range(0, len(Unodes)):
        data["UNodes-AMT"].append({"id": i, "x":Unodes[i,0], "y": Unodes[i,2], "title":label[i], "cls": cls[i], 'local-dist': 1, 'glocal-dist': gUldist[i], 'sldist': sldist[i]})
    for i in range(0, len(Ulinks)):
        data["UEdges-AMT"].append({"id": i, "source":{"id": label[Ulinks[i, 0]], "title": label[Ulinks[i,0]], "x": Unodes[Ulinks[i,0],0], "y": Unodes[Ulinks[i, 0],2], 'local-dist': Uldist[Ulinks[i, 0]], 'glocal-dist':  gUldist[Ulinks[i, 0]], 'sldist': sldist[Ulinks[i, 0]]} , "target": {"id": label[Ulinks[i, 1]], "title": label[Ulinks[i,1]], "x": Unodes[Ulinks[i,1],0], "y":  Unodes[Ulinks[i, 1],2], 'local-dist': Uldist[Ulinks[i, 1]], 'glocal-dist':  gUldist[Ulinks[i, 1]], 'sldist': sldist[Ulinks[i, 1]]}})
    return data

def load_GA_Trees(data, MGs, Tcnt, Trlabel, label, cls, GA_param, clss):
    data["GA_param"] = GA_param
    for i in range(0, Tcnt):
        for j in range(0, GA_param-1):
            data["IL-dist-"+str(Trlabel[i])+'-'+str(j+1)] = MGs['tree-'+str(i+1)]['IL-dist_'+str(j+1)]
            ncnt = len(MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)])
            for k in range(0, ncnt):
                data["Nodes-"+str(Trlabel[i])+'-'+str(j+1)].append({"id": k, "x": MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)][k, 0], "y":  MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)][k, 2], "title":label[k], "cls": clss[i][k], 'local-dist': MGs['tree-'+str(i+1)]['local-dist_'+str(j+1)][k]})
            ecnt = len(MGs['tree-'+str(i+1)]['Edges_'+str(j+1)])
            for k in range(0, ecnt):
                data["Edges-"+str(Trlabel[i])+'-'+str(j+1)].append({"id": k, "source":{"id": MGs['tree-'+str(i+1)]['Edges_'+str(j+1)][k, 0],  "x": MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)][MGs['tree-'+str(i+1)]['Edges_'+str(j+1)][k, 0],0], "y": MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)][MGs['tree-'+str(i+1)]['Edges_'+str(j+1)][k, 0],2]}, "target": {"id": MGs['tree-'+str(i+1)]['Edges_'+str(j+1)][k, 1], "x": MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)][MGs['tree-'+str(i+1)]['Edges_'+str(j+1)][k, 1],0], "y": MGs['tree-'+str(i+1)]['Nodes_'+str(j+1)][MGs['tree-'+str(i+1)]['Edges_'+str(j+1)][k, 1],2]}})
    return data

