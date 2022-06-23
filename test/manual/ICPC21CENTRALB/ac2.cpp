#include <bits/stdc++.h>
using namespace std;

/// ====*====*====*====*====*====*====*====*====*====*====*====*====*====*====*====*====

#define ll long long
#define quockhanh qk
#define fl float
#define db double
#define pb push_back
#define pii pair<int, int>
#define ld long double
#define ull unsigned long long int
#define foru(i, a, b, k) for (ll i = a; i <= b; i += k)
#define umap unordered_map
#define ford(i, a, b, k) for (ll i = a; i >= b; i -= k)
#define vint vector<int>
#define vll vector<ll>
#define all(a) (a).begin(), (a).end()
#define fi first
#define se second
#define sz(s) s.size()
#define ctn continue
#define byte unsigned char
#define uint unsigned int
#define ul unsigned long
#define ld long double
#define pb push_back
#define eb emplace_back
#define mp make_pair
#define mt make_tuple
#define fi first
#define se second
#define FORUP(i, star, end) for (ll i = star; i <= end; ++i)
#define FORDOWN(i, star, end) for (ll i = end; i >= star; --i)
#define FORAUTO(item, m) for (auto item : m)
#define foreach(vector) \
    for (auto it : vector) cout << it << ' ';
#define Map_Foreach(map) \
    for (auto it : map) cout << it.fi << ' ' << it.se << "\n";
#define REP(i, n) for (ll i = 0; i < n; ++i)
#define REV(i, n) for (ll i = n - 1; i >= 0; --i)
#define AutoInputArray(a, b, x) FORUP(a, 1, b) cin >> x[i];
#define AutoInputArrayFr0(a, b, x) REP(0, n) cin >> x[i];
#define whatis(x) cout << "Line " << __LINE__ << ": " << #x << " = " << (x) << ", ";
#define ShowTime() cerr << "Executed in " << clock() * 1000 / CLOCKS_PER_SEC << " ms";
#define UpCase(s) transform(s.begin(), s.end(), s.begin(), ::toupper);
#define LowCase(s) transform(s.begin(), s.end(), s.begin(), ::tolower);
#define rall(x) (x).rbegin(), (x).rend()
#define len(x) (int)x.size()
#define endl "\n"
#define elif else if
#define pf push_front
#define popb pop_back
#define popf pop_front
#define ins insert
#define pq priority_queue
#define minele min_element
#define maxele max_element
#define lb lower_bound //first pos >= val
#define ub upper_bound // first pos > val
#define cnt_bit __builtin_popcount
#define debug(...) " [" << #__VA_ARGS__ ": " << (__VA_ARGS__) << "] "

/// ====*====*====*====*====*====*====*====*====*====*====*====*====*====*====*====*====

void ABC(){
    //freopen("1.moivo.inp", "r", stdin);
    //freopen("1.moivo.out", "w", stdout);
    ios_base::sync_with_stdio(0);
    cin.tie(0);
    cout.tie(0);
    cerr.tie(0);
}
void XYZ(){
    // cout << fixed << setprecision(Số chữ số lẻ) << Giá trị cần in;
    return;
}

/// ====*====*====*====*====*====*====*====*====*====*====*====*====*====*====*====*====

const ll mod = 1e9 + 7;
const ll lim = sqrt(2e7 + 100);
const ll INF = 0x3f3f3f3f;
const ll LINF = 0x3f3f3f3f3f3f3f;
const ll maxm = 10011;
const ll M2 = 1ll * mod * mod;
const ll maxn = 1e7 + 9;
const ll nn = 4e3 + 9;
const ll oo = 1e9 + 1e8;
const ll inf = ~(1 << 31);
const ll nmax = 1009;
const ll mm = 2e8;
const ll filerun = 0;
const ll mmax = 1e5 + 9;

/// ====*====*====*====*====*====*====*====*====*====*====*====*====*====*====*====*====

template<typename T> void maximize(T &res, const T &val){ 
	if(res < val){
		res = val;
	} 
}
template<typename T> void minimize(T &res, const T &val){ 
	if(res > val){
		res = val;
	}
}

/// ====*====*====*====*====*====*====*====*====*====*====*====*====*====*====*====*====

