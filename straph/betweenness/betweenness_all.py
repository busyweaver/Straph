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
import random
import operator
import straph.paths.meta_walks as mw

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
    G = dict()
    cur_best = dict()
    pre = dict()
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
        pre[node], cur_best[node] = bt.dijkstra_directed(nouveau, node, events, events_reverse, neighbors, link_ind, neighbors_inv, unt)
        cur_b_arr = bt. cur_best_to_array(nouveau, cur_best[node], events, events_reverse)
        lat = bt.latencies(nouveau, cur_b_arr, events, events_reverse)
        lat_triplet, lat_rev_triplet = bt.latencies_without_0_and_rev(nouveau, lat, events)
        latency[node] = lat_triplet
        G[node] = bt.predecessor_graph(nouveau, pre[node],node)
        no_succ[node] = list(filter(lambda x: len(G[node].successors(x))==0 ,G[node].nodes()))
        GG = bt.graph_to_ordered(G[node], events, events_reverse)
        preced = bt.preced_node(nouveau, G[node],events,events_reverse)
        Gp = bt.instant_graphs(G[node])
        GT = bt.interval_graph(Gp)
        edge = bt.edges(nouveau)
        before[node], after[node] = bt.volume_instantenuous(nouveau, G[node], events, events_reverse, edge)
        before[node] = {v: {t:False for t in events} for v in s.nodes }
        after[node] = {v: {t:False for t in events} for v in s.nodes } 
        mx = bt.max_volume_superposition(GT)
        sigma = bt.volume_metapaths_at_t(G[node], node, cur_best[node], mx)
        f_edge = bt.dictionary_first_edge(G[node], cur_best[node])
        sigma_r[node] = bt.optimal_with_resting_con(nouveau, node, f_edge, events, G[node], sigma, cur_best[node], unt)
        print("instant bef",before)
        print("instant aft",after)
        print("node contri", node)
        contri[node], prev_next[node] = bt.contribution_each_latency_con(nouveau, lat_rev_triplet,events[0],events[len(events)-1], before[node], after[node])
        latence_arrival = {v : { y: [x,z] for (x,y,z) in lat_triplet[v] }  for v in nouveau.nodes }
        latence_depar = {v : { x : [y,z] for (x,y,z) in lat_triplet[v] }  for v in nouveau.nodes }
        deltasvvt[node] = bt.dictionary_svvt(G[node], node, latence_arrival, contri[node], prev_next[node], sigma_r[node],  latence_depar)
        contribution = bt.general_contribution_from_node(s, G[node], node, GG, sigma_r[node], deltasvvt[node], events, events_reverse, pre[node], GT, unt, preced)
        general_contri[node] = contribution
        update_betweenness(nouveau, contribution[0], betweenness, events)
        end_time = time.time()
        features[node] = [end_time - start_time, len(list(G[node].nodes())), mx, len(lat_triplet)]
    normalize(nouveau, betweenness, events)
    return betweenness, general_contri, nouveau, events, sigma_r,latency,prev_next, contri, before, after, deltasvvt,no_succ ,features, G, cur_best, pre

def simulations(s, name):
    bet, general_contri, nouveau, events, sigma_r, latency, prev_next, contri, before, after, deltasvvt, no_succ, features, G, cur_best, pre = betweenness_all(s)
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

def heatmap_betweenness(s, bet, deg_increa, square = True):
    events, events_reverse = events_dic(s)
    # d = s.degrees()
    # deg_increa = list(map( lambda x : (d[x], x) , list(d) ))
    # deg_increa.sort()
    # deg_increa.reverse()
    l = [ [ bet[y][t] for t in events ] for y in deg_increa  ]
    a = np.matrix(l)
    df_cm = pd.DataFrame(a, index = [v for v in deg_increa], columns = [t for t in events])
    ax = sns.heatmap(df_cm,cmap="YlGnBu",square = square , cbar_kws={"shrink": 0.6})
    return ax

def aggregated_time_betweenness(s, bet, d, square = True):
    events, events_reverse = events_dic(s)
    # d = s.degrees()
    # deg_increa = list(map( lambda x : (d[x], x) , list(d) ))
    # deg_increa.sort()
    # deg_increa.reverse()
    l =  [ [ sum(bet[d[y]][t] for y in s.nodes) for t in events]  for j in range(1) ]
    a = np.matrix(l)
    df_cm = pd.DataFrame(a,  index = ["aggregated nodes"], columns = [t for t in events])
    ax = sns.heatmap(df_cm,cmap="YlGnBu",square = square, cbar_kws={"shrink": 0.6})
    return ax

