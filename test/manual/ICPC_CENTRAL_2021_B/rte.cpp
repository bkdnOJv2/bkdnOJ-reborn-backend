#include<bits/stdc++.h>
using namespace std;

template<class T> bool umax(T &a, T b) { if (a<b) { a=b; return 1; } return 0; }
template<class T> bool umin(T &a, T b) { if (a>b) { a=b; return 1; } return 0; }

void setIO(string name="") {
    ios_base::sync_with_stdio(0);cin.tie(0);cout.tie(0);
    if (name.size()) freopen((name+".inp").c_str(),"r",stdin);
    if (name.size()) freopen((name+".out").c_str(),"w",stdout);
}

#define ll long long
#define ff first
#define ss second

typedef pair<int, int> ii;
const int NmX = 1e6 + 7, mod = 1e9+7;

int n,t;
int a[NmX];
ll s = 1,ans = INT_MIN;

int main(){
    setIO("");
	cin >> n;
	for(int i = 1; i <= n; ++i)
	{
		cin >> a[i];
		if(a[i] == 0 && t == 0) { t = 1; continue; }
		else if(a[i] == 0 && t == 1) { cout << 0; return 0; }
		s = (s%mod * a[i]%mod)%mod;
	}	
	
	for(int i = 1; i <= n; ++i)
		ans = max(ans,s/a[i]);
	cout << max(ans,s);
    return 0;
}
