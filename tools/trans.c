#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int W[6][2],D[6][2],NS[6][2],H[6][2];
int main(int argc,char**argv){
  const char*tm="1RB---_1LC0RB_0LD0LC_1RE1RB_1RD1LF_1LA0LE";
  for(int s=0;s<6;s++)for(int b=0;b<2;b++){
    const char*t=tm+s*7+b*3;
    if(t[0]=='-'){H[s][b]=1;}else{H[s][b]=0;W[s][b]=t[0]-'0';D[s][b]=t[1]=='R'?1:-1;NS[s][b]=t[2]-'A';}
  }
  const char*S0=argv[1]; int kmax=atoi(argv[2]); int kmin=atoi(argv[3]);
  long SZ=4000000; unsigned char*tape=malloc(SZ); long OFF=SZ/2;
  for(int k=kmin;k<=kmax;k++){
    memset(tape,0,SZ);
    for(int i=0;i<k;i++)tape[OFF-1-i]=1;
    int sl=strlen(S0); for(int i=0;i<sl;i++)tape[OFF+i]=S0[i]-'0';
    long pos=OFF,hi=OFF+sl-1; int st=5; long long n=0; long long left=k;
    long long last=-1000000; long lastk=-1; int seen_first=0; int done=0;
    long long cap=100000000LL+ (long long)k*k*20;
    while(n<cap){
      int b=tape[pos];
      if(H[st][b]){printf("%s %d HALT %lld\n",S0,k,n);done=1;break;}
      if(st==5 && b==1){
        long r=0,p=pos-1; while(tape[p]==1){r++;p--;}
        if(r==left && r>0){
          if(!seen_first){seen_first=1;last=n;lastk=r;}
          else{
            int cont=(n-last<=6 && r<lastk);
            if(!cont){
              long e=hi; while(e>pos && tape[e]==0)e--;
              char S[300]; long len=e-pos+1; if(len>290)len=290;
              for(long i=0;i<len;i++)S[i]='0'+tape[pos+i]; S[len]=0;
              printf("%s %d %ld %s %lld\n",S0,k,r,S,n); done=1;break;
            }
            last=n;lastk=r;
          }
        }
      }
      int w=W[st][b],d=D[st][b],ns=NS[st][b];
      tape[pos]=w;
      if(d==1){left+=w;pos++; if(pos>hi)hi=pos;} else {pos--;left-=tape[pos];}
      st=ns;n++;
    }
    if(!done)printf("%s %d NONE\n",S0,k);
  }
  return 0;
}
