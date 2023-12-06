#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2013 DEVSIM LLC
#
# SPDX-License-Identifier: Apache-2.0

from devsim import *
from .physics_drift_diffusion import *
from .initial import *
from .build_device import Detector

import numpy as np
import os
import ROOT
#####
# dio1
#
# Make doping a step function
# print dat to text file for viewing in grace
# verify currents analytically
# in dio2 add recombination
#
def main():
    open_db(filename="./output/field/SICARDB.db", permission="readonly")
    device='HPK-Si-PIN'
    region='HPK-Si-PIN'

    MyDetector = Detector('HPK-Si-PIN', 1)

    InitialSolution(device, region)

    # Initial DC solution
    solve(type="dc", absolute_error=1.0, relative_error=1e-7, maximum_iterations=1000)

    DriftDiffusionInitialSolution(device, region)
    ###
    ### Drift diffusion simulation at equilibrium
    ###
    solve(type="dc", absolute_error=1e10, relative_error=1e-7, maximum_iterations=1000)


    ####
    #### Ramp the bias to 0.5 Volts
    ####
    v = 0.0
    delete_node_model(device=device, region=region, name="IntrinsicElectrons")
    delete_node_model(device=device, region=region, name="IntrinsicHoles")
    while v < 600:
        set_parameter(device=device, name=GetContactBiasName("bot"), value=-v)
        solve(type="dc", absolute_error=1e10, relative_error=1e-4, maximum_iterations=1500)
        PrintCurrents(device, "top")
        PrintCurrents(device, "bot")
        v += 1


    x = np.array(get_node_model_values(device=device, region=region, name="x"))
    potential = np.array(get_node_model_values(device=device, region=region, name="Potential")) # get the potential dat
    NetDoping= np.array(get_node_model_values(device=device, region=region, name="NetDoping"))
    PotentialNodeCharge = np.array(get_node_model_values(device=device, region=region, name="PotentialNodeCharge"))
    Electrons = np.array(get_node_model_values(device=device, region=region, name="Electrons"))
    Holes = np.array(get_node_model_values(device=device, region=region, name="Holes"))
    edge_average_model(device=device, region=region, node_model="x", edge_model="xmid")
    x_mid = get_edge_model_values(device=device, region=region, name="xmid") # get x-node values 
    ElectricField = get_edge_model_values(device=device, region=region, name="ElectricField") # get y-node values
    TrappingRate_n = np.array(get_node_model_values(device=device, region=region, name="TrappingRate_n"))
    TrappingRate_p = np.array(get_node_model_values(device=device, region=region, name="TrappingRate_p"))

    if not os.access('output/testdiode', os.F_OK):
            os.makedirs('output/testdiode', exist_ok=True)

    draw(x,potential,"Potential","Depth[cm]","Potential[V]",v)
    draw(x_mid,ElectricField,"ElectricField","Depth[cm]","ElectricField[V/cm]",v)
    draw(x,TrappingRate_n,"TrappingRate_n","Depth[cm]","TrappingRate_n[s]",v)
    draw(x,TrappingRate_p,"TrappingRate_p","Depth[cm]","TrappingRate_p[s]",v)

    delete_node_model(device=device, region=region, name="IntrinsicElectrons:Potential")
    delete_node_model(device=device, region=region, name="IntrinsicHoles:Potential")
    write_devices(file="./output/testdiode/si_diode_1d", type="tecplot")


def draw(x,y,title,xtitle,ytitle,v):
    graph = ROOT.TGraph()
    for i in range(len(x)):
        graph.SetPoint(i, x[i],y[i])
    graph.SetTitle(title)
    canvas = ROOT.TCanvas("canvas", title, 1900, 600)
    graph.Draw("AL") 
    graph.GetXaxis().SetTitle(xtitle)
    graph.GetYaxis().SetTitle(ytitle)
    canvas.Draw()
    canvas.SaveAs("output/testdiode/"+title+"{}_1d.png".format(v))

if __name__ == "__main__":
    main()    