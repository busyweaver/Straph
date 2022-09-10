from straph.betweenness import volumes as vol
import math

def dictionary_svvt(G, node, latence_arrival, contri, prev_next, sigma_r,  latence_depar):
    deltasvvt = dict()
    for (x,y) in G.nodes():
        deltasvvt[(x,y)] = contri_delta_svvt(node, x, y, latence_arrival, contri, prev_next, sigma_r,  latence_depar)
    return deltasvvt

def contri_delta_svvt(s, v, t, lat, contri, prev_next, sigma_r, lat_rev):
    if s == v or t not in lat[v]:
        return vol.Volume(0,0)
    #voir papier matthieu clemence pour l'algo
    prev = []
    next = []
    if t in prev_next[v]:
        prev = [lat[v][e][0] for e in prev_next[v][t] if e < t]
        next = [e for e in prev_next[v][t] if e > t]
    prev =  prev + [contri[v][t][0]]
    next = next + [contri[v][t][1]]
    left = vol.Volume(0,0)
    right = vol.Volume(0,0)
    contrib = vol.Volume(0,0)
    s_prime = vol.Volume(lat[v][t][0], 0)
    vol_tv = sigma_r[(v,t)]
    for s_left in prev:
        a_prime = vol.Volume(t,0)
        right = vol.Volume(0,0)
        for a_right in next:
            enum = (s_prime - vol.Volume(s_left,0)) * (vol.Volume(a_right,0) - a_prime) * vol_tv
            denum = left + vol_tv + right
            if denum !=vol.Volume(0,0):
                res = enum / denum
            else:
                res = vol.Volume(0,0)
            contrib += res
            if a_right in lat[v]:
                right += sigma_r[(v,a_right)]
            a_prime = vol.Volume(a_right, 0)

        if (s_left in lat_rev[v]) and (lat_rev[v][s_left][0] in lat[v]):

            left += sigma_r[(v,lat_rev[v][s_left][0])]
        s_prime = vol.Volume(s_left, 0)
    return contrib


def kappa(r,tp,tp_prev):
    return vol.Volume(math.pow((tp-tp_prev),(r+1))/math.factorial(r+1) , r+1)

def prev_event(tp,event,event_rev):
    i = event_rev[tp]
    return event[i-1]

def preced_node(s, G,events,events_rev):
    res = dict()
    d = dict()
    for (v,t) in G.nodes():
        if v in d:
            d[v].append(t)
        else:
            d[v] = [t]
    for v in d.keys():
        d[v].sort()
        res[v] = dict()
        for e in d[v]:
            res[v][e] = e
        for i in range(0,len(d[v])-1):
            for j in range(events_rev[d[v][i]]+1,events_rev[d[v][i+1]]):
                res[v][events[j]] = res[v][d[v][i]]
            for j in range(events_rev[d[v][-1]]+1, len(events)):
                res[v][events[j]] = res[v][d[v][-1]]
    return res
    




def general_contribution_from_node(s, G, node, GG, sigma_r, deltasvvt, events, events_reverse, pre, GT, unt, preced, edge = False):
    contribution = dict()
    edge_contribution = dict()
    l = G.sources()
    l.sort(reverse = True)
    for star_node in l:
        if edge == False:
            contribution = contri_delta_svt(node, star_node[0], star_node[1], GG.l_nei, sigma_r, contribution, deltasvvt, events, events_reverse, pre, GT, unt, preced)
        else:
            contribution, edge_contribution = contri_delta_edge(node, star_node[0], star_node[1], GG.l_nei, sigma_r, contribution, deltasvvt, events, events_reverse, pre, GT, unt, preced, edge_contribution)
    for v in s.nodes:
        for t in events:
            if v not in contribution:
                contribution[v] = dict()
            if t not in contribution[v]:
                contribution[v][t] = vol.Volume(0,0)
    return contribution, edge_contribution