inline int readInt() {
    char c;
    while (c = getchar(), c != '-' && (c < '0' || c > '9'))
        ;
    bool sign = (c == '-');
    if (sign)
        c = getchar();
    ll n = c - '0';
    while (c = getchar(), c >= '0' && c <= '9') n = 10 * n + c - '0';
    return (!sign) ? n : -n;
}
inline ll readLong() {
    char c;
    while (c = getchar(), c != '-' && (c < '0' || c > '9'))
        ;
    bool sign = (c == '-');
    if (sign)
        c = getchar();
    ll n = c - '0';
    while (c = getchar(), c >= '0' && c <= '9') n = 10 * n + c - '0';
    return (!sign) ? n : -n;
}

/// ====*====*====*====*====*====*====*====*====*====*====*====*====*====*====*====*====

template <typename T> bool maxoreq(T &res, const T &val) {
    if (res <= val) {
        res = val;
        return true;
    }
    return false;
}
template <typename T> bool minoreq(T &res, const T &val) {
    if (res >= val) {
        res = val;
        return true;
    }
    return false;
}
template <typename T> bool maximize(T &res, const T &val) {
    if (res < val) {
        res = val;
        return true;
    }
    return false;
}
template <typename T> bool minimize(T &res, const T &val) {
    if (res > val) {
        res = val;
        return true;
    }
    return false;
}
template <typename T> ll power(T a, const T b) {
    ll res = 1, x = a, y = b;
    while (y) {
        if (y & 1)
            res *= x;
        x = x * x;
        y >>= 1;
    };
    return res;
}
template <typename T> ll modpower(T a, T b, const T &m) {
    ll res = 1, x = a, y = b;
    x %= m;
    while (y) {
        if (y & 1) {
            res *= x;
            res %= m;
        };
        x = x * x;
        x %= m;
        y >>= 1;
    }
    return res % m;
}
template <typename T> T gcd(T &a, T &b) {
    if (b == 0)
        return a;
    return gcd(b, a % b);
}
template <typename T> T lcm(T &a, T &b) {
    return a / gcd(a, b) * b;
}
template <typename _Tp> 

/// ====*====*====*====*====*====*====*====*====*====*====*====*====*====*====*====*====

void write_unsign(const _Tp &__n) {
    if (__n > 9) {
        write_unsign(__n / 10);
    }
    putchar(__n % 10 + '0');
}
void write(const int &__n) {
    if (__n < 0) {
        putchar('-');
        write_unsign(-__n);
    } else {
        write_unsign(__n);
    }
}
void write(const long long &__n) {
    if (__n < 0) {
        putchar('-');
        write_unsign(-__n);
    } else {
        write_unsign(__n);
    }
}
void write(const unsigned long long &__n) {
    if (__n < 0) {
        putchar('-');
        write_unsign(-__n);
    } else {
        write_unsign(__n);
    }
}
void write(const char &__c){ 
	putchar(__c); 
}
void write(const string &__s) {
    for (auto &__c : __s) {
        putchar(__c);
    }
}
template <typename _Tp, typename... _Ts>
void write(const _Tp &__x, const _Ts &... __y) {
    write(__x);
    write(__y...);
}

/// ====*====*====*====*====*====*====*====*====*====*====*====*====*====*====*====*====

const int base = 1000000000, base_digits = 9;
struct bigint {
    vector<int> a;
    int sign;

    bigint() : sign(1) {}

    bigint(long long v) { *this = v; }

    bigint(const string &s) { read(s); }

    void operator=(const bigint &v) {
        sign = v.sign;
        a = v.a;
    }

    void operator=(long long v) {
        sign = 1;
        if (v < 0)
            sign = -1, v = -v;
        for (; v > 0; v = v / base) a.push_back(v % base);
    }

    bigint operator+(const bigint &v) const {
        if (sign == v.sign) {
            bigint res = v;

            for (int i = 0, carry = 0; i < (int)max(a.size(), v.a.size()) || carry; ++i) {
                if (i == (int)res.a.size())
                    res.a.push_back(0);
                res.a[i] += carry + (i < (int)a.size() ? a[i] : 0);
                carry = res.a[i] >= base;
                if (carry)
                    res.a[i] -= base;
            }
            return res;
        }
        return *this - (-v);
    }

