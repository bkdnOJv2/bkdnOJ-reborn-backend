#include <iostream>
#include <vector>

using namespace std;

const int N = 1e5 + 10;

bool mark[N];

int mex(const vector<int>& vals)
{
    int n = vals.size();
    fill(mark, mark + n + 5, false);
    for (int v : vals) mark[v] = true;
    int ret = 0;
    while (mark[ret]) ++ret;
    return ret;
}

void dfs(int u, bool vis[], int f[], vector<int> g[])
{
    if (vis[u]) return;
    vis[u] = true;
    vector<int> vals;
    for (int v : g[u]) {
        dfs(v, vis, f, g);
        vals.push_back(f[v]);
    }
    f[u] = mex(vals);
}

vector<int> gFow[N], gBak[N];
int fow[N], bak[N];
bool visFow[N], visBak[N];

int main()
{
    cin.tie(NULL); ios_base::sync_with_stdio(false);
    int tests;
    cin >> tests;
    while (tests--) {
        int n, m, sA, sB;
        cin >> n >> m >> sA >> sB;

        string tmp;
        cin >> tmp;

        fill(gFow + 1, gFow + 1 + n, vector<int>());
        fill(gBak + 1, gBak + 1 + n, vector<int>());
        fill(visFow + 1, visFow + 1 + n, false);
        fill(visBak + 1, visBak + 1 + n, false);

        for (int i = 0; i < m; ++i) {
            int u, v;
            cin >> u >> v;
            gFow[u].push_back(v);
            gBak[v].push_back(u);
        }

        int X, Y, K;
        cin >> X >> Y >> K;
        for (int i = 0; i < K; ++i) {
            int t, u, v, p, q;
            cin >> t >> u >> v >> p >> q;
        }
        dfs(sA, visFow, fow, gFow), dfs(sB, visBak, bak, gBak);
//        for (int i = 1; i <= n; ++i) {
//            cout << "#" << i << ": " << fow[i] << ' ' << bak[i] << '\n';
//        }
        cout << ((fow[sA] ^ bak[sB] ^ (K & 1)) > 0 ? "YES" : "NO") << '\n';
    }
    return 0;
}

