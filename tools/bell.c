#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(){
  const char*tm="1RB---_1LC0RB_0LD0LC_1RE1RB_1RD1LF_1LA0LE";
  int W[6][2],D[6][2],NS[6][2],H[6][2];
  for(int s=0;s<6;s++)for(int b=0;b<2;b++){
    const char*t=tm+s*7+b*3;
    if(t[0]=='-'){H[s][b]=1;}else{H[s][b]=0;W[s][b]=t[0]-'0';D[s][b]=t[1]=='R'?1:-1;NS[s][b]=t[2]-'A';}
  }
  long SZ=400000000L;
  unsigned char*tape=calloc(SZ,1);
  long OFF=SZ/2;
  long pos=OFF,hi=OFF; int st=0; long long n=0;
  long long left=0; long long last=-1000000; long lastk=-1; int cnt=0;
  while(cnt<20){
    int b=tape[pos];
    if(H[st][b]){printf("HALT at %lld\n",n);return 0;}
    if(st==5 && b==1){
      long r=0,p=pos-1; while(tape[p]==1){r++;p--;}
      if(r==left && r>0){
        int cont=(n-last<=6 && lastk>=0 && r<lastk);
        if(!cont){
          long e=hi; while(e>pos && tape[e]==0)e--;
          char S[256]; long len=e-pos+1; if(len>250)len=250;
          for(long i=0;i<len;i++)S[i]='0'+tape[pos+i]; S[len]=0;
          printf("%d step %lld k %ld S=%s\n",cnt,n,r,S); fflush(stdout);
          cnt++;
        }
        last=n; lastk=r;
      }
    }
    int w=W[st][b],d=D[st][b],ns=NS[st][b];
    tape[pos]=w;
    if(d==1){left+=w;pos++; if(pos>hi)hi=pos;}
    else{pos--;left-=tape[pos];}
    st=ns;n++;
    if(pos<OFF-SZ/2+1000||pos>OFF+SZ/2-1000){printf("tape overflow\n");return 1;}
  }
  return 0;
}
