#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import devsim 
from .build_device import Detector
from . import model_create
from . import physics_drift_diffusion
from . import initial

import sys
import json
import pickle
import csv
import os
from util.output import output
from .devsim_draw import *

import numpy as np

paras = {
    "absolute_error" : 1e10, 
    "relative_error" : 1e-5, 
    "maximum_iterations" : 1000,

    "milestone_mode" : True,
    "milestone_step" : 100,

    "voltage_step" : 1,
    "acreal" : 1.0, 
    "acimag" : 0.0,
    "frequency" : 1.0
}

def main(simname):
    with open('setting/devsim_general.json') as file:
        paras.update(json.load(file))

    devsim.open_db(filename="./output/field/SICARDB.db", permission="readonly")
    device = simname
    region = simname
    MyDetector = Detector(device)

    T = MyDetector.device_dict['temperature']
    k = 1.3806503e-23  # J/K
    q = 1.60217646e-19 # coul
    devsim.add_db_entry(material="global",   parameter="T",    value=T,     unit="K",   description="T")
    devsim.add_db_entry(material="global",   parameter="k_T",    value=k*T,       unit="J",        description="k*T")
    devsim.add_db_entry(material="global",   parameter="Volt_thermal",    value=k*T/q,     unit="J/coul",   description="k*T/q")

    if "parameter_alter" in MyDetector.device_dict:
        for material in MyDetector.device_dict["parameter_alter"]:
            for parameter in material:
                devsim.devsim.add_db_entry(material=material,
                                           parameter=parameter['name'],
                                           value=parameter['value'],
                                           unit=parameter['unit'],
                                           description=parameter['name'])

    electrode = MyDetector.device_dict['bias']['electrode']

    devsim.set_parameter(name = "extended_solver", value=True)
    devsim.set_parameter(name = "extended_model", value=True)
    devsim.set_parameter(name = "extended_equation", value=True)
    devsim.circuit_element(name="V1", n1=physics_drift_diffusion.GetContactBiasName(electrode), n2=0,
                           value=0.0, acreal=paras['acreal'], acimag=paras['acimag'])
    
    initial.InitialSolution(device, region, circuit_contacts=electrode)
    devsim.solve(type="dc", absolute_error=paras['absolute_error'], relative_error=paras['relative_error'], maximum_iterations=paras['maximum_iterations'])
    initial.DriftDiffusionInitialSolution(device, region, circuit_contacts=electrode,
                                          irradiation_label=MyDetector.device_dict['irradiation']['irradiation_label'],
                                          irradiation_flux=MyDetector.device_dict['irradiation']['irradiation_flux'])
    devsim.solve(type="dc", absolute_error=paras['absolute_error'], relative_error=paras['relative_error'], maximum_iterations=paras['maximum_iterations'])
    devsim.delete_node_model(device=device, region=region, name="IntrinsicElectrons")
    devsim.delete_node_model(device=device, region=region, name="IntrinsicHoles")
    devsim.delete_node_model(device=device, region=region, name="IntrinsicElectrons:Potential")
    devsim.delete_node_model(device=device, region=region, name="IntrinsicHoles:Potential")

    voltage = []
    current = []
    capacitance = []

    voltage_milestone = []
    positions_mid = []
    intensities = []

    positions = []
    electrons = []
    holes = []

    path = output(__file__, device)

    iv_path = os.path.join(path,"iv.csv")
    f_iv = open(iv_path, "w")
    header_iv = ["Voltage","Current"]
    writer_iv = csv.writer(f_iv)
    writer_iv.writerow(header_iv)

    cv_path = os.path.join(path,"cv.csv")
    f_cv = open(cv_path, "w")
    header_cv = ["Voltage","Capacitance"]
    writer_cv = csv.writer(f_cv)
    writer_cv.writerow(header_cv)

    v_max = MyDetector.device_dict['bias']['voltage']
    area_factor = MyDetector.device_dict['area_factor']
    frequency = paras['frequency']

    v = 0.0
    if v_max > 0:
        voltage_step = paras['voltage_step']
    else: 
        voltage_step = -1 * paras['voltage_step']

    while abs(v) <= abs(v_max):
        voltage.append(v)
        devsim.set_parameter(device=device, name=physics_drift_diffusion.GetContactBiasName(electrode), value=v)
        devsim.solve(type="dc", absolute_error=paras['absolute_error'], relative_error=paras['relative_error'], maximum_iterations=paras['maximum_iterations'])
        physics_drift_diffusion.PrintCurrents(device, electrode)
        electron_current= devsim.get_contact_current(device=device, contact=electrode, equation="ElectronContinuityEquation")
        hole_current    = devsim.get_contact_current(device=device, contact=electrode, equation="HoleContinuityEquation")
        total_current   = electron_current + hole_current

        current.append(abs(total_current/area_factor))
        writer_iv.writerow([v,abs(total_current/area_factor)])

        devsim.circuit_alter(name="V1", value=v)
        devsim.solve(type="dc", absolute_error=paras['absolute_error'], relative_error=paras['relative_error'], maximum_iterations=paras['maximum_iterations'])
        devsim.solve(type="ac", frequency=frequency)
        cap=devsim.get_circuit_node_value(node="V1.I", solution="ssac_imag")/ (-2*np.pi*frequency)

        capacitance.append(abs(cap/area_factor))
        writer_cv.writerow([v,abs(cap/area_factor)])
        
        if(paras['milestone_mode']==True and v%paras['milestone_step']==0.0):
            if MyDetector.dimension == 1:
                milestone_save_1D(device, region, v, path)
            elif MyDetector.dimension == 2:
                milestone_save_2D(device, region, v, path)
            elif MyDetector.dimension == 3:
                milestone_save_3D(device, region, v, path)
            else:
                raise ValueError(MyDetector.dimension)
            
            devsim.edge_average_model(device=device, region=region, node_model="x", edge_model="xmid")
            x_mid = devsim.get_edge_model_values(device=device, region=region, name="xmid") # get x-node values 
            E = devsim.get_edge_model_values(device=device, region=region, name="ElectricField") # get y-node values
            V = v

            x = devsim.get_node_model_values(device=device, region=region, name="x") # get x-node values 
            n = devsim.get_node_model_values(device=device, region=region, name="Electrons")
            p = devsim.get_node_model_values(device=device, region=region, name="Holes")

            positions_mid.append(x_mid)
            intensities.append(E)
            voltage_milestone.append(V)

            positions.append(x)
            electrons.append(n)
            holes.append(p)

        v += voltage_step

    draw_iv(device, voltage, current)
    draw_cv(device, voltage, capacitance)
    draw_field(device, positions_mid, intensities, voltage_milestone)
    save_field(device, positions_mid, intensities, voltage_milestone)
    draw_electrons(device, positions, electrons, voltage_milestone)
    draw_holes(device, positions, holes, voltage_milestone)

