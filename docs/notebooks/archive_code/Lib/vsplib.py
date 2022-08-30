#%autoindent
import math,sys
from collections import deque
from lslib import read_link_stream,get_graph_neighborhood,get_graph_neighborhood_plus,ls_dist
from graphlib import graph_dist_sigma

# Volume operations.

def plusvol((q,d),(q_,d_)):
    q = float(q)
    q_ = float(q_)
    if d==d_:
        return (q+q_,d)
    elif d>d_:
        return (q,d)
    return (q_,d_)

def minusvol(v,(q,d)):
    q = float(q)
    return(plusvol(v,(-q,d)))

def divvol((q,d),(q_,d_)):
    q = float(q)
    q_ = float(q_)
    if d==d_:
        return float(q)/float(q_)
    assert d<d_
    return 0.

def timesvol((q,d),(q_,d_)):
    q = float(q)
    q_ = float(q_)
    return (q*q_,d+d_)

def VSP(L,(i,u),(j,v)):
    i = float(i)
    j = float(j)

    # number of paths in G_i
    N_i = get_graph_neighborhood(L,i)
    (_,sigma_i) = graph_dist_sigma(N_i,u)

    # if i==j then done
    if i==j:
        return (sigma_i.get(v,0.),0)
    # vol[(t,w)] will be the volume of shortest paths from (i,u) to (t,w).
    vol = {}

    for w in sigma_i:
        vol[(i,w)] = (sigma_i[w],0)
    # print("*************///////////// sigma_i", sigma_i)
    # print("****************//////// vol",vol)
    # distances from (i,u) to all until time j
    Dist = ls_dist(L,(i,u),j)
    # print("Dist", Dist)

    # compute the list of nodes reachable from (i,u) at each event time, ordered by distance
    reachable = {}
    for (t,w) in Dist:
        if t not in reachable:
            reachable[t] = []
        reachable[t].append((w,Dist[(t,w)]))
    for t in reachable:
        # print(reachable[t])
        reachable[t].sort(key=lambda x: x[1])
        reachable[t] = [w for (w,_) in reachable[t]]
    # print("reachable", reachable)

    # take pairs of consecutive event times in increasing order
    t = i
    for t_prime in [x for x in L.eventtimes if i<x and x<j]+[j]:
        assert t_prime>t
        N_prime = get_graph_neighborhood(L,t_prime)
        N_plus = get_graph_neighborhood_plus(L,t)

        # process nodes w reachable at t_prime from (i,u) in increasing order of distance
        for w in reachable[t_prime]:
            # print("reachable[t_prime]", reachable[t_prime])
            # compute distances and sigma in the graph G_t^+, used in the formulae...
            (d_wplus,sigma_wplus) = graph_dist_sigma(N_plus,w)
            # ...and apply the formulae
            for x in d_wplus:
                # print("t",t,"t_prime",t_prime,"x",x)
                if (t_prime,x) in Dist and (t,x) in Dist and (t_prime,w) in Dist and Dist[(t,x)]+d_wplus[x] == Dist[(t_prime,w)]:
                    vol[(t_prime,w)] = plusvol(vol.get((t_prime,w),(0.,0)), timesvol(vol.get((t,x),(0.,0)), (sigma_wplus[x]*(t_prime-t)**d_wplus[x]/math.factorial(d_wplus[x]),d_wplus[x])))
                    #if t_prime == 43.20861816893123 and w == '5':
                        # print("1", w,t_prime,t,x, "vol[(t_prime,w)]", vol[(t_prime,w)], "vol.get((t_prime,w),(0.,0))", vol.get((t_prime,w),(0.,0))," + ", "vol.get((t,x),(0.,0))",vol.get((t,x),(0.,0)),"*", "(sigma_wplus[x]*(t_prime-t)**d_wplus[x]/math.factorial(d_wplus[x]),d_wplus[x]))",(sigma_wplus[x]*(t_prime-t)**d_wplus[x]/math.factorial(d_wplus[x]),d_wplus[x]) )

            for y in N_prime.get(w,[]):
                if (t_prime,y) in Dist and Dist[(t_prime,w)] == Dist[(t_prime,y)]+1:
                    vol[(t_prime,w)] = plusvol(vol.get((t_prime,w),(0.,0)),vol.get((t_prime,y),(0.,0)))
                    #if t_prime == 43.20861816893123 and w == '5':
                        # print("2", w,t_prime,"vol[(t_prime,w)]", vol[(t_prime,w)], "vol.get((t_prime,w),(0.,0))",vol.get((t_prime,w),(0.,0)),"+", "vol.get((t_prime,y),(0.,0))", vol.get((t_prime,y),(0.,0)))
            # print("************* vol *************")
            #print(vol)
            #if ((j,v),(0.,0)) in vol:
            #    print("////////////////////////////////////////////", vol.get((j,v),(0.,0)))
        t = t_prime

    # result
    # print("***************** vol ************************")
    # print(vol)
    # print("////////////////////////////////////////////",j,v, vol.get((j,v),(0.,0)))
    return vol.get((j,v),(0.,0))

