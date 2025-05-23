RASER
======

**RA**diation **SE**miconducto**R** 

Welcome to Fork and contribute! 

link: <https://raser.team/docs/raser/> 

Prerequisites
======

An environment with 

    DevSim Geant4 ROOT NGSpice and ACTS

or 
    
    Apptainer, our .sif and cvmfs file system

If you install the softwares above, you need to change the ```dir_geant4_data``` and the ```GEANT4_INSTALL``` in cfg/setup.sh by your Geant4 data path and install path.

For external users, .sif should be in `img/`.

For developer using vscode, we recommand you follow this instruction to let Pylance able to read Python packages inside the .sif: https://stackoverflow.com/questions/63604427/launching-a-singularity-container-remotely-using-visual-studio-code

Notice that if you need to mount a symbol link to the .sif while entering the .sif by vscode, you need to mount their real paths too.

.sif download link: https://ihepbox.ihep.ac.cn/ihepbox/index.php/s/rDAgsChX9inhX8u

cvmfs setting tutorial: https://cvmfs.readthedocs.io/en/stable/cpt-quickstart.html

    wget https://ecsft.cern.ch/dist/cvmfs/cvmfs-release/cvmfs-release-latest_all.deb
    sudo apt install -y ./cvmfs-release-latest_all.deb
    sudo apt install -y cvmfs (this may take some time)
    sudo cvmfs_config setup
    sudo vi /etc/cvmfs/default.local
        `CVMFS_REPOSITORIES=cvmfs-config.cern.ch,sft.cern.ch,geant4.cern.ch`
        `CVMFS_CLIENT_PROFILE=single`
        `CVMFS_HTTP_PROXY=DIRECT`
    sudo cvmfs_config probe

For software downloading you could refer to `cfg/raser.def`. 

`/cvmfs/` could be utilized as ROOT and Geant4 source.

Note: if your system no longer supports g++-9, follow the steps below but select newer versions of g++, ROOT, and Geant4.

The download steps below are preliminary

    sudo vi /etc/apt/sources.list
        write:
            deb http://deb.debian.org/debian/ buster main
            deb-src http://deb.debian.org/debian/ buster main

    sudo apt update

    sudo apt install g++-9
        if cannot:
            sudo vi /etc/apt/sources.list
                write:
                    deb http://deb.debian.org/debian/ bullseye main

            sudo apt update

            sudo apt install g++-9

    sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-9 90

    sudo vi /etc/bash.bashrc
        write:
            source /cvmfs/geant4.cern.ch/geant4/10.7.p02/x86_64-centos7-gcc9-optdeb/CMake-setup.sh
            source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.26.06/x86_64-ubuntu20-gcc94-opt/bin/thisroot.sh

    # Libs for ROOT an Geant4
    sudo apt -y install llvm libxpm-dev libxft-dev libxext-dev libgif-dev libtbb-dev libssl-dev libtiff5 

    wget http://mirrors.kernel.org/ubuntu/pool/main/libj/libjpeg-turbo/libjpeg-turbo8_2.1.2-0ubuntu1_amd64.deb  

    sudo apt install ./libjpeg-turbo8_2.1.2-0ubuntu1_amd64.deb

    # Python binding for ROOT and Geant4
    pip install cppyy matplotlib scipy pandas geant4-pybind

Note: Python 3.9 is recommended. If your Python is of a higher version, you need to checkout a ROOT version compatible to the Python.

Before Run
======

While running raser you need in the directory of raser.

if you use .sif container:

    source cfg/setup.sh # before run
    raser <option <option tag>>

alternative:

    source cfg/setup.sh # before run
    raser-shell
    python3 raser <option <option tag>>

else if you have installed the prerequisites:

    python3 raser <option <option tag>>

update:

    git pull

For internal users on lxlogin, use cfg/setup_lxlogin.sh instead.

Output
======

The output of raser will store inside <directory of raser>/output/ .

Run Options
======

checkout __main__.py for detail.

Tutorial
======

For signal simulation of HPK devices:

    raser field [-cv] <device_name in `setting/detector`>
    raser field -wf <device_name>
    raser signal <device_name>
    raser tct signal <device_name> <laser_name in `setting/laser`>

For signal simulation of CMOS strip detector:

    mesh CMOS_strip
    raser field -umf [-cv] CMOS_strip
    raser field -wf CMOS_strip
    raser signal CMOS_strip
    raser tct signal CMOS_strip <laser_name in `setting/laser`>

For time resolution of NJU SiC PiN in https://doi.org/10.3389/fphy.2022.718071 :

    raser field [-cv] NJU-PIN
    raser field -wf NJU-PIN
    raser signal -s 20 NJU-PIN
    raser resolution NJU-PIN
