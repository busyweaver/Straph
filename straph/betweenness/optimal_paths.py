from straph import fibheap as fib
import numpy
from straph.paths import meta_walks as mw

def link_index(s):
    d = dict()
    for i in range(0, len(s.links)):
        d[s.links[i]] = i
    return d


def until(s, events, events_rev):
    unt = dict()
    for v in s.nodes:
        unt[v] = dict()
        for i in range(0,len(s.node_presence[v]),2):
            j = events_rev[s.node_presence[v][i]]
            while j<len(events) and  events[j] <= s.node_presence[v][i+1]:
                unt[v][events[j]] = s.node_presence[v][i+1]
                j += 1
    return unt

def before(s, events, events_rev):
    bef = dict()
    for v in s.nodes:
        bef[v] = dict()
        for i in range(len(s.node_presence[v])-1,-1,-2):
            j = events_rev[s.node_presence[v][i]]
            while j>-1 and  events[j] >= s.node_presence[v][i-1]:
                bef[v][events[j]] = s.node_presence[v][i-1]
                j -= 1
    return bef

def to_undirected(ss):
    s = ss.__deepcopy__()
    taille = len(s.links)
    for i in range(0,taille):
        x,y = s.links[i]
        s.links.append((y,x))
        l = s.link_presence[i]
        lc = l[:]
        s.link_presence.append(lc)
    d = dict()

    for i in range(0,len(s.links)):
        tmp = set()
        for j in range(0,len(s.link_presence[i]),2):

            tmp.add( tuple([s.link_presence[i][j],s.link_presence[i][j+1]]) )
        s.link_presence[i] = tmp
    for i in range(0,len(s.links)):
        x = min(s.links[i][0],s.links[i][1])
        y = max(s.links[i][0],s.links[i][1])
        if (x,y) in d:
            d[(x,y)] = d[(x,y)].union(s.link_presence[i])
        else:
            d[(x,y)] = s.link_presence[i]
    #print(d)
    new_s = []
    #new_to_sort = []
    new_sl = []
    for e in d:
        x = list(d[e])
        x.sort()
        new_s.append(x)
        new_s.append(x[:])
        new_sl.append(e)
        new_sl.append((e[1],e[0]))
    # for i in range(0,len(new_s)):
    #     for j in range(0, len(new_s[i])):
    new_l=[]
    new_pre = []
    for i in range(0,len(new_s)):
        new_l.append(new_sl[i])
        new_pre.append([item for sublist in new_s[i] for item in sublist])
    s.links = new_l
    s.link_presence = new_pre
    return s

# def to_undirected(ss):
#     s = ss.__deepcopy__()
#     taille = len(s.links)
#     for i in range(0,taille):
#         x,y = s.links[i]
#         s.links.append((y,x))
#         l = s.link_presence[i]
#         lc = l[:]
#         s.link_presence.append(lc)
#     return s





def neighbors_direct(s):
    res ={ i:dict() for i in s.nodes}
    res_inv = { i:dict() for i in s.nodes}
    for i in range(len(s.links)):
        x,y = s.links[i]
        if y not in res[x]:
            res[x][y] = []
        if x not in res_inv[y]:
            res_inv[y][x] = []
        #print(s.link_presence[i])
        for j in range(0,len(s.link_presence[i]),2):
            t1,t2 = s.link_presence[i][j:j+2]
            if t1 != t2:
                if (j > 0 and t1 != s.link_presence[i][j-1]) or (j==0):
                    res[x][y].append([t1, (t1,t1)])
                if (j > 0 and t1 != s.link_presence[i][j-1]) or (j==0):
                    res_inv[y][x].append([t1, (t1,t1)])
                res[x][y].append([t2, (t1,t2)])
                res_inv[y][x].append([t2, (t1,t2)])
            else:
                if (j > 0 and t1 != s.link_presence[i][j-1]) or (j==0):
                    res[x][y].append([t1, (t1,t1)])
                if (j > 0 and t1 != s.link_presence[i][j-1]) or (j==0):
                    res_inv[y][x].append([t1, (t1,t1)])
    for v in res.keys():
        for e in res[v].keys():
            res[v][e] = set(tuple([tuple(z) for z in res[v][e]]))
    for v in res_inv.keys():
        for e in res_inv[v].keys():
            res_inv[v][e] = set(tuple([tuple(z) for z in res_inv[v][e]]))

    return res,res_inv