def milestone_save_1D(device, region, v, path):
    x = np.array(devsim.get_node_model_values(device=device, region=region, name="x"))
    potential = np.array(devsim.get_node_model_values(device=device, region=region, name="Potential")) # get the potential dat
    NetDoping= np.array(devsim.get_node_model_values(device=device, region=region, name="NetDoping"))
    PotentialNodeCharge = np.array(devsim.get_node_model_values(device=device, region=region, name="PotentialNodeCharge"))
    Electrons = np.array(devsim.get_node_model_values(device=device, region=region, name="Electrons"))
    Holes = np.array(devsim.get_node_model_values(device=device, region=region, name="Holes"))
    devsim.edge_average_model(device=device, region=region, node_model="x", edge_model="xmid")
    x_mid = devsim.get_edge_model_values(device=device, region=region, name="xmid") # get x-node values 
    ElectricField = devsim.get_edge_model_values(device=device, region=region, name="ElectricField") # get y-node values
    TrappingRate_n = np.array(devsim.get_node_model_values(device=device, region=region, name="TrappingRate_n"))
    TrappingRate_p = np.array(devsim.get_node_model_values(device=device, region=region, name="TrappingRate_p"))

    draw1D(x,potential,"Potential","Depth[cm]","Potential[V]", v, path)
    draw1D(x_mid,ElectricField,"ElectricField","Depth[cm]","ElectricField[V/cm]",v, path)
    draw1D(x,TrappingRate_n,"TrappingRate_n","Depth[cm]","TrappingRate_n[s]",v, path)
    draw1D(x,TrappingRate_p,"TrappingRate_p","Depth[cm]","TrappingRate_p[s]",v, path)

    dd = os.path.join(path, str(v)+'V.dd')
    devsim.write_devices(file=dd, type="tecplot")

