// bellntt.c - exact Bell orbit with two-level blocks and an own NTT multiplication (no GMP).
// Compile: gcc -O3 -march=native -fopenmp -o bellntt bellntt.c      (without -fopenmp: one core)
// Usage:   ./bellntt N [B]      N = number of Bells, B = block size in Bells (default 2000000)
// Needs tab.txt and tab_names.txt in the current directory.
// Output: a KCHECK line (k mod 2^64, bit length of k, state), then "no halt ..." or a HALT message.
//
// Verfahren: k_neu = ((k >> (B+2)) * 3^B) << 2  +  R,  wobei R aus den unteren B+2 Bit von k
// durch B Einzelschritte entsteht. Die Schritte selbst laufen wie in bellrun.c in Teilbloecken
// zu je 40 Bells (Multiplikation mit der Konstanten 3^40, linear in der Laenge). Nur das grosse
// Produkt (k >> (B+2)) * 3^B wird mit einer NTT (zwei Primzahlen, CRT) berechnet.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>
#ifdef _OPENMP
#include <omp.h>
#endif
typedef unsigned __int128 u128; typedef uint64_t u64; typedef uint32_t u32;
#define M 40

static int n; static int *nxt,*cc; static long long *vis; static char **names;

/* ---------- Montgomery-Arithmetik fuer Primzahlen < 2^63 ---------- */
typedef struct { u64 p,pinv,r1,r2,w24; u64 *rt,*irt; u64 *fp; } Pr;
static Pr pr[2];
static inline u64 mm(u64 a,u64 b,const Pr*q){
  u128 t=(u128)a*b; u64 m=(u64)t*q->pinv; u64 u=(u64)((t+(u128)m*q->p)>>64); return u>=q->p?u-q->p:u; }
static u64 powmod(u64 a,u64 e,u64 p){ u64 r=1; a%=p; while(e){ if(e&1) r=(u64)((u128)r*a%p); a=(u64)((u128)a*a%p); e>>=1; } return r; }
static void pr_init(Pr*q,u64 p,u64 w24){
  q->p=p; q->w24=w24; u64 inv=p; for(int i=0;i<6;i++) inv*=2-p*inv; q->pinv=(u64)0-inv;
  q->r1=(u64)(((u128)1<<64)%p); q->r2=(u64)((u128)q->r1*q->r1%p); q->rt=q->irt=q->fp=NULL; }
static inline u64 tom(u64 a,const Pr*q){ return mm(a,q->r2,q); }
static int tables_lg=0;
static void build_tables(int lg){ // Twiddles fuer alle Stufen bis Transformlaenge 2^lg (lg <= 24)
  size_t T=(size_t)1<<lg;
  for(int i=0;i<2;i++){ Pr*q=&pr[i]; free(q->rt); free(q->irt); q->rt=malloc(T*8); q->irt=malloc(T*8);
    for(size_t half=1;half<T;half<<=1){
      u64 w=powmod(q->w24,(u64)1<<(24-0),q->p); (void)w; // Platzhalter
      // Wurzel der Ordnung 2*half: w24^(2^24/(2*half))
      u64 om=powmod(q->w24,((u64)1<<24)/(2*half),q->p), oi=powmod(om,q->p-2,q->p);
      u64 omm=tom(om,q), oim=tom(oi,q);
      q->rt[half]=q->r1; q->irt[half]=q->r1;
      for(size_t j=1;j<half;j++){ q->rt[half+j]=mm(q->rt[half+j-1],omm,q); q->irt[half+j]=mm(q->irt[half+j-1],oim,q); }
    } }
  tables_lg=lg; }
static void ntt_fwd(u64*a,size_t T,const Pr*q){
  u64 p=q->p;
  for(size_t half=T>>1;half;half>>=1){
    const u64*rt=q->rt+half;
    for(size_t i=0;i<T;i+=2*half){ u64*x=a+i,*y=a+i+half;
      for(size_t j=0;j<half;j++){ u64 u=x[j],v=y[j]; u64 s=u+v; if(s>=p)s-=p; u64 d=u+p-v; if(d>=p)d-=p; x[j]=s; y[j]=mm(d,rt[j],q); } } } }
