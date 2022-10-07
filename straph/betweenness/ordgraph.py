class OrdGraph:
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

