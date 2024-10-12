import os
import subprocess
import sys

device = sys.argv[1]
command = "./param_file/mesh/"+device+".py"
subprocess.run(["python3"+' '+command], shell=True, executable='/bin/bash')