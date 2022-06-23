#include <bits/stdc++.h>
using namespace std;

#define rep(i, a, b) for(int i = a; i < (b); ++i)
#define all(x) begin(x), end(x)
#define sz(x) (int)(x).size()
typedef long long ll;
typedef pair<int, int> pii;
typedef vector<int> vi;

bool agb(pair<double, int> a, pair<double, int> b) {
	return a.first*b.second > b.first*a.second;
}

void merge(pair<double, int> &a, pair<double, int> b) {
	a.first += b.first;
	a.second += b.second;
}

double solve(vector<double> a, int n) {
	vector<pair<double, int>> s;
	for (double x: a) {
		if (s.empty()) {
			s.push_back({x, 1});
		} else {
			pair<double, int> nxt(x, 1);
			while (s.size() && agb(s.back(), nxt)) {
				merge(nxt, s.back());
				s.pop_back();
			}
			s.push_back(nxt);
		}
	}

	int i = 0; double ans = 0;
	for (auto [sum, cnt]: s) {
		double avg = sum*1.0/cnt;
		while (cnt--) {
			ans += (avg - a[i])*(avg - a[i]);
			i++;
		}
	}
	return sqrtl(ans);
}

signed main() {
	ios::sync_with_stdio(0); cin.tie(0);
	
	int n; cin >> n;
	vector<double> a(n);
	for (int i = 0; i < n; i++) {
		cin >> a[i];
	}
	cout << fixed << setprecision(12) << solve(a, n) << '\n';

	return 0;
}
