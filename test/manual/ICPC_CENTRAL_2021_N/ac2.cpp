#include <bits/stdc++.h>
#define ii pair<int, int>
#define fi first
#define se second
#define pb push_back
#define all(x) x.begin(),x.end()
#define ll long long
#define FOR(i,a,b) for (int i=a; i<=b; ++i)
#define FORD(i,b,a) for (int i=b; i>=a; --i)
using namespace std;

const int MAX = 2e5+6;
const int MOD = 1e9+7;

string s, t;
int d[26][MAX], c[26][MAX], Next[MAX][26], bo[26];
vector<char> res;

bool Check(int st, int nn){
	FOR(i,0,25){
		if (d[i][st] < c[i][t.size()] - bo[i]) return false;
	}
	return true;
}

bool Remain(int i){
	return c[i][t.size()] > bo[i];
}

int main(int argc, char const *argv[])
{
	ios_base::sync_with_stdio(0);
	cin.tie(0); cout.tie(0);
	#ifdef LOCAL
	    freopen("input.txt","r",stdin);
	#endif

	cin >> s >> t;
	FOR(i,1,s.size()){
		d[s[i-1]-'a'][i] = 1;
	}
	FORD(i,s.size(),1){
		FOR(j,0,25){
			d[j][i]+= d[j][i+1];
		}
	}
	FOR(i,1,t.size()){
		FOR(j,0,25) c[j][i] += c[j][i-1];
		c[t[i-1]-'a'][i]++;
	}

	FOR(i,0,25) Next[s.size()+1][i] = s.size() + 3;
	FORD(i,s.size(),1){
		FOR(j,0,25){
			Next[i][j] = Next[i+1][j];
		}
		Next[i][s[i-1]-'a'] = i;
	}
	

	int st = 1;
	FOR(i,1,t.size()){
		// int l = st, r = s.size(), pos = -1;
		// while (l<=r){
		// 	int mid = (l+r)/2;
		// 	if (Check(mid,i)){
		// 		l = mid+1;
		// 		pos = mid;
		// 	}
		// 	else	r = mid-1;
		// }
		// cerr << pos << " " << st << "\n";
		// if (pos==-1){
		// 	cout << -1;
		// 	return 0;
		// }
		bool Ok = false;
		FOR(Char,0,25){
			if (Check(Next[st][Char],i) && Remain(Char)){
				res.push_back(Char);
				bo[Char]++;
				// cout << (char)(Char+'a') << "\n";
				st = Next[st][Char]+1;
				Ok = true;
				break;
			}
		}
		if (!Ok){
			cout << -1;
			return 0;
		}
	}
	for(char c: res){
		cout << (char)(c+'a');
	}
	return 0;
}
