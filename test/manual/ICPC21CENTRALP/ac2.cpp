#include<bits/stdc++.h>
using namespace std;
int main(){
    ios_base::sync_with_stdio(0);cin.tie(0);cout.tie(0);
    int t;
    cin>>t;
    while (t--){
        int a,b,c,d;
        cin>>a>>b>>c>>d;
        if (a < d || b < d || c < d){
            cout<<0<<'\n';
            continue;
        }
        int res = 0;
        int tmp = a/d - 1;
        a -= tmp * d;
        res += b * c * tmp;
         tmp = b/d - 1;
        b -= tmp * d;
        res += a * c * tmp;
         tmp = c/d - 1;
        c -= tmp * d;
        res += b * a * tmp;
        res += a*b*c / min(min(a,b),c);
        cout<<res<<'\n';
    }
    return 0;
}

