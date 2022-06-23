#include <bits/stdc++.h>

using namespace std;

int main()
{
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    cout.tie(NULL);

    int n, count = 0;
    cin >> n;

    double arr[n], ave = 0, ans = 0;
    setprecision(8);

    for (int i = 0; i < n; i++)
    {
        cin >> arr[i];
        if (i > 0)
        {
            if (arr[i] < arr[i - 1])
            {
                if (count == 0)
                {
                    ave += arr[i - 1];
                    count++;
                }
                ave += arr[i];
                count++;
            }
        }
    }
    if (count > 0)
    {
        ave /= count;

        count = 0;

        for (int i = 0; i < n; i++)
        {
            if (i > 0)
            {
                if (arr[i] < arr[i - 1])
                {
                    if (count == 0)
                    {
                        ans += pow(arr[i - 1] - ave, 2);
                    }
                    ans += pow(arr[i] - ave, 2);
                }
            }
        }
    }
    cout << setprecision(10) << fixed << sqrt(ans);

    return 0;
}
