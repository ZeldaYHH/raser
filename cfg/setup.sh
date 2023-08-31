# Setup raser environment     
# Author SHI Xin <shixin@ihep.ac.cn>  
# Created [2023-08-31 Thu 08:36] 

echo "Setting up raser ..."

export RASER_IMG=/afs/ihep.ac.cn/users/s/shixin/raser/raser-2.0.sif
export PATH=/afs/ihep.ac.cn/soft/common/sysgroup/hep_job/bin:$PATH

alias ls="ls -h --color"
alias raser="python3 raser"
