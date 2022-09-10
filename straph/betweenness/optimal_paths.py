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

def to_undirected(s):
    taille = len(s.links)
    for i in range(0,taille):
        x,y = s.links[i]
        s.links.append((y,x))
        l = s.link_presence[i]
        lc = l[:]
        s.link_presence.append(lc)


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
    P = dict()
    for v in sg.nodes:
        P[v] = set()
    for e in neighbors[s].keys():
        for j in range(0,len(sg.link_presence[d[(s,e)]]),2):
        #for j in range(0,2,2):
            if sg.link_presence[d[(s,e)]][j] != sg.link_presence[d[(s,e)]][j+1]:
                l = sg.link_presence[d[(s,e)]][j:j+2]
            else:
                l = sg.link_presence[d[(s,e)]][j:j+1]
            for t in l:
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
        P[a].add(t)
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
    cnew = cost(opt_walk[b][t],tp,n)
    cold = cost(opt_walk[b][tp],tp,n)
    if cmp(cnew, cold):
        #print("changement")
        pre[b][tp] = set()
        cur_best[b][tp] = cnew
        opt_walk[b][tp] = opt_walk[b][t]
        if (b,tp) in Q_nod:
            Q.decrease_key(Q_nod[b,tp], (cnew,(b,tp)))
        else:
            Q_nod[b,tp] = Q.insert( (cnew,(b,tp) ) )



def relax_paths_dis_gen(a, b, t, tp, pre, cur_best, events, Q, Q_nod, edge, cmp, cost, opt_walk, n):
    if pre[a][t] == {}:
        return
    m = opt_walk[a][t]
    mp = m.clone()
    mp.add_link(a,b,(tp, tp))
    # print("m",m)
    # print("mp", mp)
    cnew = cost(mp,tp,n)
    cold = cost(opt_walk[b][tp],tp,n)
    if cmp(cnew, cold):
        #print("changement")
        #pre[b][arrival] = set()
        pre[b][tp] = set()
        cur_best[b][tp] = cnew
        opt_walk[b][tp] = mp
        #print("Q_nod[b,arrival]",Q_nod[b,arrival])
        if (b,tp) in Q_nod:
            Q.decrease_key(Q_nod[b,tp], (cnew,(b,tp)))
        else:
            Q_nod[b,tp] = Q.insert( (cnew,(b,tp) ) )

        #Q.decrease_key(Q_nod[b,tp], (cnew, (b,tp)) )
    if cnew == cur_best[b][tp]:
        pre[b][tp].add((a,t))


def dijkstra_directed_dis_gen(sg, s, events, events_rev, neighbors, d, neighbors_inv, unt, cmp, cost):
    Q = fib.FibonacciHeap()
    cur_best = [ {t:numpy.Infinity   for t in events} for i in range(len(sg.nodes)) ]
    pre = [{t:{}   for t in events} for i in range(len(sg.nodes))]
    opt_walk = [ {t:mw.Metawalk()  for t in events} for i in range(len(sg.nodes)) ]
    nod = dict()
    n = len(sg.nodes)
    for e in neighbors[s].keys():
        for j in range(0,len(sg.link_presence[d[(s,e)]]),2):
        #for j in range(0,2,2):
            if sg.link_presence[d[(s,e)]][j] != sg.link_presence[d[(s,e)]][j+1]:
                l = sg.link_presence[d[(s,e)]][j:j+2]
            else:
                l = sg.link_presence[d[(s,e)]][j:j+1]
            for t in l:
                cur_best[s][t] = cost(mw.Metawalk([],[]), t, n)
                pre[s][t] = {(-numpy.Infinity,-numpy.Infinity)}
                opt_walk[s][t] = mw.Metawalk([],[])
                if (s,t) not in nod:
                    nod[s,t] = Q.insert( (0.0,(s,t) ) )
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
                    relax_resting_paths_dis_gen(a,t,tp,pre,cur_best, events, events_rev, Q, nod, cmp, cost, opt_walk, n)
                    # print("inv cur",cur_best)
                    # print("inv opt",opt_walk)
                    # print("inv pre",pre)

        for b in neighbors[a].keys():
            for (tp,edge) in neighbors[a][b]:
                if tp >= t and unt[a][t] >= tp:
                    #print("tp",tp)
                    #if (a,t) == (15,42.61256423310296):
                        #print("salut2",(a,t),(b,tp))
                    relax_resting_paths_dis_gen(a,t,tp,pre,cur_best, events, events_rev, Q, nod, cmp, cost, opt_walk, n)
                    #print(cur_best)
                    relax_paths_dis_gen(a,b,t,tp,pre,cur_best, events, Q, nod, edge, cmp, cost, opt_walk, n)
                    # print("relax paths cur", cur_best)
                    # print("relax paths opt", opt_walk)
                    # print("relax paths pre", pre)
    return (pre, cur_best, opt_walk)