def contri_intermeidary_vertices(v, t, w, t_p, l_nei, partial_sum, contrib_local, ii, jj, sigma_r, event, event_reverse, contribution, preced):
    if v not in contribution:
        contribution[v] = dict()
    for jjj in range(jj+1,event_reverse[l_nei[v,t][ii][0]]+1):
        if (v,event[jjj]) in l_nei:
            continue
        if v not in contrib_local:
            contrib_local[v] = dict()
        if not (event[jjj] in contribution[v]) and (event[jjj] in preced[v] and t == preced[v][event[jjj]]):
            if event[jjj] not in contrib_local[v]:
                contrib_local[v][event[jjj]] = vol.Volume(0,0)
            if event[jjj] != t_p:
                contrib_local[v][event[jjj]] = partial_sum[l_nei[v,t][ii][0]]
            else:
                if ii == len(l_nei[v,t])-1:
                    contrib_local[v][event[jjj]] += (sigma_r[(v,event[jjj])]/sigma_r[(w,t_p)] ) *contribution[w][t_p]
                else:
                    if l_nei[v,t][ii][1][-1] == w:
                        contrib_local[v][event[jjj]] += partial_sum[l_nei[v,t][ii+1][0]]  + (sigma_r[(v,event[jjj])]/sigma_r[(w,t_p)] )*contribution[w][t_p]
                    else:
                        contrib_local[v][event[jjj]] += (sigma_r[(v,event[jjj])]/sigma_r[(w,t_p)] )*contribution[w][t_p]

def contri_delta_svt(node, v, t, l_nei, sigma_r, contribution, deltasvvt, event, event_reverse, pre, GT, unt, preced):
    if (v,t) == (1, 70.1131204334166):
        print("v,t",v,t,"l_nei[(v,t)]",l_nei[(v,t)])
    if (v not in contribution) or ((v in contribution) and (t not in contribution[v])):
        partial_sum = dict()
        s = vol.Volume(0,0)
        contrib_local = dict()
        for ii in range(len(l_nei[(v,t)])-1,-1,-1):
            #normally it should be sorted
            for u in l_nei[v,t][ii][1]:
                w,t_p = (u,l_nei[v,t][ii][0])
                if (v,t) == (1, 70.1131204334166):
                    print("w,t_p",w,t_p)
                contri_delta_svt(node, w, t_p, l_nei, sigma_r, contribution, deltasvvt, event, event_reverse, pre, GT, unt, preced)
                (t1,t2) = pre[w][t_p][v,t]
                if t1 != t2 and t_p > t and unt[v][t] >=t_p:
                    if (v,t) == (1, 70.1131204334166):
                        print("case cont")
                    l = [(w, t_p)] + list(GT[t1,t2].successors((w,t_p)))
                    for yp,tpp in l:
                        if (v,t) == (1, 70.1131204334166):
                            print("yp,tpp",yp,tpp)
                        contri_delta_svt(node, yp, tpp, l_nei, sigma_r, contribution, deltasvvt, event, event_reverse, pre, GT, unt, preced)
                        ev_prev = prev_event(tpp,event,event_reverse)
                        r = GT[t1,t2].edge_weight((v,t),(yp,tpp),"weight")
                        if (w,t_p) == (yp, tpp):
                            mul = vol.Volume(1,0)
                        else:
                            mul = GT[t1,t2].edge_weight((w,t_p),(yp,tpp),"nb_paths")
                            mul = vol.Volume(mul,0)
                        if ((kappa(r,tpp,ev_prev)*sigma_r[(v,t)]/sigma_r[(yp,tpp)] ) *contribution[yp][tpp]).dim > 0:
                            print("ici",kappa(r,tpp,ev_prev),"*",sigma_r[(v,t)],"/",sigma_r[(yp,tpp)],  "*",contribution[yp][tpp])
                        s += mul * (kappa(r,tpp,ev_prev)*sigma_r[(v,t)]/sigma_r[(yp,tpp)] ) *contribution[yp][tpp]
                        if (v,t) == (1, 70.1131204334166):
                            print("s",s,"contribution[yp][tpp]", contribution[yp][tpp], "(kappa(r,tpp,ev_prev)*sigma_r[(v,t)]/sigma_r[(yp,tpp)] )",(kappa(r,tpp,ev_prev)*sigma_r[(v,t)]/sigma_r[(yp,tpp)] ),"r",r,"mul",mul, "coef", (kappa(r,tpp,ev_prev)*sigma_r[(v,t)]/sigma_r[(yp,tpp)] ) *contribution[yp][tpp])
                        #print("kappa(r,tpp,ev_prev)",kappa(r,tpp,ev_prev),"sigma_r[(v,t)]",sigma_r[(v,t)], "sigma_r[(yp,tpp)]",sigma_r[(yp,tpp)],"contribution[yp][tpp]",contribution[yp][tpp],"s",s)

                if ((t == t_p) or (t_p > t and t1 == t2)) and unt[v][t] >=t_p:
                    if (v,t) == (1, 70.1131204334166):
                            print("case discret")
                    if ((sigma_r[(v,t)]/sigma_r[(w,t_p)] ) *contribution[w][t_p]).dim > 0:
                        print("la",sigma_r[(v,t)],"/",sigma_r[(w,t_p)], "*",contribution[w][t_p], "t", t, "tp", t_p, "v", v, "w", w)
                    s += (sigma_r[(v,t)]/sigma_r[(w,t_p)] ) *contribution[w][t_p]
                    if (v,t) == (1, 70.1131204334166):
                            print("s",s, "(sigma_r[(v,t)]/sigma_r[(w,t_p)] )", (sigma_r[(v,t)]/sigma_r[(w,t_p)] ), "(sigma_r[(v,t)]/sigma_r[(w,t_p)] )", (sigma_r[(v,t)]/sigma_r[(w,t_p)] ), "coef", (sigma_r[(v,t)]/sigma_r[(w,t_p)] ) *contribution[w][t_p])
                    #print("sigma_r[(v,t)]",sigma_r[(v,t)],"sigma_r[(w,t_p)]",sigma_r[(w,t_p)],"contribution[w][t_p]",contribution[w][t_p],"s",s)

                if l_nei[v,t][ii][0] not in partial_sum:
                    partial_sum[l_nei[v,t][ii][0]] = s.copy()
                else:
                    partial_sum[l_nei[v,t][ii][0]] = s.copy()

                if ii != 0:
                    jj = event_reverse[l_nei[v,t][ii-1][0]]
                else:
                    jj = event_reverse[t]
                contri_intermeidary_vertices(v, t, w, t_p, l_nei, partial_sum, contrib_local, ii, jj, sigma_r, event, event_reverse, contribution, preced)

        if v not in contribution:
            contribution[v] = dict()
        for vv in contrib_local:
            for ss in contrib_local[vv]:
                contribution[vv][ss] = contrib_local[vv][ss]
        contribution[v][t] = s + deltasvvt[(v,t)]

    return contribution