def compute_c(last_depar, arrival, leng):
    if arrival - last_depar < 0:
        return (0.0,leng)
    else:
        return (arrival - last_depar,leng)

def relax_resting_paths(b, t, tp, pre, cur_best, events, events_rev, Q, Q_nod):
    cnew = compute_c(cur_best[b][t][0], tp, cur_best[b][t][1])
    cold = compute_c(cur_best[b][tp][0], tp, cur_best[b][tp][1])
    if cnew < cold:
        pre[b][tp] = dict()
        cur_best[b][tp] = (cur_best[b][t][0],cur_best[b][t][1])
        if (b,tp) in Q_nod:
            Q.decrease_key(Q_nod[b,tp], (cnew,(b,tp)))
        else:
            Q_nod[b,tp] = Q.insert( (cnew,(b,tp) ) )



def relax_paths(a, b, t, tp, pre, cur_best, events, Q, Q_nod, edge):
    if pre[a][t] == {}:
        return
    #print("arrivals",arrivals)
    last_depar = cur_best[a][t][0]
    relax_paths_aux(a, b, last_depar, tp, t, edge, cur_best, pre, Q, Q_nod)
    return

def relax_paths_aux(a, b, last_depar, arrival, e, edge_taken, cur_best, pre, Q, Q_nod):

    cnew = compute_c(last_depar, arrival, cur_best[a][e][1] + 1)
    cold = compute_c(cur_best[b][arrival][0], arrival, cur_best[b][arrival][1])
    if cnew < cold:
        #pre[b][arrival] = set()
        pre[b][arrival] = dict()
        cur_best[b][arrival] = (last_depar,cur_best[a][e][1] + 1)
        cold = compute_c(cur_best[b][arrival][0], arrival, cur_best[b][arrival][1])
        #print("Q_nod[b,arrival]",Q_nod[b,arrival])
        if (b,arrival) in Q_nod:
            Q.decrease_key(Q_nod[b,arrival], (cnew,(b,arrival)))
        else:
            Q_nod[b,arrival] = Q.insert( (cnew,(b,arrival) ) )

        #Q.decrease_key(Q_nod[b,arrival], (cnew, (b,arrival)) )
    if cnew == cold:
        pre[b][arrival][(a,e)] = edge_taken

def dijkstra_directed(sg, s, events, events_rev, neighbors, d, neighbors_inv, unt):
    Q = fib.FibonacciHeap()
    cur_best = [ {t:(-numpy.Infinity,numpy.Infinity)   for t in events} for i in range(len(sg.nodes)) ]
    pre = [{t:{}   for t in events} for i in range(len(sg.nodes))]
    nod = dict()


    for e in neighbors[s].keys():
        #print("neighbors", s, e,neighbors[s][e])
        for j in range(0,len(sg.link_presence[d[(s,e)]]),2):
        #for j in range(0,2,2):
            if sg.link_presence[d[(s,e)]][j] != sg.link_presence[d[(s,e)]][j+1]:
                l = sg.link_presence[d[(s,e)]][j:j+2]
            else:
                l = sg.link_presence[d[(s,e)]][j:j+1]
            for t in l:
                #print("st",s ,t)
                cur_best[s][t] = (t,0)
                pre[s][t] = {(0,0):(-1,-1)}
                if (s,t) not in nod:
                    nod[s,t] = Q.insert( ((t - cur_best[s][t][0],cur_best[s][t][1]),(s,t) ) )
    #print(Q.total_nodes)
    while Q.total_nodes != 0:
        #print("nb_nodes", Q.total_nodes,"min",Q.find_min().data)
        (x,y) = Q.extract_min().data
        del nod[y]
        (a,t) = y

        #(tpp,dis) = x
        for b in neighbors_inv[a].keys():
            for (tp,edge) in neighbors_inv[a][b]:
                if tp >= t and unt[a][t] >= tp:
                    #print("tp_inv",tp)
                    #if (a,t) == (15,42.61256423310296):
                        #print("salut2_inv",(a,t),(b,tp))
                    relax_resting_paths(a,t,tp,pre,cur_best, events, events_rev, Q, nod)
                    #print("inv",cur_best)

        for b in neighbors[a].keys():
            for (tp,edge) in neighbors[a][b]:
                if tp >= t and unt[a][t] >= tp:
                    #print("tp",tp)
                    #if (a,t) == (15,42.61256423310296):
                        #print("salut2",(a,t),(b,tp))
                    relax_resting_paths(a,t,tp,pre,cur_best, events, events_rev, Q, nod)
                    #print(cur_best)
                    relax_paths(a,b,t,tp,pre,cur_best, events, Q, nod, edge)
                    #print("relax paths", cur_best)
    return (pre, cur_best)

