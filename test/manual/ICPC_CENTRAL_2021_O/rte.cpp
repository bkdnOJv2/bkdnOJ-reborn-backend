#include <bits/stdc++.h>
using namespace std;

int dfs(vector<vector<int>> &adj, vector<int> &grundy, int u) {
	if (grundy[u] != -1) return grundy[u];

	set<int> st;
	for (int v: adj[u]) {
		st.insert(dfs(adj, grundy, v));
	}

	for (int i = 0; i <= 1000000; i++) {
		if (st.find(i) == st.end()) {
			return grundy[u] = i;
		}
	}
	return -1;
}

void solve() {
	int n, m, a, b; cin >> n >> m >> a >> b; a--, b--;
	string trash; cin >> trash;

	vector<vector<int>> adj(n);
	while (m--) {
		int u, v; cin >> u >> v;
		adj[u].push_back(v);
	}
	vector<int> grundy(n, -1);

	int x, y, k; cin >> x >> y >> k;
	int xr = k % 2;
	xr ^= dfs(adj, grundy, a);
	xr ^= dfs(adj, grundy, b);

	if (xr == 0) cout << "NO\n";
	else cout << "YES\n";

	while (k--) {
		int trashint[5];
		for (int i = 0; i < 5; i++) {
			cin >> trashint[i];
		}
	}
}

signed main() {
	ios::sync_with_stdio(0); cin.tie(0);
	
	int t; cin >> t;
	while (t--) {
		solve();
	}

	return 0;
}

