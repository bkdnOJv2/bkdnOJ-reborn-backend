import subprocess

from .__init__ import app
from .__fmt__ import *

class CONTAINER_TYPES:
    TYPE_APP='app'
    TYPE_DB_MIGRATE='db_migrate'
    ALL=[TYPE_APP, TYPE_DB_MIGRATE]

@app.command()
def containerize(type: str, push_to_remote: bool) -> None:
    if type not in CONTAINER_TYPES.ALL:
        print(bad_input(f"Type '{type}' not recognizable. Expecting one of the following {CONTAINER_TYPES.ALL}"))
    
    if type == CONTAINER_TYPES.TYPE_APP:
        result = subprocess.run([
            "bash",
            "./scripts/script_bash/dockerize.sh",
            "latest",
            "" if not push_to_remote else "push"
        ])
        if result.returncode != 0 and push_to_remote:
            print(info("If at REMOTE: credentials may expire already, please update"))
            print(info("If at LOCAL: remember to do `docker login` first if you want to push to hub.docker.com"))

    print(type, push_to_remote)