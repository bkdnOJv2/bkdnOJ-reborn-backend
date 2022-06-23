#include <bits/stdc++.h>

using namespace std;

#define ll long long 
#define ld long double
#define ull unsigned long long
#define bigint __int128
#define pb push_back

const int N = 1e3 + 2, T = 3e7, mod = 1e9 + 7;
const ll MAX = 1e18, MOD = 1000000000000000009;

int n, a[N], yero;

int main()
{
	ios_base::sync_with_stdio(false);
	cin.tie(NULL);
	cout.tie(NULL);
	
	cin >> n;
	int tich = 1;
	for (int i = 1; i <= n; i++)
	{
		cin >> a[i];
		if(a[i] < 0)
			tich *= -1;
		else if(a[i] > 0)
			tich *= 1;
		else
			yero += 1, tich *= 0;
	}
	
	if(tich > 0)
	{
		ll ans = 1;
		for(int i = 1; i <= n; i++) // remove 0 element
			ans = ans * a[i] % mod;
		cout << ans;
	}
	else if(tich == 0)
	{
		if(yero > 1)
			cout << 0; 
		else
		{
			ll ans = 1, c = 1;
			for(int i = 1; i <= n; i++)
				if(a[i] != 0)
					ans = ans * a[i] % mod, c *= a[i] / abs(a[i]);
			if(c > 0)
				cout << ans; // remove an element 0, ans = max(0, mul not 0)
			else
				cout << 0;
		}
	}
	else
	{
		int Max_ne = -1e9, pos;
		for(int i = 1; i <= n; i++)
			if(a[i] < 0 && a[i] > Max_ne)
				Max_ne = a[i], pos = i;
				
		ll ans = 1;
		for(int i = 1; i <= n; i++)
			if(i != pos)
				ans = ans * a[i] % mod;
		cout << ans; // ans = a[1] * ... * a[n] / a[j]; a[j] is the max_negative_element
	}
}

