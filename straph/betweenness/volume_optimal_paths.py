from straph.betweenness import volumes as vol
import numpy
def vol_rec_con_inst(s, e, G_rev, sigma):
    l = list(G_rev.successors(e))
    #print(e,l,sigma)
    w,tp = l[0]
    sigma[e] = dict()
    if w == s:
        sigma[e][0] = vol.Volume(1,0)
        sigma[e][-1] = vol.Volume(1,0)
        return
    else:
        res = vol.Volume(0,0)
        for (w,tp) in l:
            vol_rec_con_inst(s, (w,tp), G_rev, sigma)
            res += sigma[(w,tp)][-1]
        sigma[e][-1] = res
        sigma[e][0] = res

def vol_rec_con(s, e, G_rev, sigma, cur_best, mx):
    if e in sigma:
        return
    if e[0] == s:
        sigma[e] = dict()
        sigma[e][-1] = vol.Volume(0,0)
        return

    if cur_best[e[0]][e[1]][0] == e[1]:
        #instantenous metapaths
        vol_rec_con_inst(s, e, G_rev, sigma)
    else:
        sigma[e] = dict()
        for j in range(0,mx+1):
            l = list(G_rev.successors(e))
            res = vol.Volume(0,0)
            if j == 0:
                for (w,tp) in l:
                    vol_rec_con(s, (w,tp), G_rev, sigma, cur_best, mx)
                    #print("e",e,"res",res, "sigma[(w,tp)][-1]",sigma[(w,tp)][-1],"(w,tp)",(w,tp))
                    res += sigma[(w,tp)][-1]
                sigma[e][0] = res
            elif j == 1:
                for (w,tp) in l:
                    t1,t2 = G_rev.edge_weight(e,(w,tp),"interval")
                    if t1 != t2 and tp <= t1:
                        vol_rec_con(s, (w,tp), G_rev, sigma, cur_best, mx)
                        res += sigma[(w,tp)][-1] * vol.Volume(t2-t1,1)
                sigma[e][1] = res
            else:
                for (w,tp) in l:
                    t1,t2 = G_rev.edge_weight(e,(w,tp),"interval")
                    if t1 != t2 and tp == t2:
                        vol_rec_con(s, (w,tp), G_rev, sigma, cur_best, mx)
                        if (j-1) in sigma[(w,tp)] and sigma[(w,tp)][j-1] != vol.Volume(0,0):
                            res += sigma[(w,tp)][j-1] * vol.Volume((t2-t1)/j,1)
                sigma[e][j] = res

        sigma[e][-1] = sum( [sigma[e][jj]  for jj in range(0,mx+1)], start=vol.Volume(0,0) )


def volume_metapaths_at_t(G, s, cur_best, mx):
    sigma = dict()
    sink = G.sinks()
    G_rev = G.reverse()
    for e in sink:
        vol_rec_con(s, e, G_rev, sigma, cur_best, mx)
    return sigma

def first_edge_rec(e, edge, f_edge, G, cur_best):
    if e in f_edge:
        return
    f_edge[e] = edge, cur_best[e[0]][e[1]][1]
    l = list(G.successors(e))
    for ee in l:
        first_edge_rec(ee, edge, f_edge, G, cur_best)

def dictionary_first_edge(G, cur_best):
    f_edge = dict()
    source = G.sources()
    for sou in source:
        f_edge[sou] = sou[1],0
        for e in list(G.successors(sou)):
            first_edge_rec(e, sou[1], f_edge, G, cur_best)
    return f_edge

def optimal_with_resting_con(s, node, f_edge, events, G, sigma, cur_best, unt):
    sigma_r = dict()
    for k in s.nodes:
        pred = -1
        for t in events:
            if k == node:
                sigma_r[(k,t)] = vol.Volume(1,0)
            else:
                if pred == -1:
                    if (k,t) in G.nodes():
                        sigma_r[(k,t)] = sigma[(k,t)][-1]
                        pred = t
                        edge = f_edge[(k,t)]
                    else:
                        sigma_r[(k,t)] = vol.Volume(0,0)
                else:
                    if (k,t) in G.nodes():
                        edge2 = f_edge[(k,t)]
                        if edge == edge2 and unt[k][pred] >= t:
                            sigma_r[(k,t)] = sigma_r[(k,pred)] + sigma[(k,t)][-1]
                            pred = t
                        elif edge == edge2 and not(unt[k][pred] >= t):
                            sigma_r[(k,t)] = sigma[(k,t)][-1]
                            pred = t
                        else:
                            sigma_r[(k,t)] = sigma[(k,t)][-1]
                            pred = t
                            edge = f_edge[(k,t)]
                    else:
                        sigma_r[(k,t)] = sigma_r[(k,pred)]
    return sigma_r

def volume_instantenuous(s, G, events, events_rev, edge):
    before = {v:{t: False for t in events} for v in s.nodes}
    after = {v:{t: False for t in events} for v in s.nodes}
    volume_metapaths_instanteneous(G, events, events_rev, before, after, edge)
    return before, after

