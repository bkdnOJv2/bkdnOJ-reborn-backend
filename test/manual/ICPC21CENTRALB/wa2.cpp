#include <bits/stdc++.h>

using namespace std;

int main()
{
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    cout.tie(NULL);

    long long n, count = 0, ans = 1;
    cin >> n;
    long long arr[n];

    for (long long i = 0; i < n; i++)
    {
        cin >> arr[i];
        if (arr[i] < 0)
        {
            count++;
        }
    }
    sort(arr, arr + n);

    if (count % 2 != 0)
    {
        arr[count - 1] = 1;
    }
    for (long long i = 0; i < n; i++)
    {
        ans *= arr[i];
        ans %= 1000000007;
    }
    cout << ans;

    return 0;
}

