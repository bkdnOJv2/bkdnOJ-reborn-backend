#include <bits/stdc++.h>

using namespace std;

int n;
int a[205][205], b[205][205];
int f[205], ans[205][205];
vector<pair<int, pair<int, int> > > edges;

int find(int i)
{
	return f[i]==i? f[i]:f[i]=find(f[i]);
}

void unionn(int i, int j)
{
	f[find(i)]=find(j);
}

void solve()
{
	edges.clear();
	cin>>n;
	for(int i=1; i<=n; i++)
	{
		f[i]=i;
		for(int j=1; j<=n; j++)
		{
			cin>>a[i][j];
			b[i][j]=a[i][j];
			ans[i][j]=0;
			if(i<j) edges.push_back({a[i][j], {i, j}});
		}
	}
	for(int i=1; i<=n; i++)
	{
		for(int j=1; j<=n; j++)
		{
			for(int k=1; k<=n; k++)
			{
				b[j][k]=max(b[j][k], min(b[j][i], b[i][k]));
			}
		}
	}
	// cout<<b[1][2]<<" "<<a[1][2]<<endl;
	bool can=true;
	for(int i=1; i<=n; i++)
	{
		for(int j=1; j<=n; j++)
		{
			if(b[i][j]>a[i][j]&&i!=j)
			{
				// cout<<i<<" "<<j<<" "<<b[i][j]<<" "<<a[i][j]<<endl;
				can=false; 
			}
		}
	}
	if(!can)
	{
		cout<<"NO\n";
		return;
	}
	sort(edges.begin(), edges.end());
	reverse(edges.begin(), edges.end());
	for(auto i:edges)
	{
		if(find(i.second.first)!=find(i.second.second))
		{
			ans[i.second.first][i.second.second]=i.first;
			ans[i.second.second][i.second.first]=i.first;
			unionn(i.second.first, i.second.second);
		}
	}
	cout<<"YES\n";
	for(int i=1; i<=n; i++)
	{
		for(int j=1; j<=n; j++)
		{
			cout<<ans[i][j]<<" ";
		}
		cout<<endl;
	}
}

signed main()
{
	ios::sync_with_stdio(false);
	cin.tie(0);
	cout.tie(0);
	int tests;
	cin>>tests;
	for(int test=1; test<=tests; test++)
	{
		cout<<"Case #"<<test<<": ";
		solve();
	}
}
