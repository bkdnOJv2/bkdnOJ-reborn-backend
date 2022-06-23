#include<bits/stdc++.h>
using namespace std;
using ll = long long;

const int N = 100005;

int n;
ll x[N], y[N], w[N], h[N];

int vertex[N][2];
struct reg {
	ll lx, rx, ly, ry;
} a[N][2];

bool insect(int i, int j, int d1, int d2) {
	ll lx = max(a[i][d1].lx, a[j][d2].lx);
	ll rx = min(a[i][d1].rx, a[j][d2].rx);
	ll ly = max(a[i][d1].ly, a[j][d2].ly);
	ll ry = min(a[i][d1].ry, a[j][d2].ry);
	if (lx < rx && ly < ry) {
		return 1;
	} else {
		return 0;
	}
}

vector<int> adj[N];
vector<pair<int, int>> edges;
int now, num[N], low[N];
stack<int> stk;
int nComp, comp[N];
int vis[N], inDex[N];

void dfs(int u) {
    vis[u] = 1;
    num[u] = low[u] = ++now;
    stk.push(u);
    for (int v : adj[u]) {
        if (vis[v] == 0) {
            dfs(v);
            low[u] = min(low[u], low[v]);
        } else if (vis[v] == 1) {
            low[u] = min(low[u], num[v]);
        }
    }
    if (num[u] == low[u]) {
        nComp++;
        while (1) {
            if (stk.size() == 0) break;
            int v = stk.top();
            stk.pop();
            comp[v] = nComp; vis[v] = -1;
            if (v == u) break;
        }
    }
}

int par[N];

int find(int i) {
	if (par[i] == i) {
		return i;
	} else {
		return par[i] = find(par[i]);
	}
}
void uni(int u, int v) {
	int paru = find(u);
	int parv = find(v);
	if (paru != parv) par[paru] = parv;
}

void dfs1(int u) {
    vis[u] = 1;
    for (int v : adj[u]) {
        if (vis[v] == 0) {
            dfs1(v);
        }
    }
    inDex[u] = ++now;
}

int main() {
	ios_base::sync_with_stdio(0); cin.tie(0);

	cin >> n;
	for (int i = 1; i <= n; i++) {
		cin >> x[i] >> y[i] >> w[i] >> h[i];
		x[i] *= 2; y[i] *= 2;
		vertex[i][0] = i;
		vertex[i][1] = i + n;
		a[i][0] = {x[i] - w[i], x[i] + w[i], y[i] - h[i], y[i] + h[i]};
		a[i][1] = {x[i] - h[i], x[i] + h[i], y[i] - w[i], y[i] + w[i]};
	}

	for (int i = 1; i <= n; i++) {
		for (int j = 1; j <= n; j++) {
			if (i == j) continue;
			for (int d = 0; d <= 1; d++) {
				bool tmp0 = insect(i, j, d, 0);
				bool tmp1 = insect(i, j, d, 1);
				if (tmp0 == 0 && tmp1 == 0) continue;
				if (tmp0 == 1 && tmp1 == 0) {
					edges.push_back({vertex[i][d], vertex[j][1]});
				}
				if (tmp0 == 0 && tmp1 == 1) {
					edges.push_back({vertex[i][d], vertex[j][0]});
				}
				if (tmp0 == 1 && tmp1 == 1) {
					edges.push_back({vertex[i][d], vertex[j][0]});
					edges.push_back({vertex[i][d], vertex[j][1]});
				}
			}
		}
	}

	for (auto e : edges) {
		adj[e.first].push_back(e.second);
	}
	for (int i = 1; i <= 2 * n; i++) {
		sort(adj[i].begin(), adj[i].end());
	}
	for (int i = 1; i <= 2 * n; i++) {
		if (vis[i] == 0) {
			now = 0; dfs(i);
		}
	}
	for (int i = 1; i <= 2 * n; i++) {
		adj[i].clear();
		par[i] = i;
	}
	for (auto e : edges) {
        int u = e.first, v = e.second;
        if (comp[u] != comp[v]) {
        	adj[comp[u]].push_back(comp[v]);
        	uni(comp[u], comp[v]);
        }
    }

    for (int i = 1; i <= n; i++) {
    	if (comp[vertex[i][0]] == comp[vertex[i][1]]) {
    		cout << "No";
    		return 0;
    	}
    }

    for (int i = 1; i <= nComp; i++) vis[i] = 0;
    now = 0;
	for (int i = 1; i <= nComp; i++) {
        if (vis[i] == 0) dfs1(i);
    }

    cout << "Yes\n";
    for (int i = 1; i <= n; i++) {
    	if (inDex[comp[vertex[i][0]]] < inDex[comp[vertex[i][1]]]) {
    		cout << 'K';
    	} else {
    		cout << 'Q';
    	}
    }
}

