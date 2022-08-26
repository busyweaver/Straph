#%autoindent
import sys
import os
import pickle

path = sys.argv[0]
s = "".join(path.split("/")[0:-1]) + "/"
sys.path.append(os.path.abspath(s+"Lib/"))
from betweennesslib import Betweenness
from lslib import read_link_stream

if len(sys.argv)!=4:
	sys.stderr.write("Usage: %s input_file n\n"%(sys.argv[0]))
	sys.stderr.write("where input_file describes a link stream L=(T,V,E) and n gives the number of time points per node.\n")
	sys.stderr.write("Output: a line of the form t v b for each v in V and each time t in T with timestep |T|/n, with b the betweenness of (t,v) in L.\n")
	sys.exit()

L = read_link_stream(open(s + sys.argv[1]))
nb_points = float(sys.argv[2])
name = sys.argv[3]
if nb_points == -1:
    times = [t for t in L.eventtimes]
    times = [L.alpha] + times + [L.omega]
else:
    increment = (L.omega-L.alpha)/nb_points
    times = [L.alpha + i*increment for i in range(nb_points)]
print(times)
b = dict()
for v in L.V:
    b[v] = dict()
    for t in times:
        b[v][t] = 0
for v in sorted(L.V):
    t = L.alpha
    for t in times:
	#while t <= L.omega:
		b[v][t] = Betweenness(L,(t,v))
               	#sys.stdout.write("%g %s %g\n"%(t,v,b))
               	#sys.stdout.flush()
with open(name+"_betweenness.pic", 'wb') as handle:
    pickle.dump(b, handle)
		#last_t = t
		#t += increment
#	if str(last_t)!=str(L.omega):
#		t = L.omega
#		b = Betweenness(L,(t,v))
#               	sys.stdout.write("%g %s %g\n"%(t,v,b))
#               	sys.stdout.flush()

