#%autoindent

from graphlib import graph_dist
from collections import deque

class LinkStream:
	def __init__(self):
		self.alpha = None
		self.omega = None
		self.V = set()
		self.E = set()
		self.eventtimes = []

# read input file describing the link stream L = (T=[alpha,omega],V,E),eventtimes
def read_link_stream(f):
	L = LinkStream()
	for l in f:
		if len(l)==1 or l[0]=='#':
			continue
	        l=l.strip().split()
		if len(l)==2:
			assert l[0] in ["alpha","omega"]
	                if l[0]=="alpha":
	                        L.alpha = float(l[1])
	                else:
	                        L.omega = float(l[1])
	        else:
	                assert(len(l)==4)
	                [b,e,x,y] = l
	                b = float(b)
	                e = float(e)
	                L.V.add(x)
	                L.V.add(y)
	                L.E.add((b,e,x,y))
	                L.E.add((b,e,y,x))
	assert L.alpha != None
	assert L.omega != None
	L.eventtimes = list(set([b for (b,_,_,_) in L.E]+[e for (_,e,_,_) in L.E]))
	L.eventtimes.sort()
	assert L.eventtimes[0]>=L.alpha and L.eventtimes[-1]<=L.omega
	return(L)

# Functions to get neighborhoods of the graph at a given instant t in the link stream.
# inefficient but simple...

def get_graph_neighborhood(L,t):
        N = {}
        for (b,e,u,v) in L.E:
                if b<=t and e>=t:
                        if u not in N:
                                N[u]=set()
                        N[u].add(v)
                        if v not in N:
                                N[v]=set()
                        N[v].add(u)
        for v in N:
                N[v] = list(N[v])
        return N

def get_graph_neighborhood_minus(L,t):
        N = {}
        for (b,e,u,v) in L.E:
                if b<t and e>=t:
                        if u not in N:
                                N[u]=set()
                        N[u].add(v)
                        if v not in N:
                                N[v]=set()
                        N[v].add(u)
        for v in N:
                N[v] = list(N[v])
        return N

def get_graph_neighborhood_plus(L,t):
        N = {}
        for (b,e,u,v) in L.E:
                if b<=t and e>t:
                        if u not in N:
                                N[u]=set()
                        N[u].add(v)
                        if v not in N:
                                N[v]=set()
                        N[v].add(u)
        for v in N:
                N[v] = list(N[v])
        return N

# compute for all w in V and all event time t from i to j the distance Dist[(t,w)] from (i,u) to (t,w)
def ls_dist(L,(i,u),j):
        Dist = {}
        # first compute distances at time i
        d_iu = graph_dist(get_graph_neighborhood(L,i),u)
        for w in d_iu:
                Dist[(i,w)] = d_iu[w]
        # if i==j then done
        if i==j:
                return Dist
        # otherwise, take pairs (t,t_prime) of consecutive event times in increasing order and compute distances at time t_prime from the ones at time t
        t = i
        for t_prime in [x for x in L.eventtimes if i<x and x<j]+[j]:
                assert t_prime>t
                # use a queue Q and a list X; both contain pairs (w,d) where w is a node and d is a distance;
                # process elements from Q and X one by one by increasing order of distance; no addition to X;
                # use X in reverse order to remove elements at is end (for efficiency)
                Q = deque([])
                X = [(x,Dist[(t,x)]) for x in L.V if (t,x) in Dist]
                X.sort(key=lambda x: x[1], reverse=True)
                while len(Q)>0 or len(X)>0:
                        # take the first element of Q or X with minimal d...
                        if len(Q)==0:
                                (w,d) = X.pop()
                        elif len(X)==0:
                                (w,d) = Q.pop()
                        else:
                                (_,dQ) = Q[-1]
                                (_,dX) = X[-1]
                                if dQ<dX:
                                        (w,d) = Q.pop()
                                        assert(d==dQ)
                                else:
                                        (w,d) = X.pop()
                                        assert(d==dX)
                        # ...and process it
                        if (t_prime,w) not in Dist:
                                Dist[(t_prime,w)] = d
                        N_prime = get_graph_neighborhood(L,t_prime)
                        for y in N_prime.get(w,[]):
                                if (t_prime,y) not in Dist:
                                        Q.appendleft((y,d+1))
                t = t_prime
        return(Dist)

