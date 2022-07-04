#include <bits/stdc++.h>
using namespace std;

const bool read_file = false;
const char fi[] = "XX.INP";
const char fo[] = "XX.OUT";

void set_up() {
    if (read_file) {
        freopen(fi, "r", stdin);
        freopen(fo, "w", stdout);
    }
    cin.clear();
    ios_base::sync_with_stdio(0);
    cin.tie(0);
    cout.tie(0);
}

void just_do_it();

int main() {
    set_up();
    just_do_it();
}

struct point {
    long long x, y;
};

point p1, p2, p3, p4;

bool drt(point a, point b, point c) {
    return (c.y - a.y) * (b.x - a.x) > (b.y - a.y) * (c.x - a.x);
}

bool inr(point a, point b, point c, point d) {
    return drt(a, c, d) != drt(b, c, d) && drt(a, b, c) != drt(a, b, d);
}

bool cln(point a, point b, point c) {
    return (c.y - a.y) * (b.x - a.x) == (b.y - a.y) * (c.x - a.x);
}

bool eql(point a, point b) {
    return (a.x == b.x && a.y == b.y);
}

void query() {
    cin >> p1.x >> p1.y >> p2.x >> p2.y >> p3.x >> p3.y >> p4.x >> p4.y;
    bool flag = false;
    flag |= eql(p1, p2);
    flag |= eql(p1, p3);
    flag |= eql(p1, p4);
    flag |= eql(p2, p3);
    flag |= eql(p2, p4);
    flag |= eql(p3, p4);
    flag |= cln(p1, p2, p3);
    flag |= cln(p1, p2, p4);
    flag |= cln(p1, p3, p4);
    flag |= cln(p2, p3, p4);
    if (flag) {
        cout << "NO" << '\n';
        return;
    }
    flag |= inr(p1, p2, p3, p4);
    flag |= inr(p1, p3, p2, p4);
    flag |= inr(p1, p4, p2, p3);
    if (flag) {
        cout << "YES" << '\n';
        return;
    }
    cout << "NO" << '\n';
    return;
}

void just_do_it() {
    int t;
    cin >> t;
    for (int i = 0; i < t; i++) {
        query();
    }
}

