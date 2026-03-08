RASER
======

**RA**diation **SE**miconducto**R** 

Welcome to Fork and contribute! 

link: <https://raser.team/docs/raser/> 

Citation: https://doi.org/10.5281/zenodo.18905684

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18905684.svg)](https://doi.org/10.5281/zenodo.18905684)

<a href="https://doi.org/10.5281/zenodo.18905684"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.18905684.svg" alt="DOI"></a>


Prerequisites
======

An environment with 

    ROOT
    Geant4
    python packages in `cfg/raser.def`
        
you need to change the ```dir_geant4_data``` and the ```GEANT4_INSTALL``` in cfg/setup.sh by your Geant4 data path and install path.
we recommand use apptainer and our .sif: https://ihepbox.ihep.ac.cn/ihepbox/index.php/s/Gp2SQIXLOUcKh4C

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

For signal simulation of 
    HPK-Si-PiN and HPK-Si-LGAD in 10.1016/j.nima.2024.169479 (under reorganization):

    raser field [-cv] <device_name in `setting/detector`>
    raser field -wf <device_name>
    raser signal <device_name>
    raser tct signal <device_name> <laser_name in `setting/laser`>

For time resolution of 
    NJU-PiN in 10.3389/fphy.2022.718071
    SICAR-1 in 10.1007/s41605-023-00431-y and 10.1109/TNS.2024.3471863:

    raser field [-cv] <device_name>
    raser field -wf <device_name>
    raser signal -s 20 <device_name>
    raser resolution <device_name>

For irradiation simulation of 
    ATLAS ITk-md8 and ITk-Si-strip in arXiv:2504.20463
    NJU-PiN in arXiv:2503.0901 6 (under reorganization):

    raser field [-cv] <device_name>
    raser field -wf <device_name>
    raser signal <device_name>
