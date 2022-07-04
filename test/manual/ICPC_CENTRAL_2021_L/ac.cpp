/*input
6 3
2 4 2 1 3 1
1 3
2 3
3 4
5 3
6 5
5 1
0 3
5 1
*/

#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

const int MAXN = 200007;
int dep[MAXN];
vector<int> up[MAXN], down[MAXN], G[MAXN];
int par[MAXN], tin[MAXN], tout[MAXN], go[MAXN], timer;
int N, Q, A[MAXN];

void dfs(int u, int p) {
	tin[u] = ++timer;
	par[u] = p;
	for (int v : G[u]) if (v != p) dep[v] = dep[u] + 1, dfs(v, u);
	tout[u] = timer;

	if (dep[u] == 0) return;
	int d = dep[u] & (-dep[u]);
	for (int i = 0, &v = (go[u] = u); i < d; ++i, v = par[v]) {
		if (up[u].empty() || up[u].back() < A[v]) up[u].push_back(A[v]);
		while (!down[u].empty() && down[u].back() <= A[v]) down[u].pop_back(); down[u].push_back(A[v]);
	}
	reverse(down[u].begin(), down[u].end());
}

int query(int s, int t) {

	// cout << s << ' ' << t << endl;
	const auto is_anc = [](int p, int u) { return tin[p] <= tin[u] && tin[u] <= tout[p]; };
	int x = 0, cnt = 0;

	while (!is_anc(s, t)) {
		int u = go[s];
		if (!is_anc(u, t)) {
			cnt += (int) (up[s].end() - upper_bound(up[s].begin(), up[s].end(), x));
			x = max(x, up[s].back());
			s = u;
		} else {
			// cout << "S " << s << ' ' << t << endl;
			if (x < A[s]) x = A[s], ++cnt;
			s = par[s];
		}
	}

	// cout << "lca = " << s << endl;
	// cout << x << ' ' << cnt << endl;

	if (x < A[s]) x = A[s], ++cnt;
	vector<int> vec;
	while (s != t) {
		int u = go[t];
		if (dep[s] <= dep[u]) {
			vec.push_back(t);
			t = u;
		} else {
			vec.push_back(-t);
			t = par[t];
		}
	}
	reverse(vec.begin(), vec.end());
	for (int q : vec) {
		int u = abs(q);
		if (q < 0) {
			if (x < A[u]) x = A[u], ++cnt;
		} else {
			cnt += (int) (down[u].end() - upper_bound(down[u].begin(), down[u].end(), x));
			x = max(x, down[u].back());
		}
	}

	return cnt;
}

int main() {
	dep[0] = -1;
	ios_base::sync_with_stdio(0); cin.tie(0);
	cin >> N >> Q;
	for (int u = 1; u <= N; ++u) cin >> A[u];
	for (int i = 0; i < N - 1; ++i) {
		int u, v; cin >> u >> v;
		G[u].push_back(v);
		G[v].push_back(u);
	}
	dfs(1, 0);

	// for (int u = 1; u <= 6; ++u) {
	// 	cout << u << ": ";
	// 	cout << "(" << go[u] << ") ";
	// 	for (int v : down[u]) cout << v << ' ';
	// 	cout << endl;
	// }

	int p = 0;
	while (Q--) {
		int s, t; cin >> s >> t;
		s = (s + p) % N + 1;
		t = (t + p) % N + 1;
		p = query(s, t);
		cout << p << '\n';
	}
}
