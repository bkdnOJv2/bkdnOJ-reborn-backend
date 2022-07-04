#include <bits/stdc++.h>

using namespace std;

int D[500007];

int main()
{
    if (fopen("test.inp", "r"))
    {
        freopen("test.inp", "r", stdin);
        freopen("test.out", "w", stdout);
    }

    string s;
    int k;
    cin >> s >> k;
    int n = s.size();
    s = " " + s;
    
    while (k--)
    {
        int x, u, v;
        cin >> x >> u >> v;
        D[u] += x, D[v + 1] -= x;
    }
    
    for (int i = 1; i <= n; ++i) 
    {
        D[i] = ((D[i] + D[i - 1]) % 26 + 26) % 26;
        cout << (char)((s[i] - 'A' + D[i]) % 26 + 'A');
    }

    return 0;
}

