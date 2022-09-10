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
        return self.graph.in_degree()

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

    def descendants_at_distance(self, source, distance, distances):
        current_distance = 0
        current_layer = {(source, 0)}
        visited = {source}
        nb_paths = dict()
        dist = dict()

        # this is basically BFS, except that the current layer only stores the nodes at
        # current_distance from source at each iteration
        while current_distance < distance:
            next_layer = set()
            for node,dis in current_layer:
                # print(node, distances, visited)
                # if len(list(self.successors(node))) == 0:
                #     distances[node] = 0
                for child in self.successors(node):
                    if child not in visited:
                        visited.add(child)
                        if "nb_paths" in self.graph[node][child]:
                            nb_paths[child] = self.graph[node][child]["nb_paths"]
                        else:
                            nb_paths[child] = 1
                        #distances[node] = distances[child] + 1
                        next_layer.add((child,dis + self.graph[node][child]['weight']))
                        dist[child] = dis + self.graph[node][child]['weight']
                    else:
                        if dist[child] == dis + self.graph[node][child]['weight']:
                            if "nb_paths" in self.graph[node][child]:
                                x = self.graph[node][child]["nb_paths"]
                            else:
                                x = 1
                            nb_paths[child] += x

            current_layer = next_layer
            current_distance += 1

        return current_layer, nb_paths

    def transitive_closure_dag(self, topo_order=None):
        """variant from networkx"""
        if topo_order is None:
            topo_order = list(nx.topological_sort(self.graph))
        # print(topo_order)
        # print("///////////////////////")

        TC = self.copy()

        # idea: traverse vertices following a reverse topological order, connecting
        # each vertex to its descendants at distance 2 as we go

        for v in reversed(topo_order):
            distances = dict()
            l = list(TC.descendants_at_distance(v, 2, distances))
            #p = nx.path_graph(self.graph, source = v)
            for e,d in l[0]:
                TC.add_edge(v,e,"weight",d)
                TC.add_edge(v,e,"nb_paths",l[1][e] )
        for e in TC.edges():
            TC.graph[e[0]][e[1]]["weight"] = TC.graph[e[0]][e[1]]["weight"] -1
            if "nb_paths" not in TC.graph[e[0]][e[1]]:
                TC.graph[e[0]][e[1]]["nb_paths"] = 1


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

def predecessor_graph_dis_gen(s, pre, node):
    G = Graph()
    for k in s.nodes:
        if k != node:
            for key in pre[k].keys():
                for v2 in pre[k][key]:
                    v,t = v2
                    if v == node:
                        G.add_edge((node,-1),(k,key), "weight", 1)
                    else:
                        G.add_edge((v,t),(k,key), "weight", 1)
    return G

def predecessor_graph_edge(s, pre, node):
    G = Graph()
    for k in s.nodes:
        if k != node:
            for key in pre[k].keys():
                for bound in pre[k][key].keys():
                    for v2 in pre[k][key][bound].keys():
                        v,t,b = v2
                        G.add_edge((v,t,b),(k,key,bound),"interval",pre[k][key][bound][v2])
    return G



def graph_to_ordered(G, ev, ev_rev):
    return org.OrdGraph(G.nodes(), G.edges(), ev, ev_rev, G.sinks())



def trav_instant_graphs(G, e, GG, visited):
    if e in visited:
        return
    #print("***** start *****", e, G)
    visit = G.successors(e)
    #print("visit",visit)
    visited.add(e)
    for (w,t_p) in visit:
        inter_act = G.edge_weight(e,(w,t_p),"interval")
        t1,t2 = inter_act
        if t1 != t2 and t2 == e[1]:
            if inter_act not in GG:
                GG[inter_act] = Graph()
            GG[inter_act].add_edge(e,(w,t_p),"weight",1)
        if t1 != t2 and not t2 == e[1]:
            if inter_act not in GG:
                GG[inter_act] = Graph()
            GG[inter_act].add_edge(e,(w,t_p),"weight",1)
        trav_instant_graphs(G,(w,t_p), GG, visited)

def instant_graphs(G):
    GG = dict()
    #visited = [(x,0)]
    l = G.sources()
    for node in l:
        for e in G.successors(node):
            trav_instant_graphs(G, e, GG, set())
    return GG

def interval_graph(Gp):
    GT = dict()
    for e in Gp:
        # print("**********",e,"**************")
        GT[e] = Gp[e].transitive_closure_dag( topo_order=None)
    return GT

def max_volume_superposition(GT):
    length = []
    for e in GT:
        length.append(max( GT[e].edge_weight(i,j,"weight") for (i,j) in  GT[e].edges()))
    if length == []:
        return 0
    else:
        return  max(length) +1
