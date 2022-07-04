#include <bits/stdc++.h>
typedef long long ll;
using namespace std;
int a[2000],am[2000];
int main()
{
    int n,so_am=0,so_duong=0,zero=0;
    ll ans=1;
    cin>>n;
    for (int i=1;i<=n;i++)
    {
        cin>>a[i];
        if (a[i]>0) {
                        so_duong++;
                        ans=(ans*a[i])%1000000007;
                    }
        if (a[i]<0) {
                        so_am++;
                        am[so_am]=a[i];
                    }
        if (a[i]==0) zero++;
    }
    switch (zero)
    {
        case 0: {
                    if ( so_am % 2 == 1 ) { sort(am+1,am+1+n); am[so_am]=1; }
                    for (int i=1;i<=so_am;i++) ans=(ans*am[i])%1000000007;

        } break;
        case 1: {
                    for (int i=1;i<=so_am;i++) ans=(ans*am[i])%1000000007;
                    if (ans<0) ans=0;

        } break;
        default: ans=0;
    }
    cout<<ans;
    return 0;
}
