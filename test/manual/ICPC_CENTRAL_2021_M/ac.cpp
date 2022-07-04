#include <bits/stdc++.h>

using namespace std;

const int MOD = 1e9+7;
int add(int x, int y) {
    if ((x+=y) >= MOD) x -= MOD;
    return x;
}
int mul(long long x, int y) {
    return x * y % MOD;
}

const int N = 1e5+7;
int numNode, numEdge;
int fac[N];
int fa[N];
int res;

int root(int x) {
    return fa[x] < 0 ? x : fa[x] = root(fa[x]);
}

void unite(int u, int v) {
    u = root(u);
    v = root(v);
    if (u == v) return;
    if (fa[u] > fa[v]) swap(u,v);
    fa[u] += fa[v];
    fa[v] = u;
}

int main() {
    cin.tie(nullptr)->sync_with_stdio(false);
    #ifdef NHPHUCQT
    freopen("demo.inp", "r", stdin);
    freopen("demo.out", "w", stdout);
    #endif

    fac[0] = 1;
    for (int i = 1; i < N; ++i) {
        fac[i] = mul(fac[i-1], i);
    }

    cin >> numNode >> numEdge;
    memset(fa, -1, sizeof fa);
    for (int i = 0; i < numEdge; ++i) {
        int x, y;
        cin >> x >> y;
        unite(x,y);
    }
    for (int i = 0; i < numNode; ++i) {
        if (root(i) == i) {
            if (-fa[i] > 2) {
                res = add(res, fac[-fa[i]]);
            }
        }
    }
    cout << res;
    return 0;   
}

