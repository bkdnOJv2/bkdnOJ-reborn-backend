#include <bits/stdc++.h>

using namespace std;
int f[101][101][101][11];
int main()
{

    ios_base::sync_with_stdio(0);cin.tie(0);cout.tie(0);
    for (int u=1;u<=10;++u)
    {
        for (int i=u;i<=100;++i)
         for (int j=u;j<=100;++j)
          for (int k=u;k<=100;++k)
         {
              f[i][j][k][u]=max(f[i][j][k][u],f[i-u][j][k][u]+k*j);
              f[i][j][k][u]=max(f[i][j][k][u],f[i][j-u][k][u]+i*k);
              f[i][j][k][u]=max(f[i][j][k][u],f[i][j][k-u][u]+i*j);
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
