#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2013 DEVSIM LLC
#
# SPDX-License-Identifier: Apache-2.0

from devsim import *
from .si_simple_physics import *
from . import si_diode_common

import os
import ROOT
import numpy as np
import pickle



# dio1
#
# Make doping a step function
# print dat to text file for viewing in grace
# verify currents analytically
# in dio2 add recombination
#
def main():
    device="MyDevice"
    region="MyRegion"

    si_diode_common.Create2DMesh(device, region)

    si_diode_common.SetParameters(device=device, region=region)

    si_diode_common.SetNetDoping(device=device, region=region)

    si_diode_common.InitialSolution(device, region)

    # Initial DC solution
    solve(type="dc", absolute_error=1e1, relative_error=1e-7, maximum_iterations=1000)
    #solve(type="dc", absolute_error=1.0, relative_error=1e-12, maximum_iterations=30)

    si_diode_common.DriftDiffusionInitialSolution(device, region)
    ###
    ### Drift diffusion simulation at equilibrium
    ###
    solve(type="dc", absolute_error=1e10, relative_error=1e-4, maximum_iterations=1000)

    ####
    #### Ramp the bias to 0.5 Volts
    ####
    v = 0.0
    delete_node_model(device=device, region=region, name="IntrinsicElectrons")
    delete_node_model(device=device, region=region, name="IntrinsicHoles")
    while v < 700:
        set_parameter(device=device, name=GetContactBiasName("bot"), value=-v)
        solve(type="dc", absolute_error=1e10, relative_error=1e-3, maximum_iterations=1500)
        PrintCurrents(device, "bot")
        v += 1


    if not os.access('output/strip', os.F_OK):
        os.makedirs('output/strip', exist_ok=True)
    
    x = np.array(get_node_model_values(device=device, region=region, name="x")) # get x-node values
    y = np.array(get_node_model_values(device=device, region=region, name="y")) # get y-node values
    potential = np.array(get_node_model_values(device=device, region=region, name="Potential")) # get the potential data
    Trappingtime_n = np.array(get_node_model_values(device=device, region=region, name="Trappingtime_n"))
    Trappingtime_p = np.array(get_node_model_values(device=device, region=region, name="Trappingtime_p"))

    element_from_edge_model(edge_model="ElectricField",   device=device, region=region)
    edge_average_model(device=device, region=region, node_model="x", edge_model="xmid")
    edge_average_model(device=device, region=region, node_model="y", edge_model="ymid")
    ElectricField=np.array(get_edge_model_values(device=device, region=region, name="ElectricField"))
    x_mid = np.array(get_edge_model_values(device=device, region=region, name="xmid")) 
    y_mid = np.array(get_edge_model_values(device=device, region=region, name="ymid")) 

    draw(x,y,potential,"potential",v)
    draw(x_mid,y_mid,ElectricField,"ElectricField",v)
    draw(x,y,Trappingtime_n,"Trappingtime_n",v)
    draw(x,y,Trappingtime_p,"Trappingtime_p",v)

    delete_node_model(device=device, region=region, name="IntrinsicElectrons:Potential")
    delete_node_model(device=device, region=region, name="IntrinsicHoles:Potential")

    write_devices(file="./output/strip/si_diode_2d", type="tecplot")

    with open("./output/strip/potential_{}_1e15_.pkl".format(v),'wb') as file:
        pickle.dump(potential, file)
    with open("./output/strip/x.pkl",'wb') as file:
        pickle.dump(x, file)
    with open("./output/strip/y.pkl",'wb') as file:
        pickle.dump(y, file)
    with open("./output/strip/Trappingtime_p_1e15_{}.pkl".format(v),'wb') as file:
        pickle.dump(Trappingtime_p, file)
    with open("./output/strip/Trappingtime_n_1e15_{}.pkl".format(v),'wb') as file:
        pickle.dump(Trappingtime_n, file)

def draw(x,y,value,title,v):
    graph = ROOT.TGraph2D()
    for i in range(len(x)):
        graph.SetPoint(i, y[i], x[i], value[i]) 
    canvas = ROOT.TCanvas("canvas", title, 1500, 1000)
    graph.Draw("CONT4Z")
    canvas.Draw()
    graph.GetXaxis().SetTitle("x[um]")
    graph.GetYaxis().SetTitle("z[um]")
    graph.SetTitle(title)
    canvas.SaveAs("output/strip/"+title+"{}_1e15_2d.png".format(v))
    canvas.SaveAs("output/strip/"+title+"{}_1e15_2d.root".format(v))

if __name__ == "__main__":
    main()    