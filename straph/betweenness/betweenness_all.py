from straph.betweenness import volumes as vol
import straph.betweenness as bt
import numpy as np
import seaborn as sns
import matplotlib.pylab as plt
import pandas as pd
import time
import pickle

def events_dic(nouveau):
    events = list(nouveau.event_times())
    events.sort()
    events_reverse = dict()
    for i in range(0,len(events)):
        events_reverse[events[i]] = i
    return events, events_reverse

def initialization(s, events, betweenness):
    for v in s.nodes:
        if s.node_to_label:
            betweenness[s.node_to_label[v]] = dict()
        else:
            betweenness[v] = dict()
        for t in events:
            if s.node_to_label:
                betweenness[s.node_to_label[v]][t] = vol.Volume(0,0)
            else:
                betweenness[v][t] = vol.Volume(0,0)
def update_betweenness(s, contribution, betweenness, events):
    for v in s.nodes:
        if s.node_to_label:
            for t in events:
                betweenness[s.node_to_label[v]][t] += contribution[v][t]
        else:
            for t in events:
                betweenness[v][t] += contribution[v][t]

def normalize(s, betweenness, events):
    for v in s.nodes:
        if s.node_to_label:
            for t in events:
                betweenness[s.node_to_label[v]][t] = betweenness[s.node_to_label[v]][t].norm()
        else:
            for t in events:
                betweenness[v][t] = betweenness[v][t].norm()




def betweenness_all(s, approx = -1):
    features = dict()
    general_contri = dict()
    betweenness = dict()
    nouveau = s.fragmented_stream_graph()
    events, events_reverse = events_dic(nouveau)
    initialization(nouveau, events, betweenness)
    link_ind = bt.link_index(nouveau)
    neighbors, neighbors_inv = bt.neighbors_direct(nouveau)
    unt = bt.until(nouveau, events, events_reverse)
    if approx == -1:
        to_visit = nouveau.nodes
    else:
        lis = list(nouveau.nodes)
        to_visit = random.sample(lis, approx)
    for node in to_visit:
        print(node)
        start_time = time.time()
        pre, cur_best = bt.dijkstra_directed(nouveau, node, events, events_reverse, neighbors, link_ind, neighbors_inv, unt)
        cur_b_arr = bt. cur_best_to_array(nouveau, cur_best, events, events_reverse)
        lat = bt.latencies(nouveau, cur_b_arr, events, events_reverse)
        lat_triplet, lat_rev_triplet = bt.latencies_without_0_and_rev(nouveau, lat, events)
        G = bt.predecessor_graph(nouveau, pre,node)
        GG = bt.graph_to_ordered(G, events, events_reverse)
        Gp = bt.instant_graphs(G)
        GT = bt.interval_graph(Gp)
        edge = bt.edges(nouveau)
        before, after = bt.volume_instantenuous(nouveau, G, events, events_reverse, edge)
        mx = bt.max_volume_superposition(GT)
        sigma = bt.volume_metapaths_at_t(G, node, cur_best, mx)
        f_edge = bt.dictionary_first_edge(G, cur_best)
        sigma_r = bt.optimal_with_resting_con(nouveau, node, f_edge, events, G, sigma, cur_best, unt)
        contri, prev_next = bt.contribution_each_latency_con(nouveau, lat_rev_triplet,events[0],events[len(events)-1], before, after)
        latence_arrival = {v : { y: [x,z] for (x,y,z) in lat_triplet[v] }  for v in nouveau.nodes }
        latence_depar = {v : { x : [y,z] for (x,y,z) in lat_triplet[v] }  for v in nouveau.nodes }
        deltasvvt = bt.dictionary_svvt(G, node, latence_arrival, contri, prev_next, sigma_r,  latence_depar)
        contribution = bt.general_contribution_from_node(s, G, node, GG, sigma_r, deltasvvt, events, events_reverse, pre, GT, unt)
        general_contri[node] = contribution
        update_betweenness(nouveau, contribution, betweenness, events)
        end_time = time.time()
        features[node] = [end_time - start_time, len(list(G.nodes())), mx, len(lat_triplet)]
    normalize(nouveau, betweenness, events)
    return betweenness, general_contri, nouveau, events, features

def simulations(s, name):
    bet, general_contri, nouveau, events, features = betweenness_all(s)
    #write_betweenness(bet, s, events, name)
    with open(name+"_betweenness.pic", 'wb') as handle:
        pickle.dump(bet, handle)
    with open(name+"_features.pic", 'wb') as handle:
        pickle.dump(features, handle)

def read_dictionary(name):
    with open(name, 'rb') as handle:
        b = pickle.loads(handle.read())
    return b


# def write_betweenness(bet, s, events, output_file):
#     with open(output_file + '_betweenness.csv', 'w') as file_output:
#         for v in s.nodes:
#             for t in events:
#                 if s.node_to_label != None:
#                     file_output.write(str(s.node_to_label[v]) + "," + str(t) + "," + str(bet[v][t]), "\n")
#                 else:
#                     file_output.write(str(v),",",str(t),",",str(bet[v][t]), "\n")

def heatmap_betweenness(s, events, bet, deg_increa, square):
    # d = s.degrees()
    # deg_increa = list(map( lambda x : (d[x], x) , list(d) ))
    # deg_increa.sort()
    # deg_increa.reverse()
    l = [ [ bet[y][t] for t in events ] for y in deg_increa  ]
    a = np.matrix(l)
    df_cm = pd.DataFrame(a, index = [s.node_to_label[v] for v in deg_increa], columns = [t for t in events])
    ax = sns.heatmap(df_cm,cmap="YlGnBu",square = square , cbar_kws={"shrink": 0.3})
    return ax

def aggregated_time_betweenness(s, events, bet, deg_increa, square = True):
    # d = s.degrees()
    # deg_increa = list(map( lambda x : (d[x], x) , list(d) ))
    # deg_increa.sort()
    # deg_increa.reverse()
    l =  [ [ sum(bet[y][t] for y in s.nodes) for t in events]  for j in range(1) ]
    a = np.matrix(l)
    df_cm = pd.DataFrame(a,  index = ["aggregated nodes"], columns = [t for t in events])
    ax = sns.heatmap(df_cm,cmap="YlGnBu",square = square, cbar_kws={"shrink": 0.3})
    return ax

def aggregated_node_betweenness(s, events, bet, deg_increa, square = True,):
    # d = s.degrees()
    # deg_increa = list(map( lambda x : (d[x], x) , list(d) ))
    # deg_increa.sort()
    # deg_increa.reverse()
    l = [  [sum( bet[y][t] for t in events) for j in range(1)]   for y in deg_increa  ]

    a = np.matrix(l)
    df_cm = pd.DataFrame(a,  index = [s.node_to_label[v] for v in deg_increa], columns = ["aggregated times"])
    ax = sns.heatmap(df_cm,cmap="YlGnBu",square = square, cbar_kws={"shrink": 0.3})
    return ax











