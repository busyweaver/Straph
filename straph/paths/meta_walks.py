import matplotlib.pyplot as plt


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

    def add_link(self, l, t):
        self.time_intervals.append(t)
        self.nodes.append(l)

    def length(self):
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
        for i in range(0,self.length()):
            s += " "
            s += str(self.nodes[i])
            s += " "
            s += str(self.time_intervals[i])
        s += " "
        s += str(self.nodes[i+1])
        return s

    def __repr__(self):
        return self.__str__()

    def __eq__(self, m):
        if m.length() != self.length():
            return False
        if (m.nodes == self.nodes) and (m.time_intervals == self.time_intervals):
            return True
        return False

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
