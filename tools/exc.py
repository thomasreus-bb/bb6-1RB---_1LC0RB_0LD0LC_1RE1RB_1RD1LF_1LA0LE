import sys, collections, pickle
tm="1RB---_1LC0RB_0LD0LC_1RE1RB_1RD1LF_1LA0LE"
bz={};bd={};bs={}
for i,r in enumerate(tm.split("_"),1):
    for b in range(2):
        t=r[3*b:3*b+3]
        if t[0]=='-': bz[i,b]=1;bd[i,b]=0;bs[i,b]=0
        else: bz[i,b]=int(t[0]);bd[i,b]=1 if t[1]=='R' else -1;bs[i,b]=ord(t[2])-64
LEFT=[(s,b) for s in range(1,7) for b in range(2) if bd[s,b]==-1]
OFF=3000
def excursion(s,sym,c1,c2,im,limit=3_000_000):
    t=[0]*6000
    ml0=-(im-20)
    for p in range(ml0,-2): t[OFF+p]=1
    t[OFF-2]=c2;t[OFF-1]=c1;t[OFF]=sym
    p=0;n=0;mn=0
    while True:
        lz=t[OFF+p]
        t[OFF+p]=bz[s,lz];ns=bs[s,lz];p+=bd[s,lz];s=ns;n+=1
        if p<mn: mn=p
        if s==0: return ('HALT',n)
        if bd[s,t[OFF+p]]==0: return ('UNDEF',n)
        if p==0: break
        if n>limit: return ('LIMIT',n)
    nz=[q for q in range(-2500,1) if t[OFF+q]]
    lo=min(nz)
    ones_ok=all(t[OFF+q]==1 for q in range(lo,-3))
    return dict(s=s,c2=t[OFF-2],c1=t[OFF-1],c0=t[OFF],c3=t[OFF-3],n=n,im2=20-mn,lo=lo,ok=ones_ok and (-lo==20-mn-20+0 or True),minv=mn)
if __name__=="__main__":
    res={}
    for (s,sym) in LEFT:
        for c1 in (0,1):
            for c2 in (0,1):
                for im in range(44,141):
                    res[s,sym,c1,c2,im]=excursion(s,sym,c1,c2,im)
    pickle.dump(res,open("exc.pkl","wb"))
    kinds=collections.Counter()
    for k,v in res.items():
        kinds[v[0] if isinstance(v,tuple) else 'ok' if v['ok'] and -v['lo']==v['im2']-20 else 'shape']+=1
    print(kinds)
