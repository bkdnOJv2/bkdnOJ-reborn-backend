#include <bits/stdc++.h>

using namespace std;
int f[101][101][101][11];
int main()
{

    ios_base::sync_with_stdio(0);cin.tie(0);cout.tie(0);
    for (int u=1;u<=10;++u)
    {
        for (int i=1;i<=100;++i)
         for (int j=1;j<=100;++j)
          for (int k=1;k<=100;++k)
         {
             if (i>=u) f[i][j][k][u]=max(f[i][j][k][u],f[i-u][j][k][u]+k*j);
             if (j>=u) f[i][j][k][u]=max(f[i][j][k][u],f[i][j-u][k][u]+i*k);
             if (k>=u) f[i][j][k][u]=max(f[i][j][k][u],f[i][j][k-u][u]+i*j);
         }
    }
    int te;
    cin>>te;
    while (te--)
    {
        int x,y,z,u;
        cin>>x>>y>>z>>u;
        cout<<f[x][y][z][u]<<'\n';
    }
    return 0;
}

