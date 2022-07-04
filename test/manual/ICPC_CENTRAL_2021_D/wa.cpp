#include <cassert>
#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>

using namespace std;

struct Complex {
    double re, im;
    Complex(double r_ = 0, double i_ = 0):re(r_), im(i_) {}
    Complex operator* (const Complex &z) const {
        return Complex(re * z.re - im * z.im, re * z.im + im * z.re);
    }
    Complex operator+ (const Complex &z) const {
        return Complex(re + z.re, im + z.im);
    }
    Complex operator- (const Complex &z) const {
        return Complex(re - z.re, im - z.im);
    }
    Complex normal() const { return Complex(im, -re); }
};

Complex conj(const Complex& z) { return Complex(z.re, -z.im); }

const double PI = acos(-1);
const int N = (1 << 22);

Complex root_unity[N + 1];
void init_fft() {
    for (int i = 0; i <= N; ++i) {
        root_unity[i] = Complex(cos(2 * PI * i / N), -sin(2 * PI * i / N));
    }
}

void fft(vector<Complex>& a, const vector<int>&p) {
    int n = a.size();
    for (int i = 0; i < n; ++i)
        if (i < p[i]) swap(a[i], a[p[i]]);

    for (int m = 1, t = N / 2;  m < n ; m *= 2, t /= 2) {
        for (int i = 0; i < n; i += m * 2)
            for (int j = 0; j < m; ++j) {
                int u = i + j, v = i + j + m;
//                assert(t > 0);
                a[v] = a[v] * root_unity[j * t];
                Complex tmp = a[u] - a[v];
                a[u] = a[u] + a[v];
                a[v] = tmp;
            }
    }
}

vector<long long> polymul(const vector<int>&a, const vector<int>&b) {
    int n = max(a.size(), b.size());
    if (__builtin_popcount(n) != 1) n = 1 << (32 - __builtin_clz(n));
    n *= 2;
//    cerr << "n = " << n << '\n';
    vector<Complex> pa(n);
    for (size_t i = 0; i < pa.size(); ++i) {
        pa[i] = Complex(i < a.size() ? a[i] : 0, i < b.size() ? b[i] : 0);
    }
    vector<int> p(n);
    for (int i = 0; i < n; ++i) {
        p[i] = p[i >> 1] >> 1 | (i & 1) << (30 - __builtin_clz(n));
    }
    fft(pa, p);
    vector<Complex> pb(n);
    pb[0] = pa[0].re * pa[0].im;
    for (int i = 1; i < n; ++i) {
        Complex ai = pa[i] + conj(pa[n - i]);
        Complex bi = pa[i] - conj(pa[n - i]);
        pb[i] = conj(ai * bi.normal() * (1. / 4));
    }
    fft(pb, p);
    vector<long long> res(n);
    transform(pb.begin(), pb.end(), res.begin(), [&](auto c) {
        return lround(c.re / n);
    });
    return res;
}

int main() {
    cin.tie(NULL); ios_base::sync_with_stdio(false);
    init_fft();
//    vector<int> a = {1, 2, 3};
//    vector<int> b = {1, 2, 3};
//    vector<long long> c = polymul(a, b);
//    for (int x : c) cout << x << ' ';

    int h, w, X, Y;
    cin >> h >> w >> X >> Y;
//    h = 5e3, w = 1e2, X = h, Y = w;
    vector<int> a, b;

    a.resize(a.size() + (X / 2) * (w + Y - 1));
    for (int i = 0; i < h; ++i) {
        a.resize(a.size() + (Y / 2));
        for (int j = 0; j < w; ++j) {
            int x = 100;
            cin >> x;
            a.push_back(x);
        }
        a.resize(a.size() + (Y / 2));
    }
    a.resize(a.size() + (X / 2) * (w + Y - 1));

    b.resize(b.size() + (X / 2) * (w + Y - 1));
    for (int i = 0; i < X; ++i) {
        b.resize(b.size() + (Y / 2));

        vector<int> tmp(Y);
//        for (int j = 0; j < Y; ++j) tmp[j] = 200;
        for (int j = 0; j < Y; ++j) cin >> tmp[j];

        for (int j = 0; j < Y; ++j)
            b.push_back(tmp[j]);

        b.resize(b.size() + (w - Y) + (Y / 2));
    }
    b.resize(b.size() + (X / 2 + (h - X)) * (w + Y - 1));
    reverse(b.begin(), b.end());

//    for (int x : a) cerr << x << ' '; cerr << '\n';
//    for (int x : b) cerr << x << ' '; cerr << '\n';
    vector<long long> c = polymul(a, b);
//    for (long long x : c) cout << x << ' ';

    for (int i = 0; i < h; ++i)
        for (int j = 0; j < w; ++j) {
            int id = (i + X / 2 + h - 1) * (w + Y - 1) + (j + Y / 2 + w - 1);
            cout << c[id] << " \n"[j + 1 == w];
        }
    return 0;
}

