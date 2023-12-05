#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import devsim
from . import physics_drift_diffusion
from .build_device import Detector
import math
import sys
from array import array
import ROOT
import numpy as np
import pickle
import json
import os

simname=sys.argv[1]
device=simname
region=simname
#This requires a circuit element to integrated current
devsim.circuit_element(name="V1", n1=physics_drift_diffusion.GetContactBiasName("top"), n2=0, value=0.0, acreal=1.0, acimag=0.0)
areafactor=2e2

with open('./output/parainprogram/config_loop_elefield.json', 'r') as f:
    params = json.load(f)
bias_v=float(params["bias_v"])
voltage= float(params["voltage"])


devsim.set_parameter(name = "extended_solver", value=True)
devsim.set_parameter(name = "extended_model", value=True)
devsim.set_parameter(name = "extended_equation", value=True)

MyDetector = Detector(simname, 3)

devsim.open_db(filename="./output/field/SICARDB.db", permission="readonly")

initial.InitialSolution(device, region, circuit_contacts="top")
#diode_common.InitialSolution(device, region, circuit_contacts="bot")

# Initial DC solution
devsim.solve(type="dc", absolute_error=1e30, relative_error=1e-3, maximum_iterations=1500)


initial.DriftDiffusionInitialSolution(device, region, circuit_contacts=["top"])
#diode_common.DriftDiffusionInitialSolution(device, region, circuit_contacts=["bot"])
devsim.delete_node_model(device=device, region=region, name="IntrinsicElectrons")
devsim.delete_node_model(device=device, region=region, name="IntrinsicHoles")

devsim.solve(type="dc", absolute_error=1e30, relative_error=1e-3, maximum_iterations=1500)
folder_path="./output/{0}".format(simname)
if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def loop(bias_v,voltage):
    
    while bias_v < voltage:
        
        devsim.circuit_alter(name="V1", value=0-bias_v)
        devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-3, maximum_iterations=1500)

        # TODO: 获取电路信息

        devsim.solve(type="ac", frequency=1e6)
        
        
        if bias_v % 50== 0:
            if simname == "3d_ringcontact":
                x=devsim.get_node_model_values(device=device,region=region,name="x")
                y=devsim.get_node_model_values(device=device,region=region,name="y")
                z=devsim.get_node_model_values(device=device,region=region,name="z")
                potential=devsim.get_node_model_values(device=device,region=region,name="Potential")
                data = [x, y,z, potential]
                names = ["x", "y", "z","potential"]

                for i in range(len(data)):
                    with open('./output/{}/{}_{}.pkl'.format(simname, names[i],bias_v), 'wb') as file:
                        pickle.dump(data[i], file)
                
            else:
                x=devsim.get_node_model_values(device=device,region=region,name="x")
                y=devsim.get_node_model_values(device=device,region=region,name="y")
                potential=devsim.get_node_model_values(device=device,region=region,name="Potential")
                data = [x, y,potential]
                names = ["x", "y","potential"]

                for i in range(len(data)):
                    with open('./output/{}/{}_{}.pkl'.format(simname, names[i],bias_v), 'wb') as file:
                        pickle.dump(data[i], file)

        bias_v += 1      



loop(bias_v,voltage)
