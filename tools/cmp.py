import pickle,collections
res=pickle.load(open("exc.pkl","rb"))
def rules(s,l,im,step=0):
    """port of Left_side_rule; l: dict offset->cell (0,-1,-2). returns (matched_names,s,l,im,step)"""
    names=[]
    L=lambda k:l[k]
    if s==2 and L(0)==0 and L(-1)==0 and L(-2)==0 and im%2==1:
        names.append('S4a'); s=4; l[0]=l[-1]=l[-2]=1; step+=4
    if s==3 and L(0)==0 and L(-1)==1 and im%2==0:
        names.append('S2a'); s=2; l[0]=0; l[-1]=1; step+=2
    if s==3 and L(0)==0 and L(-1)==0 and im%2==0:
        names.append('S2b'); s=5; l[0]=0; l[-1]=1; step+=2
    if s==3 and L(0)==1 and L(-1)==1 and im%2==0:
        names.append('P2a'); s=4; l[0]=0; l[-1]=1; im+=2
    if s==3 and L(0)==1 and L(-1)==1 and im%2==1:
        names.append('P2b'); s=5; l[0]=0; l[-1]=1; im+=2
    if s==2 and L(0)==0 and L(-1)==1 and im%2==0:
        names.append('P2c'); s=4; l[0]=1; l[-1]=1; im+=2
    if s==2 and L(0)==0 and L(-1)==0 and L(-2)==1 and im%2==1:
        names.append('P2d'); s=2; l[0]=1;l[-1]=1;l[-2]=1; im+=2
    if s==6 and L(0)==1 and L(-1)==1 and L(-2)==1 and im%4==0:
        names.append('B0'); s=2; l[0]=l[-1]=l[-2]=0; im=20+6*((im-20)//4)+3
    if s==5 and L(0)==1 and L(-1)==1 and im%4==1:
        names.append('B1'); s=2; l[0]=1; l[-1]=1; im=20+6*((im-20)//4)+4
    if s==6 and L(0)==1 and L(-1)==1 and L(-2)==1 and im%4==2:
        names.append('B2'); s=2; l[0]=0;l[-1]=0;l[-2]=1; im=20+6*((im-20)//4)+5
    if s==5 and L(0)==1 and L(-1)==1 and im%4==3:
        names.append('B3'); s=2; l[0]=1; l[-1]=0; im=20+6*((im-20)//4)+8
    if s==6 and L(0)==1 and L(-1)==1 and L(-2)==1 and im%4==3:
        names.append('B4'); s=2; l[0]=0;l[-1]=0;l[-2]=1; im=20+6*((im-20)//4)+5
    if s==6 and L(0)==1 and L(-1)==1 and L(-2)==1 and im%4==1:
        names.append('B5'); s=2; l[0]=l[-1]=l[-2]=0; im=20+6*((im-20)//4)+3
    return names,s,l,im,step
if __name__=="__main__":
    status=collections.defaultdict(lambda: collections.defaultdict(list))
    for (s,sym,c1,c2,im),v in res.items():
        ctx=(s,sym,c1,c2)
        l={0:sym,-1:c1,-2:c2}
        names,s2,l2,im2,st=rules(s,dict(l),im)
        if isinstance(v,tuple):
            status[ctx][im].append(('PURE',v[0],names)); continue
        W=20-v['lo']
        if not names: status[ctx][im].append(('UNKNOWN',)); continue
        ok=(s2==v['s'] and l2[0]==v['c0'] and l2[-1]==v['c1'] and l2[-2]==v['c2'] and im2==W and v['c3']==1)
        status[ctx][im].append(('MATCH' if ok else 'MISMATCH',tuple(names),(s2,l2[-2],l2[-1],l2[0],im2),(v['s'],v['c2'],v['c1'],v['c0'],W)))
    summary={}
    for ctx in sorted(status):
        c=collections.Counter()
        for im,lst in status[ctx].items():
            for x in lst:
                c[x[0]]+=1
        print(ctx,dict(c))
    pickle.dump({k:dict(v) for k,v in status.items()},open("cmp.pkl","wb"))
