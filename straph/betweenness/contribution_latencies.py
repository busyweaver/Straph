from straph.betweenness import volumes as vol

def cal_lat(arr,latencies):
    return latencies[arr][0] - latencies[arr][1]


def check_contri( j, i,latencies, node, instant_before, instant_after):
    lati = (cal_lat(i,latencies),latencies[i][2])
    latj = (cal_lat(j,latencies),latencies[j][2])

    if instant_before[latencies[i][0]] and j == i-1:
        # latencies are instantenous
        return 2

    if instant_after[latencies[i][0]] and j == i+1:
        return 2

    if latj < lati:
        return 1
    elif latj == lati:
        if lati[0] == 0:
            if j < i and instant_before[latencies[j][0]]:
                return 1
            #a verifier quand meme
            if j > i and instant_after[latencies[j][1]]:
                return 1
        return 0
    else:
        return -1

def contribution_each_latency_con(s, latencies, mini, maxi, instant_before, instant_after):
    #        contri = [dict() for i in range(len(self.nodes))]
    contri = [dict() for i in range(len(s.nodes))]
    prev_next = [dict() for i in range(len(s.nodes))]
    for k in s.nodes:
        # l contains first arrival times
        #l = [e for e in latencies[k].keys() ]
        #l.sort()
        l = [x for (x,y,z) in latencies[k] ]
        for i in range(0,len(l)):
            #check left contribution
            j = i - 1
            S = mini
            b = True
            while(j >= 0 and b):
                #cond = self.check_contri_dis(l[j], l[i], latencies[k], k)
                cond = check_contri(j, i, latencies[k],  k, instant_before[k], instant_after[k])
                print(i,j, cond, k, latencies[k])
                if cond == 2:
                    S = latencies[k][i][1]
                    b = False
                if  cond == 1:
                    #S = latencies[k][l[j]][0]
                    S = latencies[k][j][1]
                    b = False
                else:
                    if cond == 0:
                        if l[i] not in prev_next[k]:
                            prev_next[k][l[i]] = [l[j]]
                        else:
                            prev_next[k][l[i]].append(l[j])
                    j = j - 1
            #check right contribution
            j = i + 1
            A = maxi
            b = True
            while(j < len(l) and b):
                #cond = self.check_contri_dis(l[j], l[i], latencies[k], k)
                cond = check_contri(j, i, latencies[k],  k, instant_before[k], instant_after[k])
                if cond == 2:
                    A = l[i]
                    b = False
                if cond == 1:
                    A = l[j]
                    b = False
                else:
                    if cond == 0:
                        if l[i] not in prev_next[k]:
                            prev_next[k][l[i]] = [l[j]]
                        else:
                            prev_next[k][l[i]].append(l[j])
                    j = j + 1
            contri[k][l[i]] = (S,A)
    return contri,prev_next
