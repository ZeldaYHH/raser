# Setup raser environment     
# Author SHI Xin <shixin@ihep.ac.cn>  
# Created [2023-08-31 Thu 08:36] 

echo "Setting up raser ..."

dir_raser=$(cd $(dirname $(dirname $BASH_SOURCE[0])) && pwd)
Geant4PATH=/cvmfs/common.ihep.ac.cn/software/geant4/10.7.p02

cfg_env=$dir_raser/cfg/env
rm -f $cfg_env
cat << EOF >> $cfg_env
# PATH 
PATH=/cvmfs/common.ihep.ac.cn/software/hepjob/bin:/usr/bin:\$PATH

# ROOT 
ROOTSYS=/usr/local/share/root_install

# Geant4 
GEANT4_INSTALL=$Geant4PATH/install
G4ENSDFSTATEDATA=$Geant4PATH/data/G4ENSDFSTATE2.3
G4PIIDATA=$Geant4PATH/data/G4PII1.3
G4INCLDATA=$Geant4PATH/data/G4INCL1.0
G4LEDATA=$Geant4PATH/data/G4EMLOW7.13
G4PARTICLEXSDATA=$Geant4PATH/data/G4PARTICLEXS3.1.1
G4NEUTRONHPDATA=$Geant4PATH/data/G4NDL4.6
G4SAIDXSDATA=$Geant4PATH/data/G4SAIDDATA2.0
G4REALSURFACEDATA=$Geant4PATH/data/RealSurface2.2
G4ABLADATA=$Geant4PATH/data/G4ABLA3.1
G4LEVELGAMMADATA=$Geant4PATH/data/PhotonEvaporation5.7
G4RADIOACTIVEDATA=$Geant4PATH/data/RadioactiveDecay5.6

# Python 
PYTHONPATH=$dir_raser/raser:/usr/local/share/root_install/lib:$Geant4PATH/install/lib64/python3.6/site-packages:/usr/local/share/acts_build/python
LD_LIBRARY_PATH=$Geant4PATH/install/lib64:/usr/local/share/root_install/lib:/.singularity.d/libs

#pyMTL3 Verilator
PYMTL_VERILATOR_INCLUDE_DIR="/usr/local/share/verilator/include"
EOF

export PATH=/cvmfs/common.ihep.ac.cn/software/hepjob/bin:$PATH
export IMGFILE=/afs/ihep.ac.cn/users/s/shixin/img/raser-2.2.sif
export BINDPATH=/afs,/besfs5,/cefs,/cvmfs,/publicfs,/scratchfs,/workfs2

alias raser="python3 raser"
alias raser-test="apptainer exec --env-file $cfg_env -B $BINDPATH $IMGFILE python3 -m unittest discover -v -s tests"
alias raser-shell="apptainer shell --env-file $cfg_env -B $BINDPATH $IMGFILE"
alias pytest="apptainer exec --env-file $cfg_env -B $BINDPATH $IMGFILE pytest"
alias raser-install="apptainer exec --env-file $cfg_env -B $BINDPATH $IMGFILE pip install -e ."  

