# Setup raser environment     
# Author SHI Xin <shixin@ihep.ac.cn>  
# Created [2023-08-31 Thu 08:36] 

echo "Setting up raser ..."

dir_raser=$(cd $(dirname $(dirname $BASH_SOURCE[0])) && pwd)
cfg_env=$dir_raser/cfg/env
rm -f $cfg_env
cat << EOF >> $cfg_env
# PATH 
PATH=/afs/ihep.ac.cn/soft/common/sysgroup/hep_job/bin:/usr/bin:\$PATH

# ROOT 
ROOTSYS=/usr/local/share/root_install

# Geant4 
G4ENSDFSTATEDATA=/cvmfs/common.ihep.ac.cn/software/geant4/10.7.p02/data/G4ENSDFSTATE2.3
G4PIIDATA=/cvmfs/common.ihep.ac.cn/software/geant4/10.7.p02/data/G4PII1.3
G4INCLDATA=/cvmfs/common.ihep.ac.cn/software/geant4/10.7.p02/data/G4INCL1.0
G4LEDATA=/cvmfs/common.ihep.ac.cn/software/geant4/10.7.p02/data/G4EMLOW7.13
G4PARTICLEXSDATA=/cvmfs/common.ihep.ac.cn/software/geant4/10.7.p02/data/G4PARTICLEXS3.1.1
GEANT4_INSTALL=/cvmfs/common.ihep.ac.cn/software/geant4/10.7.p02/install
G4NEUTRONHPDATA=/cvmfs/common.ihep.ac.cn/software/geant4/10.7.p02/data/G4NDL4.6
G4SAIDXSDATA=/cvmfs/common.ihep.ac.cn/software/geant4/10.7.p02/data/G4SAIDDATA2.0
G4REALSURFACEDATA=/cvmfs/common.ihep.ac.cn/software/geant4/10.7.p02/data/RealSurface2.2
G4ABLADATA=/cvmfs/common.ihep.ac.cn/software/geant4/10.7.p02/data/G4ABLA3.1
G4LEVELGAMMADATA=/cvmfs/common.ihep.ac.cn/software/geant4/10.7.p02/data/PhotonEvaporation5.7
G4RADIOACTIVEDATA=/cvmfs/common.ihep.ac.cn/software/geant4/10.7.p02/data/RadioactiveDecay5.6

# Python 
PYTHONPATH=$dir_raser/raser:/usr/local/share/root_install/lib:/cvmfs/common.ihep.ac.cn/software/geant4/10.7.p02/install/lib64/python3.6/site-packages:/usr/local/share/acts_build/python
LD_LIBRARY_PATH=/cvmfs/common.ihep.ac.cn/software/geant4/10.7.p02/install/lib64:/usr/local/share/root_install/lib:/.singularity.d/libs

#pyMTL3 Verilator
PYMTL_VERILATOR_INCLUDE_DIR="/usr/local/share/verilator/include"
EOF

export PATH=/afs/ihep.ac.cn/soft/common/sysgroup/hep_job/bin:$PATH
export IMGFILE=/afs/ihep.ac.cn/users/s/shixin/img/raser-2.2.sif
export BINDPATH=/afs,/besfs5,/cefs,/cvmfs,/publicfs,/scratchfs,/workfs2

alias raser="python3 raser"
alias raser-test="apptainer exec --env-file $cfg_env -B $BINDPATH $IMGFILE python3 -m unittest discover -v -s tests"
alias raser-shell="apptainer shell --env-file $cfg_env -B $BINDPATH $IMGFILE"
alias pytest="apptainer exec --env-file $cfg_env -B $BINDPATH $IMGFILE pytest"
alias raser-install="apptainer exec --env-file $cfg_env -B $BINDPATH $IMGFILE pip install -e ."  

