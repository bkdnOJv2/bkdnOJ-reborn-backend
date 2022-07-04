#include <bits/stdc++.h>
using namespace std;

typedef vector <int> vi;

signed main() {
	ios_base::sync_with_stdio(0);
	
	int h, w, X, Y; 
	cin >> h >> w >> X >> Y;
	
	int bx = (int) (ceil((X * 1.0 + 1)/2) + 1e-9);
	int by = (int) (ceil((Y * 1.0 + 1)/2) + 1e-9);

	vector <vi> A, L;
	A.push_back(vector <int>());
	L.push_back(vector <int>());
	for (int i = 1; i <= h; i++) {
		A.push_back(vector <int> ()); A[i].push_back(0);
		for (int j = 1; j <= w; j++) {
			int x; cin >> x;
			A[i].push_back(x);
		}
	}
	for (int i = 1; i <= X; i++) {
		L.push_back(vector <int> ()); L[i].push_back(0);
		for (int j = 1; j <= Y; j++) {
			int x; cin >> x;
			L[i].push_back(x);
		}
	}
	
	vector <vi> B;
	for (int i = 1; i <= h; i++) {
		B.push_back(vector <int> ());
		for (int j = 1; j <= w; j++) {
			long long r = 0;
			
			// kernel
			for (int kx = 1; kx <= X; kx++) {
				if (i + kx - bx < 1) continue;
				if (i + kx - bx > h) continue;
				for (int ky = 1; ky <= Y; ky++) {
					if (j + ky - by < 1) continue;
					if (j + ky - by > w) continue;
					r += L[kx][ky] * 1ll * A[i + kx - bx][j + ky - by];
				}
			}
			
			cout << r << ' ';
		}
		cout << '\n';
	}
	
	
	return 0;
}
