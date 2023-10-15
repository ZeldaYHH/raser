#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import devsim
import physics_2d
import build_2d_device
import math
import sys
from array import array
import ROOT
import numpy as np
import pickle
import json
import os
import pixel_3d_mesh
simname=sys.argv[1]
device="MyDevice"
region="MyRegion"
#This requires a circuit element to integrated current
devsim.circuit_element(name="V1", n1=physics_2d.GetContactBiasName("top"), n2=0, value=0.0, acreal=1.0, acimag=0.0)
areafactor=2e2

with open('./output/parainprogram/config_loop_elefield.json', 'r') as f:
    params = json.load(f)
bias_v=float(params["bias_v"])
voltage= float(params["voltage"])


devsim.set_parameter(name = "extended_solver", value=True)
devsim.set_parameter(name = "extended_model", value=True)
devsim.set_parameter(name = "extended_equation", value=True)

pixel_3d_mesh.Create3DSICARFromGmesh(device,region)
pixel_3d_mesh.SetDoping(device,region)
build_2d_device.SetParameters(device=device, region=region)

    
physics_2d.InitialSolution(device, region, circuit_contacts="top")
#diode_common.InitialSolution(device, region, circuit_contacts="bot")

# Initial DC solution
devsim.solve(type="dc", absolute_error=1e30, relative_error=1e-3, maximum_iterations=1500)


physics_2d.SiDriftDiffusionInitialSolution(device, region, circuit_contacts=["top"])
#diode_common.DriftDiffusionInitialSolution(device, region, circuit_contacts=["bot"])
devsim.delete_node_model(device=device, region=region, name="IntrinsicElectrons")
devsim.delete_node_model(device=device, region=region, name="IntrinsicHoles")

devsim.solve(type="dc", absolute_error=1e30, relative_error=1e-3, maximum_iterations=1500)

def loop(bias_v,voltage):
    
    while bias_v < voltage:
        
        devsim.circuit_alter(name="V1", value=bias_v)
        devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-3, maximum_iterations=1500)

        # TODO: 获取电路信息

        devsim.solve(type="ac", frequency=1e6)
        
        bias_v += 1
        devsim.write_devices(file="./output/pixel/{0}_{1}_2d_dd".format(simname,bias_v), type="tecplot")
      


loop(bias_v,voltage)
