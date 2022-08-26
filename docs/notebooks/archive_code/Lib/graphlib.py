#%autoindent
import Queue

def graph_dist(N,v):
	d = {}
	d[v]=0
	if v not in N:
		return d
	q = Queue.Queue()
	q.put(v)
	while not q.empty():
		v = q.get()
		assert v in N
		for u in N[v]:
			if u not in d:
				q.put(u)
				d[u] = d[v]+1
	return d

def graph_is_reachable(N,w,v):
	if w==v:
		return True
	if w not in N or v not in N:
		return False
	marked = set()
	q = Queue.Queue()
	q.put(v)
	marked.add(v)
	while not q.empty():
		v = q.get()
		assert v in N
		for u in N[v]:
			if u not in marked:
				if u==w:
					return True
				q.put(u)
				marked.add(u)
	return False

def graph_non_trivial_connected_components(N):
	result = []
	marked = set()
	for v in N:
		if v not in marked:
			component = set()
			component.add(v)
			q = Queue.Queue()
			q.put(v)
			marked.add(v)
			while not q.empty():
				v = q.get()
				assert v in N
				for u in N[v]:
					if u not in marked:
						component.add(u)
						q.put(u)
						marked.add(u)
			result.append(component)
	return result

# given a graph described by its neighborhood dict N, and a node v,
# computes the distance d[u] and number of shortest paths s[u]
# from v to any other node u.
def graph_dist_sigma(N,v):
	d = {}
	s = {}
	d[v]=0
	s[v]=1
	if v not in N:
		return (d,s)
	q = Queue.Queue()
	q.put(v)
	while not q.empty():
		v = q.get()
		assert v in N
		for u in N[v]:
			if u not in d:
				q.put(u)
				d[u] = d[v]+1
				s[u] = 0
			if d[u]==d[v]+1:
				s[u] += s[v]
	return (d,s)

