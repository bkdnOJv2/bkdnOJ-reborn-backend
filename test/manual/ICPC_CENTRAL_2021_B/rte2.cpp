#include "bits/stdc++.h"
using namespace std;
#define int long long
#define cebug(x) cerr << "[" << #x << "] = " << x << endl

const int N=1e5;
const int mod=1e9+7;

int n,a[N],pro=1;
void sol(){
	cin>>n;
	map <int,int> mp;
	for(int i=1; i<=n; i++){
		cin>>a[i];
		mp[a[i]]++;
		if(a[i]==0) continue;
		pro*=a[i];
		pro%=mod;
	}
	if(pro>0){
		cout<<pro;
		return;
	}
	if(mp[0]==1){
		cout<<max(0LL,pro);
	}
	else if(mp[0]>1) cout<<0;
	else{
		int ans=max(0LL,pro);
		for(int i=1; i<=n; i++){
			ans=max(ans,(pro/ans)%mod);
		}
		cout<<ans%mod;
	}
}
signed main(){
	ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    //freopen(".inp", "r", stdin);
    //freopen(".out", "w", stdout);
    int t=1;
    //cin>>t; 
    while(t--){
    	sol();
    }
    cerr << "\nTime elapsed: " << 1000.0 * clock() / CLOCKS_PER_SEC << " ms.\n";
    return 0;
}
