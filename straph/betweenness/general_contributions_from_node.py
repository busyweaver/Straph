from straph.betweenness import volumes as vol
import math
def contri_delta_svvt_con(s, v, t, lat, contri, prev_next, sigma_r, lat_rev):
    #if (v,t) in deltasvvt:
        #return deltasvvt[(v,t)]
    print("///////// call svvt, ","s",s,"v",v,"t",t)
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

            print("s_prime", s_prime, "s_left", s_left, "a_right", a_right, "a_prime", a_prime)
            enum = (s_prime - vol.Volume(s_left,0)) * (vol.Volume(a_right,0) - a_prime) * vol_tv

            print("left", left, "vol_tv", vol_tv, "right", right)
            denum = left + vol_tv + right
            print("enum", enum, "denum", denum)
            #print("enum-denum degree",enum_degree, denum_degree)
            if denum !=vol.Volume(0,0):
                res = enum / denum
            else:
                res = vol.Volume(0,0)
            #contrib += (enum/denum)
            contrib += res
            print("contrib",contrib)
            #if pointer[(v,a_right)] in sigma_r:
            if a_right in lat[v]:
                print("**************", right,sigma_r[(v,a_right)],"********************" )
                right += sigma_r[(v,a_right)]
            # else:
            #     right = 0
            a_prime = vol.Volume(a_right, 0)
        #if pointer[(v,lat_rev[v][s_left])] in sigma_r:
        if (s_left in lat_rev[v]) and (lat_rev[v][s_left][0] in lat[v]):
        #if lat_rev[v][s_left] in lat[v]:
            left += sigma_r[(v,lat_rev[v][s_left][0])]
        # else:
        #     left = 0
        s_prime = vol.Volume(s_left, 0)
    print("end svvt", contrib)
    #deltasvvt[(v,t)] = contrib
    return contrib


def kappa(r,tp,tp_prev):
    print("tp",tp,"tp_prev",tp_prev)
    return vol.Volume((tp-tp_prev)/math.factorial(r+1) , r+1)

def prev_event(tp,event,event_rev):
    i = event_rev[tp]
    return event[i-1]


def contri_intermeidary_vertices(v, t, w, t_p, l_nei, partial_sum, contrib_local, ii, jj, sigma_r, event, event_reverse):
    for jjj in range(jj+1,event_reverse[l_nei[v,t][ii][0]]+1):
        print("v", v, "t",t,"event[jj]", event[jj], "dic_nodes[u][ii]", "index actual event",jj,"index succ events", jjj, "contri event time" ,event[jjj])
        print("comp vol", sigma_r[v,t], sigma_r[v,event[jjj]])

        if v not in contrib_local:
            contrib_local[v] = dict()
        if not (v in contribution and event[jjj] in contribution[v]):
            if sigma_r[v,t] != sigma_r[v,event[jjj]]:
                print("ERREUUUUUUUR ",sigma_r[v,t],sigma_r[v,event[jjj]])
            print("add_contri_local","v",v,"event[jjj]",event[jjj],"w,t_p",w,t_p)
            if event[jjj] != t_p:
                print("ici")
                contrib_local[v][event[jjj]] = partial_sum[l_nei[v,t][ii][0]]
            else:
                print("la")
                if ii == len(l_nei[v,t])-1:
                    contrib_local[v][event[jjj]] =  contribution[w][t_p]*(self.coef_volume_con(node, v,event[jjj],w,t_p,sigma_r, pre, nppol.Polynomial([1]) ))
                else:
                    contrib_local[v][event[jjj]] = partial_sum[l_nei[v,t][ii+1][0]]  + contribution[w][t_p]*(self.coef_volume_con(node, v,event[jjj],w,t_p,sigma_r, pre, nppol.Polynomial([1])))




def contri_delta_svt(node, v, t, l_nei, sigma_r, contribution, deltasvvt, event, event_reverse, pre, GT, unt):
    print("******** new call contri_delta_svt","v", v, "t", t)
    if (v not in contribution) or ((v in contribution) and (t not in contribution[v])):
        partial_sum = dict()
        s = vol.Volume(0,0)
        contrib_local = dict()
        # l_ord = list(dic_nodes_rev.keys())
        # l_ord.sort()
        for ii in range(len(l_nei[(v,t)])-1,-1,-1):
            #normally it should be sorted
            for u in l_nei[v,t][ii][1]:
                w,t_p = (u,l_nei[v,t][ii][0])
                print("from",(v,t), "next",w,t_p,)
                contri_delta_svt(node, w, t_p, l_nei, sigma_r, contribution, deltasvvt, event, event_reverse, pre, GT, unt)
                (t1,t2) = pre[w][t_p][v,t]
                print("lol","v", v, "t", t, "w",w,"t_p",t_p)
                if t1 != t2 and t_p > t and unt[v][t] >=t_p:
                    for yp,tpp in GT[t1,t2].successors((v,t)):
                        print("*!*!*!*!*!*!  instant graph","v",v,"t",t,"t1",t1,"t2",t2, "w",w,"t_p",t_p, "yp", yp, "tpp", tpp)
                        contri_delta_svt(node, yp, tpp, l_nei, sigma_r, contribution, deltasvvt, event, event_reverse, pre, GT, unt)
                        ev_prev = prev_event(tpp,event,event_reverse)
                        r = GT[t1,t2].edge_weight((v,t),(yp,tpp),"weight")
                        s += (kappa(r,tpp,ev_prev)*sigma_r[(v,t)]/sigma_r[(yp,tpp)] ) *contribution[yp][tpp]

                if (t == t_p) or (t_p > t and t1 == t2 and unt[v][t] >=t_p):
                    s += (sigma_r[(v,t)]/sigma_r[(w,t_p)] ) *contribution[w][t_p]

                if l_nei[v,t][ii][0] not in partial_sum:
                    partial_sum[l_nei[v,t][ii][0]] = s
                else:
                    partial_sum[l_nei[v,t][ii][0]] += s

                print("******** half call contri_delta_svt","v", v, "t", t, "sum", s)
                if ii != 0:
                    jj = event_reverse[l_nei[v,t][ii-1][0]]
                else:
                    jj = event_reverse[t]
                print("u", u, "dic_nodes[u]", l_nei[v,t][ii])
                print("******** half after call contri_delta_svt","v", v, "t", t)
                print("dic_nodes[u]",l_nei[v,t],"u",u)



        if v not in contribution:
            contribution[v] = dict()
        for vv in contrib_local:
            for ss in contrib_local[vv]:
                contribution[vv][ss] = contrib_local[vv][ss]
        contribution[v][t] = s + deltasvvt[(v,t)]
    print("******** end call contri_delta_svt","v", v, "t", t,"contribution[v][t]",contribution[v][t])
    return contribution

