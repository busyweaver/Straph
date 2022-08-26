#%autoindent
import sys
import os
import pickle
path = sys.argv[0]
s = "".join(path.split("/")[0:-1]) + "/"
sys.path.append(os.path.abspath(s+"Lib/"))
from betweennesslib import Betweenness
from betweennesslib import contri_point
from lslib import read_link_stream

if len(sys.argv)!=5:
	sys.stderr.write("Usage: %s input_file \n"%(sys.argv[0]))
	sys.stderr.write("where input_file describes a link stream L=(T,V,E), t is a time in T and v a node in V.\n")
	sys.stderr.write("Output: the betweenness L.\n")
	sys.exit()
name = sys.argv[4]
print("filename", name)
L = read_link_stream(open(s + sys.argv[1]))
v = sys.argv[3]
L = read_link_stream(open(s + sys.argv[1]))
nb_points = float(sys.argv[2])
if nb_points == -1:
    times = [t for t in L.eventtimes]
    times = [L.alpha] + times + [L.omega]
else:
    increment = (L.omega-L.alpha)/nb_points
    times = [L.alpha + i*increment for i in range(nb_points)]
res = {e:dict()  for e in L.V }

for e in L.V:
	print("lol")
	for t in times:
		print("wech")
		res[e][t] = contri_point(L,(t,e),v)


for e in L.V:
	for t in times:
		sys.stdout.write("%s %g  %g\n"%(e,t,res[e][t]))

with open(name+"_contri.pic", 'wb') as handle:
    pickle.dump(res, handle)
