#include <bits/stdc++.h>
#define mod 1000000007
using namespace std;

int n,q;
int a[100005];
int cl[100005];
vector < int > g[100005];
int pr[3][100005][20];
int vl[2][100005][20];
int d[100005];
int p=0;

void DFS(int u)
{
    cl[u]=1;
    vl[0][u][0]=vl[1][u][0]=a[u];

    for(auto &v : g[u])
    if(!cl[v])
        pr[0][v][0]=u,d[v]=d[u]+1,DFS(v);
}

int LCA(int u,int v)
{
    while(d[u]>d[v])
    {
        int h=log2(d[u]-d[v]);
        u=pr[0][u][h];
    }

    while(d[v]>d[u])
    {
        int h=log2(d[v]-d[u]);
        v=pr[0][v][h];
    }

    if(u==v)
        return u;

    int h=log2(d[u]);

    while(h>=0)
    {
        if(pr[0][u][h]!=pr[0][v][h])
            u=pr[0][u][h],v=pr[0][v][h];

        h--;
    }

    return pr[0][u][0];
}

int main ()
{
    //freopen("main.inp","r",stdin);

    cin >> n >> q;

    for(int i=1;i<=n;++i)
        cin >> a[i];

    for(int i=1;i<n;++i)
    {
        int u,v;
        cin >> u >> v;
        g[u].push_back(v);
        g[v].push_back(u);
    }

    d[1]=1;
    DFS(1);

    int k=log2(n);

    for(int i=1;i<=k;++i)
    for(int j=1;j<=n;++j)
    {
        pr[0][j][i]=pr[0][pr[0][j][i-1]][i-1];
        vl[0][j][i]=min(vl[0][j][i-1],vl[0][pr[0][j][i-1]][i-1]);
        vl[1][j][i]=max(vl[1][j][i-1],vl[1][pr[0][j][i-1]][i-1]);
    }

    for(int i=1;i<=n;++i)
    {
        int h=log2(d[i]);
        int u=i;

        while(h>=0)
        {
            if(vl[0][u][h]>=a[i])
                u=pr[0][u][h];

            h--;
        }

        pr[1][i][0]=u;

        h=log2(d[i]);
        u=i;

        while(h>=0)
        {
            if(vl[1][u][h]<=a[i])
                u=pr[0][u][h];

            h--;
        }

        pr[2][i][0]=u;
    }

    for(int i=1;i<=k;++i)
    for(int j=1;j<=n;++j)
    for(int z=1;z<=2;++z)
        pr[z][j][i]=pr[z][pr[z][j][i-1]][i-1];

    for(int i=1;i<=q;++i)
    {
        int u,v;

        cin >> u >> v;

        u=(u+p)%n+1;
        v=(v+p)%n+1;

        int z=LCA(u,v);

        int ans=0;

        int h=log2(d[u]);

        while(h>=0)
        {
            if(d[pr[2][u][h]]>=d[z])
                u=pr[2][u][h],ans+=(1<<h);

            h--;
        }

        h=log2(d[v]);

        while(h>=0)
        {
            if(d[pr[2][v][h]]>=d[z])
                v=pr[2][v][h];

            h--;
        }

        if(a[v]>a[u])
            ans++;

        h=log2(d[v]);

        while(h>=0)
        {
            if(d[pr[1][v][h]]>=d[z]&&a[pr[1][v][h]]>a[u])
                v=pr[1][v][h],ans+=(1<<h);

            h--;
        }

        cout << ans+1<<"\n";

        p=ans;
    }
}