def relax_resting_bellman_dis_gen(b, t, tp, pre, cur_best, events, events_rev):
    cnew = cost(opt_walk[b][t],tp,n)
    cold = cost(opt_walk[b][tp],tp,n)
    if cmp(cnew, cold):
        #print("changement")
        pre[b][tp] = set()
        cur_best[b][tp] = cnew
        opt_walk[b][tp] = opt_walk[b][t]
    return


def relax_bellman_gen_dis(a, b, t, tp, pre, cur_best, events):
    if pre[a][t] == {}:
        return
    m = opt_walk[a][t]
    mp = m.clone()
    mp.add_link(a,b,(tp, tp))
    # print("m",m)
    # print("mp", mp)
    cnew = cost(mp,tp,n)
    cold = cost(opt_walk[b][tp],tp,n)
    if cmp(cnew, cold):
        #print("changement")
        #pre[b][arrival] = set()
        pre[b][tp] = set()
        cur_best[b][tp] = cnew
        opt_walk[b][tp] = mp
        #print("Q_nod[b,arrival]",Q_nod[b,arrival])
        #Q.decrease_key(Q_nod[b,tp], (cnew, (b,tp)) )
    if cnew == cur_best[b][tp]:
        pre[b][tp].add((a,t))


    return

def ford_bellman_directed_gen_dis(sg, s, events, events_rev, neighbors, d, neighbors_inv, unt, cmp, cost):
    cur_best = [ {t:numpy.Infinity   for t in events} for i in range(len(sg.nodes)) ]
    pre = [{t:{}   for t in events} for i in range(len(sg.nodes))]
    opt_walk = [ {t:mw.Metawalk()  for t in events} for i in range(len(sg.nodes)) ]
    n = len(sg.nodes)
    for e in neighbors[s].keys():
        for j in range(0,len(sg.link_presence[d[(s,e)]]),2):
        #for j in range(0,2,2):
            if sg.link_presence[d[(s,e)]][j] != sg.link_presence[d[(s,e)]][j+1]:
                l = sg.link_presence[d[(s,e)]][j:j+2]
            else:
                l = sg.link_presence[d[(s,e)]][j:j+1]
            for t in l:
                cur_best[s][t] = cost(mw.Metawalk([],[]), t, n)
                pre[s][t] = {(-numpy.Infinity,-numpy.Infinity)}
                opt_walk[s][t] = mw.Metawalk([],[])
        #the 2 loops inside the first are to iterate over each temporal link 
        for k in self.nodes:
            for t in events:
                for i in range(0,len(self.links)):
                    a,b = self.links[i]
                    for j in range(0,len(self.link_presence[i]),2):
                        tp,t2 = self.link_presence[i][j:j+2]
                        for t in events:
                            if t <= tp:
                                self.relax_bellman_dis_gen(a,b,t,tp,pre,cur_best, events)
                                self.relax_resting_bellman_dis_gen(b,t,tp,pre,cur_best, events, events_rev)

        return (pre, cur_best, opt_walk)
