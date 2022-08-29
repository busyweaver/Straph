#%autoindent
import sys
import os
sys.path.append(os.path.abspath("Lib/"))
from lslib import read_link_stream
from vsplib import VSP

if len(sys.argv) != 6:
	sys.stderr.write("Computes the volume of shortest paths between two temporal nodes in a link stream.\n")
	sys.stderr.write("Usage: %s i u j v < ls.dat\n"%sys.argv[0])
	sys.stderr.write("where ls.dat is a file descrition of a link stream L=(T,V,E),\n")
        sys.stderr.write("u and v are two nodes in V, and i and j are two timestamps in T.\n")
	sys.exit(-1)

i = float(sys.argv[1])
u = sys.argv[2]
j = float(sys.argv[3])
v = sys.argv[4]

L = read_link_stream(open(sys.argv[5]))
assert i<=L.omega and i>=L.alpha
assert j<=L.omega and j>=L.alpha
assert u in L.V and v in L.V

sys.stderr.write("VSP (%g,%s) -> (%g,%s): "%(i,u,j,v))
sys.stderr.flush()
vol = VSP(L,(i,u),(j,v))
sys.stderr.write("(%g,%d)\n"%vol)
sys.stdout.write("(%g,%d)\n"%vol)

