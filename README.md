RASER
======

**RA**diation **SE**miconducto**R** 

Welcome to Fork and contribute! 

link: <https://raser.team/docs/raser/> 

Prerequisites
======

An environment with 

    ROOT
    Geant4
        you need to change the ```dir_geant4_data``` and the ```GEANT4_INSTALL``` in cfg/setup.sh by your Geant4 data path and install path.
    A virtual environment with all other prerequisites, mainly all kinds of python packages
        we recommand use apptainer and our .sif: https://ihepbox.ihep.ac.cn/ihepbox/index.php/s/rDAgsChX9inhX8u
        or you could refer to `cfg/raser.def`. 

For external users, .sif should be in `img/`.

For developer using vscode, we recommand you follow this instruction to let Pylance able to read Python packages inside the .sif: https://stackoverflow.com/questions/63604427/launching-a-singularity-container-remotely-using-visual-studio-code

Notice that if you need to mount a symbol link to the .sif while entering the .sif by vscode, you need to mount their real paths too.

Note: Python 3.9 is recommended. If your Python is of a higher version, you need to checkout a ROOT version compatible to the Python.

Before Run
======

While running raser you need in the directory of raser.

run steps:

    source cfg/setup.sh # before run
    raser-shell (or entering your own's python virtual environment)
    python3 src/raser <option <option tag>>

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

For time resolution of NJU SiC PiN in https://doi.org/10.3389/fphy.2022.718071 :

    raser field [-cv] NJU-PIN
    raser field -wf NJU-PIN
    raser signal -s 20 NJU-PIN
    raser resolution NJU-PIN
