from straph.betweenness import volumes as vol
import straph.betweenness as bt
import straph.paths.meta_walks as mw
import numpy as np
import seaborn as sns
import matplotlib.pylab as plt
import pandas as pd
import time
import pickle
import networkx as nx

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
    sigma_r = dict()
    latency = dict()
    prev_next = dict()
    contri = dict()
    before = dict()
    after = dict()
    deltasvvt = dict()
    no_succ = dict()
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
        # print(node)
        start_time = time.time()
        pre, cur_best = bt.dijkstra_directed(nouveau, node, events, events_reverse, neighbors, link_ind, neighbors_inv, unt)
        cur_b_arr = bt. cur_best_to_array(nouveau, cur_best, events, events_reverse)
        lat = bt.latencies(nouveau, cur_b_arr, events, events_reverse)
        lat_triplet, lat_rev_triplet = bt.latencies_without_0_and_rev(nouveau, lat, events)
        latency[node] = lat_triplet
        G = bt.predecessor_graph(nouveau, pre,node)
        no_succ[node] = list(filter(lambda x: len(G.successors(x))==0 ,G.nodes()))
        GG = bt.graph_to_ordered(G, events, events_reverse)
        preced = bt.preced_node(nouveau, G,events,events_reverse)
        Gp = bt.instant_graphs(G)
        GT = bt.interval_graph(Gp)
        edge = bt.edges(nouveau)
        before[node], after[node] = bt.volume_instantenuous(nouveau, G, events, events_reverse, edge)
        mx = bt.max_volume_superposition(GT)
        sigma = bt.volume_metapaths_at_t(G, node, cur_best, mx)
        f_edge = bt.dictionary_first_edge(G, cur_best)
        sigma_r[node] = bt.optimal_with_resting_con(nouveau, node, f_edge, events, G, sigma, cur_best, unt)
        contri[node], prev_next[node] = bt.contribution_each_latency_con(nouveau, lat_rev_triplet,events[0],events[len(events)-1], before[node], after[node])
        latence_arrival = {v : { y: [x,z] for (x,y,z) in lat_triplet[v] }  for v in nouveau.nodes }
        latence_depar = {v : { x : [y,z] for (x,y,z) in lat_triplet[v] }  for v in nouveau.nodes }
        deltasvvt[node] = bt.dictionary_svvt(G, node, latence_arrival, contri[node], prev_next[node], sigma_r[node],  latence_depar)
        contribution = bt.general_contribution_from_node(s, G, node, GG, sigma_r[node], deltasvvt[node], events, events_reverse, pre, GT, unt, preced)
        general_contri[node] = contribution
        update_betweenness(nouveau, contribution, betweenness, events)
        end_time = time.time()
        features[node] = [end_time - start_time, len(list(G.nodes())), mx, len(lat_triplet)]
    normalize(nouveau, betweenness, events)
    return betweenness, general_contri, nouveau, events, sigma_r,latency,prev_next, contri, before, after, deltasvvt,no_succ ,features

def simulations(s, name):
    bet, general_contri, nouveau, events, sigma_r, latency, prev_next, contri, before, after, deltasvvt, no_succ, features = betweenness_all(s)
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
    df_cm = pd.DataFrame(a, index = [v for v in deg_increa], columns = [t for t in events])
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






################################ for discrete temporal graphs generic ################################

def initialization_dis_gen(s, events, betweenness):
    for v in s.nodes:
        if s.node_to_label:
            betweenness[s.node_to_label[v]] = dict()
        else:
            betweenness[v] = dict()
        for t in events:
            if s.node_to_label:
                betweenness[s.node_to_label[v]][t] = 0.0
            else:
                betweenness[v][t] = 0.0


def optimal_paths_resting_type(s, node, events, G, sigma, cur_best, node_inf, opt_walk, cost, n, walk_type):
    if walk_type == "active":
        sigma_r = bt.optimal_with_resting_dis_gen(s, node, events, G, sigma, cur_best, node_inf, opt_walk, cost, n)
    else:
        sigma_r = dict()
        for e in sigma.keys():
            sigma_r[e] = sigma[e]
    return sigma_r

