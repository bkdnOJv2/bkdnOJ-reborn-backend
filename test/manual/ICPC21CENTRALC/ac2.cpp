/*input
3
1 1 2
*/
#define NDEBUG

#include <bits/stdc++.h>

using namespace std;

using db = long double;
const db inf = 1e6;

struct func_t { db x, a, b, c; };

struct SlopeTrick {
	vector<func_t> vec;
	SlopeTrick() { vec = {{-inf, 0, 0, 0}}; } 

	void add(db a, db b, db c) {
		vec.back().a += a, vec.back().b += b, vec.back().c += c;
	}

	void relax() {
		while (true) {
			assert(!vec.empty());
			auto u = vec.back();
			db deri = 2 * u.a * u.x + u.b;
			if (deri > 0) {
				vec.pop_back();
				assert(!vec.empty());
				vec.back().a += u.a, vec.back().b += u.b, vec.back().c += u.c;
			} else {
				db x = -u.b / (2 * u.a);
				assert(x >= u.x);
				db y = u.a * x * x + u.b * x + u.c;
				vec.back().c -= y;
				vec.push_back({x, 0, 0, y});
				break;
			}
		}
	}

	db get() {
		return vec.back().c;
	}
} st;

int32_t main() {
	ios_base::sync_with_stdio(0); cin.tie(0);
	int n; cin >> n;
	while (n--) {
		db a; cin >> a;
		st.add(1, -2 * a, a * a);
		st.relax();
	}
	cout << fixed << setprecision(9) << sqrt(st.get()) << '\n';
}
