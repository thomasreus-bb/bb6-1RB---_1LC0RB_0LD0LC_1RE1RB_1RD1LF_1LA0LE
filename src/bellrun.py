#!/usr/bin/env python3
"""Echte Bell-Bahn mit Block-Spruengen (exakt). Aufruf: python3 bellrun.py N [checkpoint.pkl]
Benoetigt tab.txt und tab_names.txt (Uebergangstabelle: Zustand S, k mod 4 -> S', c, Halt)."""
import sys,time,pickle,os
M=40; W=62; MASK=(1<<W)-1; P3=3**M
tab=open('tab.txt').read().split('\n'); n=int(tab[0])
nxt=[];cc=[]
for i in range(n):
    a,b,c,d=map(int,tab[1+i].split()); nxt+=[a,c]; cc+=[b,d]
names=open('tab_names.txt').read().split('\n')
N=int(sys.argv[1]); ck=sys.argv[2] if len(sys.argv)>2 else None
if ck and os.path.exists(ck): k,s,done,visits=pickle.load(open(ck,'rb'))
else: k,s,done,visits=92,0,0,[0]*n   # Start: Bell #4: k=92, S=11 (S_pascal='1')
t0=time.time(); last=t0; trace=[]
while done<N:
    m=min(M,N-done)
    L=k&MASK; st=s; cnt=0; stop=None
    for _ in range(m):
        visits[st]+=1
        idx=2*st+((L&3)>>1)
        t=nxt[idx]
        if t<0: stop=t; break
        L=3*(L>>1)+cc[idx]; st=t; cnt+=1
    if stop is not None:
        done+=cnt
        print('HALT' if stop==-1 else 'UNBEKANNTER ZUSTAND', 'bei Bell',done,'S_pascal=',names[st],'k mod 4 =',L&3); sys.exit(0)
    if cnt==M: k=(((k>>W)*P3)<<(W-M))+L
    else: k=(((k>>W)*3**cnt)<<(W-cnt))+L
    s=st; done+=cnt
    if ck and time.time()-last>300:
        pickle.dump((k,s,done,visits),open(ck,'wb')); last=time.time()
    if done in (22,) : print('Bell',done,'k=',k,'S=',names[s])
print('kein Halt in',done,'Bells; Zeit',round(time.time()-t0,1),'s; k hat',k.bit_length(),'Bit; Zustand',names[s])
tot=sum(visits)
top=sorted(range(n),key=lambda i:-visits[i])[:8]
print('Haeufigkeiten:',[(names[i],round(visits[i]/tot,4)) for i in top])
if ck: pickle.dump((k,s,done,visits),open(ck,'wb'))