static void ntt_inv(u64*a,size_t T,const Pr*q){
  u64 p=q->p;
  for(size_t half=1;half<T;half<<=1){
    const u64*rt=q->irt+half;
    for(size_t i=0;i<T;i+=2*half){ u64*x=a+i,*y=a+i+half;
      for(size_t j=0;j<half;j++){ u64 u=x[j],v=mm(y[j],rt[j],q); u64 s=u+v; if(s>=p)s-=p; u64 d=u+p-v; if(d>=p)d-=p; x[j]=s; y[j]=d; } } } }

/* ---------- Langzahl-Hilfen (Limbs zu 64 Bit, little endian) ---------- */
static void mul_small(u64*a,size_t*len,u64 m){ u64 c=0; for(size_t i=0;i<*len;i++){ u128 t=(u128)a[i]*m+c; a[i]=(u64)t; c=(u64)(t>>64);} if(c) a[(*len)++]=c; }
static void pow3(u64*P,size_t*plen,long long m){ P[0]=1; *plen=1; u64 p40=1; for(int i=0;i<M;i++)p40*=3;
  for(long long i=0;i<m/M;i++) mul_small(P,plen,p40); u64 r=1; for(int i=0;i<m%M;i++) r*=3; if(r>1) mul_small(P,plen,r); }
static int ceillog2(size_t x){ int l=0; while(((size_t)1<<l)<x) l++; return l; }

/* ---------- Produkt hi * P mit NTT, Ergebnis als 32-Bit-Ziffern in out ---------- */
static u64 *tmp[2]; static u128 *bufc,*tailc; static size_t tmpcap=0;
static int fp_lg=-1; static long long fp_m=-1; static size_t fp_lp=0;
static size_t mul_ntt(const u64*h,size_t hl,const u64*P,size_t plen,long long m,u64*out){
  size_t hc=2*hl; size_t lp=2*plen; if((P[plen-1]>>32)==0) lp--;
  int lgstd=ceillog2(4*lp), lgneed=ceillog2(hc+lp), lgmin=ceillog2(2*lp+2);
  int lg=lgstd<lgneed?lgstd:lgneed; if(lg<lgmin) lg=lgmin; if(lg<4) lg=4;
  if(lg>tables_lg){ if(lg>24){ fprintf(stderr,"transform length too large\n"); exit(1);} build_tables(lg); }
  size_t T=(size_t)1<<lg, c=T-lp+1;
  if(T>tmpcap){ for(int i=0;i<2;i++){ free(tmp[i]); tmp[i]=malloc(T*8);} free(bufc); free(tailc); bufc=malloc(T*16); tailc=malloc(T*16); tmpcap=T; }
  if(fp_lg!=lg||fp_m!=m||fp_lp!=lp){
    for(int i=0;i<2;i++){ free(pr[i].fp); pr[i].fp=malloc(T*8); u64*f=pr[i].fp; memset(f,0,T*8);
      for(size_t j=0;j<lp;j++) f[j]=(P[j>>1]>>((j&1)*32))&0xffffffffULL;
      ntt_fwd(f,T,&pr[i]); for(size_t j=0;j<T;j++) f[j]=tom(f[j],&pr[i]); }
    fp_lg=lg; fp_m=m; fp_lp=lp; }
  u64 invM=tom(powmod(pr[0].p%pr[1].p,pr[1].p-2,pr[1].p),&pr[1]);
  u64 tinv0=tom(powmod(T,pr[0].p-2,pr[0].p),&pr[0]), tinv1=tom(powmod(T,pr[1].p-2,pr[1].p),&pr[1]);
  u32*o=(u32*)out; size_t pos=0; u128 carry=0; memset(tailc,0,(lp>1?lp-1:1)*16);
  for(size_t start=0;start<hc;start+=c){
    size_t cl=hc-start<c?hc-start:c;
#ifdef _OPENMP
#pragma omp parallel for num_threads(2)
#endif
    for(int q=0;q<2;q++){
      u64*t=tmp[q]; for(size_t j=0;j<cl;j++){ size_t idx=start+j; t[j]=(h[idx>>1]>>((idx&1)*32))&0xffffffffULL; }
      memset(t+cl,0,(T-cl)*8);
      ntt_fwd(t,T,&pr[q]); const u64*f=pr[q].fp; for(size_t j=0;j<T;j++) t[j]=mm(t[j],f[j],&pr[q]);
      ntt_inv(t,T,&pr[q]); u64 ti=q?tinv1:tinv0; size_t L=cl+lp-1; for(size_t j=0;j<L;j++) t[j]=mm(t[j],ti,&pr[q]); }
    size_t L=cl+lp-1;
    for(size_t j=0;j<L;j++){
      u64 r1=tmp[0][j], r2=tmp[1][j]; u64 d=r2>=r1?r2-r1:r2+pr[1].p-r1; u64 u=mm(d,invM,&pr[1]);
      u128 x=(u128)r1+(u128)pr[0].p*u; if(j<lp-1) x+=tailc[j]; bufc[j]=x; }
    for(size_t j=0;j<cl;j++){ u128 v=bufc[j]+carry; o[pos++]=(u32)v; carry=v>>32; }
    for(size_t j=0;j<lp-1;j++) tailc[j]=bufc[cl+j];
  }
  for(size_t j=0;j<lp-1;j++){ u128 v=tailc[j]+carry; o[pos++]=(u32)v; carry=v>>32; }
  while(carry){ o[pos++]=(u32)carry; carry>>=32; }
  if(pos&1) o[pos++]=0;
  return pos/2; // Anzahl 64-Bit-Limbs
}