def aggregated_node_betweenness(s, bet, d, square = True,):
    events, events_reverse = events_dic(s)
    # d = s.degrees()
    # deg_increa = list(map( lambda x : (d[x], x) , list(d) ))
    # deg_increa.sort()
    # deg_increa.reverse()
    l = [  [sum( bet[d[y]][t] for t in events) for j in range(1)]   for y in s.nodes  ]

    a = np.matrix(l)
    df_cm = pd.DataFrame(a,  index = [v for v in d], columns = ["aggregated times"])
    ax = sns.heatmap(df_cm,cmap="YlGnBu",square = square, cbar_kws={"shrink": 0.6})
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

def remove_infinite_from_predecessor_dis_gen(s, G, events, events_reverse, opt_walk, cur_best, fun, n, walk_type, b):
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
    if walk_type == "active":
        clos_inf = bt.infinite_closure(s, events, events_reverse, temp_inf, opt_walk, cur_best, fun, n, b)
    else:
        clos_inf = {}
    #node_inf = temp_inf.union(clos_inf)
    return temp_inf, clos_inf

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
    link_ind = bt.link_index(s)
    neighbors, neighbors_inv = bt.neighbors_direct(s)
    if approx == -1:
        to_visit = s.nodes
    else:
        lis = list(s.nodes)
        to_visit = random.sample(lis, approx)
    for node in to_visit:
        print(node, "out of", len(s.nodes))
        start_time = time.time()
        s_time = time.time()
        pre, cur_best, opt_walk = bt.dijkstra_directed_dis_gen(s, node, events, events_reverse, neighbors, neighbors_inv, link_ind, b, fun, walk_type)
        e_time = time.time()
        print("finish optimal paths", (e_time - s_time)/60)
        s_time = time.time()
        G = bt.predecessor_graph_dis_gen(s, pre,node)
        preced = bt.preced_node(s, G,events,events_reverse)
        e_time = time.time()
        print("finish predecessor", (e_time - s_time)/60, "size pred", len(G.nodes()))
        s_time = time.time()
        node_inf, clos_inf = bt.remove_infinite_from_predecessor_dis_gen(s, G, events, events_reverse, opt_walk, cur_best, fun, len(s.nodes), walk_type, b)
        GG = bt.graph_to_ordered(G, events, events_reverse)
        e_time = time.time()
        print("remove and ordrered", (e_time - s_time)/60, "new size", len(G.nodes()))
        sigma = bt.volume_metapaths_at_dis_gen(G, node)
        #print("sigma",sigma)
        bt.sigma_infinite(sigma, node_inf)
        print("finish sigma")
        s_time = time.time()
        sigma_tot, min_values, sigma_tot_t = bt.sigma_total_dis_gen(sigma, s, cur_best, node, events)
        #print("sigmatot", sigma_tot)
        sigma_tot_r = bt.complete_sigma_tot_t(s, sigma_tot_t, node_inf, events, node)
        node_inf = node_inf.union(clos_inf)
        sigma_r = optimal_paths_resting_type(s, node, events, G, sigma, cur_best, node_inf, opt_walk, fun, len(s.nodes), walk_type)
        e_time = time.time()
        print("finish sigma_r, sigma_tot", (e_time - s_time)/60)
        deltasvvt[node] = bt.dictionary_svvt_dis_gen(s, node, sigma_tot_r,min_values, cur_best, sigma_tot, events)
        print("finish delta")
        s_time = time.time()
        general_contri[node] = bt.general_contribution_from_node_dis_gen(s, G, node, GG, sigma_r, deltasvvt[node], events, events_reverse, pre, preced, walk_type)
        e_time = time.time()
        print("finish contribution", (e_time - s_time)/60)
        update_betweenness(s, general_contri[node], betweenness, events)
        end_time = time.time()
        features[node] = [end_time - start_time]
    if approx == -1:
        exact_between = exact_betweenness_dis_gen(s, betweenness, general_contri, deltasvvt)
    else:
        exact_between = {}
    return exact_between, betweenness ,features, general_contri

def simulations_dis_gen(s, name, b, fun, walk_type, approx = -1):
    exact_between, betweenness, features, general_contri = betweenness_all_dis_gen(s, b, fun, walk_type, approx)
    #write_betweenness(bet, s, events, name)
    with open(name+"_betweenness.pic", 'wb') as handle:
        pickle.dump(betweenness, handle)
    with open(name+"_exact_betweenness.pic", 'wb') as handle:
        pickle.dump(exact_between, handle)
    with open(name+"_features.pic", 'wb') as handle:
        pickle.dump(features, handle)


def computation_betweenness_many_optimal_dis_gen(s, name, approx = -1):
    walk_type = ["active", "passive"]
    fun_list = [["sfp" , mw.Metawalk.co_sfp], ["short" , mw.Metawalk.co_short], ["foremost" , mw.Metawalk.co_first_arrival]]
    b = operator.lt
    for wa in walk_type:
        for fun in fun_list:
            simulations_dis_gen(s, name + "_" + wa + "_" + fun[0], b, fun[1], wa, approx)











