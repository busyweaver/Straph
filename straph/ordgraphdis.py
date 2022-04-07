class OrdGraphDis:
    """
    A Graph

    """

    def __init__(self,
                 nodes=None,
                 links=None,
                 ev=None,
                 ev_rev=None,
                 sinks=None
    ):
        """
        A basic constructor for a ``StreamGraph`` object
        
        :param id: A parameter to identify a stream graph.
        :param times: Continous interval of time during the stream graph exists 
        :param nodes: A list of nodes present in  the stream graph
        :param node_presence : List of lists in the same order as the nodes. Each list contains 
        succescively the time of apparition and time of disparition of the node.
        :param links : A list of links present in the stream graph
        :param link_presence : same as node_presence
        """
        self.nodes = nodes
        self.links = links
        self.nei = dict()
        self.l_nei = dict()
        for (x,y) in links:
            v,t = x
            w,tp = y
            if x in self.nei:
                self.nei[x][ev_rev[tp]].append(w)
            else:
                self.nei[x] = [[] for e in ev ]
                self.nei[x][ev_rev[tp]].append(w)
        for e in sinks:
            self.nei[e] = [[] for e in ev ]
        for v in nodes:
            self.l_nei[v] = []
            for i in range(0,len(self.nei[v])):
                if self.nei[v][i] != []:
                    self.l_nei[v].append([ev[i],self.nei[v][i]])

