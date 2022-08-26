#%autoindent
from graphlib import graph_non_trivial_connected_components
from lslib import get_graph_neighborhood

# Given a link stream L and a node u, returns the (ordered) latency list LL[w] from u to w, for all node w.
# This is the list of all pairs (s,a) of event times such that the latency from (s,u) to (a,w) is equal to a-s.
def Latency_lists(L,u):
	LL = {w:[] for w in L.V}
        for t in L.eventtimes:
                LL[u].append((t,t))
        	components = graph_non_trivial_connected_components(get_graph_neighborhood(L,t))
	        for C in components:
                	s,X = None,set()
                	for w in C:
				if len(LL[w])>0:
					(s_prime,a_prime)=LL[w][-1]
					if s==None or s_prime>s:
						s,X = s_prime,{w}
					elif s_prime==s:
						X.add(w)
			if len(X)>0:
				for w in C.difference(X):
						LL[w].append((s,t))
	return(LL)

