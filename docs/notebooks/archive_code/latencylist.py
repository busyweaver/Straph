#%autoindent
import sys
import os
import pickle
path = sys.argv[0]
s = "".join(path.split("/")[0:-1])
# print(s)
if s != "":
    s = s + "/"
sys.path.append(os.path.abspath(s+"Lib/"))
from lslib import read_link_stream
from latencylib import Latency_lists
from betweennesslib import PrevList, NextList


def cond(l,v,lat_other):
    res = []
    for e in l:
        if e[0] in lat_other:
            res.append(lat_other[e[0]])
        else:
            res.append(e[0])
    return res

if len(sys.argv)!=4:
	sys.stderr.write("Usage: %s u < ls.dat\n"%sys.argv[0])
	sys.exit(-1)
u = sys.argv[1]
name = sys.argv[3]
L = read_link_stream(open(s + sys.argv[2]))
# print(L.alpha,L.omega)
prev_next = dict()
LL = Latency_lists(L,u)
lat_other = dict()
for v in LL:
    lat_other[v] = dict()
    for e in LL[v]:
        x,y = e
        lat_other[v][x] = y

for v in L.V:
    for x,y in LL[v]:
        # print(u,v,x,y)
        res1 = PrevList(L,u,v,(x,y),LL[v])
        # print(lat_other[v], LL[v])
        # print("res1", res1)
        res1 = cond(res1,v,lat_other[v])
        res1.reverse()
        if res1 == []:
            res1 = [x]
        # print("res1 after", res1)
        res2 = NextList(L,u,v,(x,y),LL[v])
        # print("res2", res2)
        res2 = list(map(lambda x:x[0], res2))
        if res2 == []:
            res2 = [y]
        # print("res2 after", res2)
        res = res1 + res2
        # res = []
        # for i in range(0, max(len(res1),len(res2))):
        #     if i >= len(res1):
        #         res.append([L.alpha,res2[i][0]])
        #     elif i >= len(res2):
        #         res.append([res1[i][0],L.omega])
        #     else:
        #         res.append([res1[i][0],res2[i][0]])
        prev_next[(u,v,x,y)] = res

with open(s+name+"_latency_prev_next.pic", 'wb') as handle:
    pickle.dump(prev_next, handle)