def vol_inst_bef(s, e, G, events, events_rev, before, after, time, t1, t2):
    l = list(G.successors(e))
    for (w,tp) in l:
        # print(e[0],w,time, t1,t2)
        t1p,t2p = G.edge_weight(e, (w,tp), "interval")
        # print("t1p,t2p",t1p,t2p)
        if t1 == -1:
            t1 = t1p
            t2 = t2p
        if tp == time and t1 == t1p and t2 == t2p and t1 != t2:
            before[w][tp] = True
            if events_rev[tp] > 0:
                after[w][events[events_rev[tp] -1]] = True
            vol_inst_bef(e, (w,tp), G, events, events_rev, before, after, time, t1, t2)

def vol_inst_after(s, e, G, events, events_rev, before, after, time, edge, t1_after, t2_after):
    l = list(G.successors(e))
    for (w,tp) in l:
        # print(e[0],w,time, t1_after, t2_after)
        edge_after1, edge_after2 = -1,-1
        if events_rev[tp] < len(events)-1 and (events[events_rev[tp] +1]) in edge[e[0]][w]:
            edge_after1, edge_after2 = edge[e[0]][w][events[events_rev[tp] +1]]
            if t1_after == -1:
                t1_after, t2_after = edge_after1, edge_after2 
            # print("edge after",edge_after1, edge_after2)
        if t1_after == -1 and edge_after1 != edge_after2:
            t1_after, t2_after = edge_after1, edge_after2
        if t1_after == -1:
            return
        if tp == time  and  edge_after1 == t1_after and edge_after2 == t2_after:
                after[w][tp] = True
                if events_rev[tp] < len(events):
                    before[w][events[events_rev[tp] +1]] = True
                vol_inst_after(e, (w,tp), G, events, events_rev, before, after, time, edge, t1_after, t2_after)


def volume_metapaths_instanteneous(G, events, events_rev, before, after, edge):
    sigma = dict()
    sou = G.sources()
    for s in sou:
        vol_inst_bef(-1, s, G, events, events_rev, before, after, s[1], -1, -1)
        vol_inst_after(-1, s, G, events, events_rev, before, after, s[1], edge, -1, -1)

def edges(s):
    res ={ i:dict() for i in s.nodes}
    for i in range(len(s.links)):
        x,y = s.links[i]
        if y not in res[x]:
            res[x][y] = dict()
        #print(s.link_presence[i])
        for j in range(0,len(s.link_presence[i]),2):
            t1,t2 = s.link_presence[i][j:j+2]
            if t1 != t2:
                if (j > 0 and t1 != s.link_presence[i][j-1]) or (j==0):
                    res[x][y][t1] = (t1,t1)
                res[x][y][t2] = (t1,t2)
            else:
                if (j > 0 and t1 != s.link_presence[i][j-1]) or (j==0):
                    res[x][y][t1] = (t1,t1)
    return res

####################################  number of paths generic discrete ####################################

def vol_rec_dis_gen(s, e, G_rev, sigma):
    if e in sigma:
        return
    if e[0] == s:
        sigma[e] = 1
        return
    l = list(G_rev.successors(e))
    res = 0
    for (w,tp) in l:
        vol_rec_dis_gen(s, (w,tp), G_rev, sigma)
        if w == s:
            res += 1
        else:
            res += sigma[(w,tp)]
    sigma[e] = res



def volume_metapaths_at_dis_gen(G, s):
    sigma = dict()
    sink = G.sinks()
    G_rev = G.reverse()
    for e in sink:
        vol_rec_dis_gen(s, e, G_rev, sigma)
    return sigma

def optimal_with_resting_dis_gen(s, node, events, G, sigma, cur_best, node_inf, opt_walk, cost, n):
    sigma_r = dict()
    #assuming -1 is an unexisting time
    for k in s.nodes:
        pred = -1
        for t in events:
            if k == node:
                if (k,t) in sigma:
                    sigma_r[(k,t)] = sigma[(k,t)]
                else:
                    sigma_r[(k,t)] = 0

                pred = t
            else:
                if pred == -1:
                    if (k,t) in G.nodes():
                        sigma_r[(k,t)] = sigma[(k,t)]
                        pred = t
                    else:
                        sigma_r[(k,t)] = 0.0
                else:
                    if (k,t) in G.nodes():
                        if cur_best[k][t] == cost(opt_walk[k][pred], t, n):
                            sigma_r[(k,t)] = sigma_r[(k,pred)] + sigma[(k,t)]
                            pred = t
                        else:
                            sigma_r[(k,t)] = sigma[(k,t)]
                            pred = t
                    else:
                        # dans ce cas il y a des chemin a pred, leur extension est necessairement optimale car il n'y en a pas d'autres
                        sigma_r[(k,t)] = sigma_r[(k,pred)]
            if (k,t) in node_inf:
                sigma_r[(k,t)] = numpy.Infinity
    return sigma_r

