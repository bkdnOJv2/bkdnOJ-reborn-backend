#pragma GCC optimize("Ofast")
#pragma GCC optimization("unroll-loops")
#pragma GCC target("avx,avx2,fma")

#include <bits/stdc++.h>
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/trie_policy.hpp>
#include <ext/rope>

using namespace std;
using namespace __gnu_pbds;
using namespace __gnu_cxx;

mt19937 rng(chrono::steady_clock::now().time_since_epoch().count());

#define fi first
#define se second
#define pb push_back
#define eb emplace_back
#define mp make_pair
#define gcd __gcd
#define fastio ios_base::sync_with_stdio(0); cin.tie(0); cout.tie(0)
#define rep(i, n) for (int i=0; i<(n); i++)
#define rep1(i, n) for (int i=1; i<=(n); i++)
#define all(x) (x).begin(), (x).end()
#define rall(x) (x).rbegin(), (x).rend()
#define endl "\n"

typedef long long ll;
typedef unsigned long long ull;
typedef unsigned uint;
typedef long double ld;
typedef pair<int, int> pii;
typedef pair<ll, ll> pll;
typedef vector<int> vi;
typedef vector<vector<int>> vvi;
typedef vector<ll> vll;
typedef vector<vector<ll>> vvll;
typedef vector<bool> vb;
typedef vector<vector<bool>> vvb;
template<typename T, typename cmp = less<T>>
using ordered_set=tree<T, null_type, cmp, rb_tree_tag, tree_order_statistics_node_update>;
typedef trie<string, null_type, trie_string_access_traits<>, pat_trie_tag, trie_prefix_search_node_update> pref_trie;

struct dsu {
    vi d;
    dsu(int n): d(n, -1) {}
    int find(int x) {return d[x] < 0 ? x : d[x] = find(d[x]);}
    bool join(int x, int y) {
        x = find(x), y = find(y);
        if(x == y) return 0;
        if(d[x] > d[y]) swap(x, y);
        d[x] += d[y]; d[y] = x;
        return 1;
    }
    int size(int x) {return -d[find(x)];}
};

vvi construct(const vector<tuple<int, int, int>>& edges, int n) {
    vector<vector<pii>> adj(n);
    for(auto& [w, u, v]: edges) {
        adj[u].eb(v, w);
        adj[v].eb(u, w);
    }
    vvi mat(n, vi(n));
    auto dfs = [&](int u, vi& mat, int p = -1) -> void {
        auto dfs = [&](int u, vi& mat, int p = -1, const auto& self) -> void {
            for(auto& [v, w]: adj[u]) if(v != p) {
                mat[v] = min(mat[u], w);
                self(v, mat, u, self);
            }
        };
        dfs(u, mat, p, dfs);
    };
    rep(i, n) {
        mat[i][i] = INT_MAX;
        dfs(i, mat[i]);
        mat[i][i] = 0;
    }
    return mat;
}

int32_t main() {
    fastio;
    int T; cin >> T;
    rep1(t, T) {
        int n; cin >> n;
        vector<tuple<int, int, int>> edges, mst;
        vvi a(n, vi(n));
        rep(i, n) rep(j, n) {
            cin >> a[i][j];
            if(a[i][j] && i < j) edges.eb(a[i][j], i, j);
        }
        sort(rall(edges));
        dsu d(n);
        for(auto& [w, u, v]: edges) if(d.join(u, v)) {
            mst.eb(w, u, v);
        }
        if(construct(mst, n) != a) cout << "Case #" << t << ": NO\n";
        else {
            vvi ans(n, vi(n));
            for(auto& [w, u, v]: mst) ans[u][v] = ans[v][u] = w;
            cout << "Case #" << t << ": YES\n";
            rep(i, n) rep(j, n) cout << ans[i][j] << " \n"[j + 1 == n];
        }
    }
}
