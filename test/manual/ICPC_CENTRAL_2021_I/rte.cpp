#include <bits/stdc++.h>
using namespace std;

struct TWO_SAT{
    vector<vector<int> > e;
    vector <int> flag;
    stack <int> st;

    TWO_SAT(int n) {
        e.resize(n * 2);
    }

    void add(int x, int tx, int y, int ty){
        x = x << 1 ^ tx;
        y = y << 1 ^ ty;
        e[x].push_back(y);
    }

    bool dfs(int u)
    {
        if (flag[u ^ 1])
        {
            return 0;
        }
        if (flag[u])
        {
            return 1;
        }
        flag[u] = 1;
        st.push(u);
        for (auto &v: e[u])
        {
            if (!dfs(v))
            {
                return 0;
            }
        }
        return 1;
    }

    vector <int> solve()
    {
        int n = e.size();
        for (int i = 0; i < n; i += 2)
        {
            if (!flag[i] && !flag[i ^ 1])
            {
                st = stack <int>();
                if (!dfs(i))
                {
                    while (!st.empty())
                    {
                        flag[st.top()] = 0;
                        st.pop();
                    }
                    if (!dfs(i ^ 1))
                    {
                        return {};
                    }
                }
            }
        }
        vector <int> ans(n >> 1);
        for (int i = 0; i < n; i += 2)
        {
            ans[i >> 1] = flag[i ^ 1];
        }
        return ans;
    }
};
int x[2505],y[2505],u[2505],v[2505];
bool khonggiao(int i,int h,int j,int k)
{
    int x1,y1,x2,y2,u1,v1,u2,v2;
    x1=x[i];
    y1=y[i];
    u1=u[i];
    v1=v[i];

    x2=x[j];
    y2=y[j];
    u2=u[j];
    v2=v[j];

    if (h) swap(u1,v1);
    if (k) swap(u2,v2);

    return ((2*x1+u1<=2*x2-u2) || (2*x2+u2<=2*x1-u1) || (2*y1+v1<=2*y2-v2) || (2*y2+v2<=2*y1-v1));
}
int main()
{
    ios_base::sync_with_stdio(0);cin.tie(0);cout.tie(0);
    int n;
    cin>>n;
    TWO_SAT X(n);
    for (int i=0;i<n;++i)
    {
        cin>>x[i]>>y[i]>>u[i]>>v[i];
        for (int j=0;j<i;++j)
        {
            for (int h=0;h<2;++h)
             for (int k=0;k<2;++k)

            if (!khonggiao(i,h,j,k))
            {
                X.add(i,h,j,k^1);
                X.add(j,k,i,h^1);
            }
        }

    }
    vector<int> ans=X.solve();
    if (ans.empty()) cout<<"No";
    else
    {
        cout<<"Yes"<<'\n';
        for (int i=0;i<n;++i)
         if (ans[i]) cout<<'Q';else cout<<'K';
    }



    return 0;
}

