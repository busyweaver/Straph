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


def general_contribution_from_node(s, G, node, GG, sigma_r, deltasvvt, events, events_reverse, pre, GT, unt):
    contribution = dict()
    l = G.sources()
    l.sort(reverse = True)
    for star_node in l:
        contribution = contri_delta_svt(node, star_node[0], star_node[1], GG.l_nei, sigma_r, contribution, deltasvvt, events, events_reverse, pre, GT, unt)
    for v in s.nodes:
        for t in events:
            if v not in contribution:
                contribution[v] = dict()
            if t not in contribution[v]:
                contribution[v][t] = vol.Volume(0,0)
    return contribution


def contri_intermeidary_vertices(v, t, w, t_p, l_nei, partial_sum, contrib_local, ii, jj, sigma_r, event, event_reverse, contribution):
    for jjj in range(jj+1,event_reverse[l_nei[v,t][ii][0]]+1):
        if (v,event[jjj]) in l_nei:
            return
        if v not in contrib_local:
            contrib_local[v] = dict()
        if not (v in contribution and event[jjj] in contribution[v]):
            if event[jjj] not in contrib_local[v]:
                contrib_local[v][event[jjj]] = vol.Volume(0,0)
            if (v,event[jjj]) == (2, 80.41206683462686):
                print("v,t",v,t, "w_tp",w,t_p, "ii", ii,"partial_sum",partial_sum)
            if event[jjj] != t_p:
                contrib_local[v][event[jjj]] = partial_sum[l_nei[v,t][ii][0]]
                if (v,event[jjj]) == (2, 80.41206683462686):
                    print("v,t",v,t, "w_tp",w,t_p,"partial_sum[l_nei[v,t][ii][0]]", partial_sum[l_nei[v,t][ii][0]],"contrib_local[v][event[jjj]]",contrib_local[v][event[jjj]])
            else:
                if ii == len(l_nei[v,t])-1:
                    contrib_local[v][event[jjj]] += (sigma_r[(v,event[jjj])]/sigma_r[(w,t_p)] ) *contribution[w][t_p]
                    if (v,event[jjj]) == (2, 80.41206683462686):
                        print("v,t",v,t, "w_tp",w,t_p,"(sigma_r[(v,event[jjj])]/sigma_r[(w,t_p)] )",(sigma_r[(v,event[jjj])]/sigma_r[(w,t_p)] ),"contribution[w][t_p]",contribution[w][t_p],"contrib_local[v][event[jjj]]",contrib_local[v][event[jjj]])
                else:
                    if l_nei[v,t][ii][1][-1] == w:
                        contrib_local[v][event[jjj]] += partial_sum[l_nei[v,t][ii+1][0]]  + (sigma_r[(v,event[jjj])]/sigma_r[(w,t_p)] )*contribution[w][t_p]
                    else:
                        contrib_local[v][event[jjj]] += (sigma_r[(v,event[jjj])]/sigma_r[(w,t_p)] )*contribution[w][t_p]
                    if (v,event[jjj]) == (2, 80.41206683462686):
                        print("v,t",v,t, "w_tp",w,t_p,"l_nei[v,t][ii+1][0]",l_nei[v,t][ii+1][0],"partial_sum[l_nei[v,t][ii+1][0]]",partial_sum[l_nei[v,t][ii+1][0]],"(sigma_r[(v,event[jjj])]/sigma_r[(w,t_p)] )",(sigma_r[(v,event[jjj])]/sigma_r[(w,t_p)] ),"contribution[w][t_p]",contribution[w][t_p],"contrib_local[v][event[jjj]]",contrib_local[v][event[jjj]])


