#include<bits/stdc++.h>
using namespace std;
int n,m;
int cnt[2000100];
int a[501];
int main(){
    cin>>n>>m;
    for (int i = 0;i < m;i ++)cin>>a[i];
    sort(a,a+m);
    vector <pair<int,int>> bruh;
            bruh.push_back({a[0],1});

    for (int i = 1;i < m;i ++){
        if (a[i] != a[i-1]){
            bruh.push_back({a[i],1});
        }
        else{
            bruh[bruh.size() - 1].second++;
        }
    }
    for (auto x:bruh){
        for (int j = 1;x.first * j <= n;j ++){
            cnt[x.first * j] += x.second;
        }
    }
    int res = 0;
    for (int i = 1;i <= n;i ++){
        res = max(res,cnt[i]);
    }
    cout<<res;
    return 0;
}

