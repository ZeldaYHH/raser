#!/usr/bin/env python3
# Main driver to run RASER    
# Author FU Chenxi <1256257282@qq.com>  
# Created [2023-08-29 Tue 11:48] 

# Call mirror:
# apptainer shell --env-file cfg/env -B /cefs,/afs,/besfs5,/cvmfs,/scratchfs,/workfs2 /afs/ihep.ac.cn/users/s/shixin/raser/raser-4.0.sif

import argparse
import json
import importlib
import subprocess

parser = argparse.ArgumentParser()

# define temperary custom settings
parser.add_argument("option",nargs="+")
parser.add_argument('-a',"--absorber")
parser.add_argument('-d',"--detector")
parser.add_argument('-e',"--electronics")
parser.add_argument('-l',"--laser")
args = parser.parse_args()

args_dict = vars(args)

with open('setting/setting.json') as f:
    # define permanent custom settings in setting.json
    json_settings = json.load(f)
    for key in json_settings:
        if args_dict[key] == None:
            args_dict.update({key:json_settings[key]})

module_name = args_dict['option'][0]
args_dict['option']=args_dict['option'][1:]
try:
    module = importlib.import_module(module_name)
    module.main(args_dict)
except ModuleNotFoundError:
    try:
        subprocess.run('apptainer exec --env-file cfg/env -B /cefs,/afs,/besfs5,/cvmfs,/scratchfs,/workfs2 \
                    /afs/ihep.ac.cn/users/s/shixin/raser/raser-2.0.sif \
                    \"./raser/'+module_name+'.py\"', shell=True)
    except FileNotFoundError:
        print("No subcommand found")