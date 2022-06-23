/* 
// is short or still long ???
hollwo_pelw's template(short)
// Note : -Dhollwo_pelw_local
*/

#include <bits/stdc++.h>
// #include <ext/pb_ds/assoc_container.hpp>
// #include <ext/pb_ds/trie_policy.hpp>
// #include <ext/rope>

using namespace std;
// using namespace __gnu_pbds;
// using namespace __gnu_cxx;

void FAST_IO(string filein = "", string fileout = "", string fileerr = ""){
	if (fopen(filein.c_str(), "r")){
		freopen(fileout.c_str(), "w", stdout);
		freopen(filein.c_str(), "r", stdin);
#ifdef hollwo_pelw_local
		freopen(fileerr.c_str(), "w", stderr);
#endif
	}
	cin.tie(0), cout.tie(0) -> sync_with_stdio(0);
}

void Hollwo_Pelw();

signed main(){
#ifdef hollwo_pelw_local
	FAST_IO("input.inp", "output.out", "error.err");
	auto start = chrono::steady_clock::now();
#else
	FAST_IO("L.inp", "L.out");
#endif
	int testcases = 1;
	// cin >> testcases;
	for (int test = 1; test <= testcases; test++){
		// cout << "Case #" << test << ": ";
		Hollwo_Pelw();
	}
#ifdef hollwo_pelw_local
	auto end = chrono::steady_clock::now();
	cout << endl;
	cout << "Excution time : " << chrono::duration_cast<chrono::milliseconds> (end - start).count() << "[ms]" << endl;
#endif
	return 0;
}

const int N = 2e5 + 5;

vector<int> adj[N];
int n, q, a[N];
int par[N], nxt[N], sz[N];
int tin[N], ord[N], timer;

void pre_dfs(int u, int p) {
	par[u] = p;
	nxt[u] = u;
	sz[u] = 1;
	for (int &v : adj[u]) {
		if (v == p) swap(v, adj[u].back());
		if (v == p) {
			adj[u].pop_back();
			break ;
		}
		pre_dfs(v, u);
		sz[u] += sz[v];
		if (sz[v] > sz[adj[u][0]])
			swap(v, adj[u][0]);
	}
}

void dfs_hld(int u) {
	tin[u] = ++ timer;
	ord[timer] = u;
	for (int v : adj[u]) {
		if (v == adj[u][0])
			nxt[v] = nxt[u];
		dfs_hld(v);
	}
}

int upt[18][N], dwt[18][N], mx[18][N], lg[N];

void __build_sparse__() {
	for (int i = 0; i < 18; i++) {
		for (int j = 0; j <= n + 1; j++)
			upt[i][j] = 0, dwt[i][j] = n + 1;
	}

	{
		vector<int> st;
		for (int i = 1; i <= n; i++) {
			while (!st.empty() && a[ord[st.back()]] <= a[ord[i]])
				st.pop_back();
			upt[0][i] = st.empty() ? 1 - 1 : st.back();
			st.push_back(i);
		}
	}
	{
		vector<int> st;
		for (int i = n; i >= 1; i--) {
			while (!st.empty() && a[ord[st.back()]] <= a[ord[i]])
				st.pop_back();
			dwt[0][i] = st.empty() ? n + 1 : st.back();
			st.push_back(i);
		}
	}

	lg[0] = -1;
	for (int i = 1; i <= n; i++)
		mx[0][i] = a[ord[i]], lg[i] = lg[i >> 1] + 1;

	for (int i = 1; i < 18; i++) {
		for (int j = 0; j + (1 << i) <= n + 2; j++) {
			upt[i][j] = upt[i - 1][upt[i - 1][j]];
			dwt[i][j] = dwt[i - 1][dwt[i - 1][j]];
			mx[i][j] = max(mx[i - 1][j], mx[i - 1][j + (1 << (i - 1))]);
		}
	}
}

inline int lca(int u, int v) {
	while (nxt[u] != nxt[v]) {
		if (tin[u] < tin[v])
			swap(u, v);
		u = par[nxt[u]];
	}
	return tin[u] < tin[v] ? u : v;
}

inline int query_mx(int l, int r) {
	int j = lg[r - l + 1];
	return max(mx[j][l], mx[j][r - (1 << j) + 1]);
}

inline int query_dw(int l, int r, int& cur) {
	if (l > r || query_mx(l, r) <= cur) return 0;
	{
		int tl = l, tr = r, f = r;
		while (tl <= tr) {
			int tm = tl + tr >> 1;
			if (query_mx(l, tm) > cur)
				f = tm, tr = tm - 1;
			else
				tl = tm + 1;
		}
		l = f;
	}

	int res = 1;

	for (int i = 17; ~i; i--) {
		if (dwt[i][l] <= r) {
			l = dwt[i][l];
			res += 1 << i;
		}
	}

	cur = a[ord[l]];
	return res;
}

inline int query_up(int l, int r, int& cur) {
	if (l > r || query_mx(l, r) <= cur) return 0;
	{
		int tl = l, tr = r, f = l;
		while (tl <= tr) {
			int tm = tl + tr >> 1;
			if (query_mx(tm, r) > cur)
				f = tm, tl = tm + 1;
			else
				tr = tm - 1;
		}
		r = f;
	}
	int res = 1;

	for (int i = 17; ~i; i--) {
		if (upt[i][r] >= l) {
			r = upt[i][r];
			res += 1 << i;
		}
	}

	cur = a[ord[r]];
	return res;
}

inline int query(int u, int v) {
	int w = lca(u, v), cur = 0, res = 0;

	{
		vector<pair<int, int>> st;
		while (nxt[u] != nxt[w]) {
			st.emplace_back(tin[u], tin[nxt[u]]);
			u = par[nxt[u]];
		}
		st.emplace_back(tin[u], tin[w]);
		for (auto lr : st)
			res += query_up(lr.second, lr.first, cur);
	}

	{
		vector<pair<int, int>> st;
		while (nxt[v] != nxt[w]) {
			st.emplace_back(tin[v], tin[nxt[v]]);
			v = par[nxt[v]];
		}
		st.emplace_back(tin[v], tin[w] + 1);
		
		reverse(st.begin(), st.end());
		for (auto lr : st)
			res += query_dw(lr.second, lr.first, cur);
	}

	return res;
}

void Hollwo_Pelw() {
	cin >> n >> q;
	for (int i = 1; i <= n; i++)
		cin >> a[i];
	for (int i = 1, u, v; i < n; i++) {
		cin >> u >> v;
		adj[u].push_back(v);
		adj[v].push_back(u);
	}
	// build chain
	pre_dfs(1, 0);
	dfs_hld(1);

	__build_sparse__();

	for (int p = 0, x, y; q --; ) {
		cin >> x >> y;
		x = (x + p) % n + 1;
		y = (y + p) % n + 1;
		// cout << x << ' ' << y << '\n';
		cout << (p = query(x, y)) << '\n';
	}
}

