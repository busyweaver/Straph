import sys
import math

if len(sys.argv)!=2:
	sys.stderr.write("Usage: %s basename\n")
	sys.stderr.write("Reads a link stream in file basename.ls and node weights in basename.val.\n")
	sys.stderr.write("Writes on standard output a python script that produces an xfig visualization of these data.\n")
	exit(1)
basename = sys.argv[1]

mygrey = "#CCCCCC"

# read link stream (sequence of "b e u v") (undirected)
T = set()
V = set()
E = set()
f = open(basename+".ls")
for line in f:
	l = line.strip().split()
	if len(l)==2:
		assert(l[0] in ("alpha","omega"))
		if l[0]=="alpha":
			alpha = float(l[1])
		else:
			omega = float(l[1])
	else:
		assert(len(l)==4)
		[b,e,u,v] = l
		b = float(b)
		e = float(e)
		assert(b<=e)
		T.add(b)
		T.add(e)
		V.add(u)
		V.add(v)
		E.add((b,e,min(u,v),max(u,v)))
f.close()

# read temporal node values (sequence of "t v val") (t float, val float)
f = open(basename+".val")
val = {}
for line in f:
	l = line.strip().split()
	assert(len(l)==3)
	[t,v,x] = l
	t = float(t)
	if v not in val:
		val[v] = {}
	assert(t not in val[v])
	val[v][t] = float(x)
f.close()

min_val = None
max_val = None
for v in V:
	for t in val[v]:
		if min_val==None or val[v][t]<min_val:
			min_val = val[v][t]
		if max_val==None or val[v][t]>max_val:
			max_val = val[v][t]
#min_val = min([min([val[v][t] for t in val[v]]) for v in V])
#max_val = max([max([val[v][t] for t in val[v]]) for v in V])

def output_preambule(f):
	f.write("from Drawing import *\n")
	f.write("s = Drawing(alpha=%g, omega=%g)\n"%(alpha,omega))
	f.write("s.addColor(\"mygrey\",\""+mygrey+"\")\n")

def output_nodes(f,V):
	for v in sorted(V):
		f.write("s.addNode(\""+v+"\", [(%g,%g)])\n"%(alpha,omega))
	f.write("\n")

max_width = 200
min_width = 20
def val_transfo(x):
	return(min_width+max_width*((x-min_val)/max_val))

def output_values(f,val):
	for v in val:
		times = sorted(val[v].keys())
		for i in xrange(len(times)):
			if i>0:
				start = max(alpha,(times[i]+times[i-1])/2.)
			else:
				start = alpha
			if i<len(times)-1:
				end = min(omega,(times[i]+times[i+1])/2.)
			else:
				end = omega
			if val[v][times[i]] > 0:
				f.write("s.addNodeCluster(\""+v+"\", [(%g,%g)], width=%g, color=0)\n"%(start,end,val_transfo(val[v][times[i]])))
			#f.write("s.addNodeCluster(\""+v+"\", [(%g,%g)], width=%g, color=0)\n"%(start,end,val_transfo(val[v][times[i]])))

def output_links(f,E):
	for (b,e,u,v) in E:
		f.write("s.addLink(\""+u+"\", \""+v+"\", %g, %g, color=\"mygrey\")\n"%(b,e))

def output_end(f):
	f.write("\n")
	f.write("\ns.addTimeLine(ticks=2)\n")
	f.close()

output_preambule(sys.stdout)
output_nodes(sys.stdout,V)
output_values(sys.stdout,val)
output_links(sys.stdout,E)
output_end(sys.stdout)