/* ---------- ein Teilblock aus m<=40 Schritten, wie in bellrun.c ---------- */
static void blk(u64*k,size_t*lenp,int*sp,int m,long long*cntp,int*stopp){
  size_t len=*lenp; u128 L=k[0]; int st=*sp,cnt=0,stop=0;
  for(int j=0;j<m;j++){ vis[st]++; int idx=2*st+(int)((L&3)>>1); int t=nxt[idx]; if(t<0){stop=t;break;} L=3*(L>>1)+cc[idx]; st=t; cnt++; }
  *cntp=cnt; *sp=st; if(stop){ *stopp=stop; *lenp=len; k[0]=(u64)L; return; }
  u64 mul=1; for(int i=0;i<cnt;i++) mul*=3; int sh=64-cnt;
  u64 carry=0,prev=0; size_t q=len-1;
  for(size_t i=0;i<=q;i++){ u64 p; if(i<q){ u128 t=(u128)k[i+1]*mul+carry; p=(u64)t; carry=(u64)(t>>64);} else { p=carry; carry=0; }
    u64 out=(p<<sh)|(sh?(prev>>(64-sh)):0); prev=p; k[i]=out; }
  size_t nl=q+1; { u64 lo=prev>>(64-sh); if(lo){ k[nl++]=lo; } }
  if(nl==0){ nl=1; k[0]=0; }
  { u128 t=(u128)k[0]+(u64)L; k[0]=(u64)t; u128 c2=(t>>64)+(u64)(L>>64);
    if(nl<2){ k[1]=0; nl=2; }
    t=(u128)k[1]+(u64)c2; k[1]=(u64)t; u128 c3=(t>>64)+(u64)(c2>>64);
    size_t i=2; while(c3){ if(i>=nl){ k[i]=0; nl=i+1; } t=(u128)k[i]+(u64)c3; k[i]=(u64)t; c3=(t>>64)+(u64)(c3>>64); i++; } }
  len=nl; while(len>1&&k[len-1]==0) len--; *lenp=len;
}
static double now(){ struct timespec ts; clock_gettime(CLOCK_MONOTONIC,&ts); return ts.tv_sec+1e-9*ts.tv_nsec; }