def contri_delta_edge(node, v, t, l_nei, sigma_r, contribution, deltasvvt, event, event_reverse, pre, GT, unt, preced, edge_contribution):
    if (v,t) == (1, 70.1131204334166):
        print("v,t",v,t,"l_nei[(v,t)]",l_nei[(v,t)])
    if (v not in contribution) or ((v in contribution) and (t not in contribution[v])):
        s = vol.Volume(0,0)
        for ii in range(len(l_nei[(v,t)])-1,-1,-1):
            #normally it should be sorted
            for u in l_nei[v,t][ii][1]:
                edge_vol = vol.Volume(0,0)
                w,t_p = (u,l_nei[v,t][ii][0])
                if (v,t) == (1, 70.1131204334166):
                    print("w,t_p",w,t_p)
                contri_delta_edge(node, w, t_p, l_nei, sigma_r, contribution, deltasvvt, event, event_reverse, pre, GT, unt, preced, edge_contribution)
                (t1,t2) = pre[w][t_p][v,t]
                if t1 != t2 and t_p > t and unt[v][t] >=t_p:
                    if (v,t) == (1, 70.1131204334166):
                        print("case cont")
                    l = [(w, t_p)] + list(GT[t1,t2].successors((w,t_p)))
                    for yp,tpp in l:
                        if (v,t) == (1, 70.1131204334166):
                            print("yp,tpp",yp,tpp)
                        contri_delta_edge(node, yp, tpp, l_nei, sigma_r, contribution, deltasvvt, event, event_reverse, pre, GT, unt, preced, edge_contribution)
                        ev_prev = prev_event(tpp,event,event_reverse)
                        r = GT[t1,t2].edge_weight((v,t),(yp,tpp),"weight")
                        if (w,t_p) == (yp, tpp):
                            mul = vol.Volume(1,0)
                        else:
                            mul = GT[t1,t2].edge_weight((w,t_p),(yp,tpp),"nb_paths")
                            mul = vol.Volume(mul,0)
                        if ((kappa(r,tpp,ev_prev)*sigma_r[(v,t)]/sigma_r[(yp,tpp)] ) *contribution[yp][tpp]).dim > 0:
                            print("ici",kappa(r,tpp,ev_prev),"*",sigma_r[(v,t)],"/",sigma_r[(yp,tpp)],  "*",contribution[yp][tpp])
                        s += mul * (kappa(r,tpp,ev_prev)*sigma_r[(v,t)]/sigma_r[(yp,tpp)] ) *contribution[yp][tpp]
                        edge_vol += mul * (kappa(r,tpp,ev_prev)*sigma_r[(v,t)]/sigma_r[(yp,tpp)] ) *contribution[yp][tpp]
                        if (v,t) == (1, 70.1131204334166):
                            print("s",s,"contribution[yp][tpp]", contribution[yp][tpp], "(kappa(r,tpp,ev_prev)*sigma_r[(v,t)]/sigma_r[(yp,tpp)] )",(kappa(r,tpp,ev_prev)*sigma_r[(v,t)]/sigma_r[(yp,tpp)] ),"r",r,"mul",mul, "coef", (kappa(r,tpp,ev_prev)*sigma_r[(v,t)]/sigma_r[(yp,tpp)] ) *contribution[yp][tpp])
                        #print("kappa(r,tpp,ev_prev)",kappa(r,tpp,ev_prev),"sigma_r[(v,t)]",sigma_r[(v,t)], "sigma_r[(yp,tpp)]",sigma_r[(yp,tpp)],"contribution[yp][tpp]",contribution[yp][tpp],"s",s)

                if ((t == t_p) or (t_p > t and t1 == t2)) and unt[v][t] >=t_p:
                    if (v,t) == (1, 70.1131204334166):
                            print("case discret")
                    if ((sigma_r[(v,t)]/sigma_r[(w,t_p)] ) *contribution[w][t_p]).dim > 0:
                        print("la",sigma_r[(v,t)],"/",sigma_r[(w,t_p)], "*",contribution[w][t_p], "t", t, "tp", t_p, "v", v, "w", w)
                    s += (sigma_r[(v,t)]/sigma_r[(w,t_p)] ) *contribution[w][t_p]
                    edge_vol += (sigma_r[(v,t)]/sigma_r[(w,t_p)] ) *contribution[w][t_p]
                    if (v,t) == (1, 70.1131204334166):
                            print("s",s, "(sigma_r[(v,t)]/sigma_r[(w,t_p)] )", (sigma_r[(v,t)]/sigma_r[(w,t_p)] ), "(sigma_r[(v,t)]/sigma_r[(w,t_p)] )", (sigma_r[(v,t)]/sigma_r[(w,t_p)] ), "coef", (sigma_r[(v,t)]/sigma_r[(w,t_p)] ) *contribution[w][t_p])
                    #print("sigma_r[(v,t)]",sigma_r[(v,t)],"sigma_r[(w,t_p)]",sigma_r[(w,t_p)],"contribution[w][t_p]",contribution[w][t_p],"s",s)
                #print(edge_contribution)
                if (v,w,t_p) in edge_contribution:
                    edge_contribution[(v,w,t_p)] += edge_vol
                else:
                    edge_contribution[(v,w,t_p)] = edge_vol

        if v not in contribution:
            contribution[v] = dict()
        contribution[v][t] = s + deltasvvt[(v,t)]

    return contribution, edge_contribution