    bigint operator-(const bigint &v) const {
        if (sign == v.sign) {
            if (abs() >= v.abs()) {
                bigint res = *this;
                for (int i = 0, carry = 0; i < (int)v.a.size() || carry; ++i) {
                    res.a[i] -= carry + (i < (int)v.a.size() ? v.a[i] : 0);
                    carry = res.a[i] < 0;
                    if (carry)
                        res.a[i] += base;
                }
                res.trim();
                return res;
            }
            return -(v - *this);
        }
        return *this + (-v);
    }

    void operator*=(int v) {
        if (v < 0)
            sign = -sign, v = -v;
        for (int i = 0, carry = 0; i < (int)a.size() || carry; ++i) {
            if (i == (int)a.size())
                a.push_back(0);
            long long cur = a[i] * (long long)v + carry;
            carry = (int)(cur / base);
            a[i] = (int)(cur % base);
            // asm("divl %%ecx" : "=a"(carry), "=d"(a[i]) : "A"(cur), "c"(base));
        }
        trim();
    }

    bigint operator*(int v) const {
        bigint res = *this;
        res *= v;
        return res;
    }

    friend pair<bigint, bigint> divmod(const bigint &a1, const bigint &b1) {
        int norm = base / (b1.a.back() + 1);
        bigint a = a1.abs() * norm;
        bigint b = b1.abs() * norm;
        bigint q, r;
        q.a.resize(a.a.size());

        for (int i = a.a.size() - 1; i >= 0; i--) {
            r *= base;
            r += a.a[i];
            int s1 = r.a.size() <= b.a.size() ? 0 : r.a[b.a.size()];
            int s2 = r.a.size() <= b.a.size() - 1 ? 0 : r.a[b.a.size() - 1];
            int d = ((long long)base * s1 + s2) / b.a.back();
            r -= b * d;
            while (r < 0) r += b, --d;
            q.a[i] = d;
        }

        q.sign = a1.sign * b1.sign;
        r.sign = a1.sign;
        q.trim();
        r.trim();
        return make_pair(q, r / norm);
    }

    bigint operator/(const bigint &v) const { return divmod(*this, v).first; }

    bigint operator%(const bigint &v) const { return divmod(*this, v).second; }

    void operator/=(int v) {
        if (v < 0)
            sign = -sign, v = -v;
        for (int i = (int)a.size() - 1, rem = 0; i >= 0; --i) {
            long long cur = a[i] + rem * (long long)base;
            a[i] = (int)(cur / v);
            rem = (int)(cur % v);
        }
        trim();
    }

    bigint operator/(int v) const {
        bigint res = *this;
        res /= v;
        return res;
    }

    int operator%(int v) const {
        if (v < 0)
            v = -v;
        int m = 0;
        for (int i = a.size() - 1; i >= 0; --i) m = (a[i] + m * (long long)base) % v;
        return m * sign;
    }

    void operator+=(const bigint &v) { *this = *this + v; }
    void operator-=(const bigint &v) { *this = *this - v; }
    void operator*=(const bigint &v) { *this = *this * v; }
    void operator/=(const bigint &v) { *this = *this / v; }

    bool operator<(const bigint &v) const {
        if (sign != v.sign)
            return sign < v.sign;
        if (a.size() != v.a.size())
            return a.size() * sign < v.a.size() * v.sign;
        for (int i = a.size() - 1; i >= 0; i--)
            if (a[i] != v.a[i])
                return a[i] * sign < v.a[i] * sign;
        return false;
    }

    bool operator>(const bigint &v) const { return v < *this; }
    bool operator<=(const bigint &v) const { return !(v < *this); }
    bool operator>=(const bigint &v) const { return !(*this < v); }
    bool operator==(const bigint &v) const { return !(*this < v) && !(v < *this); }
    bool operator!=(const bigint &v) const { return *this < v || v < *this; }

    void trim() {
        while (!a.empty() && !a.back()) a.pop_back();
        if (a.empty())
            sign = 1;
    }

    bool isZero() const { return a.empty() || (a.size() == 1 && !a[0]); }

    bigint operator-() const {
        bigint res = *this;
        res.sign = -sign;
        return res;
    }

