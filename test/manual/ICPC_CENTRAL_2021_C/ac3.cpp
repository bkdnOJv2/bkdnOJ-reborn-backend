
#include <bits/stdc++.h>
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>
using namespace std;
using namespace __gnu_pbds;

#define endl '\n'
#define fi first
#define se second
#define For(i, l, r) for (int i = l; i < r; i++)
#define ForE(i, l, r) for (int i = l; i <= r; i++)
#define FordE(i, l, r) for (int i = l; i >= r; i--)
#define Fora(v, a) for (auto v: a)
#define bend(a) a.begin(), a.end()
#define isz(a) ((signed)a.size())

typedef long long ll;
typedef double ld;
typedef pair <int, int> pii;
typedef vector <int> vi;
typedef vector <pii> vpii;
typedef vector <vi> vvi;

const int N = 1e6 + 5;

int n;
ld a[N];

priority_queue <pair <ld, int>> pq;
ld val[N];
ld b, c;

signed main(){
    ios_base::sync_with_stdio(0);
    cin.tie(0); cout.tie(0);
    // freopen("KEK.inp", "r", stdin);
    // freopen("KEK.out", "w", stdout);
    cin >> n;
    ForE(i, 1, n){
        cin >> a[i];
        b += 2;
        c -= 2 * a[i];
        while (!pq.empty()){
            ld x = -c / b, tx = pq.top().fi;
            if (x < tx){
                int cnt = pq.top().se;
                ld tb = b + cnt, tc;
                pq.pop();
                tc = b * tx + c - tb * tx;
                b = tb; c = tc;
                continue;
            }
            break;
        }
        ld x = -c / b;
        pq.emplace(x, b);
        b = 0; c = 0;
    }
    ld ans = 0;
    ld x = pq.top().fi; int cnt = pq.top().se; pq.pop();
    FordE(i, n, 1){
        ans += (a[i] - x) * (a[i] - x);
        cnt -= 2;
        if (!cnt){
            x = pq.top().fi; cnt = pq.top().se; pq.pop();
        }
    }
    ans = sqrtl(ans);
    cout << fixed << setprecision(9) << ans << endl;
}

/*
==================================================+
INPUT:                                            |
--------------------------------------------------|

--------------------------------------------------|
==================================================+
OUTPUT:                                           |
--------------------------------------------------|

--------------------------------------------------|
==================================================+
*/

