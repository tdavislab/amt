from __future__ import division
from functions_util import *
from tree_util import calculate_whole_dist_matrix


def fill_sym_matrix(M):
    for i in range(0, len(M)):
        for j in range(0, i):
            M[i][j] = M[j][i]
    return M

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
    for i in range(0, Tcnt):
        Trees['tree-'+str(i+1)]['local-dist'] = calculate_local_dist(Trees['tree-'+str(i+1)]["Nodes"], Trees['tree-'+str(i+1)]["Edges"], Udist, DELTA, mapping_mode, ED_param)
        ldist += Trees['tree-'+str(i+1)]['local-dist']
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