def edges_at_time(s, events):
    res = { t: {v: set() for v in range(len(s.nodes)) } for t in events}
    for i in range(len(s.links)):
        x,y = s.links[i]
        for j in range(0,len(s.link_presence[i]),2):
            t1,t2 = s.link_presence[i][j:j+2]
            res[t1][x].add(y)
            res[t2][x].add(y)
    return res


def clem_new_algorithm(sg, s, events, events_rev, neighbors, d, neighbors_inv, unt):
    edgesT = edges_at_time(sg, events)
    lst = dict()
    l = dict()
    realpath = dict()
    nod = dict()
    pre = [{t:set()   for t in events} for i in range(len(sg.nodes))]
    M = max(events)
    for v in range(len(sg.nodes)):
        lst[v] = -numpy.Infinity
        l[v] = numpy.Infinity
        realpath[v] = set()
    for t in events:
        Q = fib.FibonacciHeap()
        if s not in nod:
            nod[s] = Q.insert( ((M-t,0),s ) )
        lst[s] = t
        l[s] = 0
        realpath[s] = {t}
        for v in range(len(sg.nodes)):
            if v != s:
                # j = events_rev[t]
                # if (t != events[0]) and events[j-1] in unt[v]  and (unt[v][events[j-1]] >= t):
                #     pre[v][t] = pre[v][events[j-1]]
                if lst[v] != -numpy.Infinity:
                    if v not in nod:
                        nod[v] = Q.insert( ((M - lst[v],l[v]),v ) )
        while Q.total_nodes != 0:
            (x,y) = Q.extract_min().data
            del nod[y]
            v = y
            for u in edgesT[t][v]:
                if (lst[v] > lst[u]) or (lst[v] == lst[u] and l[v] + 1 < l[u]):
                    lst[u] = lst[v]
                    l[u] = l[v] + 1
                    realpath[u] = {t}
                    pre[u][t] = { (v,tp)  for tp in realpath[v]}
                    if u not in nod:
                        nod[u] = Q.insert( ((M - lst[u],l[u]),u ) )
                if lst[v] == lst[u] and l[u] == l[v] + 1:
                    realpath[u].add(t)
                    pre[u][t] = pre[u][t].union( { (v,tp) for  tp in realpath[v]})
        for v in range(len(sg.nodes)):
            #print(t,events_rev[t],events[events_rev[t] + 1],unt[v])
            #print("v",v)
            if (t not in unt[v])  or ((t != events[-1]) and (not (unt[v][t] >= events[events_rev[t] + 1]))):
                lst[v] = -numpy.Infinity
                l[v] = numpy.Infinity
                realpath[v] = {}
    return pre


################################ for edge betwenness ################################

