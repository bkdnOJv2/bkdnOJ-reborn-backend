#include<bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef pair<int, int> II;
const int N = 5e5 + 3;
const ll MOD = 1e9 + 7;
const ll INF = 1e18;

string s;
int k, n, sum[N];

int main(){
    //freopen(".inp","r",stdin);
    //freopen(".out","w",stdout);
    ios_base::sync_with_stdio(0);
    cin.tie(0);
    cin >> s >> k;
    n = s.size();
    s = ' ' + s;
    while(k --){
       int shift, l, r;
       cin >> shift >> l >> r;
       sum[l] += shift;
       sum[r + 1] -= shift;
    }
    for(int i = 1; i <= n; i ++) sum[i] += sum[i - 1];
    for(int i = 1; i <= n; i ++){
        int cur = s[i] - 'A';
        cout << char('A' + (cur + sum[i]) % 26);
    }
    cout << endl;
    return 0;
}

