#!/usr/bin/env python3
"""Bell-Bahn mit grossen Bloecken (B Bells je Block), exakt. Aufruf: python3 bellfast.py N [B]
Idee: k_neu = 3^B * (k >> (B+2)) << 2  +  L_B,  L_B = unterer Teil (B+2 Bit), Schritt fuer Schritt.
Benoetigt tab.txt, tab_names.txt."""
import sys,time
tab=open('tab.txt').read().split('\n'); n=int(tab[0]); nxt=[];cc=[]
for i in range(n):
    a,b,c,d=map(int,tab[1+i].split()); nxt+=[a,c]; cc+=[b,d]
names=open('tab_names.txt').read().split('\n')
N=int(sys.argv[1]); B=int(sys.argv[2]) if len(sys.argv)>2 else 20000
k,s,done=92,0,0; t0=time.time(); P3=None; tm=tl=0.0
while done<N:
    m=min(B,N-done); W=m+2
    ta=time.time()
    L=k&((1<<W)-1); hi=k>>W; st=s; stop=None; cnt=0
    for _ in range(m):
        idx=2*st+((L&3)>>1); t=nxt[idx]
        if t<0: stop=t; break
        L=3*(L>>1)+cc[idx]; st=t; cnt+=1
    tb=time.time(); tl+=tb-ta
    if stop is not None:
        done+=cnt; print('HALT' if stop==-1 else 'UNBEKANNT','bei Bell',done,names[st],'k mod 4 =',L&3); sys.exit(0)
    if cnt==B:
        if P3 is None: P3=3**B
        p=P3
    else: p=3**cnt
    k=((hi*p)<<(W-cnt))+L
    s=st; done+=cnt; tm+=time.time()-tb
bits=k.bit_length()
print('KCHECK',k&(2**64-1),bits,names[s])
print('kein Halt in',done,'Bells; Zeit',round(time.time()-t0,1),'s (unterer Teil',round(tl,1),'s, Multiplikation',round(tm,1),'s); B =',B)