def relax_resting_edge(b, t, bound_t, tp, bound_tp, pre, cur_best, events, events_rev, Q, Q_nod):
    cnew = compute_c(cur_best[b][t][bound_t][0], tp, cur_best[b][t][bound_t][1])
    cold = compute_c(cur_best[b][tp][bound_tp][0], tp, cur_best[b][tp][bound_tp][1])
    if cnew < cold:
        pre[b][tp][bound_tp] = dict()
        cur_best[b][tp][bound_tp] = (cur_best[b][t][bound_t][0],cur_best[b][t][bound_t][1])
        if (b,tp,bound_tp) in Q_nod:
            Q.decrease_key(Q_nod[b,tp,bound_tp], (cnew,(b,tp,bound_tp)))
        else:
            Q_nod[b,tp,bound_tp] = Q.insert( (cnew,(b,tp,bound_tp) ) )


def relax_paths_edge(a, b, t, bound_t, tp, bound_tp, pre, cur_best, events, Q, Q_nod, edge):
    if pre[a][t][bound_t] == {}:
        return
    #print("arrivals",arrivals)
    last_depar = cur_best[a][t][bound_t][0]
    relax_paths_aux_edge(a, b, last_depar, bound_tp, tp, bound_t, t, edge, cur_best, pre, Q, Q_nod)
    return

def relax_paths_aux_edge(a, b, last_depar, bound_tp, tp, bound_t, t, edge_taken, cur_best, pre, Q, Q_nod):

    cnew = compute_c(last_depar, tp, cur_best[a][t][bound_t][1] + 1)
    cold = compute_c(cur_best[b][tp][bound_tp][0], tp, cur_best[b][tp][bound_tp][1])
    if cnew < cold:
        #pre[b][tp] = set()
        pre[b][tp][bound_tp] = dict()
        cur_best[b][tp][bound_tp] = (last_depar,cur_best[a][t][bound_t][1] + 1)
        print("cur_best[b][tp]", cur_best[b][tp])
        cold = compute_c(cur_best[b][tp][bound_tp][0], tp, cur_best[b][tp][bound_tp][1])
        #print("Q_nod[b,tp]",Q_nod[b,tp])
        if (b,tp,bound_tp) in Q_nod:
            Q.decrease_key(Q_nod[b,tp,bound_tp], (cnew,(b,tp,bound_tp)))
        else:
            Q_nod[b,tp,bound_tp] = Q.insert( (cnew,(b,tp, bound_tp) ) )

        #Q.decrease_key(Q_nod[b,tp], (cnew, (b,tp)) )
    if cnew == cold:
        pre[b][tp][bound_tp][(a,t,bound_t)] = edge_taken

