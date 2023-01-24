#%autoindent
from graphlib import graph_dist
from lslib import get_graph_neighborhood_minus,get_graph_neighborhood_plus,ls_dist
from vsplib import VSP,plusvol,timesvol,divvol,plusvol
from latencylib import Latency_lists

# utility functions
# given a link stream L, two nodes u and w, a latency pair (s,a) from u to w, and the ordered latency list LL from u to w, compute ... see paper.

VSPsuaw = dict()
def VSP_mem(L,(s_prime,u),(a_prime,w)):
    if ((s_prime,u),(a_prime,w)) in VSPsuaw:
        return VSPsuaw[((s_prime,u),(a_prime,w))]
    else:
        VSPsuaw[((s_prime,u),(a_prime,w))] = VSP(L,(s_prime,u),(a_prime,w))
        return VSPsuaw[((s_prime,u),(a_prime,w))]




def PrevList(L,u,w,(s,a),LL):
	R,vol = [],(0.,0)
	dist_su_aw = dist_mem(L,(s,u),a).get((a,w),None)
	assert(dist_su_aw!=None)
	if s==a:
		d_u_w = graph_dist(get_graph_neighborhood_minus(L,s),u).get(w,None)
		if d_u_w==dist_su_aw:
			return(R)
	for (s_prime,a_prime) in reversed(LL):
		if s_prime<s:
			if a_prime-s_prime<a-s:
				R.append((s_prime,vol))
				return(R)
			if a_prime-s_prime==a-s:
				dist_su_aw_prime = dist_mem(L,(s_prime,u),a_prime).get((a_prime,w),None)
				if dist_su_aw==None or (dist_su_aw_prime!=None and dist_su_aw_prime<dist_su_aw):
					R.append((s_prime,vol))
					return(R)
				if dist_su_aw_prime!=None and dist_su_aw_prime == dist_su_aw: # then necessarily dist_su_aw!=None
					R.append((s_prime,vol))
					d_u_w = graph_dist(get_graph_neighborhood_minus(L,s_prime),u).get(w,None)
					if s_prime==a_prime and d_u_w==dist_su_aw:
						return(R)
					vol = plusvol(vol,VSP_mem(L,(s_prime,u),(a_prime,w)))
	R.append((L.alpha,vol))
        return R

def NextList(L,u,w,(s,a),LL):
	R,vol = [],(0.,0)
	dist_su_aw = dist_mem(L,(s,u),a).get((a,w),None)
	assert(dist_su_aw!=None)
	if s==a:
		d_u_w = graph_dist(get_graph_neighborhood_plus(L,a),u).get(w,None)
		if d_u_w==dist_su_aw:
			return(R)
	for (s_prime,a_prime) in LL:
		if a_prime>a:
			if a_prime-s_prime<a-s:
				R.append((a_prime,vol))
				return(R)
			if a_prime-s_prime==a-s:
				dist_su_aw_prime = dist_mem(L,(s_prime,u),a_prime).get((a_prime,w),None)
				if dist_su_aw==None or (dist_su_aw_prime!=None and dist_su_aw_prime<dist_su_aw):
					R.append((a_prime,vol))
					return(R)
				if dist_su_aw_prime!=None and dist_su_aw_prime == dist_su_aw: # then necessarily dist_su_aw!=None
					R.append((a_prime,vol))
					d_u_w = graph_dist(get_graph_neighborhood_plus(L,a_prime),u).get(w,None)
					if s_prime==a_prime and d_u_w==dist_su_aw:
						return(R)
					vol = plusvol(vol,VSP_mem(L,(s_prime,u),(a_prime,w)))
	R.append((L.omega,vol))
        return R

dist = dict()
def dist_mem(L,(i,u),j):
    if (i,u,j) in dist:
        return dist[(i,u,j)]
    else:
        dist[(i,u,j)] = ls_dist(L,(i,u),j)
        return dist[(i,u,j)]

# computes the contribution of nodes u and w to the betweenness of (t,v) in L
def Contribution(L,u,w,(t,v),LL, dist):
	#print L,u,w,(t,v),"latency",LL
	assert u in L.V and w in L.V and v in L.V
	assert t>=L.alpha and t <= L.omega
	# add t to event times to ensure that ls_dist(L,(s,u),a) will compute a value for (t,v)
	L.eventtimes = [x for x in L.eventtimes if x<t]+[t]+[x for x in L.eventtimes if x>t]
        vol_tv=(0.,0)
        for (s,a) in LL:
                if t >= s and t <= a:
			dist_su = dist_mem(L,(s,u),a)
			dist_tv = dist_mem(L,(t,v),a)
			if (t,v) in dist_su and (a,w) in dist_tv:
				d_su_aw = dist_su[(a,w)]
				d_su_tv = dist_su[(t,v)]
				d_tv_aw = dist_tv[(a,w)]
				if d_su_aw == d_su_tv+d_tv_aw:
					vsp_su_tv = VSP_mem(L, (s,u),(t,v))
					vsp_tv_aw = VSP_mem(L,(t,v),(a,w))
					if vsp_su_tv!=(0.,0) and vsp_tv_aw!=(0.,0):
						vol_tv = timesvol(vsp_su_tv,vsp_tv_aw)
				break
	if vol_tv==(0.,0):
		return(0.)
	middle = VSP_mem(L,(s,u),(a,w))
	Prev = PrevList(L,u,w,(s,a),LL)
	Next = NextList(L,u,w,(s,a),LL)
	#print "prev",Prev
	#print "next",Next
	contrib = 0.
	s_prime = s
        for (s_left,left) in Prev:
        	#print("left",left)
                a_prime = a
        	for (a_right,right) in Next:
        		#print("right",right)
        		#print("vol_tv", vol_tv, "denum", plusvol(plusvol(left,right),middle) )
			contrib += (s_prime-s_left)*(a_right-a_prime)*divvol(vol_tv,plusvol(plusvol(left,right),middle))
			#print("contrib",contrib)
			a_prime = a_right
                s_prime = s_left
        return contrib

def Betweenness(L,(t,v), LaL,  dist):
	assert v in L.V and t >= L.alpha and t <= L.omega
	contri = {e:0.0 for e in L.V}
        B = 0.
        for u in L.V:
                LL = LaL[u]
                for w in L.V:
                	x = Contribution(L,u,w,(t,v),LL[w], dist)
                	# print("contri",u,w," = ",x)
                	contri[u] = contri[u] + x
                	B += x
        # print(contri)
        return B

def Betweenness_contri(L,(t,v)):
    # print(v,t)
    assert v in L.V and t >= L.alpha and t <= L.omega
    contri = {e:0.0 for e in L.V}
    B = 0.
    for u in L.V:
        LL = Latency_lists(L,u)
        for w in L.V:
            x = Contribution(L,u,w,(t,v),LL[w])
            print("contri",u,w," = ",x,"w",w)
            contri[u] = contri[u] + x
            B += x
    return B,contri

def contri_point(L,(t,v),a):
	contri = 0.
        LL = Latency_lists(L,a)
        for w in L.V:
        	x = Contribution(L,a,w,(t,v),LL[w])
               	print("contri",a,w," = ",x)
                contri = contri + x
        return contri


