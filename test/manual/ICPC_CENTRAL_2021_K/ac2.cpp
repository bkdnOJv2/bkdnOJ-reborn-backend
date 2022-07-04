#include    <bits/stdc++.h>
#define fo(i,a,b) for(int i=(a);i<=(b);++i)
#define __unique(V) (V).resize(unique((V).begin(),(V).end())-(V).begin())
#define cntbit(X)   __builtin_popcount((X))
#define bit(S,i) (((S)>>(i))&1)
#define PI	acos(-1)
#define fi  first
#define se  second
#define LL  long long
#define ii  pair<int,int>
#define iii pair<int,ii>
#define eb  emplace_back
#define lch ((k) << 1)
#define rch ((k) << 1|1)
#define _abs(x) ((x) > 0 ? (x) : -(x))
#define TASK "mtk"
using namespace std;
mt19937_64 rng(chrono::steady_clock::now().time_since_epoch().count());
const int dx[] = {0,0,1,-1};
const int dy[] = {1,-1,0,0};
const int N = 105;
const int MOD = 1e9 + 7;
char c[N][N];
int n,m;
struct matrix{
    int x[N][N];
    matrix(){
        memset(x,0,sizeof(x));
    }
};
int siz = 0,t;
int node[N][N];
///--------------------------
matrix operator * (matrix A,matrix B){
    matrix C;
    for(int i = 1; i < siz; ++i){
        for(int j = 1; j < siz; ++j){
            for(int k = 1; k < siz; ++k){
                C.x[i][j] = (C.x[i][j] + 1ll * A.x[i][k] * B.x[k][j]) % MOD;
            }
        }
    }
    return C;
}
///--------------------------
matrix operator ^ (matrix A,int B){
    matrix C;
    for(int i = 1; i < siz; ++i){
        C.x[i][i] = 1;
    }

    for( ; B > 0 ; A = A * A, B >>= 1)
    if (B & 1){
        C = C * A;
    }
    return C;
}
///--------------------------
bool    onSide(int x,int y){
    return 0 < x && x <= n && 0 < y && y <= m && c[x][y] != '#';
}
///--------------------------
int     main(){
    ///
        srand(time(NULL));
        ios::sync_with_stdio(0);
        cin.tie(0);cout.tie(0);
        #ifdef TLH2203
            freopen(TASK".inp", "r", stdin);
            freopen(TASK".out", "w", stdout);
        #endif // TLH2203
    ///

    cin >> n >> m >> t;
    siz = 0;
    for(int i = 1; i <= n; ++i){
        for(int j = 1; j <= m; ++j){
            cin >> c[i][j];
            node[i][j] = ++siz;
        }
    }
    ++siz;


    matrix S;
    matrix P;
    for(int i = 1; i <= n; ++i){
        for(int j = 1; j <= m; ++j) if (c[i][j] != '#'){
            S.x[1][node[i][j]] = 1;
            if (c[i][j] == 'L'){
                int u = i, v = j - 1;
                if (!onSide(u,v)) continue;
                P.x[node[i][j]][node[u][v]] = 1;
            }

            if (c[i][j] == 'R'){
                int u = i, v = j + 1;
                if (!onSide(u,v)) continue;
                P.x[node[i][j]][node[u][v]] = 1;
            }

            if (c[i][j] == 'U'){
                int u = i - 1, v = j;
                if (!onSide(u,v)) continue;
                P.x[node[i][j]][node[u][v]] = 1;
            }

            if (c[i][j] == 'D'){
                int u = i + 1, v = j;
                if (!onSide(u,v)) continue;
                P.x[node[i][j]][node[u][v]] = 1;
            }

            if (c[i][j] == '+')
            for(int k = 0; k < 4; ++k){
                int u = i + dx[k];
                int v = j + dy[k];
                if (!onSide(u,v)) continue;
                P.x[node[i][j]][node[u][v]] = 1;
            }
        }
    }

    S = S * (P ^ t);
    
    int ans = 0;
    for(int i = 1; i < siz; ++i){
        ans = (ans + S.x[1][i]) % MOD;
    }

    cout << ans << '\n';
}