def dijkstra_directed_edge(sg, s, events, events_rev, neighbors, d, neighbors_inv, unt, avoid = {}):
    Q = fib.FibonacciHeap()
    cur_best = [ {t:{0: (-numpy.Infinity,numpy.Infinity), 1:(-numpy.Infinity,numpy.Infinity)}   for t in events} for i in range(len(sg.nodes)) ]
    pre = [{t:{0:{},1:{}}   for t in events} for i in range(len(sg.nodes))]
    nod = dict()
    for e in neighbors[s].keys():
        for j in range(0,len(sg.link_presence[d[(s,e)]]),2):
        #for j in range(0,2,2):
            if sg.link_presence[d[(s,e)]][j] != sg.link_presence[d[(s,e)]][j+1]:
                l = sg.link_presence[d[(s,e)]][j:j+2]
                print("iciiiiiii")
                for t in l:
                    cur_best[s][t][0] = (t,0)
                    cur_best[s][t][1] = (t,0)
                    pre[s][t][0] = {(0,0):(-1,-1)}
                    pre[s][t][1] = {(0,0):(-1,-1)}
                    if (s,t,0) not in nod:
                        nod[s,t,0] = Q.insert( ((t - cur_best[s][t][0][0],cur_best[s][t][0][1]),(s,t,0) ) )
                    if (s,t,1) not in nod:
                        nod[s,t,1] = Q.insert( ((t - cur_best[s][t][1][0],cur_best[s][t][1][1]),(s,t,1) ) )
            else:
                l = sg.link_presence[d[(s,e)]][j:j+1]
                print("laaaaaaaa")
                for t in l:
                    cur_best[s][t][1] = (t,0)
                    pre[s][t][1] = {(0,0):(-1,-1)}
                    if (s,t,1) not in nod:
                        nod[s,t,1] = Q.insert( ((t - cur_best[s][t][1][0],cur_best[s][t][1][1]),(s,t,1) ) )

    #print(Q.total_nodes)
    print("avant debut", "crubest", cur_best, "pre", pre)
    while Q.total_nodes != 0:
        print("nb_nodes", Q.total_nodes,"min",Q.find_min().data)
        (x,y) = Q.extract_min().data
        del nod[y]
        (a,t,bound) = y
        #(tpp,dis) = x
        for b in neighbors_inv[a].keys():
            for (tp,edge) in neighbors_inv[a][b]:
                if tp >= t and unt[a][t] >= tp:
                    #print("tp_inv",tp)
                    #if (a,t) == (15,42.61256423310296):
                        #print("salut2_inv",(a,t),(b,tp))
                    t1,t2 = edge
                    if t1 != t2:
                        relax_resting_edge(a,t,bound,tp,0,pre,cur_best, events, events_rev, Q, nod)
                    relax_resting_edge(a,t,bound,tp,1,pre,cur_best, events, events_rev, Q, nod)
                    #print("inv",cur_best)
        print("apres boucle 1", "cur_best",cur_best[a], "pre", pre[a])
        for b in neighbors[a].keys():
            for (tp,edge) in neighbors[a][b]:
                if tp >= t and unt[a][t] >= tp:
                    #print("tp",tp)
                    #if (a,t) == (15,42.61256423310296):
                        #print("salut2",(a,t),(b,tp))
                    t1,t2 = edge
                    if t1 != t2:
                        relax_resting_edge(a,t,bound,tp,0,pre,cur_best, events, events_rev, Q, nod)
                        #print(cur_best)
                        relax_paths_edge(a,b,t,bound,tp,0,pre,cur_best, events, Q, nod, edge)
                        #print("relax paths", cur_best)
                    relax_resting_edge(a,t,bound,tp, 1,pre,cur_best, events, events_rev, Q, nod)
                    #print(cur_best)
                    relax_paths_edge(a,b,t,bound,tp,1,pre,cur_best, events, Q, nod, (tp,tp))
                    #print("relax paths", cur_best)
                    print("fin boucle 2a", "cur_best",cur_best[a], "pre", pre[a])
                    print("fin boucle 2b", "cur_best",cur_best[b], "pre", pre[b])
    return (pre, cur_best)

################################ for discrete temporal graphs generic ################################

def relax_resting_paths_dis_gen(b, t, tp, pre, cur_best, events, events_rev, Q, Q_nod, cmp, cost, opt_walk, n):
    #print("opt_walk[b][t]", opt_walk[b][t], "opt_walk[b][tp]", opt_walk[b][tp])
    #print("opt_walk", opt_walk)
    cold = cur_best[b][t]
    cnew = cost(cur_best[b][t], n, t, tp, True)
    # cnew = cost(opt_walk[b][t],tp,n)
    # cold = cost(opt_walk[b][tp],tp,n)
    if cmp(cnew, cold):
        #print("changement")
        pre[b][tp] = set()
        cur_best[b][tp] = cnew
        #opt_walk[b][tp] = opt_walk[b][t]
        if (b,tp) in Q_nod:
            Q.decrease_key(Q_nod[b,tp], (cnew,(b,tp)))
        else:
            Q_nod[b,tp] = Q.insert( (cnew,(b,tp) ) )



