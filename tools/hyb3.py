import collections, pickle, sys
from exc import bz,bd,bs,excursion
from cmp import rules
TL=500
def run_one(S,j1,ctxlog,maxiter=2_000_000):
    t=[0]*1400
    mr=TL//2+40; im=80+j1; ml=mr-im+1; s=6; pos=mr-len(S)
    for q in range(ml,pos+2): t[q]=1
    for i,ch in enumerate(S,1): t[pos+i]=int(ch)
    new_f=False; step=0; it=0
    while True:
        it+=1
        if it>maxiter: return ('LIMIT',)
        if im>40 and pos==mr-19 and bd[s,t[pos]]==-1:
            l={0:t[pos],-1:t[pos-1],-2:t[pos-2]}
            c3=t[pos-3]
            ctx=(s,l[0],l[-1],l[-2],c3)
            names,s2,l2,im2,st=rules(s,dict(l),im)
            pure=excursion(s,l[0],l[-1],l[-2],im)
            tag='UNKNOWN' if not names else 'RULE'
            if isinstance(pure,tuple):
                ctxlog[ctx,tag+('/HALT' if pure[0]=='UNDEF' else '/'+pure[0]),tuple(names)].append((S,j1,im))
                return ('HALTCTX',ctx,im,S,j1)
            W=20-pure['lo']
            if names:
                ok=(s2==pure['s'] and l2[0]==pure['c0'] and l2[-1]==pure['c1'] and l2[-2]==pure['c2'] and im2==W)
                ctxlog[ctx,'RULE/'+('OK' if ok else 'WRONG'),tuple(names)].append((S,j1,im))
            else:
                ctxlog[ctx,'UNKNOWN',()].append((S,j1,im))
            # continue with TRUE result (so BFS goes on)
            s=pure['s']; t[pos]=pure['c0']; t[pos-1]=pure['c1']; t[pos-2]=pure['c2']; im=W
            new_f=True
        else:
            lz=t[pos]; ls=s
            t[pos]=bz[ls,lz]; s=bs[ls,lz]; pos+=bd[ls,lz]; step+=1
            if pos==ml: new_f=True
            if pos>mr: mr=pos; im+=1
            if pos>mr-20 and im>30:
                if s==6 and new_f and all(t[q] for q in range(ml,pos)):
                    if t[pos]==0: return ('HALT_ENTRY',im%8)
                    return ('OK',''.join(str(t[q]) for q in range(pos+1,mr+1)),im%8)
            if pos<ml: ml=pos; im+=1
        if s==0: return ('HALT',)
        if bd[s,t[pos]]==0: return ('UNDEFSTEP',s,pos-mr)
if __name__=="__main__":
    ctxlog=collections.defaultdict(list)
    groups=['1']; seen={'1'}; g=0; outcomes=collections.Counter(); maxlen=int(sys.argv[1]) if len(sys.argv)>1 else 40
    trans={}
    while g<len(groups) and g<863:
        S=groups[g]
        for j in range(8):
            r=run_one(S,j,ctxlog)
            outcomes[r[0]]+=1
            trans[S,j]=r
            if r[0]=='OK' and r[1] not in seen and len(r[1])<=maxlen:
                seen.add(r[1]); groups.append(r[1])
        g+=1
    print("groups discovered",len(groups),"processed",g,"maxlen S",max(map(len,groups)))
    print(outcomes)
    pickle.dump((groups,trans,dict(ctxlog)),open("hyb3.pkl","wb"))
    agg=collections.defaultdict(int)
    for (ctx,tag,names),lst in ctxlog.items(): agg[(ctx,tag,names)]+=len(lst)
    for k in sorted(agg,key=str): print(k,agg[k])
