#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
Description:  Run batch model     
@Date       : 2021/09/02 17:13:04
@Author     : tanyuhang
@version    : 1.0
'''

import os
import sys
import subprocess

def main():
    destination_subfolder = sys.argv[1]
    if destination_subfolder == "devsim":
        group = "physics"
    else:
        group = "atlas"
    command = sys.argv[2]
    create_path("./output/{}/jobs".format(destination_subfolder))
    command_name = command.replace(" ","_").replace("/","_")
    jobfile_name = "./output/{}/jobs/".format(destination_subfolder)+command_name+".job"
    gen_job(jobfile_name,run_code="raser \"./python/"+command+"\"")
    # run code: raser "./python/xxx.py parameters"
    submit_job(jobfile_name,destination_subfolder,group)

def gen_job(jobfile_name,run_code):
    jobfile = open(jobfile_name,"w")
    jobfile.write("export PATH=$PATH:/afs/.ihep.ac.cn/soft/common/sysgroup/hepjob-4.0-dev/bin/ \n")
    jobfile.write("source ./run raser \n")
    jobfile.write(run_code)
    jobfile.close()
    print("Generate job file: ", jobfile_name)

def submit_job(jobfile_name,destination_subfolder,group):
    print("Submit job file: ", jobfile_name)
    runcmd("chmod u+x {}".format(jobfile_name))
    runcmd("hep_sub -o ./output/{}/jobs -e ./output/{}/jobs {} -g {}"\
        .format(destination_subfolder,destination_subfolder,jobfile_name,group))

def create_path(path):
    """ If the path does not exit, create the path"""
    if not os.access(path, os.F_OK):
        os.makedirs(path, exist_ok=True) 

def runcmd(command):
    ret = subprocess.run([command],shell=True)

if __name__ == "__main__":
    main()