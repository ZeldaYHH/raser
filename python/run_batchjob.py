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
import time
import json
import subprocess

class Input_parameters:
    def __init__(self,args):
        self.name = args[0].split("=")[-1] # model name
        self.events_each_run = int(args[1].split("=")[-1]) # events/run
        self.events_total = int(args[2].split("=")[-1]) # events/total
        self.instance_in = int(args[3].split("=")[-1]) #singularity instance start number
        self.output_path = args[4].split("=")[-1]      #output name
        self.run_mode = args[5].split("=")[-1]       # 1 run example, 2 run the batch
        self.para_name = args[6].split("=")[-1]    # the change of parameter name in batch
        self.para_number = int(args[7].split("=")[-1])    # the change of parameter numbers in batch
    @property
    def instance_number(self): #singularity instance number
        return int(self.events_total/self.events_each_run)

def main():
    args = sys.argv[1:]
    input=Input_parameters(args)
    job_name=write_job(input,run_code="./python/gsignal.py det_name="+input.name)
    if input.run_mode == "True":
        run_job(job_name)

def write_job(input,run_code):
    now = time.strftime("%Y_%m%d_%H%M")
    path = "job/"+now+"/"
    create_path(path)
    create_path(input.output_path)
    modify_json(input,path)
    k = 1
    for j in range (1,input.para_number+1):
        mm = 1
        for i in range(input.instance_number):
            e_number=input.events_each_run*(i+1)
            para_code = "total_e=%s instan=%s output=%s"%(input.events_each_run, 
                                                        input.instance_in+i, 
                                                        os.getcwd()+"/"+input.output_path)
            f1 = open(path+str(k)+".sh","w")
            parfile="parfile="+os.getcwd()+"/"+path+"setting%s.json"%(j)
            f1.write("#!/bin/bash \n")
            f1.write(" export GEANT4_INSTALL=/cvmfs/common.ihep.ac.cn/software/geant4/10.7.p02/install \n")
            f1.write(" source $GEANT4_INSTALL/bin/geant4.sh \n")
            f1.write(" export PYTHONPATH=$PYTHONPATH:$GEANT4_INSTALL/lib64/python3.6/site-packages  \n")
            f1.write(run_code+" "+parfile+" "+para_code+" "+"scan=True")
            f1.close()
            runcmd("chmod u+x "+path+"*")
            if input.run_mode == "False" and mm == 1:
                run_command = "/cvmfs/container.ihep.ac.cn/bin/hep_container exec HepcMyImage -g higgs " + path+str(k)+".sh" + " &"
                print(run_command)
                runcmd(run_command)
            k = k+1
            mm += 1
    time.sleep(1)
    return path

def run_job(job_name):
    for root,dirs,files in os.walk(job_name):
        for file in files:
            if ".sh" in file:
                path = os.path.join(job_name, file)
                job_command = "hep_sub "+ path +" -image track-1.2.sif -wn bws0765.ihep.ac.cn"
                print(job_command)
                runcmd(job_command)

def create_path(path):
    """ If the path does not exit, create the path"""
    if not os.access(path, os.F_OK):
        os.makedirs(path, exist_ok=True) 

def runcmd(command):
    ret = subprocess.run([command],shell=True)

def modify_json(input,name):
    path_file = "setting.json"
    with open(path_file) as f:
        paras = json.load(f)
        for para in paras:
            if input.name == para['name'] and para['det_model'] in "plugin3D":
                for i in range(input.para_number):
                    if input.para_name == "NO":
                        pass
                    else:
                        if input.para_name == "scan_voltage":
                            para.update({'voltage':str(-500+i*50)})
                        elif input.para_name == "scan_doping":
                            para.update({'doping':str(10.0+i*10)})
                        elif input.para_name == "scan_temp":
                            para.update({'temp':str(300+i*30)})
                        elif input.para_name == "scan_thick":
                            para.update({'lz':str(150.0+i*30)})
                        elif input.para_name == "scan_gap":
                            para.update({'e_gap':str(140.0+i*20)})
                        else:
                            print("Select right para_name:scan_volatge,scan_doping,scan_gap,scan_temp,scan_thick,NO")     
                    outfile = name+"setting%s.json"%(i+1)
                    json_str = json.dumps([para], indent=4)
                    # keep the same with json in main program, using a list of dic to set different paras
                    with open(outfile,"w") as f:
                        f.write(json_str)
                        f.close()

            elif input.name == para['name'] and para['det_model'] in "planar3D":
                for i in range(input.para_number):
                    if input.para_name == "NO":
                        pass
                    else:
                        if input.para_name == "scan_voltage":
                            para.update({'voltage':str(-200-i*30)})
                        elif input.para_name == "scan_doping":
                            para.update({'doping':str(10.0+i*10)})
                        elif input.para_name == "scan_temp":
                            para.update({'temp':str(300-i*10)})
                        elif input.para_name == "scan_thick":
                            para.update({'lz':str(100.0+i*50)})
                        else:
                            print("Select right para_name:scan_volatge,scan_doping,scan_temp,scan_thick,NO")                 
                    outfile = name+"setting%s.json"%(i+1)
                    json_str = json.dumps([para], indent=4)
                    with open(outfile,"w") as f:
                        f.write(json_str)
                        f.close()

            elif input.name == para['name'] and para['det_model'] in "lgad3Dscan":
                for i in range(input.para_number):
                    if input.para_name == "NO":
                        pass
                    else:
                        if input.para_name == "scan_voltage":
                            para.update({'voltage':str(-200-i*30)})
                        elif input.para_name == "scan_doping":#triangle wall
                            para.update({'doping1':str(250+i*1e5)})
                        elif input.para_name == "scan_temp":
                            para.update({'temp':str(300-i*10)})
                        elif input.para_name == "scan_thick":
                            para.update({'lz':str(100.0+i*50)})
                        else:
                            print("Select right para_name:scan_volatge,scan_doping,scan_temp,scan_thick,NO")                 
                    outfile = name+"setting%s.json"%(i+1)
                    json_str = json.dumps([para], indent=4)
                    with open(outfile,"w") as f:
                        f.write(json_str)
                        f.close()        
            else:
                pass

if __name__ == '__main__':
    main()