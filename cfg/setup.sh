# Setup raser environment     
# Author SHI Xin <shixin@ihep.ac.cn>  
# Created [2023-08-31 Thu 08:36] 

echo "Setting up raser ..."

export PATH=/afs/ihep.ac.cn/soft/common/sysgroup/hep_job/bin:$PATH
export IMGFILE=/afs/ihep.ac.cn/users/s/shixin/raser/raser-2.0.sif
export BINDPATH=/cefs,/afs,/besfs5,/cvmfs,/scratchfs,/workfs2,/publicfs

alias raser="apptainer exec --env-file cfg/env -B $BINDPATH $IMGFILE python3 raser"
alias test-raser="apptainer exec --env-file cfg/env -B $BINDPATH $IMGFILE python3 -m unittest discover -v -s tests"

