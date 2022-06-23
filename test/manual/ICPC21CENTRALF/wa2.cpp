#include<bits/stdc++.h>
using namespace std;

#define taskname "E"
template<typename TH> void _dbg(const char* sdbg, TH h) { cerr << sdbg << " = " << h << "\n"; }
template<typename TH, typename... TA> void _dbg(const char* sdbg, TH h, TA... t) { while (*sdbg != ',') cerr << *sdbg++; cerr << " = " << h << ","; _dbg(sdbg + 1, t...); }
#define db(...) _dbg(#__VA_ARGS__, __VA_ARGS__)
#define chkpt cerr << "------\n";
#define sp ' '
#define el '\n'

struct Point {
  int64_t x, y;
};

int t;
Point a[4], b[4];

int area(Point p1, Point p2, Point p3) {
  int64_t area = (p2.x - p1.x) * (p2.y + p1.y);
  area += (p3.x - p2.x) * (p3.y + p2.y);
  area += (p1.x - p3.x) * (p1.y + p3.y);
  return (area < 0) ? -1 : (area > 0);
}

bool check() {
  int x = area(b[0], b[1], b[2]);
  int y = area(b[1], b[2], b[3]);
  int z = area(b[2], b[3], b[1]);
  int t = area(b[3], b[1], b[2]);
  if (x != 0 && y != 0 && z != 0 && t != 0) {
    if (x == y && y == z && z == t) {
      return true;
    }
    return false;
  }
  return false;
}

int main(){
//  freopen(taskname".INP","r",stdin);
//  freopen(taskname".OUT","w",stdout);
  ios_base::sync_with_stdio(0);
  cin.tie(0);
  cin >> t;
  while (t--) {
    for (int i = 0; i < 4; ++i) {
      cin >> a[i].x >> a[i].y;
    }
    vector<int> vt = {0, 1, 2, 3};
    bool ans = false;
    do {
      for (int i = 0; i < 4; ++i) {
        b[i] = a[vt[i]];
      }
      if (check()) {
        ans = true;
        break;
      }
      break;
    }
    while (next_permutation(vt.begin(), vt.end()));
    cout << (ans ? "YES" : "NO") << el;
  }
  return 0;
}

