from straph.betweenness import volumes as vol

def vol_rec_con_inst(s, e, G_rev, sigma):
    l = list(G_rev.successors(e))
    #print(e,l,sigma)
    w,tp = l[0]
    sigma[e] = dict()
    if w == s:
        t1,t2 = G_rev.edge_weight(e,(w,tp),"interval")
        if t1 == t2:
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
            #print(e,l,sigma)
            res = vol.Volume(0,0)
            if j == 0:
                for (w,tp) in l:
                    vol_rec_con(s, (w,tp), G_rev, sigma, cur_best, mx)
                    res += sigma[(w,tp)][-1]
                sigma[e][0] = res
            elif j == 1:
                for (w,tp) in l:
                    t1,t2 = G_rev.edge_weight(e,(w,tp),"interval")
                    if t1 != t2 and tp <= t1:
                        self.vol_rec_con(s, (w,tp), G_rev, sigma, cur_best, mx)
                        res += sigma[(w,tp)][-1] * vol.Volume((t2-t1,1))
                sigma[e][1] = res
            else:
                for (w,tp) in l:
                    t1,t2 = G_rev.edge_weight(e,(w,tp),"interval")
                    if t1 != t2 and tp == t2:
                        self.vol_rec_con(s, (w,tp), G_rev, sigma, cur_best, mx)
                        if (j-1) in sigma[(w,tp)]:
                            res += sigma[(w,tp)][j-1] * vol.Volume((t2-t1)/j,1)
                sigma[e][j] = res
        sigma[e][-1] = sum( sigma[e][jj]  for jj in range(0,mx+1))


def volume_metapaths_at_t(G, s, cur_best, mx):
    sigma = dict()
    sink = G.sinks()
    G_rev = G.reverse()
    for e in sink:
        vol_rec_con(s, e, G_rev, sigma, cur_best, mx)
    return sigma
