// C++ Template

#include "bits/stdc++.h"
using namespace std;

// Type
typedef long long ll;
typedef long double ld;

// Pair/Vector
typedef pair<ll, ll> ii;
typedef vector<ll> vi;
typedef vector<ii> vii;
typedef vector<vi> vvi;

// Priority Queue
template <class T> using maxpq = priority_queue<T>;
template <class T> using minpq = priority_queue<T, vector<T>, greater<T>>;

// Macro
#define stat(x) (x) && cout << "YES\n" || cout << "NO\n";
#ifdef LOCAL
    #define debug(x) cout << #x << " = " << x << "\n";
#else
    #define debug(x) ;
#endif

// Custom output
template <class A, class B>
ostream& operator << (ostream& out, pair<A, B> x){
    out << "(" << x.first << ", " << x.second << ")";
    return out;
}

template <class T>
ostream& operator << (ostream& out, vector<T> x){
    out << "[";
    for (int i=0; i<(ll)x.size(); i++){
        if (i) out << ", ";
        out << x[i];
    }
    out << "]";
    return out;
}

void fastio(string finp = "", string fout = ""){
    if (fopen(finp.c_str(), "r")){
        freopen(finp.c_str(), "r", stdin);
        freopen(fout.c_str(), "w", stdout);
    }
}

// Const
const int interactive = 0;
const ld PI = acos(-1.0);
const ll allmod[2] = {int(1e9)+7, 998244353};
const ll mod = allmod[0];
const ll maxn = 2e5;
const ll inf = 1e18;
const int multitest = 1;
const ld eps = 1e-6;

#define int long long

struct Point{
	int x, y;
};

ld sq(ld x){
	return x*x;
}

ld dist(Point a, Point b){
	return sqrt(sq(a.x - b.x) + sq(a.y - b.y));
}

ld area(Point a, Point b, Point c){
	ld da = dist(a, b), db = dist(b, c), dc = dist(c, a);

	ld p = (da + db + dc) / 2;

	return sqrt(p * (p-da) * (p-db) * (p-dc));
}

void main_program(){
    Point v[4];
    cin >> v[0].x >> v[0].y >> v[1].x >> v[1].y >> v[2].x >> v[2].y >> v[3].x >> v[3].y;

    for (int center = 0; center < 4; center++){
    	vector<Point> tmp;
    	Point check;
    	for (int i=0; i<4; i++){
    		if (i != center) tmp.push_back(v[i]);
    		else check = v[i];
    	}

    	ld a0 = area(tmp[0], tmp[1], tmp[2]);
    	ld a1 = area(tmp[0], tmp[1], check);
    	ld a2 = area(tmp[1], tmp[2], check);
    	ld a3 = area(tmp[2], tmp[0], check);

    	if (abs(a1 + a2 + a3 - a0) < eps){
    		cout << "NO\n";
    		return;
    	}
    }
    cout << "YES\n";
}

void pre_main(){
    
}

signed main(){

    #ifdef LOCAL
        auto start_time = chrono::high_resolution_clock::now();
    #endif

    if (!interactive) {ios_base::sync_with_stdio(0); cin.tie(0); cout.tie(0);}
    #ifndef ONLINE_JUDGE
        fastio(".inp", ".out");
    #endif

    int t = 1;
    if (multitest) cin >> t;
    pre_main();
    while (t--) main_program();

    #ifdef LOCAL
        auto end_time = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::milliseconds>(end_time - start_time).count();
        cout << "\n[" << duration << "ms]\n";
    #endif
}