def relax_paths_dis_gen(a, b, t, tp, pre, cur_best, events, events_rev, Q, Q_nod, cmp, cost, opt_walk, n, walk_type, neighbors_inv):
    if pre[a][t] == set():
        return
    # m = opt_walk[a][t]
    # mp = m.clone()
    # mp.add_link(a,b,(tp, tp))
    # cnew = cost(mp,tp,n)
    # cold = cost(opt_walk[b][tp],tp,n)

    cold = cur_best[b][tp]
    cnew = cost(cur_best[a][t], n, t, tp, False)
    # print("m",m)
    # print("mp", mp)

    if cmp(cnew, cold):
        #print("changement")
        #pre[b][arrival] = set()
        pre[b][tp] = set()
        cur_best[b][tp] = cnew
        #opt_walk[b][tp] = mp
        #print("Q_nod[b,arrival]",Q_nod[b,arrival])
        if (b,tp) in Q_nod:
            Q.decrease_key(Q_nod[b,tp], (cnew,(b,tp)))
        else:
            Q_nod[b,tp] = Q.insert( (cnew,(b,tp) ) )

        if walk_type == "active":
            for c in neighbors_inv[b].keys():
                for (tpp,edge) in neighbors_inv[b][c]:
                    if tpp > tp :
                        #print("tp_inv",tp)
                        #if (a,t) == (15,42.61256423310296):
                        #print("salut2_inv",(a,t),(b,tp))
                        relax_resting_paths_dis_gen(b,tp,tpp,pre,cur_best, events, events_rev, Q, Q_nod, cmp, cost, opt_walk, n)

        #Q.decrease_key(Q_nod[b,tp], (cnew, (b,tp)) )
    if cnew == cur_best[b][tp]:
        pre[b][tp].add((a,t))

def dijkstra_directed_dis_gen(sg, s, events, events_rev, neighbors, neighbors_inv, d, cmp, cost, walk_type):
    Q = fib.FibonacciHeap()
    cur_best = [ {t:numpy.Infinity   for t in events} for i in range(len(sg.nodes)) ]
    pre = [{t:set()   for t in events} for i in range(len(sg.nodes))]
    opt_walk = [ {t:mw.Metawalk()  for t in events} for i in range(len(sg.nodes)) ]
    nod = dict()
    n = len(sg.nodes)
    for e in neighbors[s].keys():
        for j in range(0,len(sg.link_presence[d[(s,e)]]),2):
        #for j in range(0,2,2):
            l = sg.link_presence[d[(s,e)]][j:j+1]
            for t in l:
                #opt_walk[s][t] = mw.Metawalk([],[])
                #cur_best[s][t] = cost(opt_walk[s][t], t, n)
                cur_best[s][t] = cost(-1, n, t, t, False)
                pre[s][t] = {(-numpy.Infinity,-numpy.Infinity)}
                if (s,t) not in nod:
                    nod[s,t] = Q.insert( (cur_best[s][t],(s,t) ) )
    while Q.total_nodes != 0:
        #print("nb_nodes", Q.total_nodes,"min",Q.find_min().data)
        (x,y) = Q.extract_min().data
        del nod[y]
        (a,t) = y


        for b in neighbors[a].keys():
            for (tp,edge) in neighbors[a][b]:
                if tp >= t:
                    relax_paths_dis_gen(a,b,t,tp,pre,cur_best, events, events_rev, Q, nod, cmp, cost, opt_walk, n, walk_type, neighbors_inv)

    return (pre, cur_best, opt_walk)




def relax_resting_bellman_dis_gen(b, t, tp, pre, cur_best, events, events_rev, cmp, cost, opt_walk, n):
    cold = cur_best[b][t]
    cnew = cost(cur_best[b][t], n, t, tp, True)
    # cnew = cost(opt_walk[b][t],tp,n)
    # cold = cost(opt_walk[b][tp],tp,n)
    if cmp(cnew, cold):
        #print("changement")
        pre[b][tp] = set()
        cur_best[b][tp] = cnew
        #opt_walk[b][tp] = opt_walk[b][t]
    return


def co_sh_im(val,n,t,tp, extend):
    if val == numpy.Infinity:
        return numpy.Infinity
    if val == -1:
        return 0
    if extend:
        return val

    return val + 1

def co_sfp_im(val,n,t, tp, extend):
    if val == numpy.Infinity:
        return numpy.Infinity
    if val == -1:
        return 0.0
    dur = val//n
    l = val%n
    dep = t-dur
    if extend:
        return (tp-dep)*n+l
    return (tp-dep)*n+l+1