    bigint abs() const {
        bigint res = *this;
        res.sign *= res.sign;
        return res;
    }

    long long longValue() const {
        long long res = 0;
        for (int i = a.size() - 1; i >= 0; i--) res = res * base + a[i];
        return res * sign;
    }

    friend bigint gcd(const bigint &a, const bigint &b) { return b.isZero() ? a : gcd(b, a % b); }
    friend bigint lcm(const bigint &a, const bigint &b) { return a / gcd(a, b) * b; }

    void read(const string &s) {
        sign = 1;
        a.clear();
        int pos = 0;
        while (pos < (int)s.size() && (s[pos] == '-' || s[pos] == '+')) {
            if (s[pos] == '-')
                sign = -sign;
            ++pos;
        }
        for (int i = s.size() - 1; i >= pos; i -= base_digits) {
            int x = 0;
            for (int j = max(pos, i - base_digits + 1); j <= i; j++) x = x * 10 + s[j] - '0';
            a.push_back(x);
        }
        trim();
    }

    friend istream &operator>>(istream &stream, bigint &v) {
        string s;
        stream >> s;
        v.read(s);
        return stream;
    }

    friend ostream &operator<<(ostream &stream, const bigint &v) {
        if (v.sign == -1)
            stream << '-';
        stream << (v.a.empty() ? 0 : v.a.back());
        for (int i = (int)v.a.size() - 2; i >= 0; --i) stream << setw(base_digits) << setfill('0') << v.a[i];
        return stream;
    }

    static vector<int> convert_base(const vector<int> &a, int old_digits, int new_digits) {
        vector<long long> p(max(old_digits, new_digits) + 1);
        p[0] = 1;
        for (int i = 1; i < (int)p.size(); i++) p[i] = p[i - 1] * 10;
        vector<int> res;
        long long cur = 0;
        int cur_digits = 0;
        for (int i = 0; i < (int)a.size(); i++) {
            cur += a[i] * p[cur_digits];
            cur_digits += old_digits;
            while (cur_digits >= new_digits) {
                res.push_back(int(cur % p[new_digits]));
                cur /= p[new_digits];
                cur_digits -= new_digits;
            }
        }
        res.push_back((int)cur);
        while (!res.empty() && !res.back()) res.pop_back();
        return res;
    }

    static vll karatsubaMultiply(const vll &a, const vll &b) {
        int n = a.size();
        vll res(n + n);
        if (n <= 32) {
            for (int i = 0; i < n; i++)
                for (int j = 0; j < n; j++) res[i + j] += a[i] * b[j];
            return res;
        }

        int k = n >> 1;
        vll a1(a.begin(), a.begin() + k);
        vll a2(a.begin() + k, a.end());
        vll b1(b.begin(), b.begin() + k);
        vll b2(b.begin() + k, b.end());

        vll a1b1 = karatsubaMultiply(a1, b1);
        vll a2b2 = karatsubaMultiply(a2, b2);

        for (int i = 0; i < k; i++) a2[i] += a1[i];
        for (int i = 0; i < k; i++) b2[i] += b1[i];

        vll r = karatsubaMultiply(a2, b2);
        for (int i = 0; i < (int)a1b1.size(); i++) r[i] -= a1b1[i];
        for (int i = 0; i < (int)a2b2.size(); i++) r[i] -= a2b2[i];

        for (int i = 0; i < (int)r.size(); i++) res[i + k] += r[i];
        for (int i = 0; i < (int)a1b1.size(); i++) res[i] += a1b1[i];
        for (int i = 0; i < (int)a2b2.size(); i++) res[i + n] += a2b2[i];
        return res;
    }

    bigint operator*(const bigint &v) const {
        vector<int> a6 = convert_base(this->a, base_digits, 6);
        vector<int> b6 = convert_base(v.a, base_digits, 6);
        vll a(a6.begin(), a6.end());
        vll b(b6.begin(), b6.end());
        while (a.size() < b.size()) a.push_back(0);
        while (b.size() < a.size()) b.push_back(0);
        while (a.size() & (a.size() - 1)) a.push_back(0), b.push_back(0);
        vll c = karatsubaMultiply(a, b);
        bigint res;
        res.sign = sign * v.sign;
        for (int i = 0, carry = 0; i < (int)c.size(); i++) {
            long long cur = c[i] + carry;
            res.a.push_back((int)(cur % 1000000));
            carry = (int)(cur / 1000000);
        }
        res.a = convert_base(res.a, 6, base_digits);
        res.trim();
        return res;
    }
};

