#include <iostream>

using namespace std;

const int N = 1e5 + 100;
int bef[26], suf[N][26];

void Solve() {
    string st;
    cin >> st;
    int n = st.size();
    for (int i = 0; i < 26; ++i) {
        bef[i] = -1;
        suf[n][i] = n;
    }
    for (int i = n - 1; i >= 0; --i) {
        int c = st[i] - 'a';
        for (int j = 0; j < 26; ++j) suf[i][j] = suf[i + 1][j];
        suf[i][c] = i;
    }
    long long ans = 0;
    for (int i = 0; i < n; ++i) {
        int c = st[i] - 'a';
        ans += 1ll * (i - bef[c]) * (suf[i + 1][c] - i);
        bef[c] = i;
    }
    cout << ans << '\n';
}
int main() {
    ios::sync_with_stdio(false); cin.tie(NULL);
    int test;
    cin >> test;
    while (test--) Solve();
}

