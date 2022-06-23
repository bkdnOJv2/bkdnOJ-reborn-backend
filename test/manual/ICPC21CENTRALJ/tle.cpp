#include <bits/stdc++.h>
using namespace std;
const int N = 5e5 + 5;

const int Mod = 998244353;

int n, k, P[N], a[N];
long long b[N];
void Input(){
    cin >> n >> k;
    for (int i = 1; i <= n; i++) cin >> a[i];
}

void Solve(){
    for (int i = 1; i <= n; i++) b[i] = 1;
    for (int i = 1; i <= k; i++) {
        long long Sum = 0;
        for (int i = 1; i <= n; i++) {
            b[i] = b[i] * a[i] % Mod;
            Sum = (Sum + b[i]) % Mod;
        }
        cout << Sum << endl;
    }
}

int main(){
    if(fopen("test.inp", "r")) {
        freopen("test.inp", "r", stdin);
        freopen("test.out", "w", stdout);
    }
    int testcase = 1;
    ///cin >> testcase;
    while (testcase--) {
        Input();
        Solve();
    }
}

