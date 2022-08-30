#%autoindent
import sys
import os
import pickle
path = sys.argv[0]
s = "".join(path.split("/")[0:-1])
if s != "":
    s = s + "/"
# print(s)
sys.path.append(os.path.abspath(s+"Lib/"))
from betweennesslib import Betweenness
from lslib import read_link_stream
from betweennesslib import Betweenness_contri
if len(sys.argv)!=5:
	sys.stderr.write("Usage: %s input_file t v\n"%(sys.argv[0]))
	sys.stderr.write("where input_file describes a link stream L=(T,V,E), t is a time in T and v a node in V.\n")
	sys.stderr.write("Output: the betweenness of (t,v) in L.\n")
	sys.exit()
# print(s + sys.argv[3])
L = read_link_stream(open(s + sys.argv[3]))
print("============>", L.alpha, L.omega)
# print("nodes", L.V)
t = float(sys.argv[1])
v = sys.argv[2]
name = sys.argv[4]

if t not in L.eventtimes:
	T = [x for x in L.eventtimes if x<t] + [t] + [x for x in L.eventtimes if x>t]
	L.eventtimes = T
b, contri = Betweenness_contri(L,(t,v))
sys.stdout.write("%g %s %g\n"%(t,v,b))

with open(s+name+"_contri_point.pic", 'wb') as handle:
    pickle.dump(contri, handle)
