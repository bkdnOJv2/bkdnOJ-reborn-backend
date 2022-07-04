#include <bits/stdc++.h>
#define MAXN 100000
using namespace std;
vector<int> G[MAXN+5];
int N,M,type[MAXN+5];
#define MOD 1000000007
long long F[MAXN+5];
long long cnt=0;
void dfs(int u)
{
    cnt++;
    type[u]=1;
    for(auto v : G[u]) if(!type[v]) dfs(v); 
}
int main()
{
    //freopen("M.inp","r",stdin);
    ios_base::sync_with_stdio(0);cin.tie(0);
    F[0]=1;
    for(int i=1;i<=MAXN;++i) F[i]=F[i-1]*i%MOD;
    cin>>N>>M;

    for(int i=0;i<M;++i)
    {
        int u,v;
        cin>>u>>v;
        G[u].push_back(v);
        G[v].push_back(u);
    }
    long long ans=0;
    for(int u=0;u<N;++u) if(!type[u]) 
    {
        cnt=0;
        dfs(u);
        if(cnt<=2) continue;
        ans=(ans+F[cnt])%MOD;
    }
    cout<<ans;

}

