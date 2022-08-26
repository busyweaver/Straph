#%autoindent
import sys
import os
sys.path.append(os.path.abspath("../Lib/"))
from lslib import read_link_stream
from latencylib import Latency_lists

def test(filename,u,v,val):
	f = open(filename)
	L = read_link_stream(f)
	f.close()
	sys.stderr.write("%s %s %s:\n"%(filename,u,v))
	sys.stderr.flush()
	LL = Latency_lists(L,u)
        for w in sorted(L.V):
		sys.stderr.write(" %s -> %s: %s\n"%(u,w,str(sorted(LL[w]))))
	assert(LL[v]==val)

test('test0','a','b',[(5.,5.)])
test('test0','b','a',[(5.,5.)])

test('test1','a','a',[(4.,4.),(6.,6.)])
test('test1','a','b',[(4.,4.),(6.,6.)])

test('test6','a','b',[(3.,3.),(4.,4.),(5.,5.)])

test('ex-intro','a','e',[(2.,9.),(9.,16.),(16.,23.),(24.,30.)]) # expliciter dans l'article

test('ex-intro','b','a',[(1.,1.),(2.,2.),(5.,8.),(15.,15.),(16.,16.),(23.,23.),(24.,24.)]) # expliciter dans l'article
test('ex-intro','b','c',[(3.,3.),(5.,5.),(11.,11.),(14.,18.),(19.,19.),(22.,22.),(25.,25.),(27.,27.),(28.,28.)])
test('ex-intro','b','d',[(5.,6.),(12.,12.),(14.,14.),(19.,19.),(27.,27.),(28.,28.)])
test('ex-intro','b','e',[(5.,9.),(14.,16.),(19.,23.),(28.,30.)])

test('ex-prevlist','a','d',[(15.0, 16.0), (24.0, 26.0), (31.0, 33.0), (40.0, 42.0), (51.0, 53.0), (60.0, 65.0), (71.0, 72.0), (83.0, 87.0), (96.0, 96.0)])

test('ex-prevlist_bis','a','d',[(15.0, 16.0), (24.0, 26.0), (31.0, 33.0), (35.,35.),(36.,36.),(37.,37.),(40.0, 42.0), (51.0, 53.0), (60.0, 65.0),(68.,68.),(71.0, 72.0), (83.0, 87.0), (96.0, 96.0)])

sys.stderr.write("All good!\n")


