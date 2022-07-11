from straph.betweenness import volumes as vol

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

def first_edge_rec(e, edge, f_edge, G):
    if e in f_edge:
        return
    f_edge[e] = edge
    l = list(G.successors(e))
    for ee in l:
        first_edge_rec(ee, edge, f_edge, G)

def dictionary_first_edge(G):
    f_edge = dict()
    source = G.sources()
    for sou in source:
        f_edge[sou] = sou[1]
        for e in list(G.successors(sou)):
            first_edge_rec(e, sou[1], f_edge, G)
    return f_edge

def optimal_with_resting_con(s, node, f_edge, events, G, sigma, cur_best, unt):
    sigma_r = dict()
    for k in s.nodes:
        pred = -1
        for t in events:
            if k == node:
                sigma_r[(k,t)] = vol.Volume(0,0)
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

def volume_instantenuous(s, G, GI, events, events_rev):
    before = {v:{t: False for t in events} for v in s.nodes}
    after = {v:{t: False for t in events} for v in s.nodes}
    l = []
    for e in G.sources():
        for (v,t) in G.successors(e):
            t1,t2 = G.edge_weight(e, (v,t), "interval")
            if t1 != t2:
                before[v][t2] = True
                after[v][t1] = True
                l.append([v,t1,t2])
    for v,t1,t2 in l:
        if (t1,t2) in GI and (v,t2) in GI[(t1,t2)].nodes():
            print(t1,t2)
            for (w,tp) in GI[(t1,t2)].successors((v,t2)):
                if tp == t2:
                    before[w][t2] = True
                    after[w][t1] = True

    # for e in GI:
    #     source = GI[e].sources()
    #     #if before[source[0]][source[1]] == True:
    #     for (v,t) in GI[e].successors(source[0]):
    #         if source[1] == e[1]:
    #             print("v",v,"t",t,"e",e,"source",source)
    #             before[v][e[1]] = True
    #             after[v][e[0]] = True
    return before, after
