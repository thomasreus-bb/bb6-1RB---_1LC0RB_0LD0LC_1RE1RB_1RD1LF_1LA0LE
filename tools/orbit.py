import sys,collections; sys.set_int_max_str_digits(0); sys.path.insert(0,'.')
src=open('hyb3.py').read().split('if __name__')[0]
src=src.replace("return ('OK',''.join(str(t[q]) for q in range(pos+1,mr+1)),im%8)","return ('OK',''.join(str(t[q]) for q in range(pos+1,mr+1)),im%8,im)")
src=src.replace("return ('HALT_ENTRY',im%8)","return ('HALT_ENTRY',im%8,im)")
ns={};exec(compile(src,'h','exec'),ns); run_one=ns['run_one']
cache={}
def trans(Sp,k):
    # k = exact number of ones left of head; returns (Sp',k') or 'HALT'
    L=len(Sp)
    j=(k+1+L)%8      # im=80+j
    key=(Sp,j)
    if key not in cache:
        cache[key]=run_one(Sp,j,collections.defaultdict(list))
    r=cache[key]
    im0=80+j; k0=im0-1-L
    if r[0]=='HALT_ENTRY': return 'HALT'
    if r[0]!='OK': return ('ERR',r)
    Sn=r[1]; kn0=r[3]-1-len(Sn)
    # k' = 3(k-k0)/2 + kn0  (Bell-Rule linear in k)
    d=k-k0
    assert d%4==0, (d)
    return Sn, 3*d//2+kn0
if __name__=="__main__":
    Sp,k='1',92; N=int(sys.argv[1]); seen=collections.Counter(); maxlen=0
    for n in range(N):
        if n<22: print(n,k if n<30 else '', '1'+Sp)
        r=trans(Sp,k)
        if r=='HALT': print('HALT bei Bell',n,Sp,k%(1<<20)); break
        if r[0]=='ERR': print('ERR',n,Sp,r); break
        Sp,k=r; maxlen=max(maxlen,len(Sp)); seen[Sp]+=1
    else: print('kein Halt in',N,'Bells; max len S',maxlen,'k Dezimalstellen',len(str(k)),'verschiedene S',len(seen))
