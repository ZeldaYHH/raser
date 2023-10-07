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
    solve(type="dc", absolute_error=1e10, relative_error=1e-7, maximum_iterations=1000)
    #solve(type="dc", absolute_error=1.0, relative_error=1e-12, maximum_iterations=30)

    si_diode_common.DriftDiffusionInitialSolution(device, region)
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
    while v < 300:
        set_parameter(device=device, name=GetContactBiasName("bot"), value=v)
        solve(type="dc", absolute_error=1e10, relative_error=1e-3, maximum_iterations=1500)
        PrintCurrents(device, "bot")
        v += 1


    if not os.access('output/testdiode', os.F_OK):
        os.makedirs('output/testdiode', exist_ok=True)

    x = np.array(get_node_model_values(device=device, region=region, name="x")) # get x-node values
    y = np.array(get_node_model_values(device=device, region=region, name="y")) # get y-node values
    potential = np.array(get_node_model_values(device=device, region=region, name="Potential")) # get the potential dat

    graph = ROOT.TGraph2D()
    for i in range(len(x)):
        graph.SetPoint(i, y[i], x[i], potential[i]) 
    canvas = ROOT.TCanvas("canvas", "potential", 1000, 600)
    graph.Draw("COLZ")
    canvas.Draw()
    graph.SetTitle("potential")
    canvas.SaveAs("output/testdiode/potential_2d.png")

    delete_node_model(device=device, region=region, name="IntrinsicElectrons:Potential")
    delete_node_model(device=device, region=region, name="IntrinsicHoles:Potential")

    write_devices(file="./output/testdiode/si_diode_2d", type="tecplot")

if __name__ == "__main__":
    main()    