/// ====*====*====*====*====*====*====*====*====*====*====*====*====*====*====*====*====

string add(string a, string b) {
    string res = "";
    while (a.size() < b.size()) a = "0" + a;
    while (b.size() < a.size()) b = "0" + b;
    int carry = 0;
    for (int i = a.size() - 1; i >= 0; i--) {
        int tmp = a[i] - 48 + b[i] - 48 + carry;
        carry = tmp / 10;
        tmp = tmp % 10;
        res = (char)(tmp + 48) + res;
    }
    if (carry > 0)
        res = "1" + res;
    return res;
}
string sub(string a, string b) {
    string res = "";
    while (a.size() < b.size()) a = "0" + a;
    while (b.size() < a.size()) b = "0" + b;
    bool neg = false;
    if (a < b) {
        swap(a, b);
        neg = true;
    }
    int borrow = 0;
    for (int i = a.size() - 1; i >= 0; i--) {
        int tmp = a[i] - b[i] - borrow;
        if (tmp < 0) {
            tmp += 10;
            borrow = 1;
        } else
            borrow = 0;
        res = (char)(tmp % 10 + 48) + res;
    }
    while (res.size() > 1 && res[0] == '0') res.erase(0, 1);
    if (neg)
        res = "-" + res;
    return res;
}
string mul(string a, string b) {
    string res = "";
    int n = a.size();
    int m = b.size();
    int len = n + m - 1;
    int carry = 0;
    for (int i = len; i >= 0; i--) {
        int tmp = 0;
        for (int j = n - 1; j >= 0; j--)
            if (i - j <= m && i - j >= 1) {
                int a1 = a[j] - 48;
                int b1 = b[i - j - 1] - 48;
                tmp += a1 * b1;
            }
        tmp += carry;
        carry = tmp / 10;
        res = (char)(tmp % 10 + 48) + res;
    }
    while (res.size() > 1 && res[0] == '0') res.erase(0, 1);
    return res;
}

/// ====*====*====*====*====*====*====*====*====*====*====*====*====*====*====*====*====

short n, negativecnt, duong, i, zerocnt;
ll ans = 1, a[1005], the[1005];

int main(){
	ABC();
    cin >> n;
    for(; i < n; i++){
    	cin >> a[i];
    	if(a[i] < 0){the[negativecnt] = a[i];negativecnt++;}
		if(a[i] == 0){zerocnt++;}
		/*
    	if(a[i] > 0){
    		b[duong] = a[i];
    		duong++;
		}
		*/
    }
    // Số lượng số 0 > 1 => ans = 0
    if(zerocnt > 1){cout << 0;return 0;}
	// Chắn hoặc là không có số âm nào với việc không có số âm thì nhân bình thường
	if((negativecnt == 0 || !(negativecnt & 1)) && !zerocnt)
		for(i = 0; i < n; i++) ans = ans * a[i] % mod;
	else{
		// Nếu số lượng số âm là lẻ mà còn có một số 0 => ans = 0 => giá trị lớn nhất
		if(negativecnt & 1 && zerocnt){cout << 0;return 0;}
		// Nếu số lượng số âm là chắn mà còn có một số 0 => bỏ số 0 đó đi
		else if(!(negativecnt & 1) && zerocnt)
			for(i = 0; i < n; i++){if(a[i] == 0)continue;ans = ans * a[i] % mod;}
		// Nếu không có số 0 thì sắp xếp lại theo thứ tự tăng dần
		// Lấy số trung gian giữa 2 đoạn số trung gian để có thể bỏ qua số âm to nhất
		// số âm lớn nhất trước số dương nhỏ nhất
		else{
			sort(the, the + negativecnt);
			sort(a, a + n);
			for(i = 0; i < negativecnt - 1; i++){
				ans = ans * the[i] % mod;
			}
			for(i = negativecnt; i < n; i++){
				ans = ans * a[i] % mod;
			}
		}
	}
	cout << ans;
	XYZ();
}