def infinite_closure(G, events, events_rev, node_inf, opt_walk, cur_best, cost, n, cmp):
    res = set()
    for (v,t) in node_inf:
        i = events_rev[t]+1
        while(i < len(events) and  (v,events[i]) not in G.nodes()):
            # for infinite cur_best we put <=
            if cmp(cost(opt_walk[v][t],events[i],n), cur_best[v][events[i]]):
                res.add((v,events[i]))
            i += 1
    return res

def sigma_total_dis_gen(sigma, s, cur_best, node, events):
    sigma_tot, min_values, sigma_tot_t = sigma_total_passive_dis_gen(sigma, s, cur_best, node, events)
    return sigma_tot, min_values, sigma_tot_t


def sigma_total_passive_dis_gen(sigma, s, cur_best, node, events):
    min_values = { i:min(cur_best[i].values())   for i in s.nodes}
    sigma_dic = dict()
    for (v,t) in sigma:
        if v not in sigma_dic:
            sigma_dic[v] = dict()
        sigma_dic[v][t] = sigma[(v,t)]
    sigma_tot = dict()
    sigma_tot_t = dict()
    for i in s.nodes:
        sigma_tot_t[i] = dict()
        if  i in sigma_dic:
            for t  in events:
                if t in sigma_dic[i]:
                    #print(i,t)
                    if i in min_values and cur_best[i][t] == min_values[i]:
                        sigma_tot_t[i][t] = sigma_dic[i][t]
                    else:
                        sigma_tot_t[i][t] = 0
            sigma_tot[i] = sum(sigma_tot_t[i][t] for t in sigma_tot_t[i])
    return sigma_tot, min_values, sigma_tot_t


# def sigma_total_active_dis_gen(sigma, s, cur_best, node, events):
#     min_values = { i:min(cur_best[i].values())   for i in s.nodes}
#     sigma_dic = dict()
#     for (v,t) in sigma:
#         if v not in sigma_dic:
#             sigma_dic[v] = dict()
#         sigma_dic[v][t] = sigma[(v,t)]
#     sigma_tot = dict()
#     sigma_tot_t = dict()
#     for i in s.nodes:
#         if  i in sigma_dic:
#             for t  in events:
#                 if t in sigma_dic[i]:
#                     if i not in sigma_tot_t:
#                         sigma_tot_t[i] = dict()
#                         pred = t
#                         if i in min_values and cur_best[i][t] == min_values[i]:
#                             sigma_tot_t[i][t] = sigma_dic[i][t]
#                         else:
#                             sigma_tot_t[i][t] = 0
#                     else:
#                         if i in min_values and cur_best[i][t] == min_values[i]:
#                             sigma_tot_t[i][t] = sigma_tot_t[i][pred] + sigma_dic[i][t]
#                             pred = t
#                         else:
#                             sigma_tot_t[i][t] = sigma_tot_t[i][pred]
#                             pred = t
#             sigma_tot[i] = sigma_tot_t[i][pred]
#     return sigma_tot, min_values, sigma_tot_t

def complete_sigma_tot_t(s, sigma_tot_t, node_inf, events, node, walk_type):
    if False:
        sigma_tot_r = complete_sigma_tot_active(s, sigma_tot_t, node_inf, events, node)
    else:
        sigma_tot_r = complete_sigma_tot_passive(s, sigma_tot_t, node_inf, events, node)
    return sigma_tot_r

def complete_sigma_tot_passive(s, sigma_tot_t, node_inf, events, node):
    sigma_tot_r = dict()
    #assuming -1 is an unexisting time
    for k in s.nodes:
        pred = -1
        for t in events:
            if k in sigma_tot_t and t in sigma_tot_t[k]:
                sigma_tot_r[(k,t)] =  sigma_tot_t[k][t]
            else:
                if (k,t) in node_inf:
                    sigma_tot_r[(k,t)] =  numpy.Infinity
                else:
                    sigma_tot_r[(k,t)] =  0
    return sigma_tot_r

# def complete_sigma_tot_active(s, sigma_tot_t, node_inf, events, node):
#     sigma_tot_r = dict()
#     #assuming -1 is an unexisting time
#     for k in s.nodes:
#         pred = -1
#         for t in events:
#             if (k,t) in node_inf:
#                 continue
#             if False:
#                 sigma_tot_r[(k,t)] = sigma_tot_t[k][t]
#                 pred = t
#             else:
#                 if pred == -1:
#                     if k in sigma_tot_t and t in sigma_tot_t[k]:
#                         sigma_tot_r[(k,t)] = sigma_tot_t[k][t]
#                         pred = t
#                     else:
#                         sigma_tot_r[(k,t)] = 0.0
#                 else:
#                     if k in sigma_tot_t and t in sigma_tot_t[k]:
#                         sigma_tot_r[(k,t)] =  sigma_tot_t[k][t]
#                         pred = t
#                     else:
#                         sigma_tot_r[(k,t)] = sigma_tot_r[(k,pred)]
#     return sigma_tot_r

def sigma_infinite(sigma, node_inf):
    for e in node_inf:
        sigma[e] = numpy.Infinity
