# Setup raser environment     
# Author SHI Xin <shixin@ihep.ac.cn>  
# Created [2023-08-31 Thu 08:36] 

echo "Setting up raser ..."

export PATH=/afs/ihep.ac.cn/soft/common/sysgroup/hep_job/bin:$PATH
export IMGFILE=/afs/ihep.ac.cn/users/s/shixin/raser/raser-2.2.sif
export BINDPATH=/afs,/besfs5,/cefs,/cvmfs,/publicfs,/scratchfs,/workfs2

alias raser="python3 raser"
alias raser-test="apptainer exec --env-file cfg/env -B $BINDPATH $IMGFILE python3 -m unittest discover -v -s tests"
alias raser-shell="apptainer shell --env-file cfg/env -B $BINDPATH $IMGFILE"
alias pytest="apptainer exec --env-file cfg/env -B $BINDPATH $IMGFILE pytest"