def milestone_save_2D(device, region, v, path):
    x = np.array(devsim.get_node_model_values(device=device, region=region, name="x")) # get x-node values
    y = np.array(devsim.get_node_model_values(device=device, region=region, name="y")) # get y-node values
    Potential = np.array(devsim.get_node_model_values(device=device, region=region, name="Potential")) # get the potential data
    TrappingRate_n = np.array(devsim.get_node_model_values(device=device, region=region, name="TrappingRate_n"))
    TrappingRate_p = np.array(devsim.get_node_model_values(device=device, region=region, name="TrappingRate_p"))

    devsim.element_from_edge_model(edge_model="ElectricField",   device=device, region=region)
    devsim.edge_average_model(device=device, region=region, node_model="x", edge_model="xmid")
    devsim.edge_average_model(device=device, region=region, node_model="y", edge_model="ymid")
    ElectricField=np.array(devsim.get_edge_model_values(device=device, region=region, name="ElectricField"))
    x_mid = np.array(devsim.get_edge_model_values(device=device, region=region, name="xmid")) 
    y_mid = np.array(devsim.get_edge_model_values(device=device, region=region, name="ymid")) 

    draw2D(x,y,Potential,"Potential",v, path)
    draw2D(x_mid,y_mid,ElectricField,"ElectricField",v, path)
    draw2D(x,y,TrappingRate_n,"TrappingRate_n",v, path)
    draw2D(x,y,TrappingRate_p,"TrappingRate_p",v, path)

    dd = os.path.join(path, str(v)+'V.dd')
    devsim.write_devices(file=dd, type="tecplot")

    metadata = {}
    metadata['voltage'] = v
    metadata['dimension'] = 2

    with open(os.path.join(path, "ElectricField_{}V.pkl".format(v)),'wb') as file:
        data = {}
        ElectricFieldFunction = zip(ElectricField, x_mid, y_mid)
        data['ElectricField'] = zip(*ElectricFieldFunction)
        data['metadata'] = metadata
        pickle.dump(data, file)
    with open(os.path.join(path, "Potential_{}V.pkl".format(v)),'wb') as file:
        data = {}
        PotentialFunction = zip(Potential, x, y)
        data['Potential'] = zip(*PotentialFunction)
        data['metadata'] = metadata
        pickle.dump(data, file)
    with open(os.path.join(path, "TrappingRate_p_{}V.pkl".format(v)),'wb') as file:
        data = {}
        TrappingRate_pFunction = zip(TrappingRate_p, x, y)
        data['TrappingRate_p'] = zip(*TrappingRate_pFunction)
        data['metadata'] = metadata
        pickle.dump(data, file)
    with open(os.path.join(path, "TrappingRate_n_{}V.pkl".format(v)),'wb') as file:
        data = {}
        TrappingRate_nFunction = zip(TrappingRate_n, x, y)
        data['TrappingRate_n'] = zip(*TrappingRate_nFunction)
        data['metadata'] = metadata
        pickle.dump(data, file)

def milestone_save_3D(device, region, v, path):
    x=devsim.get_node_model_values(device=device,region=region,name="x")
    y=devsim.get_node_model_values(device=device,region=region,name="y")
    z=devsim.get_node_model_values(device=device,region=region,name="z")
    Potential=devsim.get_node_model_values(device=device,region=region,name="Potential")

    metadata = {}
    metadata['voltage'] = v
    metadata['dimension'] = 3

    with open(os.path.join(path, "Potential_{}V.pkl".format(v)),'wb') as file:
        data = {}
        PotentialFunction = zip(Potential, x, y, z)
        data['Potential'] = zip(*PotentialFunction)
        data['metadata'] = metadata
        pickle.dump(data, file)

if __name__ == "__main__":
    main(simname = sys.argv[1])
