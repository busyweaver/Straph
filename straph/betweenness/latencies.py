import numpy

def cur_best_to_array(s, cur_best, ev, ev_rev):
    cur_b_arr = [ [0 for t in ev    ]   for k in s.nodes]
    for v in s.nodes:
        for t in cur_best[v]:
            cur_b_arr[v][ev_rev[t]] = (t,cur_best[v][t][0],cur_best[v][t][1])
    return cur_b_arr

def latencies(s, cur_b_arr, ev, ev_rev):
    latencies = [ [0 for t in ev    ]   for k in s.nodes]
    last_depr = [ [numpy.Infinity for t in ev    ]   for k in s.nodes]
    for k in s.nodes:
        for i in range(0,len(cur_b_arr[k])):
            if cur_b_arr[k][i][1] != -numpy.Infinity:
                if latencies[k][ev_rev[cur_b_arr[k][i][1]]] == 0:
                    latencies[k][ev_rev[cur_b_arr[k][i][1]]] = (cur_b_arr[k][i][0],cur_b_arr[k][i][2])
                if last_depr[k][ev_rev[cur_b_arr[k][i][1]]] == numpy.Infinity:
                    last_depr[k][ev_rev[cur_b_arr[k][i][1]]] = cur_b_arr[k][i][0]
                else:
                    #we already have one element for the departure
                    if last_depr[k][ev_rev[cur_b_arr[k][i][1]]] > cur_b_arr[k][i][0]:
                        last_depr[k][ev_rev[cur_b_arr[k][i][1]]] = cur_b_arr[k][i][0]
                        #print("i",i,"cur_b_arr[k][i][0]",cur_b_arr[k][i][0],"ev_rev[cur_b_arr[k][i][1]]",ev_rev[cur_b_arr[k][i][1]])
                        latencies[k][ev_rev[cur_b_arr[k][i][1]]] = (cur_b_arr[k][i][0],cur_b_arr[k][i][2])

    return latencies

def latencies_without_0_and_rev(s, lat, ev):
    latency = [[] for k in s.nodes]
    latency_rev = [[] for k in s.nodes]
    for k in s.nodes:
        for i in range(0,len(ev)):
            if lat[k][i] != 0:
                latency[k].append([ev[i],lat[k][i][0], lat[k][i][1]])
                latency_rev[k].append([ lat[k][i][0],ev[i],lat[k][i][1] ])
    return latency, latency_rev

def cur_best_to_array_edge(s, cur_best, ev, ev_rev):
    cur_b_arr = [ [0 for t in ev    ]   for k in s.nodes]
    for v in s.nodes:
        for t in cur_best[v]:
            cur_b_arr[v][ev_rev[t]] = (t,cur_best[v][t][1][0],cur_best[v][t][1][1])
    return cur_b_arr
