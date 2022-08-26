#%autoindent
import sys
import os
path = sys.argv[0]
s = "".join(path.split("/")[0:-1])
print(s)
if s != "":
    s = "/"+s
sys.path.append(os.path.abspath(s+"Lib/"))
from betweennesslib import Betweenness
from lslib import read_link_stream

if len(sys.argv)!=4:
	sys.stderr.write("Usage: %s input_file t v\n"%(sys.argv[0]))
	sys.stderr.write("where input_file describes a link stream L=(T,V,E), t is a time in T and v a node in V.\n")
	sys.stderr.write("Output: the betweenness of (t,v) in L.\n")
	sys.exit()

L = read_link_stream(open(s + sys.argv[1]))
t = float(sys.argv[2])
v = sys.argv[3]

if t not in L.eventtimes:
	T = [x for x in L.eventtimes if x<t] + [t] + [x for x in L.eventtimes if x>t]
	L.eventtimes = T
b = Betweenness(L,(t,v))
sys.stdout.write("%g %s %g\n"%(t,v,b))

