#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import devsim
from . import physics_2d
from . import diode_common
from .build_device import Detector
import math
import sys
from array import array
import ROOT
import numpy as np
import pickle
import json
import os



areafactor=1.6e4
if len(sys.argv)>1:
    simname=sys.argv[1]
else:
    simname='NJUPIN'


device=simname
region=simname
with open('./output/parainprogram/config_loopiv.json', 'r') as f:
    params = json.load(f)
bias_v=float(params["bias_v"])
voltage= float(params["voltage"])

devsim.set_parameter(name = "extended_solver", value=True)
devsim.set_parameter(name = "extended_model", value=True)
devsim.set_parameter(name = "extended_equation", value=True)

MyDetector = Detector(simname)

#build_2d_device.InitialSolution(device, region, circuit_contacts=False)
diode_common.InitialSolution(device, region, circuit_contacts="bot")

# Initial DC solution
devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=1500)


#build_2d_device.DriftDiffusionInitialSolution(device, region, circuit_contacts=False)
diode_common.DriftDiffusionInitialSolution(device, region, circuit_contacts=["bot"])
devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=1500)



data = []
intensities=[]
positions=[]
def loop(bias_v,voltage):   
    while bias_v < voltage:
        devsim.set_parameter(device=device, name=physics_2d.GetContactBiasName("top"), value=0-bias_v)
        devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-6, maximum_iterations=1500)
        physics_2d.PrintCurrents(device, "top")
        physics_2d.PrintCurrents(device, "bot")
        reverse_top_electron_current= devsim.get_contact_current(device=device, contact="top", equation="ElectronContinuityEquation")
        reverse_top_hole_current    = devsim.get_contact_current(device=device, contact="top", equation="HoleContinuityEquation")
        #reverse_bot_electron_current= devsim.get_contact_current(device=device, contact="bot", equation="ElectronContinuityEquation")
        #reverse_bot_hole_current    = devsim.get_contact_current(device=device, contact="bot", equation="HoleContinuityEquation")
        reverse_top_total_current   = reverse_top_electron_current + reverse_top_hole_current   
        #reverse_bot_total_current   = reverse_bot_electron_current + reverse_bot_hole_current
        reverse_total_current =   reverse_top_total_current 
        # TODO: 获取电路信息

        if bias_v % 100 == 0:
            devsim.edge_average_model(device=device, region=region, node_model="x", edge_model="xmid")
            x_mid = devsim.get_edge_model_values(device=device, region=region, name="xmid") # get x-node values 
            E = devsim.get_edge_model_values(device=device, region=region, name="ElectricField")
            x = devsim.get_node_model_values(device=device, region=region, name="x")

            positions.append(x)
            intensities.append(E)
            efield = zip(positions, intensities)
            path = "./output/field/sicar1d/efield"+str(bias_v)+"200.pkl"
            metadata=[]
            metadata['voltage'] = bias_v
            metadata['dimension'] = 1
            data = {}
            data['efield'] = zip(*efield)
            data['metadata'] = metadata
            with open(path,'wb') as file:
                pickle.dump(data, file)
            file.close        
       

        data.append((bias_v,  abs(reverse_total_current) ))
        bias_v += 1



loop(bias_v,voltage)