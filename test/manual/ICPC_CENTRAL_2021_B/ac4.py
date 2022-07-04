n, a, am, duong = int(input()), list(map(int, input().split())), [], []
for x in a:
    if x < 0: am.append(x)
    else: duong.append(x)
res = 1
if len(am) % 2 == 1: 
    am.sort(reverse = True)
    am = am[1:len(am)]
else:
    duong.sort()
    if len(duong) > 0 and duong[0] == 0: duong = duong[1:len(duong)]
for x in am: res = (res * x) % 1000000007
for x in duong: res = (res * x) % 1000000007
print(res)
