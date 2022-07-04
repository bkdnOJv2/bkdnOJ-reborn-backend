#define Link ""

#include <iostream>
#include <cstdio>
#include <algorithm>

#define TASK ""

using namespace std;

typedef pair<int, int> ii;
#define X first
#define Y second

ii origin;
void operator-=(ii &A, ii B) {
    A.X -= B.X;
    A.Y -= B.Y;
}
bool ccw(ii O, ii A, ii B) {
    A -= O, B -= O;
    return A.X * B.Y > A.Y * B.X;
}
bool cmp(ii A, ii B) { return ccw(origin, A, B); }

int n;
ii a[12309];

void Solve()
{
    n = 4;
    for (int i=1;i<=n;++i)
        cin >> a[i].X >> a[i].Y;
    sort(a+1,a+n+1);
    sort(a+2,a+n+1,
         [] (ii A, ii B) {
            return ccw(a[1], A, B);
         });
    a[0] = a[n];
    a[n + 1] = a[1];
    int j = 1;
    for (int i = 1; i <= n + 1; i++) {
        while (j > 2 && !ccw(a[j - 2], a[j - 1], a[i])) j--;
        a[j++] = a[i];
    }
    n = j - 2;
    cout << (n == 4 ? "YES" : "NO") << '\n';
}

int main()
{
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    cout.tie(NULL);

#ifdef LHL
    freopen(".INP","r",stdin);
    freopen(".OUT","w",stdout);
#else
//    freopen(TASK".INP","r",stdin);
//    freopen(TASK".OUT","w",stdout);
#endif // LHL

    int t;
    for (cin>>t;t>0;--t)
        Solve();
}

