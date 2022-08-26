#%autoindent
import sys
import os
sys.path.append(os.path.abspath("../Lib/"))
from lslib import read_link_stream
from latencylib import Latency_lists
from betweennesslib import PrevList,NextList,Contribution,Betweenness

def test_prev_next(filename,u,w,(s,a),val_prev,val_next):
	f = open(filename)
	L = read_link_stream(f)
	f.close()
	sys.stderr.write("%s %s %s (%g,%g):\n"%(filename,u,w,s,a))
	LL = Latency_lists(L,u)
	resu_prev = PrevList(L,u,w,(s,a),LL[w])
	resu_next = NextList(L,u,w,(s,a),LL[w])
	sys.stderr.write(" prev: "+str(resu_prev)+"\n")
	sys.stderr.write(" next: "+str(resu_next)+"\n")
	sys.stderr.flush()
	assert(resu_next == val_next)
	assert(resu_prev == val_prev)

test_prev_next('test6','a','b',(4.,4.),[],[])

test_prev_next('ex-prevlist','a','d',(15.,16.),[(0.0,(0.0,0))],[(72.0,(0.0,0)),(96.0,(1.0,1))])
test_prev_next('ex-prevlist','a','d',(24.,26.),[(15.0, (0.0, 0))],[(72.0, (0.0,0))])
test_prev_next('ex-prevlist','a','d',(31.,33.),[(24.0, (0.0, 0))],[(53.0, (0.0, 0)), (72.0, (1.0, 1))])
test_prev_next('ex-prevlist','a','d',(40.,42.),[(31.0, (0.0, 0))],[(53.0, (0.0, 0))])
test_prev_next('ex-prevlist','a','d',(51.,53.),[(31.0, (0.0, 0)), (24.0, (1.0, 1))],[(72.0, (0.0, 0))])
test_prev_next('ex-prevlist','a','d',(60.,65.),[(51.0, (0.0, 0))],[(72.0, (0.0, 0))])
test_prev_next('ex-prevlist','a','d',(71.,72.),[(15.0, (0.0, 0)), (0.0, (1.0, 1))],[(96.0, (0.0, 0))])
test_prev_next('ex-prevlist','a','d',(83.,87.),[(71.0, (0.0, 0))],[(96.0, (0.0, 0))])
test_prev_next('ex-prevlist','a','d',(96.,96.),[(0.0, (0.0, 0))],[(100.0, (0.0, 0))])

test_prev_next('ex-prevlist_bis','a','d',(15.,16.),[(0.0,(0.0,0))],[(35.0,(0.0,0))])
test_prev_next('ex-prevlist_bis','a','d',(24.,26.),[(15.0, (0.0, 0))],[(35.0, (0.0,0))])
test_prev_next('ex-prevlist_bis','a','d',(31.,33.),[(24.0, (0.0, 0))],[(35.0, (0.0, 0))])
test_prev_next('ex-prevlist_bis','a','d',(35.,35.),[(0., (0.0, 0))],[])
test_prev_next('ex-prevlist_bis','a','d',(36.,36.),[],[])
test_prev_next('ex-prevlist_bis','a','d',(37.,37.),[],[(68.,(0.,0)),(96.0, (1.0, 0)),(100.,(2.,0))])
test_prev_next('ex-prevlist_bis','a','d',(40.,42.),[(37.0, (0.,0))],[(53.0,(0.,0))])
test_prev_next('ex-prevlist_bis','a','d',(51.,53.),[(37.0, (0.0, 0))],[(68.0, (0.0, 0))])
test_prev_next('ex-prevlist_bis','a','d',(60.,65.),[(51.0, (0.0, 0))],[(68.0, (0.0, 0))])
test_prev_next('ex-prevlist_bis','a','d',(68.,68.),[(37.0, (0.0, 0))],[(96.0, (0.0, 0)),(100.,(1.,0))])
test_prev_next('ex-prevlist_bis','a','d',(71.,72.),[(68.0, (0.0, 0))],[(96.0, (0.0, 0))])
test_prev_next('ex-prevlist_bis','a','d',(83.,87.),[(71.0, (0.0, 0))],[(96.0, (0.0, 0))])
test_prev_next('ex-prevlist_bis','a','d',(96.,96.),[(68.0, (0.0, 0)),(37.,(1.,0))],[(100.0, (0.0, 0))])

test_prev_next('test9','a','d',(1.,3.),[(0., (0.0, 0))],[(6.,(0.,0)),(9.,(1.,0)),(12.,(2.,0)),(15.,(3.,0))])

sys.stderr.write("\nPrev/NextList: good!\n\n")

def test_contrib(filename,u,w,(t,v),val):
	f = open(filename)
	L = read_link_stream(f)
	f.close()
	sys.stderr.write("%s: contribution of %s and %s to the betweenness of (%g,%s): "%(filename,u,w,t,v))
	LL = Latency_lists(L,u)
	c = Contribution(L,u,w,(t,v),LL[w])
	sys.stderr.write(str(c)+", val: "+str(val)+"\n")
	sys.stderr.flush()
	assert(c == val)

test_contrib('test8','a','e',(2.,'b'),0.)
test_contrib('test8','a','e',(7.,'b'),0.)
test_contrib('test8','a','e',(3.5,'b'),6.)
test_contrib('test8','a','e',(5.,'b'),2.)
test_contrib('test8','a','e',(4.5,'c'),4.)
test_contrib('test8','a','e',(5.,'c'),4.)
test_contrib('test8','a','e',(5.5,'c'),2.)
test_contrib('test8','a','e',(10.,'c'),0.)
test_contrib('test8','a','e',(4.,'d'),0.)
test_contrib('test8','a','e',(6.,'d'),2.)
test_contrib('test8','a','e',(7.5,'d'),6.)
test_contrib('test8','a','e',(9.,'d'),0.)
test_contrib('test8','a','e',(8.,'e'),6.)
test_contrib('test8','a','e',(9.,'e'),0.)

test_contrib('test9','a','d',(2.5,'c'),1*3*1.+1*3*1./2+1*3*1./3+1*3*1./4)
test_contrib('test9','a','d',(5.5,'c'),3*3*1.+1*3*1./2+1*3*1./3+1*3*1./4+3*3*1./2+3*3*1./3)
test_contrib('test9','a','d',(8.5,'c'),3*3*1.+3*3*1./2+3*3*1./2+3*3*1./3+1*3*1./3+1*3*1./4)
test_contrib('test9','a','d',(11.5,'c'),3*3*1.+3*3*1./2+3*3*1./3+1*3*1./4)

test_contrib('test10','a','c',(2.,'b'),0.)

sys.stderr.write("\nContribution: good!\n\n")

sys.exit()

def test_betweenness(filename,t,v,val):
	f = open(filename)
	L = read_link_stream(f)
	f.close()
	resu = Betweenness(L,(t,v))
	sys.stderr.write("Betweenness of (%g,%s): %g\n"%(t,v,resu))
	assert(val==resu)

test_betweenness('ex-prevlist',10.,'c',20.)
test_betweenness('ex-prevlist',19.,'c',2.)
test_betweenness('ex-prevlist',3.14,'c',0.)

sys.stderr.write("\nAll good!\n\n")