def fm_im(val,n,t,tp, extend):
    if val == numpy.Infinity:
        return numpy.Infinity
    if val == -1:
        return 0.0
    #should not go in here
    if extend:
        return -1
    return tp



def relax_bellman_dis_gen(a, b, t, tp, pre, cur_best, events, events_rev, cmp, cost, opt_walk, n, walk_type, neighbors_inv, com = 0):
    if com == 1:
        print("a",a,"b",b,"t",t,"tp",tp)
    if pre[a][t] == set():
        return


    # m = opt_walk[a][t]
    # mp = m.clone()
    # mp.add_link(a,b,(tp, tp))
    # cnew = cost(mp,tp,n)
    # cold = cost(opt_walk[b][tp],tp,n)
    cold = cur_best[b][tp]
    cnew = cost(cur_best[a][t], n, t, tp, False)

    if com == 1:
        print("cold", cold, "cnew", cnew, "cur_best[a][t]", cur_best[a][t])
    if cmp(cnew, cold):
        #print("changement")
        #pre[b][arrival] = set()
        pre[b][tp] = set()
        cur_best[b][tp] = cnew

        #opt_walk[b][tp] = mp

        if walk_type == "active":
            for c in neighbors_inv[b].keys():
                for (tpp,edge) in neighbors_inv[b][c]:
                    if tpp > tp :
                        #print("tp_inv",tp)
                        #if (a,t) == (15,42.61256423310296):
                        #print("salut2_inv",(a,t),(b,tp))
                        relax_resting_bellman_dis_gen(b,tp,tpp,pre,cur_best, events, events_rev, cmp, cost, opt_walk, n)
        #print("after possible rest", )
        #print("Q_nod[b,arrival]",Q_nod[b,arrival])
        #Q.decrease_key(Q_nod[b,tp], (cnew, (b,tp)) )
    if cnew == cur_best[b][tp] and cnew != numpy.Infinity:
        pre[b][tp].add((a,t))


    return

def ford_bellman_directed_gen_dis(sg, s, events, events_rev, neighbors, neighbors_inv, d, cmp, cost, walk_type, com = 0):
    cur_best = [ {t:numpy.Infinity   for t in events} for i in range(len(sg.nodes)) ]
    pre = [{t:set()   for t in events} for i in range(len(sg.nodes))]
    opt_walk = [ {t:mw.Metawalk()  for t in events} for i in range(len(sg.nodes)) ]
    n = len(sg.nodes)
    if com == 1:
        print("n = ", n)
    for e in neighbors[s].keys():
        for j in range(0,len(sg.link_presence[d[(s,e)]]),2):
        #for j in range(0,2,2):
            l = sg.link_presence[d[(s,e)]][j:j+1]
            for t in l:
                #print("init", "s", s,"t",t)
                #opt_walk[s][t] = mw.Metawalk([],[])
                #cur_best[s][t] = cost(opt_walk[s][t], t, n)
                cur_best[s][t] = cost(-1, n, t, t, False)
                pre[s][t] = {(-numpy.Infinity,-numpy.Infinity)}
    if com == 1:
        print("n2 = ", n)
    for xx in sg.nodes:
        for zz in range(len(events)):
            for i in range(0,len(sg.links)):
                a,b = sg.links[i]
                for j in range(0,len(sg.link_presence[i]),2):
                    tp,t2 = sg.link_presence[i][j:j+2]
                    for t in events:
                        if t <= tp:
                            # if walk_type == "active":
                            #     relax_resting_bellman_dis_gen(a,t,tp,pre,cur_best, events, events_rev, cmp, cost, opt_walk, n)
                            if com == 1:
                                print("current node", s, "iter", xx*zz, "xx",xx,"zz",zz)
                            relax_bellman_dis_gen(a,b,t,tp,pre,cur_best, events, events_rev, cmp, cost, opt_walk, n, walk_type, neighbors_inv, com = com)
                        else:
                            break

    return (pre, cur_best, opt_walk)