def contri_delta_svt(node, v, t, l_nei, sigma_r, contribution, deltasvvt, event, event_reverse, pre, GT, unt):
    print("v,t",v,t,"l_nei[(v,t)]",l_nei[(v,t)])
    if (v,t) == (2, 80.41206683462686):
        print("bah si")
    if (v not in contribution) or ((v in contribution) and (t not in contribution[v])):
        partial_sum = dict()
        s = vol.Volume(0,0)
        contrib_local = dict()
        for ii in range(len(l_nei[(v,t)])-1,-1,-1):
            #normally it should be sorted
            for u in l_nei[v,t][ii][1]:
                w,t_p = (u,l_nei[v,t][ii][0])
                contri_delta_svt(node, w, t_p, l_nei, sigma_r, contribution, deltasvvt, event, event_reverse, pre, GT, unt)
                (t1,t2) = pre[w][t_p][v,t]
                if t1 != t2 and t_p > t and unt[v][t] >=t_p:
                    l = [(w, t_p)] + list(GT[t1,t2].successors((w,t_p)))
                    for yp,tpp in l:
                        if (v,t) == (2, 80.41206683462686):
                            print("cas cont w_tp",w,t_p,"yptpp",yp,tpp)
                        contri_delta_svt(node, yp, tpp, l_nei, sigma_r, contribution, deltasvvt, event, event_reverse, pre, GT, unt)
                        ev_prev = prev_event(tpp,event,event_reverse)
                        r = GT[t1,t2].edge_weight((v,t),(yp,tpp),"weight")
                        if ((kappa(r,tpp,ev_prev)*sigma_r[(v,t)]/sigma_r[(yp,tpp)] ) *contribution[yp][tpp]).dim > 0:
                            print("ici",kappa(r,tpp,ev_prev),"*",sigma_r[(v,t)],"/",sigma_r[(yp,tpp)],  "*",contribution[yp][tpp])
                        s += (kappa(r,tpp,ev_prev)*sigma_r[(v,t)]/sigma_r[(yp,tpp)] ) *contribution[yp][tpp]
                        if (v,t) == (2, 80.41206683462686):
                            print("s",s,"sigma_r[(v,t)]",sigma_r[(v,t)],"sigma_r[(yp,tpp)]",sigma_r[(yp,tpp)],"contribution[yp][tpp]",contribution[yp][tpp],"kappa(r,tpp,ev_prev)",kappa(r,tpp,ev_prev))
                        #print("kappa(r,tpp,ev_prev)",kappa(r,tpp,ev_prev),"sigma_r[(v,t)]",sigma_r[(v,t)], "sigma_r[(yp,tpp)]",sigma_r[(yp,tpp)],"contribution[yp][tpp]",contribution[yp][tpp],"s",s)

                if ((t == t_p) or (t_p > t and t1 == t2)) and unt[v][t] >=t_p:
                    if (v,t) == (2, 80.41206683462686):
                            print("cas discret w_tp",w,t_p)
                    if ((sigma_r[(v,t)]/sigma_r[(w,t_p)] ) *contribution[w][t_p]).dim > 0:
                        print("la",sigma_r[(v,t)],"/",sigma_r[(w,t_p)], "*",contribution[w][t_p], "t", t, "tp", t_p, "v", v, "w", w)
                    s += (sigma_r[(v,t)]/sigma_r[(w,t_p)] ) *contribution[w][t_p]
                    if (v,t) == (2, 80.41206683462686):
                            print("s",s, "sigma_r[(v,t)]",sigma_r[(v,t)], "sigma_r[(w,t_p)]", sigma_r[(w,t_p)], "contribution[w][t_p]", contribution[w][t_p])
                    #print("sigma_r[(v,t)]",sigma_r[(v,t)],"sigma_r[(w,t_p)]",sigma_r[(w,t_p)],"contribution[w][t_p]",contribution[w][t_p],"s",s)

                if l_nei[v,t][ii][0] not in partial_sum:
                    partial_sum[l_nei[v,t][ii][0]] = s.copy()
                else:
                    partial_sum[l_nei[v,t][ii][0]] = s.copy()
                if (v,t) == (2, 80.41206683462686):
                    print("partial_sum", partial_sum,"w_tp",w,t_p,)


                if ii != 0:
                    jj = event_reverse[l_nei[v,t][ii-1][0]]
                else:
                    jj = event_reverse[t]
                contri_intermeidary_vertices(v, t, w, t_p, l_nei, partial_sum, contrib_local, ii, jj, sigma_r, event, event_reverse, contribution)

        if v not in contribution:
            contribution[v] = dict()
        for vv in contrib_local:
            for ss in contrib_local[vv]:
                contribution[vv][ss] = contrib_local[vv][ss]
        contribution[v][t] = s + deltasvvt[(v,t)]

    return contribution