####################################  number of paths generic discrete ####################################

def dictionary_svvt_dis_gen(G, node, sigma_r,min_values, cur_best, sigma_tot):
    deltasvvt = dict()
    for (x,y) in G.nodes():
        deltasvvt[(x,y)] = contri_delta_svvt_dis_gen(node, x, y, sigma_r, min_values, cur_best, sigma_tot)
    return deltasvvt

def contri_delta_svvt_dis_gen(s, v, t, sigma_r, min_values, cur_best, sigma_tot):
    if s == v:
        return 0.0
    if cur_best[v][t] == min_values[v]:
        return sigma_r[(v,t)]/sigma_tot[v]
    else:
        return 0.0

    return contrib


def general_contribution_from_node_dis_gen(s, G, node, GG, sigma_r, deltasvvt, events, events_reverse, pre, unt, preced):
    contribution = dict()
    l = G.sources()
    l.sort(reverse = True)
    for star_node in l:
        contribution = contri_delta_svt_dis_gen(node, star_node[0], star_node[1], GG.l_nei, sigma_r, contribution, deltasvvt, events, events_reverse, pre, unt, preced)
    for v in s.nodes:
        for t in events:
            if v not in contribution:
                contribution[v] = dict()
            if t not in contribution[v]:
                contribution[v][t] = 0.0
    return contribution