def relax_resting_bfs_dis_gen(b, t, tp, pre, cur_best, events, events_rev, Q, cmp, cost, opt_walk, n):

    cold = cur_best[b][t]
    cnew = cost(cur_best[b][t], n, t, tp, True)
    # cnew = cost(opt_walk[b][t],tp,n)
    # cold = cost(opt_walk[b][tp],tp,n)
    if cmp(cnew, cold):
        #print("changement")
        pre[b][tp] = set()
        cur_best[b][tp] = cnew
        #opt_walk[b][tp] = opt_walk[b][t]
        if False:
        #if (b,tp) in Q_nod:
            #Q.decrease_key(Q_nod[b,tp], (cnew,(b,tp)))
            print("relax resting: should never happen if good cost function")
        else:
            Q.append( (b,tp) )



def relax_bfs_dis_gen(a, b, t, tp, pre, cur_best, events, events_rev, Q, cmp, cost, opt_walk, n, walk_type, neighbors_inv):
    if pre[a][t] == set():
        return
    # m = opt_walk[a][t]
    # mp = m.clone()
    # mp.add_link(a,b,(tp, tp))
    # cnew = cost(mp,tp,n)
    # cold = cost(opt_walk[b][tp],tp,n)

    cold = cur_best[b][tp]
    cnew = cost(cur_best[a][t], n, t, tp, False)
    # print("m",m)
    # print("mp", mp)

    if cmp(cnew, cold):
        #print("changement")
        #pre[b][arrival] = set()
        pre[b][tp] = set()
        cur_best[b][tp] = cnew
        #opt_walk[b][tp] = mp
        #print("Q_nod[b,arrival]",Q_nod[b,arrival])
        if False:
        #if (b,tp) in Q:
            #Q.decrease_key(Q_nod[b,tp], (cnew,(b,tp)))
            print("relax: should never happen if good cost function")
        else:
            Q.append( (b,tp) )

        if walk_type == "active":
            for c in neighbors_inv[b].keys():
                for (tpp,edge) in neighbors_inv[b][c]:
                    if tpp > tp :
                        #print("tp_inv",tp)
                        #if (a,t) == (15,42.61256423310296):
                        #print("salut2_inv",(a,t),(b,tp))
                        relax_resting_bfs_dis_gen(b,tp,tpp,pre,cur_best, events, events_rev, Q, cmp, cost, opt_walk, n)

        #Q.decrease_key(Q_nod[b,tp], (cnew, (b,tp)) )
    if cnew == cur_best[b][tp]:
        pre[b][tp].add((a,t))

def bfs_directed_dis_gen(sg, s, events, events_rev, neighbors, neighbors_inv, d, cmp, cost, walk_type):
    Q = []
    cur_best = [ {t:numpy.Infinity   for t in events} for i in range(len(sg.nodes)) ]
    pre = [{t:set()   for t in events} for i in range(len(sg.nodes))]
    opt_walk = [ {t:mw.Metawalk()  for t in events} for i in range(len(sg.nodes)) ]
    nod = dict()
    n = len(sg.nodes)
    for e in neighbors[s].keys():
        for j in range(0,len(sg.link_presence[d[(s,e)]]),2):
        #for j in range(0,2,2):
            l = sg.link_presence[d[(s,e)]][j:j+1]
            for t in l:
                #opt_walk[s][t] = mw.Metawalk([],[])
                #cur_best[s][t] = cost(opt_walk[s][t], t, n)
                cur_best[s][t] = cost(-1, n, t, t, False)
                pre[s][t] = {(-numpy.Infinity,-numpy.Infinity)}
                if (s,t) not in nod:
                    Q.append( (s,t) )
    while len(Q) != 0:
        #print("nb_nodes", Q.total_nodes,"min",Q.find_min().data)
        (a,t) = Q.pop()


        for b in neighbors[a].keys():
            for (tp,edge) in neighbors[a][b]:
                if tp >= t:
                    relax_bfs_dis_gen(a,b,t,tp,pre,cur_best, events, events_rev, Q, cmp, cost, opt_walk, n, walk_type, neighbors_inv)

    return (pre, cur_best, opt_walk)
