#include <bits/stdc++.h>

using namespace std;

const int MOD = 1e9 + 7; 

struct Matrix { 
    vector<vector<int>> a; 

    Matrix(int _n = 0) { 
        a.resize(_n); 
        for (int i = 0; i < _n; ++i) { 
            a[i].resize(_n, 0); 
            a[i][i] = 1; 
        }
    }

    void init() { 
        for (int i = 0; i < a.size(); ++i) 
            for (int j = 0; j < a.size(); ++j) 
                a[i][j] = 0; 
    }

    void set(int x, int y) { 
        a[x][y] = 1; 
    }

    Matrix multiply(const Matrix &other) { 
        Matrix temp(a.size()); 
        temp.init(); 
        for (int i = 0; i < a.size(); ++i)  
            for (int j = 0; j < a.size(); ++j)  
                for (int k = 0; k < a.size(); ++k) 
                    temp.a[i][j] = (temp.a[i][j] + 1ll * this->a[i][k] * other.a[k][j] % MOD) % MOD; 
        return temp; 
    }

    Matrix Pow(int t) { 
        // if (t == 0) 
        //     return Matrix(a.size()); 
        // if (t == 1) 
        //     return (*this); 
        // Matrix temp = this->Pow(t / 2); 
        // temp = temp.multiply(temp); 
        // return t & 1 ? temp.multiply(*this) : temp; 
        Matrix ret(a.size()), mul = *this; 
        for (int i = 0; i < 31; ++i) { 
            if (t >> i & 1)    
                ret = ret.multiply(mul); 
            mul = mul.multiply(mul); 
        }
        return ret; 
    }

    int sum() { 
        int ret = 0; 
        for (int i = 0; i < a.size(); ++i) 
            for (int j = 0; j < a.size(); ++j) 
                ret = (ret + a[i][j]) % MOD; 
        assert(ret >= 0); 
        return ret; 
    }
};

bool inside(int x, int y, int n, int m) { 
    return 0 <= x && x < n && 0 <= y && y < m; 
}

int main() { 
    ios_base::sync_with_stdio(0); 
    cin.tie(0); cout.tie(0); 

    int n, m, t; 
    cin >> n >> m >> t; 
    Matrix ma(n * m); 
    ma.init(); 
    vector<string> a; 
    for (int i = 0; i < n; ++i) { 
        string str; 
        cin >> str; 
        a.push_back(str); 
    }
    for (int i = 0; i < n; ++i) { 
        for (int j = 0; j < m; ++j) { 
            if (a[i][j] == '#') 
                continue; 
            int newX, newY; 
            if (a[i][j] == 'R' || a[i][j] == '+') { 
                newX = i; newY = j + 1; 
                if (inside(newX, newY, n, m) && a[newX][newY] != '#') 
                    ma.set(i * n + j, newX * n + newY); 
            }
            if (a[i][j] == 'L' || a[i][j] == '+') { 
                newX = i; newY = j - 1; 
                if (inside(newX, newY, n, m) && a[newX][newY] != '#') 
                    ma.set(i * n + j, newX * n + newY); 
            }
            if (a[i][j] == 'D' || a[i][j] == '+') { 
                newX = i + 1; newY = j; 
                if (inside(newX, newY, n, m) && a[newX][newY] != '#') 
                    ma.set(i * n + j, newX * n + newY); 
            }
            if (a[i][j] == 'U' || a[i][j] == '+') { 
                newX = i - 1; newY = j; 
                if (inside(newX, newY, n, m) && a[newX][newY] != '#') 
                    ma.set(i * n + j, newX * n + newY); 
            }
        }
    }
    ma = ma.Pow(t); 
    // for (int i = 0; i < n * m; ++i) { 
    //     for (int j = 0; j < n * m; ++j) 
    //         cout << ma.a[i][j] << " "; cout << endl; } 
    cout << ma.sum() << endl; 

    return 0; 
}

