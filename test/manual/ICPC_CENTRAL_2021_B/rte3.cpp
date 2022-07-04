#include <bits/stdc++.h>
using namespace std;

long long MOD = 1e9 + 7;
int a[1000005];
int main() {

    ios::sync_with_stdio(0);
    cin.tie(NULL);
    int n;
    cin >> n;
    int d = 0;
    vector <int> am;
    vector <int> duong;

    int k = 0;
    long long prod = 1;

    for (int i = 1; i <= n; i++) {
        cin >> a[i];
        if (a[i] == 0) {
            k++;
        }
        if (a[i] < 0) {
            am.push_back(a[i]);
            d++;
            prod = (prod * a[i]) % MOD ;

        }
        else {
            duong.push_back(a[i]);
            prod = (prod * a[i]) % MOD ;
        }
    }
    sort (am.begin(), am.end());
    sort (duong.begin(), duong.end());


    if (k == 2) {
        cout << 0;
        return 0;
    }
    if (d % 2 == 0) {
        cout << prod;
    }
    else {
        long long h = 0;
        if (k == 1)
        cout << max(h,prod);
        else {
            cout << prod / am[am.size() - 1];
        }
    }

    return 0;
}
