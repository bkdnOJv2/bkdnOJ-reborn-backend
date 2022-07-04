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
const int multitest = 0;

#define int long long

struct Point{
	ld x, y;

	Point(ld X, ld Y): x(X), y(Y) {}
	Point(): x(0), y(0) {}
};

ld sq(ld x){
	return x*x;
}

ld dist(Point a, Point b){
	return sqrt(sq(a.x - b.x) + sq(a.y - b.y));
}

ld area(ld a, ld b, ld c){
	ld p = (a+b+c)/2;
	return sqrt(p * (p-a) * (p-b) * (p-c));
}

void main_program(){
    Point a, b, c;
    cin >> a.x >> a.y >> b.x >> b.y >> c.x >> c.y;

    ld r, p; cin >> r >> p;

    ld x1, y1, x2, y2;
    if (a.x == b.x){
    	ld dx = abs(c.x - a.x);
    	if (dx >= r){
    		cout << "NO\n";
    		return;
    	}
    	
    	ld dy = sqrt(sq(r) - sq(dx));

    	x1 = x2 = a.x;
    	y1 = c.y + dy;
    	y2 = c.y - dy;
    }
    else{
    	ld linea = (a.y - b.y) / (a.x - b.x);
    	ld lineb = a.y - a.x * linea;
    	debug(linea); debug(lineb);

    	ld A = sq(linea) + 1;
    	ld B = 2 * (c.x + linea * (c.y - lineb));
    	ld C = sq(c.x) + sq(c.y - lineb) - sq(r);

    	debug(A); debug(B); debug(C);

    	ld delta = sq(B) - 4*A*C;

    	if (delta <= 0){
    		cout << "NO\n";
    		return;
    	}

    	x1 = (B + sqrt(delta)) / (2*A);
    	x2 = (B - sqrt(delta)) / (2*A);

    	y1 = linea * x1 + lineb;
    	y2 = linea * x2 + lineb;
    }

    debug(x1); debug(y1); debug(x2); debug(y2);

    ld diff = dist(Point(x1, y1), Point(x2, y2));

    debug(diff);

    ld angle = asin(diff / (2 * r));
    debug(angle * 360 / PI);

    ld big_area = r*r*PI * (angle / PI);
    debug(big_area);

    ld small_area = area(r, r, diff);
    debug(small_area);

    ld desired = big_area - small_area;

    ld frac = desired / (r*r*PI); frac *= 100;

    if (abs(frac - p) <= 5){
    	cout << "YES\n";
    }
    else{
    	cout << "NO\n";	
    }
}

void pre_main(){
    debug(PI);
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

