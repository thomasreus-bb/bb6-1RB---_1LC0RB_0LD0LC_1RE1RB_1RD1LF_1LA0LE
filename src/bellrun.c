// Bell-Bahn mit Block-Spruengen, exakt. Uebersetzen: gcc -O3 -march=native -o bellrun bellrun.c
// Aufruf: ./bellrun N [checkpoint.bin]     (tab.txt, tab_names.txt im selben Ordner)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>
typedef unsigned __int128 u128; typedef uint64_t u64;
#define M 40
int n; int *nxt,*cc; long long *vis; char **names;
u64 *k; size_t len; size_t cap; int s; long long done;
static void save(const char*f){FILE*o=fopen("ck.tmp","wb");fwrite(&len,8,1,o);fwrite(&s,4,1,o);fwrite(&done,8,1,o);fwrite(vis,8,n,o);fwrite(k,8,len,o);fclose(o);rename("ck.tmp",f);}
int main(int argc,char**argv){
  long long N=atoll(argv[1]); const char*ck=argc>2?argv[2]:NULL;
  FILE*f=fopen("tab.txt","r"); fscanf(f,"%d",&n); nxt=malloc(8*n);cc=malloc(8*n); // 2 Eintraege je Zustand
  nxt=realloc(nxt,sizeof(int)*2*n);cc=realloc(cc,sizeof(int)*2*n);
  for(int i=0;i<n;i++){int a,b,c,d;fscanf(f,"%d %d %d %d",&a,&b,&c,&d);nxt[2*i]=a;cc[2*i]=b;nxt[2*i+1]=c;cc[2*i+1]=d;} fclose(f);
  names=malloc(sizeof(char*)*n); f=fopen("tab_names.txt","r"); for(int i=0;i<n;i++){names[i]=malloc(64);fscanf(f,"%63s",names[i]);} fclose(f);
  vis=calloc(n,8); cap=(size_t)(0.585*N/64)+1024; k=calloc(cap,8);
  len=1;k[0]=92;s=0;done=0;
  if(ck&&(f=fopen(ck,"rb"))){fread(&len,8,1,f);fread(&s,4,1,f);fread(&done,8,1,f);fread(vis,8,n,f);fread(k,8,len,f);fclose(f);printf("fortgesetzt bei Bell %lld\n",done);}
  u64 P3=1;for(int i=0;i<M;i++)P3*=3;
  time_t t0=time(0),last=t0;
  while(done<N){
    int m=(N-done<M)?(int)(N-done):M;
    u128 L=k[0]; int st=s,cnt=0,stop=0;
    for(int j=0;j<m;j++){
      vis[st]++; int idx=2*st+(int)((L&3)>>1); int t=nxt[idx];
      if(t<0){stop=t;break;}
      L=3*(L>>1)+cc[idx]; st=t; cnt++;
    }
    if(stop){done+=cnt;printf("%s bei Bell %lld S_pascal=%s k mod 4=%d\n",stop==-1?"HALT":"UNBEKANNTER ZUSTAND",done,names[st],(int)(L&3));
      save("halt_state.bin");return 0;}
    u64 mul=P3; int sh=64-M;
    if(cnt<M){mul=1;for(int i=0;i<cnt;i++)mul*=3;sh=64-cnt;}
    // k_neu = L + 2^sh * mul * q, q = k[1..len-1]
    u64 carry=0, prev=0; size_t q=len-1;
    for(size_t i=0;i<=q;i++){
      u64 p;
      if(i<q){u128 t=(u128)k[i+1]*mul+carry;p=(u64)t;carry=(u64)(t>>64);}
      else {p=carry;carry=0;}
      u64 out=(p<<sh)|(sh? (prev>>(64-sh)):0);
      prev=p; k[i]=out;
    }
    size_t nl=q+1;
    { u64 last_out=prev>>(64-sh); if(last_out){k[nl++]=last_out;} }
    if(nl==0){nl=1;k[0]=0;}
    // + L (128 Bit)
    { u128 t=(u128)k[0]+(u64)L; k[0]=(u64)t; u128 c2=(t>>64)+(u64)(L>>64);
      size_t i=1; if(nl<2){k[1]=0;nl=2;}
      t=(u128)k[1]+(u64)c2; k[1]=(u64)t; u128 c3=(t>>64)+(u64)(c2>>64);
      i=2; while(c3){ if(i>=nl){k[i]=0;nl=i+1;} t=(u128)k[i]+(u64)c3; k[i]=(u64)t; c3=(t>>64)+(u64)(c3>>64); i++; } }
    len=nl; while(len>1&&k[len-1]==0)len--;
    s=st; done+=cnt;
    if(ck&&time(0)-last>300){save(ck);last=time(0);}
    { static long long nextp=100000000LL; if(done>=nextp){ printf("Bell %lld  k=%zu Limbs  Zustand %s  Zeit %lds\n",done,len,names[s],(long)(time(0)-t0)); fflush(stdout); nextp+=100000000LL; } }
  }
  int bits=(int)(64*(len-1)+64-__builtin_clzll(k[len-1]));
  printf("KCHECK %llu %d %s\n",(unsigned long long)k[0],bits,names[s]);
  printf("kein Halt in %lld Bells; Zeit %lds; k hat %d Bit; Zustand %s\n",done,(long)(time(0)-t0),bits,names[s]);
  long long tot=0;for(int i=0;i<n;i++)tot+=vis[i];
  for(int r=0;r<6;r++){int b=0;for(int i=1;i<n;i++)if(vis[i]>vis[b])b=i;printf(" %s %.4f",names[b],(double)vis[b]/tot);vis[b]=-1;} printf("\n");
  if(ck)save(ck); return 0;}
