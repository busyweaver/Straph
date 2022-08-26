#%autoindent
import sys
import os
sys.path.append(os.path.abspath("../Lib/"))
from lslib import read_link_stream
from vsplib import VSP

def test(filename,(i,u),(j,v),val):
	f = open(filename)
	L = read_link_stream(f)
	f.close()
	sys.stderr.write("%s (%g,%s) -> (%g,%s): "%(filename,i,u,j,v))
	sys.stderr.flush()
	vol = VSP(L,(i,u),(j,v))
	sys.stderr.write("(%g,%d)\n"%vol)
	assert(vol==val)

test('test0',(5.,'a'),(5.,'b'),(1.,0))
test('test0',(4.,'a'),(5.,'b'),(1.,0))
test('test0',(4.,'a'),(8.,'b'),(1.,0))
test('test0',(4.,'a'),(10.,'b'),(1.,0))
test('test0',(7.,'a'),(10.,'b'),(0.,0))

test('test1',(4.,'a'),(4.,'b'),(1.,0))
test('test1',(5.,'a'),(5.,'b'),(1.,0))
test('test1',(4.,'a'),(5.,'b'),(1.,1))
test('test1',(4.,'a'),(8.,'b'),(2.,1))
test('test1',(4.,'a'),(10.,'b'),(2.,1))
test('test1',(7.,'a'),(10.,'b'),(0.,0))

test('test2',(-1.,'a'),(0.5,'d'),(0.,0))
test('test2',(-1.,'a'),(1.,'d'),(0.5,2))
test('test2',(-1.,'a'),(1.5,'d'),(0.25,3))
test('test2',(-1.,'a'),(2.,'d'),(1.,0))
test('test2',(-1.,'a'),(3.,'d'),(1.,0))
test('test2',(-1.,'b'),(0.5,'d'),(0.,0))
test('test2',(-1.,'b'),(1.,'d'),(1.,1))
test('test2',(-1.,'b'),(1.5,'d'),(0.5,2))
test('test2',(-1.,'b'),(2.,'d'),(1.,2))
test('test2',(-1.,'b'),(3.,'d'),(1.,2))
test('test2',(0.,'a'),(1.,'c'),(.5,2))

test('test3',(0.,'a'),(5.6,'b'),(1.,1))
test('test3',(0.,'a'),(9.,'c'),(2.,2))
test('test3',(4.5,'a'),(9.,'c'),(1.,2))
test('test3',(5.,'a'),(9.,'c'),(2.,1))
test('test3',(4.,'a'),(7.,'c'),(1.,2))

#test('test4',(6,'a'),(7,'b'),(1.,1))
#test('test4',(7,'b'),(7,'c'),(1.,0))
test('test4',(3.,'a'),(6.,'c'),(0.5,2))
test('test4',(4.,'a'),(4.,'c'),(1.,0))
test('test4',(4.5,'a'),(4.5,'c'),(1.,0))
test('test4',(4.2,'a'),(4.7,'c'),(.125,2))
test('test4',(4.,'a'),(5.,'b'),(1.,1))
test('test4',(4.,'b'),(5.,'c'),(1.,1))
test('test4',(4.,'a'),(5.,'c'),(0.5,2))

test('test5',(3.,'a'),(5.,'c'),(2.,2))
test('test5',(3.,'a'),(3.,'c'),(1.,0))
test('test5',(4.,'a'),(4.,'c'),(1.,0))
test('test5',(5.,'a'),(5.,'c'),(1.,0))
test('test5',(3.,'a'),(5.,'d'),(2.**3/6,3))
test('test5',(3.,'a'),(6.,'d'),(2.**3/6+1.+2.,3))

test('ex-intro',(2.,'a'),(9.,'e'),(2.,2))
test('ex-intro',(9.,'a'),(16.,'e'),(2.,1))
test('ex-intro',(16.,'a'),(23.,'e'),(1.,0))
test('ex-intro',(24.,'a'),(30.,'e'),(5.5,2))

test('ex-intro',(0.,'a'),(9.,'e'),(2.,3))
test('ex-intro',(0.,'a'),(14.,'e'),(4.,4))

test('ex-intro',(9.,'d'),(16.,'e'),(2.,1))
test('ex-intro',(11.,'d'),(16.,'e'),(2.,0))

test('ex-intro',(0.,'a'),(17.,'e'),(2.,2))
test('ex-intro',(2.,'a'),(17.,'e'),(2.,1))
test('ex-intro',(3.,'a'),(17.,'e'),(2.,2))

test('ex-intro',(3.,'a'),(25.,'e'),(1.,3))
test('ex-intro',(1.5,'a'),(25.,'e'),(2.,3))

test('ex-intro',(21.,'a'),(32.,'e'),(5.5,4))
test('ex-intro',(21.,'a'),(32.,'e'),(5.5,4))
test('ex-intro',(14.,'a'),(32.,'e'),(17.,4))

# examples of the paper

test('ex-intro',(0.,'a'),(14.,'e'),(4.,4))
test('ex-intro',(4.,'a'),(17.,'e'),(2.,2))
test('ex-intro',(12.,'a'),(26.,'e'),(1.,2))
test('ex-intro',(20.,'a'),(32.,'e'),(5.5,4))

test('ex-intro',(0.,'a'),(18.,'e'),(2.,2))
test('ex-intro',(0.,'a'),(23.,'e'),(5.,2))
test('ex-intro',(0.,'a'),(26.,'e'),(3.,3))
test('ex-intro',(0.,'a'),(32.,'e'),(8.,3))

sys.stderr.write("All good!\n")

