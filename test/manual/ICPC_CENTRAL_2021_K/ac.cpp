#include <bits/stdc++.h>
using namespace std;

#ifdef DEBUG
#include "debug.hpp"
#define debug(x...) cerr << "[" << #x << "] = [", _print(x)
#else
#define debug(x...)
#endif

template<const int n, const int mod>
struct Matrix {
    int x[n][n];

    Matrix() {
        memset(x, 0, sizeof(x));
    }
    int* operator [] (int r) {
        return x[r];
    }
    static Matrix unit() {
        Matrix res;
        for (int i = 0; i < n; i++) res[i][i] = 1;
        return res;
    }
    friend Matrix operator + (Matrix A, Matrix B) {
        Matrix res;
        for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) {
                res[i][j] = A[i][j] + B[i][j];
                if (res[i][j] >= mod) res[i][j] -= mod;
            }
        return res;
    }
    friend Matrix operator * (Matrix A, Matrix B) {
        Matrix res;
        for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) {
                long long SQmod = (long long) mod * mod;
                long long sum = 0;
                for (int k = 0; k < n; k++) {
                    sum += (long long) A[i][k] * B[k][j];
                    if (sum >= SQmod) sum -= SQmod;
                }
                res[i][j] = sum % mod;
            }
        return res;
    }
    friend Matrix operator ^ (Matrix A, long long k) {
        if (k == 0) return unit();
        Matrix res, tmp;
        for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) {
                res[i][j] = tmp[i][j] = A[i][j];
            }
        k--;
        while (k) {
            if (k & 1) res = res * tmp;
            tmp = tmp * tmp;
            k >>= 1;
        }
        return res;
    }
    //Calculate geometric series: A^0 + A^1 + ... + A^k
    friend Matrix geometricSeries(Matrix A, long long k) {
        if (k == 0) return unit();
        if (k == 1) return A + unit();
        vector<int> bit;
        while (k) {
            bit.push_back(k & 1);
            k >>= 1;
        }
        Matrix res = A, tmp = A;
        for (int i = bit.size() - 2; i >= 0; i--) {
            res = res + (res * tmp);
            tmp = tmp * tmp;
            if (bit[i] & 1) {
                tmp = tmp * A;
                res = res + tmp;
            }
        }
        res = res + unit();
        return res;
    }
};

int h, w;
char A[105][105];

const int base = 1e9 + 7;
const int r[4] = {-1, 1, 0, 0};
const int c[4] = {0, 0, -1, 1};

int id(int x, int y) {
    return x * w + y;
};

bool inside(int x, int y) {
    return 0 <= x && x < h && 0 <= y && y < w && A[x][y] != '#';
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
#ifdef DEBUG
    freopen("input", "r", stdin);
#endif
    int t;
    cin >> h >> w >> t;
    Matrix<105, base> a;
    Matrix<105, base> m;
    for (int i = 0; i < h; ++i)
        for (int j = 0; j < w; ++j) {
            cin >> A[i][j];
        }

    for (int i = 0; i < h; ++i)
        for (int j = 0; j < w; ++j) {
            if (A[i][j] == '#') continue;
            a[0][id(i, j)] = 1;
            if (A[i][j] == '+') {
                for (int k = 0; k < 4; ++k) {
                    int x = i + r[k];
                    int y = j + c[k];
                    if (inside(x, y)) m[id(i, j)][id(x, y)] = 1;
                }
            } else if (A[i][j] == 'U') {
                int x = i + r[0];
                int y = j + c[0];
                if (inside(x, y)) m[id(i, j)][id(x, y)] = 1;
            } else if (A[i][j] == 'D') {
                int x = i + r[1];
                int y = j + c[1];
                if (inside(x, y)) m[id(i, j)][id(x, y)] = 1;
            } else if (A[i][j] == 'L') {
                int x = i + r[2];
                int y = j + c[2];
                if (inside(x, y)) m[id(i, j)][id(x, y)] = 1;
            } else if (A[i][j] == 'R') {
                int x = i + r[3];
                int y = j + c[3];
                if (inside(x, y)) m[id(i, j)][id(x, y)] = 1;
            }
        }
    Matrix<105, base> res = a * (m ^ t);
    long long ans = 0;
    for (int i = 0; i < h * w; ++i)
        ans = (ans + res[0][i]) % base;
    cout << ans;
}

