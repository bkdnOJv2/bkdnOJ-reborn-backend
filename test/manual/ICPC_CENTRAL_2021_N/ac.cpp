#pragma GCC optimize("Ofast")
#pragma GCC optimization("unroll-loops")
#pragma GCC target("avx,avx2,fma")

#include <bits/stdc++.h>
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/trie_policy.hpp>
#include <ext/rope>

using namespace std;
using namespace __gnu_pbds;
using namespace __gnu_cxx;

mt19937 rng(chrono::steady_clock::now().time_since_epoch().count());

#define fi first
#define se second
#define pb push_back
#define eb emplace_back
#define mp make_pair
#define gcd __gcd
#define fastio ios_base::sync_with_stdio(0); cin.tie(0); cout.tie(0)
#define rep(i, n) for (int i=0; i<(n); i++)
#define rep1(i, n) for (int i=1; i<=(n); i++)
#define all(x) (x).begin(), (x).end()
#define rall(x) (x).rbegin(), (x).rend()
#define endl "\n"

typedef long long ll;
typedef unsigned long long ull;
typedef unsigned uint;
typedef long double ld;
typedef pair<int, int> pii;
typedef pair<ll, ll> pll;
typedef vector<int> vi;
typedef vector<vector<int>> vvi;
typedef vector<ll> vll;
typedef vector<vector<ll>> vvll;
typedef vector<bool> vb;
typedef vector<vector<bool>> vvb;
template<typename T, typename cmp = less<T>>
using ordered_set=tree<T, null_type, cmp, rb_tree_tag, tree_order_statistics_node_update>;
typedef trie<string, null_type, trie_string_access_traits<>, pat_trie_tag, trie_prefix_search_node_update> pref_trie;

int32_t main() {
    fastio;
    string s, t; cin >> s >> t;
    int cnt[26] = {0};
    for(char c: t) cnt[c - 'a']++;
    vi pos[26];
    rep(i, s.size()) pos[s[i] - 'a'].pb(i);
    auto check = [&](int id, int t) -> bool {
        rep(i, 26) {
            int rst = lower_bound(rall(pos[i]), id, greater<>()) - pos[i].rbegin() + (i == t);
            if(rst < cnt[i]) return 0;
        }
        return 1;
    };
    string ans; int id = -1;
    if(!check(-1, -1)) return puts("-1"), 0;
    rep(_, t.size()) {
        bool ok = 0;
        rep(i, 26) if(cnt[i]) {
            auto _nxt = upper_bound(all(pos[i]), id);
            if(_nxt != pos[i].end()) {
                int nxt = *_nxt;
                if(check(nxt, i)) {
                    ok = 1;
                    id = nxt;
                    cnt[i]--;
                    ans.pb(char(i + 'a'));
                    break;
                }
            }
        }
    }
    cout << ans << endl;
}

