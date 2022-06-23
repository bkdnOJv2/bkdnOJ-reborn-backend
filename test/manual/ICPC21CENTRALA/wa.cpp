#include <bits/stdc++.h>

#define taskname ""
#define pb push_back
#define eb emplace_back
#define fi first
#define se second
#define all(x) (x).begin(), (x).end()
#define rall(x) (x).rbegin(), (x).rend()
#define for0(i, n) for (int i = 0; i < (int)(n); ++i)
#define for1(i, n) for (int i = 1; i <= (int)(n); ++i)
#define ford(i, n) for (int i = (int)(n) - 1; i >= 0; --i)
#define fore(i, a, b) for (int i = (int)(a); i <= (int)(b); ++i)

using namespace std;

typedef long long ll;
typedef long double ld;
typedef vector <int> vi;

template<class T> bool uin(T &a, T b)
{
    return a > b ? (a = b, true) : false;
}
template<class T> bool uax(T &a, T b)
{
    return a < b ? (a = b, true) : false;
}

mt19937 rng(chrono::system_clock::now().time_since_epoch().count());

const int maxN = 200 + 10;

int n, a[maxN][maxN], b[maxN][maxN], c[maxN][maxN], p[maxN];
vector <pair <int, int>> adj[maxN];
bool flag[maxN];

int root(int u)
{
    return u == p[u] ? u : p[u] = root(p[u]);
}

bool unify(int u, int v)
{
    u = root(u);
    v = root(v);
    if (u == v)
    {
        return 0;
    }
    p[v] = u;
    return 1;
}

void solve()
{
    cin >> n;
    for0(i, n)
    {
        for0(j, n)
        {
            a[i][j] = b[i][j] = c[i][j] = 0;
        }
        adj[i].clear();
        p[i] = i;
    }
    for0(i, n)
    {
        for0(j, n)
        {
            cin >> a[i][j];
        }
    }
    vector <array <int, 3>> edges;
    for0(i, n)
    {
        for0(j, n)
        {
            edges.pb({a[i][j], i, j});
        }
    }
    sort(all(edges), greater <array <int, 3>>());
    for (auto &edge: edges)
    {
        int u = edge[1], v = edge[2];
        if (unify(u, v))
        {
            c[u][v] = c[v][u] = edge[0];
            adj[u].eb(v, edge[0]);
            adj[v].eb(u, edge[0]);
        }
    }
    for0(i, n)
    {
        queue <int> q;
        q.push(i);
        fill(flag, flag + n, 0);
        flag[i] = 1;
        b[i][i] = 1e6;
        while (!q.empty())
        {
            int u = q.front();
            q.pop();
            for (auto &e: adj[u])
            {
                int v, w;
                tie(v, w) = e;
                if (!flag[v])
                {
                    b[i][v] = min(b[i][u], w);
                    q.push(v);
                    flag[v] = 1;
                }
            }
        }
    }
    for0(i, n)
    {
        b[i][i] = 0;
    }
    bool ok = 1;
    for0(i, n)
    {
        for0(j, n)
        {
            ok &= (a[i][j] == b[i][j]);
        }
    }
    cout << (ok ? "YES" : "NO") << "\n";
    if (ok)
    {
        for0(i, n)
        {
            for0(j, n)
            {
                cout << c[i][j] << " ";
            }
            cout << "\n";
        }
    }
}

int main()
{
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    int T = 1;
    cin >> T;
    for1(t, T)
    {
        cout << "Case #" << t << ": ";
        solve();
    }
    return 0;
}

