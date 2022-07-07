import networkx as nx
from straph.betweenness import ordgraph as org


class Graph:

    def __init__(self,g = None):
        if g != None:
            self.graph = g
        else:
            self.graph = nx.DiGraph()



    def add_edge(self, v, w, att, wei):
        self.graph.add_edge(v,w,**{att: wei})
    def nodes(self):
        return self.graph.nodes
    def edges(self):
        return self.graph.edges
    def out_degree(self):
        return self.graph.out_degree()
    def in_degree(self):
        return self.grah.in_degree()

    def sinks(self):
        return list((node for node, out_degree in self.graph.out_degree() if out_degree == 0))

    def sources(self):
        return list((node for node, in_degree in self.graph.in_degree() if in_degree == 0))
    def edge_weight(self, v, w, s):
        return self.graph[v][w][s]
    def successors(self, v):
        return list(self.graph[v])
    def topological_sort(self):
        return self.graph.topological_sort(G)
    def copy(self):
         return Graph(self.graph.copy())
    def reverse(self, copy = True):
        nouv = self.graph.reverse(copy = copy)
        return Graph(nouv)

    def descendants_at_distance(self, source, distance):
        current_distance = 0
        current_layer = {(source,0)}
        visited = {(source,0)}

        # this is basically BFS, except that the current layer only stores the nodes at
        # current_distance from source at each iteration
        while current_distance < distance:
            next_layer = set()
            for node,dis in current_layer:
                for child in self.successors(node):
                    if child not in visited:
                        visited.add((child,dis+self.edge_weight(node,child,"weight")))
                        next_layer.add((child,self.edge_weight(node,child,"weight")))
            current_layer = next_layer
            current_distance += 1

        return current_layer

    def transitive_closure_dag(self, topo_order=None):
        """variant from networkx"""
        if topo_order is None:
            topo_order = list(nx.topological_sort(self.graph))

        TC = self.copy()

        # idea: traverse vertices following a reverse topological order, connecting
        # each vertex to its descendants at distance 2 as we go
        for v in reversed(topo_order):
            l = list(TC.descendants_at_distance(v, 2)) 
            for (e,d) in l:
                TC.add_edge(v,e,"weight",d)
        return TC


def predecessor_graph(s, pre, node):
    G = Graph()
    for k in s.nodes:
        if k != node:
            for key in pre[k].keys():
                for v2 in pre[k][key].keys(): 
                    v,t = v2
                    G.add_edge((v,t),(k,key),"interval",pre[k][key][v2])
    return G



def graph_to_ordered(G, ev, ev_rev):
    return org.OrdGraph(G.nodes(), G.edges(), ev, ev_rev, G.sinks())

def trav_instant_graphs(G, node, e, GG, visited):
    if e in visited:
        return
    #print("***** start *****", e)
    visit = G.successors(e)
    #print("visit",visit)
    visited.add(e)
    inter_act = G.edge_weight(node,e,"interval")
    t1,t2 = inter_act
    if t1 != t2 and t2 == node[1]:
        if inter_act not in GG:
            GG[inter_act] = Graph()
        GG[inter_act].add_edge(node,e,"weight",1)
    for ee in visit:
        trav_instant_graphs(G,e, ee, GG, visited)

def instant_graphs(G):
    GG = dict()
    #visited = [(x,0)]
    l = G.sources()
    for node in l:
        for e in G.successors(node):
            trav_instant_graphs(G, node, e, GG, set())
    return GG



