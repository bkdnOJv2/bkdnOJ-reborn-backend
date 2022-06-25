import requests as R

HOST = 'http://localhost:8000'
TEST_USER_PREFIX = 'tester1'
TEST_USER_COUNT = 80

users = [TEST_USER_PREFIX+str(i) for i in range(1, TEST_USER_COUNT+1)]
tokens = [None] * len(users)

TEST_CONTEST = 'icpc2'
TEST_PROBLEM_CODE_PREFIX = 'ICPC21CENTRAL'
TEST_PROBLEM_RANGE = range(ord('A'), ord('G')+1)
TEST_PROBLEM = [TEST_PROBLEM_CODE_PREFIX+chr(c) for c in TEST_PROBLEM_RANGE]

RATIO = [28, 1319, 113, 17, 652, 360, 625, 318, 40, 77, 107, 29, 577, 347, 4, 227]
PF_RATIO = []
for x in RATIO:
    if len(PF_RATIO) == 0:
        PF_RATIO.append(x)
    else:
        PF_RATIO.append(x + PF_RATIO[-1])

SUM = sum(RATIO)

if len(RATIO) < len(TEST_PROBLEM_RANGE):
    RATIO+= [1]*(len(TEST_PROBLEM_RANGE) - len(RATIO))

def authenticate_users(start=0, end=9999):
    global tokens
    for i, u in enumerate(users[start:min(end, len(users))]):
        req = R.post(HOST+'/sign-in/', data={'username':u, 'password':'password'})
        if req.status_code == 200:
            print('auth ' + u + ' success')
            tokens[i+start] = (req.json()['access'])
        else:
            print('auth ' + u + ' failed')
            #tokens.append(None)

SUBMIT_BASEURL = HOST + f"/contest/{TEST_CONTEST}/problem/"
import threading
import time
import random
import json
import os

def random_problem():
    l = len(TEST_PROBLEM)
    s = sum(RATIO[0:l])
    rnd = random.randint(0, s)
    if rnd < PF_RATIO[0]:
        return TEST_PROBLEM[0]
    for i in range(1, l):
        if PF_RATIO[i-1] <= rnd < PF_RATIO[i]:
            return TEST_PROBLEM[i]
    print(rnd)
    print(PF_RATIO)
    raise Exception('Unreachable code is reachable www')

def random_user():
    while True:
        tok = random.choice(tokens)
        if tok is not None:
            return tok

def random_source(prob):
    src = os.listdir(prob)
    src = [code for code in src if code.endswith('.cpp') or code.endswith('.py')]
    rnd_src = random.choice(src)

    if rnd_src.endswith('.cpp'):
        language = 15
    elif rnd_src.endswith('.py'):
        language = 8

    data = {
        'language': language,
        'source': open(f"{prob}/{rnd_src}", "r").read()
    }
    return data

def random_submit():
    rnd_prob = random_problem()
    rnd_tok = random_user()
    rnd_source = random_source(rnd_prob)
    data = json.dumps(rnd_source)
    submit_url = SUBMIT_BASEURL + rnd_prob + '/submit/'
    return R.post(submit_url, data=data,
        headers={'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer '+rnd_tok})

def spam_random_submit(times=1, tid=None):
    for _ in range(times):
        print(f"Thread {tid}: Submitting randomly..")
        req = random_submit()
        print(f"Thread {tid}: Received {req.status_code}")
        rnd_sleep = random.randint(10, 15)
        print(f"Thread {tid}: Sleeping for {rnd_sleep}")
        time.sleep( rnd_sleep )

if __name__ == '__main__':
    print('Mass submitting script --')

    THREADS = 4

    threads = []
    for tid in range(THREADS):
        st = TEST_USER_COUNT//THREADS*tid
        ed = st + TEST_USER_COUNT//THREADS
        print(st, ed)
        t = threading.Thread(name=f"auth-{tid}", target=authenticate_users, args=(st, ed))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
    print(f"{len(tokens)} user(s) successfully authenticated")

    for p in TEST_PROBLEM:
        if not os.path.exists(p):
            raise Exception(f"Folder {p} does not exist.")

    SUBS = 500

    threads = []
    for tid in range(THREADS):
        t = threading.Thread(name=f"random_submit-{tid}", target=spam_random_submit, args=(SUBS, tid))
        t.start()

    for th in threads:
        th.join()
    print("Finished")
