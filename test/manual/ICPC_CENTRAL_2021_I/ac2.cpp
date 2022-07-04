#include<bits/stdc++.h>
using namespace std;
long long n;
long long ap[2601];
long long x[2610],y[2610],w[2610],h[2610];
bool overlap(long long i,long long j,bool x1, bool y1){
    if (x1){
        swap(w[i],h[i]);
    }
    if (y1){
        swap(w[j],h[j]);
    }
    if (x[i] + w[i] <= x[j] - w[j] || x[i] - w[i] >= x[j] + w[j]){
            if (x1){
        swap(w[i],h[i]);
    }
    if (y1){
        swap(w[j],h[j]);
    }
        return 0;
    }
    if (y[i] + h[i] <= y[j] - h[j] || y[i] - h[i] >= y[j] + h[j]){
        if (x1){
        swap(w[i],h[i]);
    }
    if (y1){
        swap(w[j],h[j]);
    }
        return 0;
    }
    if (x1){
        swap(w[i],h[i]);
    }
    if (y1){
        swap(w[j],h[j]);
    }
    return 1;
}
int main(){
    cin>>n;
    for (long long i = 1;i <= n;i ++){
        cin>>x[i]>>y[i]>>w[i]>>h[i];
        x[i] *= 2;
        y[i] *= 2;
    }
    memset(ap,-1,sizeof ap);
    bool error = 0;
    for (long long i = 1;i <= n; i++){
        if (ap[i] == -1){
            bool fuck = 0;
            ap[i] = 0;
            queue <long long> q;
            queue <long long> q1;
            q.push(i);
            q1.push(i);
            while (!q.empty() && !fuck){
                long long u = q.front();
                q.pop();
                for (long long v = 1;v <= n;v ++){
                    if (v==u)continue;
                    if (ap[v] == -1){
                        bool ok[2];
                        ok[0] = overlap(u,v,ap[u],0);
                        ok[1] = overlap(u,v,ap[u],1);
                        if (ok[0]){
                            if (!ok[1]){
                                q.push(v);
                                ap[v] = 1;
                            }
                            else{
                                fuck = 1;
                                break;
                            }
                        }
                        else{
                            if (ok[1]){
                                q.push(v);
                                ap[v] = 0;
                            }
                        }
                    }
                    else{
                        if (overlap(u,v,ap[u],ap[v])){
                            fuck = 1;
                            break;
                        }
                    }
                }
            }
            if (fuck){
                while (!q1.empty()){
                    long long x = q1.front();
                    ap[x] = -1;
                    q1.pop();
                }
                while (!q.empty()){
                    q.pop();
                }
                fuck = 0;
                ap[i] = 1;
                q.push(i);
                q1.push(i);
                while (!q.empty() && !fuck){
                    long long u = q.front();
                    q.pop();
                    for (long long v = 1;v <= n;v ++){
                        if (v==u)continue;
                        if (ap[v] == -1){
                            bool ok[2];
                            ok[0] = overlap(u,v,ap[u],0);
                            ok[1] = overlap(u,v,ap[u],1);
                            if (ok[0]){
                                if (!ok[1]){
                                    q.push(v);
                                    ap[v] = 1;
                                }
                                else{
                                    fuck = 1;
                                    break;
                                }
                            }
                            else{
                                if (ok[1]){
                                    q.push(v);
                                    ap[v] = 0;
                                }
                            }
                        }
                        else{
                            if (overlap(u,v,ap[u],ap[v])){
                                fuck = 1;
                                break;
                            }
                        }
                    }
                }
                if (fuck){
                    error = 1;
                    break;
                }
            }
        }
    }
    if (error){
        cout<<"No\n";
    }
    else{
        cout<<"Yes\n";
        for (long long i = 1;i <= n;i ++){
            if (ap[i] == 1){
                cout<<"Q";
            }
            else{
                cout<<"K";
            }
        }
    }
    return 0;
}