def contri_intermeidary_vertices_dis_gen(v, t, w, t_p, l_nei, partial_sum, contrib_local, ii, jj, sigma_r, event, event_reverse, contribution, preced):
    if v not in contribution:
        contribution[v] = dict()
    for jjj in range(jj+1,event_reverse[l_nei[v,t][ii][0]]+1):
        if (v,event[jjj]) in l_nei:
            continue
        if v not in contrib_local:
            contrib_local[v] = dict()
        if not (event[jjj] in contribution[v]) and (event[jjj] in preced[v] and t == preced[v][event[jjj]]):
            if event[jjj] not in contrib_local[v]:
                contrib_local[v][event[jjj]] = 0.0
            if event[jjj] != t_p:
                contrib_local[v][event[jjj]] = partial_sum[l_nei[v,t][ii][0]]
            else:
                if ii == len(l_nei[v,t])-1:
                    contrib_local[v][event[jjj]] += (sigma_r[(v,event[jjj])]/sigma_r[(w,t_p)] ) *contribution[w][t_p]
                else:
                    if l_nei[v,t][ii][1][-1] == w:
                        contrib_local[v][event[jjj]] += partial_sum[l_nei[v,t][ii+1][0]]  + (sigma_r[(v,event[jjj])]/sigma_r[(w,t_p)] )*contribution[w][t_p]
                    else:
                        contrib_local[v][event[jjj]] += (sigma_r[(v,event[jjj])]/sigma_r[(w,t_p)] )*contribution[w][t_p]

def contri_delta_svt_dis_gen(node, v, t, l_nei, sigma_r, contribution, deltasvvt, event, event_reverse, pre, unt, preced):
    if (v,t) == (1, 70.1131204334166):
        print("v,t",v,t,"l_nei[(v,t)]",l_nei[(v,t)])
    if (v not in contribution) or ((v in contribution) and (t not in contribution[v])):
        partial_sum = dict()
        s = 0.0
        contrib_local = dict()
        for ii in range(len(l_nei[(v,t)])-1,-1,-1):
            #normally it should be sorted
            for u in l_nei[v,t][ii][1]:
                w,t_p = (u,l_nei[v,t][ii][0])
                contri_delta_svt_dis_gen(node, w, t_p, l_nei, sigma_r, contribution, deltasvvt, event, event_reverse, pre, unt, preced)
                s += (sigma_r[(v,t)]/sigma_r[(w,t_p)] ) *contribution[w][t_p]

                if l_nei[v,t][ii][0] not in partial_sum:
                    partial_sum[l_nei[v,t][ii][0]] = s
                else:
                    partial_sum[l_nei[v,t][ii][0]] = s

                if v != node:
                    if ii != 0:
                        jj = event_reverse[l_nei[v,t][ii-1][0]]
                    else:
                        jj = event_reverse[t]
                    contri_intermeidary_vertices(v, t, w, t_p, l_nei, partial_sum, contrib_local, ii, jj, sigma_r, event, event_reverse, contribution, preced)

        if v not in contribution:
            contribution[v] = dict()
        for vv in contrib_local:
            for ss in contrib_local[vv]:
                contribution[vv][ss] = contrib_local[vv][ss]
        contribution[v][t] = s + deltasvvt[(v,t)]

    return contribution
