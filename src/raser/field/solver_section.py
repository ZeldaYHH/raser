#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import sys
import os
import subprocess
import time
import math

import devsim 
import numpy as np

from device.build_device import Detector
from .create_mesh import DevsimMesh
from .create_parameter import create_parameter, delete_init
from . import save_milestone
from . import loop_section
from . import physics_drift_diffusion
from util.output import output
from .devsim_draw import *

v_current = 0
V = []
c = []
Current = []
noise = []

paras = {
    "absolute_error_Initial" : 1e10, 
    "relative_error_Initial" : 1e-4, 
    "maximum_iterations_Initial" : 100,

    "absolute_error_VoltageSteps" : 1e20, 
    "relative_error_VoltageSteps" : 1e-4, 
    "maximum_iterations_VoltageSteps" : 100,

    "milestone_mode" : True,
    "milestone_step" : 100.0,

    "max_voltage_step" :8,
    "increase_factor": 2,
    "decrease_factor":0.1,

    "voltage_step" : 1,
    "acreal" : 1.0, 
    "acimag" : 0.0,
    "frequency" : 1000.0,
    "Cylindrical_coordinate": False,

    "ac-weightfield" : False,

    "Voltage-step-model" : False,
    "step":1,

}
os.environ["OMP_NUM_THREADS"] = "1"
def main (kwargs):
    simname = kwargs['label']
    is_cv = kwargs['cv']
    is_wf = kwargs["wf"]
    is_noise = kwargs["noise"]
    irradiation_flux = kwargs["irradiation_flux"]
    v_goal = kwargs["bias"]
    
    if is_wf:
        paras.update({"weightfield": True})
    else:
        paras.update({"weightfield": False})

    device = simname
    region = simname
    MyDetector = Detector(device)
    MyDevsimMesh = DevsimMesh(MyDetector, devsim_solve_paras=paras)
    MyDevsimMesh.mesh_define()

    if "frequency" in MyDetector.device_dict:
        paras.update({"frequency": MyDetector.device_dict['frequency']})
    if "area_factor" in MyDetector.device_dict:
        paras.update({"area_factor": MyDetector.device_dict['area_factor']})
    if "default_dimension" in MyDetector.device_dict:
        default_dimension =MyDetector.device_dict["default_dimension"]
    if "irradiation" in MyDetector.device_dict and not is_wf:
        irradiation = True
    else:
        irradiation = False

    create_parameter(MyDetector, device, region)

    if "irradiation" in MyDetector.device_dict:
        irradiation_model=MyDetector.device_dict['irradiation']['irradiation_model']
        if irradiation_flux == None:
            irradiation_flux=MyDetector.device_dict['irradiation']['irradiation_flux']
    else:
        irradiation_model=None
        irradiation_flux=0
    if 'avalanche_model' in MyDetector.device_dict:
        impact_model=MyDetector.device_dict['avalanche_model']
    else:
        impact_model=None
        
    circuit_contacts=[]
    if is_wf == True:
        if MyDetector.device_dict.get("mesh", {}).get("2D_mesh", {}).get("ac_contact"):
            print("=========RASER info===================\nACLGAD is simulating\n=============info====================")
            for read_out_electrode in MyDetector.device_dict["mesh"]["2D_mesh"]["ac_contact"]:
                circuit_contacts.append(read_out_electrode["name"])
            for i,c in enumerate(circuit_contacts):
                devsim.circuit_element(name="V{}".format(i+1), n1=physics_drift_diffusion.GetContactBiasName(c), n2=0,
                        value=0.0, acreal=paras['acreal'], acimag=paras['acimag'])
        else:
            print("===============RASER info===================\nNot AC detector\n===========info=============")
            for read_out_electrode in MyDetector.device_dict["read_out_contact"]:
                circuit_contacts.append(read_out_electrode)
            for i,c in enumerate(circuit_contacts):
                devsim.circuit_element(name="V{}".format(i+1), n1=physics_drift_diffusion.GetContactBiasName(c), n2=0,
                        value=0.0, acreal=paras['acreal'], acimag=paras['acimag'])
            
    else:
        circuit_contacts = MyDetector.device_dict['bias']['electrode']
        devsim.circuit_element(name="V1", n1=physics_drift_diffusion.GetContactBiasName(circuit_contacts), n2=0,
                           value=0.0, acreal=paras['acreal'], acimag=paras['acimag'])
    T1 = time.time()
    print("================RASER info============\nWelcome to RASER TCAD PART, mesh load successfully\n=============info===============")
    devsim.set_parameter(name = "debug_level", value="info")
    devsim.set_parameter(name = "extended_solver", value=True)
    devsim.set_parameter(name = "extended_model", value=True)
    devsim.set_parameter(name = "extended_equation", value=True)
    
    if is_cv ==True:
        solve_model = "cv"
    elif is_noise == True:
        solve_model = "noise"
    elif is_wf ==True:
        solve_model = "wf"
    else :
        solve_model = None

    path = output(__file__, device)
    if irradiation:
        path = output(__file__, device, str(irradiation_flux))

    loop=loop_section.loop_section(paras=paras,device=device,region=region,solve_model=solve_model,irradiation=irradiation)
   
    if is_wf == True:
        v_current=1
        print("=======RASER info========\nBegin simulation WeightingField\n======================")
        for contact in circuit_contacts:
            print(path)
            folder_path = os.path.join(path, "weightingfield")
            print(folder_path)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            
            paras["milestone_step"] == 1
            paras.update({"milestone_step":paras["milestone_step"]})

            loop.initial_solver(contact=contact,set_contact_type=None,impact_model=impact_model,irradiation_model=irradiation_model,irradiation_flux=irradiation_flux)
            loop.loop_solver(circuit_contact=contact,v_current=v_current,area_factor=paras["area_factor"])

            save_milestone.save_milestone(device=device, region=region, v=v_current, path=folder_path,dimension=default_dimension,contact=contact,is_wf=is_wf)
            devsim.write_devices(file=os.path.join(folder_path,"weightingfield.dat"), type="tecplot")
            
    elif is_wf == False:
        loop.initial_solver(contact=circuit_contacts, set_contact_type=None, impact_model=impact_model, irradiation_model=irradiation_model, irradiation_flux=irradiation_flux)
        v_current = 0
        if v_goal is None:
            v_goal = MyDetector.device_dict['bias']['voltage']
        voltage_step = 1.0 
        if v_goal > 0:
            voltage_step = paras['voltage_step']
        else:
            voltage_step = -1 * paras['voltage_step']
        max_voltage_step = paras['max_voltage_step']

        step_too_small = False
        while abs(v_current) <= abs(v_goal):
            v_last = v_current
            try:
                loop.loop_solver(circuit_contact=circuit_contacts, v_current=v_current, area_factor=paras["area_factor"])
                if abs(voltage_step) < max_voltage_step:
                    voltage_step = voltage_step *paras['increase_factor']
                else:
                    pass
                print("=========RASER info===========\nConvergence success, voltage = {}, increased voltage step = {}\n================".format(v_current, voltage_step))      
            except devsim.error as msg:
                if str(msg).find("Convergence failure") != 0:
                    raise
                voltage_step *= paras['decrease_factor'] 

                print("=========RASER info===========\nConvergence failure, voltage = {}, decreased voltage step = {}\n================".format(v_current, voltage_step))
  
                if abs(voltage_step) < 1e-7:
                    step_too_small = True
                    break  
                continue  
            if (paras['milestone_mode'] and abs(v_current % paras['milestone_step']) < 0.01 * paras['voltage_step']) or abs(abs(v_current) - abs(v_goal)) < 0.01 * paras['milestone_step']:
                save_milestone.save_milestone(device=device, region=region, v=v_current, path=path, dimension=default_dimension, contact=circuit_contacts, is_wf=is_wf)
                dd = os.path.join(path, str(v_current) + 'V.dd')
                devsim_device = os.path.join(path, str(v_current) + 'V.devsim')
                devsim.write_devices(file=dd, type="tecplot")
                devsim.write_devices(file=devsim_device, type="devsim")
            v_current = v_last + voltage_step 

            if abs(v_current) > abs(v_goal):
                v_current = v_goal
                loop.loop_solver(circuit_contact=circuit_contacts, v_current=v_current, area_factor=paras["area_factor"])
                break

        else:
            print("Loop completed successfully.")
        if step_too_small:
            raise RuntimeError("Step size too small (less than 1e-7). Exiting loop.")
        else:
            print("Loop completed successfully.")

    if is_wf != True:
    
        draw_iv(device, V=loop.get_voltage_values(), I=loop.get_current_values(),path=path)
        if is_cv == True:
            draw_cv(device, V=loop.get_voltage_values(), C=loop.get_cap_values(),path=path)
        if is_noise == True:
            draw_noise(device, V=loop.get_voltage_values(), noise=loop.get_noise_values(),path=path)
    T2 =time.time()
    print("=========RASER info===========\nSimulation finish ,total used time: {}s !^w^!\n================".format(T2-T1))