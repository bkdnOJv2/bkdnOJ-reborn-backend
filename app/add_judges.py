# CHANGE BELOW TO YOUR JUDGE CONFIG
YAML_TEMPLATE = """
problem_storage_root:
    - /home/ubuntu/backend/media/problem_data
runtime:
    as_x64: /usr/bin/x86_64-linux-gnu-as
    as_x86: /usr/bin/as
    awk: /usr/bin/mawk
    cat: /usr/bin/cat
    g++: /usr/bin/g++
    g++11: /usr/bin/g++
    g++14: /usr/bin/g++
    g++17: /usr/bin/g++
    gcc: /usr/bin/gcc
    gcc11: /usr/bin/gcc
    ld_x64: /usr/bin/x86_64-linux-gnu-ld
    ld_x86: /usr/bin/ld
    perl: /usr/bin/perl
    python3: /usr/bin/python3
    sed: /usr/bin/sed
"""

JUDGE_PREFIX = 'judge'
JUDGE_SECRET = 'GTjFfvbHYTRFghj23456YGhu5redCVBHJuytrdcgVSWertyujmKI&^trfdcfvgbvCDSErtgbnjuy6trdFGH'
JUDGE_COUNT = 3

# Will write configs file to this location
JUDGE_CONFIG_LOCATION = "/home/ubuntu/judge/configs"

def gen_secret(key=0): # Implement hash here if want unique secret per judge
    return JUDGE_SECRET

import os, sys
if os.path.exists(JUDGE_CONFIG_LOCATION):
    print("Ok. Found config folder")
else:
    print(f"Cannot find path '{JUDGE_CONFIG_LOCATION}', please create a folder there")
    sys.exit(0)

from judger.models.runtime import Judge
from django.db import transaction

with transaction.atomic():
    try:
        for jidx in range(1, JUDGE_COUNT+1):
            name = f"{JUDGE_PREFIX}_{jidx}"
            secret = gen_secret(jidx)
            Judge.objects.create(name=name, auth_key=secret)
            print(f"Created judge {name}.")
    except Exception as e:
        print(f"Error {e}")
        print(f"Error while creating judge {name}. Rollback.")

print("Done creating Judges. Now creating configs")
try:
    for jidx in range(1, JUDGE_COUNT+1):
        filename = f"{JUDGE_PREFIX}_{jidx}_config.yaml"
        name = f"{JUDGE_PREFIX}_{jidx}"
        secret = gen_secret(jidx)
        with open(f"{JUDGE_CONFIG_LOCATION}/{filename}", "w") as f:
            f.write(
                f"id: '{name}'\n"+
                f"key: '{secret}'\n"+
                YAML_TEMPLATE
            )
except Exception as e:
    print(f"Error while creating configs for judge {name}. Err: {e}")