int main(int argc,char**argv){
  long long N=atoll(argv[1]); long long B=argc>2?atoll(argv[2]):2000000;
  FILE*f=fopen("tab.txt","r"); if(fscanf(f,"%d",&n)!=1) return 1; nxt=malloc(sizeof(int)*2*n); cc=malloc(sizeof(int)*2*n);
  for(int i=0;i<n;i++){ int a,b,c,d; if(fscanf(f,"%d %d %d %d",&a,&b,&c,&d)!=4) return 1; nxt[2*i]=a;cc[2*i]=b;nxt[2*i+1]=c;cc[2*i+1]=d; } fclose(f);
  names=malloc(sizeof(char*)*n); f=fopen("tab_names.txt","r"); for(int i=0;i<n;i++){ names[i]=malloc(64); if(fscanf(f,"%63s",names[i])!=1) return 1; } fclose(f);
  vis=calloc(n,8);
  pr_init(&pr[0],9223372036636672001ULL,510271893463106651ULL);
  pr_init(&pr[1],9223372036737335297ULL,2419180138865645092ULL);
  size_t capK=(size_t)(0.6*N/64)+4*(size_t)(B/64)+8192;
  u64*k=calloc(capK+8,8),*hi=calloc(capK+8,8),*out=calloc(capK*2+8192,8);
  size_t capL=(size_t)(1.7*(B+2)/64)+4096; u64*L=calloc(capL,8),*P=calloc(capL,8);
  size_t len=1,plen=0; k[0]=92; int s=0; long long done=0;
  double t0=now(),tlow=0,tmul=0; long long nextp=100000000LL;
  long long Pm=-1;
  while(done<N){
    long long m=(N-done<B)?(N-done):B; size_t W=m+2, wl=(W+63)/64;
    double ta=now();
    size_t Ll=len<wl?len:wl; memcpy(L,k,Ll*8); if(len>=wl&&(W&63)) L[wl-1]&=((u64)1<<(W&63))-1;
    while(Ll>1&&L[Ll-1]==0) Ll--;
    size_t off=W>>6; int sh=W&63; size_t hl=0;
    if(len>off){ hl=len-off; for(size_t i=0;i<hl;i++){ u64 v=k[off+i]>>sh; if(sh&&off+i+1<len) v|=k[off+i+1]<<(64-sh); hi[i]=v; } while(hl>0&&hi[hl-1]==0) hl--; }
    int st=s; long long rem=m;
    while(rem>0){ int mmx=rem<M?(int)rem:M; long long c=0; int stp=0; blk(L,&Ll,&st,mmx,&c,&stp); done+=c; rem-=c;
      if(stp){ printf("%s at Bell %lld S_pascal=%s k mod 4=%d\n",stp==-1?"HALT":"UNKNOWN STATE",done,names[st],(int)(L[0]&3)); return 0; } }
    double tb=now(); tlow+=tb-ta;
    if(hl==0){ memcpy(k,L,Ll*8); len=Ll; }
    else {
      if(Pm!=m){ pow3(P,&plen,m); Pm=m; }
      size_t ol=mul_ntt(hi,hl,P,plen,m,out);
      u64 carry=0,prevhi=0; size_t i=0;
      for(i=0; i<ol||i<Ll||carry||prevhi; i++){ u64 v=(i<ol)?out[i]:0; u64 lo=(v<<2)|prevhi; prevhi=v>>62; u128 sum=(u128)lo+(i<Ll?L[i]:0)+carry; k[i]=(u64)sum; carry=(u64)(sum>>64); }
      len=i; while(len>1&&k[len-1]==0) len--;
    }
    tmul+=now()-tb; s=st;
    if(done>=nextp){ printf("Bell %lld  k=%zu limbs  state %s  time %.0fs (low part %.0f, products %.0f)\n",done,len,names[s],now()-t0,tlow,tmul); fflush(stdout); nextp+=100000000LL; }
  }
  int bits=(int)(64*(len-1)+64-__builtin_clzll(k[len-1]));
  printf("KCHECK %llu %d %s\n",(unsigned long long)k[0],bits,names[s]);
  printf("no halt in %lld Bells; time %.1fs (low part %.1fs, products %.1fs); B=%lld; k has %d bits; state %s\n",done,now()-t0,tlow,tmul,B,bits,names[s]);
  long long tot=0; for(int i=0;i<n;i++) tot+=vis[i];
  for(int r=0;r<6;r++){ int b=0; for(int i=1;i<n;i++) if(vis[i]>vis[b]) b=i; printf(" %s %.4f",names[b],(double)vis[b]/tot); vis[b]=-1; } printf("\n");
  return 0; }
