import matplotlib.pyplot as plt
import numpy as np
import numpy.polynomial.polynomial as nppol

class Metawalk:
    def __init__(self,
                 time_intervals=None,
                 nodes=None,
                 ):
        """
        A basic constructor for a ``Metwalks`` object

        :param times : A list of couples of floats which represents times corresponding to the time intervals
        :param links : A list of nodes. (first node = source ; last node = destination)
        """
        self.time_intervals = time_intervals
        self.nodes = nodes

    def is_empty(self):
        return self.time_intervals == []

    def is_none(self):
        return self.time_intervals == None

    def add_link(self, a, b, t):
        if self.nodes == []:
            self.nodes = self.nodes + [a,b]
            self.time_intervals.append(t)
        else:
            if self.nodes[-1] == a:
                self.time_intervals.append(t)
                self.nodes.append(b)

    def length(self):
        if self.is_none():
            return -1
        return len(self.time_intervals)

    def duration(self):
        return self.time_intervals[-1][1] - self.time_intervals[0][0]

    def clone(self):
        return Metawalk(self.time_intervals[:],self.nodes[:])

    def __hash__(self):
        m = tuple(self.nodes)
        n = tuple(self.time_intervals)
        return hash((m,n))
    def __str__(self):
        s = ""
        if self.is_none():
            return ""
        if self.is_empty():
            return "empty"
        for i in range(0,self.length()):
            s += " "
            s += str(self.nodes[i])
            s += " "
            s += str(self.time_intervals[i])
        s += " "
        s += str(self.nodes[i+1])
        s += " | volume = "
        s += str(self.volume())
        return s

    def __repr__(self):
        return self.__str__()

    def __eq__(self, m):
        if m == None:
            return False
        if m.length() != self.length():
            return False
        if (m.nodes == self.nodes) and (m.time_intervals == self.time_intervals):
            return True
        return False

    def is_instantenous(self):

        #we check from the last because of the algirothm that uses it add new links to the end of the metawalk
        b = True
        if len(self.time_intervals) == 1:
            return True
        x = self.time_intervals[-1]
        for i in range(-2,-len(self.time_intervals)-1,-1):
            if self.time_intervals[i] != x:
                return False
        return True

    def update_following_last(self,b):
        #sometimes when adding a metaedge the metawalk has to be cut at some points because some paths are no longer valid.
        if b == 0:
            #last edge added ends at same time but starts before
            self.time_intervals[-1][0] = self.time_intervals[-2][0]
        else:
            end = self.time_intervals[-1][1]
            # last edge starts at same time but ends before
            for i in range(-2,-len(self.time_intervals)-1,-1):
                if self.time_intervals[i][1] > end:
                    self.time_intervals[i][1] = end



    def volume(self):
        """Normally the link are either exactly the same or disjoint, need to check for inclusion, exclusion of intervals  """
        time_intervals = self.time_intervals[:]
        time_intervals.append([-1,-1])
        res = [0 for i in range(len(time_intervals)+ 1)]
        last_x,last_y = time_intervals[0]
        b = True
        somme = 0
        if len(time_intervals)==1:
            last_x,last_y = time_intervals[0]
            if last_x != last_y:
                b = False
                res[1] = np.around((last_y - last_x), decimals=2)
        else:

            if last_x == last_y:
                degree = 0
                chevau = 0
            else:
                degree = 1
                chevau = 1
            for i in range(1,len(time_intervals)):
                if last_x != last_y:
                    b = False
                x,y = time_intervals[i]
                #it should be enough to check one bound no overlap in linkq in fragmented link streams but maybe its ok to generalise it and make it work whenvever later on, update : false, [1,2],[1,1]
                if x == last_x and y == last_y and chevau > 0:
                    degree += 1
                    chevau += 1
                else:
                    somme += np.around((last_y - last_x)/np.math.factorial(chevau), decimals=2) 
                    if x != y:
                        chevau = 1
                        degree += 1
                    else:
                        chevau = 0
                    last_x = x
                    last_y = y
        if b == True:
            res[0] = 1
        else:
            res[degree] = somme
        res = [np.around(e,decimals=2) for e in res]
        return nppol.Polynomial(res)

    def merge_meta_paths(self, m2, stream):
        if m2.nodes[0] != self.nodes[-1]:
            #error
            return Metawalk([],[])
        else:
            return Metawalk(self.nodes + m2.nodes[1:],self.time_intervals + m2.time_intervals[1:])




    def passes_through(self,t,v):

        if v in self.nodes:
            indice = self.nodes.index(v)
        else:
            return False
        if indice == 0:
            if t < self.time_intervals[0][0]:
                return True
            else:
                return False
        elif indice == len(self.nodes) -1:
            if t >= self.time_intervals[-1][1]:
                return True
            else:
                return False
        else:
            if t >= self.time_intervals[indice-1][1] and t < self.time_intervals[indice][0]:
                return True
            else:
                return False

    def passes_through_whole_interval(self,v,t1,t2):
        return False

    def passes_through_somewhere_interval(self,v,t1,t2):
        #t1 included, but t2 not

        return False
    def add_interval_betweenness(self,t_max,interval_size):
        res = []
        for i in range(0,len(self.time_intervals)-1):
            left_bound = self.time_intervals[i][1]
            right_bound = self.time_intervals[i+1][0]
            nb_interval_contributes_to = (left_bound - right_bound) // interval_size
            fst_interval_left_bound = left_bound // interval_size
            for j in range(1,nb_interval_contributes_to+1):
                res.append((self.nodes[i+1], fst_interval_left_bound, fst_interval_left_bound + j * interval_size ))
                fst_interval_left_bound =  fst_interval_left_bound + j * interval_size
        return res





    def fastest_meta_walk(self):
        if self.time_intervals[0] == self.time_intervals[-1]:
            return self.clone()
        else:
            nodes = self.nodes[:] 
            time_intervals = self.time_intervals[:]
            time_intervals[0] = (time_intervals[0][1],time_intervals[0][1])
            time_intervals[-1] = (time_intervals[-1][0],time_intervals[-1][0])
            for i in range(1,len(time_intervals)):
                if time_intervals[i][0] < time_intervals[0][0]:
                    time_intervals[i] = (time_intervals[0][0],time_intervals[i][1])
                if time_intervals[i][1] > time_intervals[-1][1]:
                    time_intervals[i] = (time_intervals[i][0],time_intervals[-1][1])

        return Metawalk(time_intervals,nodes)



    def first_time(self):
        return self.time_intervals[0][0]

    def last_departure(self):
        return self.time_intervals[0][1]

    def first_arrival(self):
        return self.time_intervals[-1][0]

    def first_node(self):
        return self.nodes[0]
    def last_node(self):
        return self.nodes[-1]

    

    def plot(self, S, color="#18036f",
             markersize=10, dag=False, fig=None):
        """
        Draw a path on the ``StreamGraph`` object *S*

        :param S:
        :param color:
        :param markersize:
        :param dag:
        :param fig:
        :return:
        """
        if fig is None:
            fig, ax = plt.subplots()
        else:
            ax = plt.gca()

        if dag:
            dag = S.condensation_dag()
            dag.plot(node_to_label=S.node_to_label, ax=ax)
        else:
            S.plot(ax=ax)

        # Plot Source
        id_source = S.nodes.index(self.nodes[0])
        plt.plot([self.time_intervals[0]], [id_source], color=color,
                 marker='o', alpha=0.8, markersize=markersize)
        # Plot Destination
        id_destination = S.nodes.index(self.nodes[-1])
        plt.plot([self.time_intervals[-1]], [id_destination], color=color,
                 marker='o', alpha=0.8, markersize=markersize)
        # Plot Path
        for i in range(self.length()):
            l = self.nodes[i]
            l2 = self.nodes[i+1]

            t = self.time_intervals[i][0]
            t2 = self.time_intervals[i][1]
            id1 = S.nodes.index(l)
            id2 = S.nodes.index(l2)
            idmax = max(id1, id2)
            idmin = min(id1, id2)

            # verts = [
            #     (idmin, t),  # left, bottom
            #     (idmax, t),  # left, top
            #     (idmax, t2),  # right, top
            #     (idmin, t2),  # right, bottom
            # ]



            plt.vlines(t, ymin=idmin, ymax=idmax, linewidth=6, alpha=0.8, color=color)
            plt.vlines(t2, ymin=idmin, ymax=idmax, linewidth=6, alpha=0.8, color=color)
            if i != self.length() - 1:
                plt.hlines(id2, xmin=t, xmax=t2,
                           linewidth=4, alpha=0.8, color=color)
                plt.hlines(id1, xmin=t, xmax=t2,
                           linewidth=4, alpha=0.8, color=color)
                # Plot marker
                # if t != self.times[i + 1]:
                #     plt.plot([t], [id2], color=color,
                #              marker='>', alpha=0.8, markersize=markersize)
            # if i != 0 and (t, id1) != (self.times[0], id_source) != (self.times[-1], id_destination):
            #     # Plot marker
            #     if id1 == idmin:
            #         plt.plot([t], [id1], color=color,
            #                  marker='^', alpha=0.8, markersize=markersize)
            #     else:
            #         plt.plot([t], [id1], color=color,
            #                  marker='v', alpha=0.8, markersize=markersize)
        plt.tight_layout()
        return fig

    def check_coherence(self, S):
        for i in range(self.length()):
            l = (self.nodes[i],self.nodes[i+1])
            inter = self.time_intervals[i]
            l_ = (self.nodes[i+1],self.nodes[i])  # Inverse the order of the interval
            if l not in S.links and l_ not in S.links:
                raise ValueError("Link : " + str(l) + " does not exists in the Stream Graph !")
            else:
                t = inter[0]
                t2 = inter[1]
                if l in S.links:
                    id_link = S.links.index(l)
                else:
                    id_link = S.links.index(l_)
                is_present = False
                for lt0, lt1 in zip(S.link_presence[id_link][::2], S.link_presence[id_link][1::2]):
                    if (lt0 <= t <= lt1) and (lt0 <= t2 <= lt1) and (t <= t2):
                        is_present = True
                if not is_present:
                    raise ValueError("Link : " + str(l) + " does not exists at time " + str(t) + " !")
        print("Check Path Coherence ok !")
        return

    def co_sfp(m, t, cons):
        if m.is_none():
            return np.Infinity
        if m.is_empty():
            return 0.0
        return cons * (t - m.last_departure()) + m.length()

    def co_first_arrival(m, t, cons):
        if m.is_none():
            return np.Infinity
        if m.is_empty():
            return 0.0
        return m.first_arrival()

    def co_short(m, t, cons):
        if m.is_none():
            return np.Infinity
        return m.length()

    def co_duration(m, t, cons):
        if m.is_none():
            return np.Infinity
        if m.is_empty():
            return 0.0
        return m.first_arrival() - m.last_departure()