def remove_infinite_from_predecessor_dis_gen(s, G, events, events_reverse, opt_walk, cur_best, fun, n):
    inf_scc = []
    scc = nx.kosaraju_strongly_connected_components(G.graph)
    for s in scc:
        if len(s) > 1:
            inf_scc.append(list(s))
    H = nx.condensation(G.graph)
    y = H.nodes.data()
    for s in H:
        if len(list(y[s]["members"])) == 1:
            continue
        for e in nx.bfs_successors(H, s):
            for ee in e[1]:
                inf_scc.append(list(y[ee]["members"]))
    temp_inf = set()
    for s in inf_scc:
        for v in s:
            temp_inf.add(v)
    for v in temp_inf:
        G.graph.remove_node(v)
    clos_inf = bt.infinite_closure(s, G, events, events_reverse, temp_inf, opt_walk, cur_best, fun, n)
    node_inf = temp_inf.union(clos_inf)
    return node_inf

def exact_betweenness_dis_gen(s, betweenness, general_contri, deltasvvt):
    exact_between = dict()
    for v in s.nodes:
        if s.node_to_label:
            exact_between[s.node_to_label[v]] = dict()
        else:
            exact_between[v] = dict()
    for v in s.nodes:
        if s.node_to_label:
            for t in betweenness[s.node_to_label[v]].keys():
                exact_between[s.node_to_label[v]][t] = betweenness[s.node_to_label[v]][t] - general_contri[v][v][t] - sum( deltasvvt[w][(v,t)] for w in s.nodes    )
        else:
            for t in betweenness[v].keys():
                exact_between[v][t] = betweenness[v][t] - general_contri[v][v][t] - sum( deltasvvt[w][(v,t)] for w in s.nodes    )
    return exact_between


def betweenness_all_dis_gen(s, b, fun, walk_type, approx = -1):
    features = dict()
    general_contri = dict()
    betweenness = dict()
    deltasvvt = dict()
    events, events_reverse = events_dic(s)
    initialization_dis_gen(s, events, betweenness)
    neighbors, neighbors_inv = bt.neighbors_direct(s)
    if approx == -1:
        to_visit = s.nodes
    else:
        lis = list(s.nodes)
        to_visit = random.sample(lis, approx)
    for node in to_visit:
        #print(node)
        start_time = time.time()
        pre, cur_best, opt_walk = bt.dijkstra_directed_dis_gen(s, node, events, events_reverse, neighbors, neighbors_inv, b, fun, walk_type)
        G = bt.predecessor_graph_dis_gen(s, pre,node)
        preced = bt.preced_node(s, G,events,events_reverse)
        node_inf = bt.remove_infinite_from_predecessor_dis_gen(s, G, events, events_reverse, opt_walk, cur_best, mw.Metawalk.co_short, len(s.nodes))
        GG = bt.graph_to_ordered(G, events, events_reverse)
        sigma = bt.volume_metapaths_at_dis_gen(G, node, s.alpha)
        #print("sigma",sigma)
        bt.sigma_infinite(sigma, node_inf)
        sigma_r = optimal_paths_resting_type(s, node, events, G, sigma, cur_best, node_inf, opt_walk, mw.Metawalk.co_short, len(s.nodes), walk_type)
        sigma_tot, min_values, sigma_tot_t = bt.sigma_total_dis_gen(sigma, s, cur_best, node, events, walk_type)
        #print("sigmatot", sigma_tot)
        sigma_tot_r = bt.complete_sigma_tot_t(s, sigma_tot_t, node_inf, events, node, walk_type)
        deltasvvt[node] = bt.dictionary_svvt_dis_gen(s, node, sigma_tot_r,min_values, cur_best, sigma_tot, events)
        general_contri[node] = bt.general_contribution_from_node_dis_gen(s, G, node, GG, sigma_r, deltasvvt[node], events, events_reverse, pre, preced, walk_type)
        update_betweenness(s, general_contri[node], betweenness, events)
        end_time = time.time()
        features[node] = [end_time - start_time]
    exact_between = exact_betweenness_dis_gen(s, betweenness, general_contri, deltasvvt)
    return exact_between, betweenness ,features

def simulations_dis_gen(s, name):
    exact_between, betweenness, general_contri, deltasvvt ,features = betweenness_all_dis_gen(s)
    #write_betweenness(bet, s, events, name)
    with open(name+"_betweenness.pic", 'wb') as handle:
        pickle.dump(exact_between, handle)
    with open(name+"_features.pic", 'wb') as handle:
        pickle.dump(features, handle)

