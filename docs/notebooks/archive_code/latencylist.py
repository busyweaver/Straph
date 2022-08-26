#%autoindent
import sys
import os
sys.path.append(os.path.abspath("Lib/"))
from lslib import read_link_stream
from latencylib import Latency_lists

if len(sys.argv)!=2:
	sys.stderr.write("Usage: %s u < ls.dat\n"%sys.argv[0])
	sys.exit(-1)
u = sys.argv[1]

L = read_link_stream(sys.stdin)

LL = Latency_lists(L,u)
for v in sorted(LL):
	print u,v,':',LL[v]
sys.exit()

