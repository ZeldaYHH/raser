import os
import subprocess
import sys

device = sys.argv[1]
command = "./param_file/mesh/"+device+".py"

IMGFILE = os.environ.get('IMGFILE')
BINDPATH = os.environ.get('BINDPATH')
raser_shell = "/usr/bin/apptainer exec --env-file cfg/env -B" + " " \
            + BINDPATH + " " \
            + IMGFILE + " " \
            + "python3"
subprocess.run([raser_shell+' '+command], shell=True, executable='/bin/bash')