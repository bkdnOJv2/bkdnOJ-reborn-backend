#include<bits/stdc++.h>
using namespace std;
int main(){
	long long a[100005],i,n,dem1=0,dem2=0,ln=0,ok=0,kq=1,mod=pow(10,9)+7;
	cin>>n;
	for (i=1;i<=n;++i){
		cin>>a[i];
		if (a[i]<0){
			dem1++;
		}
		if (a[i]==0){
			dem2++;
		}
		if (a[i]<0&&abs(a[i])<ln){
			ln=a[i];
		}
	}
	if (dem2>1){
		cout<<"0";
		return 0;
	}
	for (i=1;i<=n;i++){
		if (dem1%2==1){
			if (ok==0){
				ok=1;
				continue;
			}
			else {
				kq=kq*a[i]%mod;
			}
		}
		else kq=kq*a[i]%mod;
	}
	cout<<kq;
}
