#include <bits/stdc++.h>
#define long long long

using namespace std;

int main() {
    ios_base::sync_with_stdio(false); cin.tie(NULL);

    int ntest; cin >> ntest;
    while(ntest--) {
        string s; cin >> s;
        map<char, int> last;
        vector<vector<int>> pos(26);
        for(int i = 0; i < s.size(); ++i) {
            pos[s[i] - 'a'].push_back(i);
        }

        long ans = 0;
        for(int c = 0; c < 26; ++c) {
            pos[c].push_back(s.size());
            int last = -1;
            for(int j = 0; j + 1 < pos[c].size(); ++j) {
                ans += 1ll * (pos[c][j] - last) * (pos[c][j+1] - pos[c][j]);
                last = pos[c][j];
            }
        }

        cout << ans << "\n";
    }

    return 0;
}

