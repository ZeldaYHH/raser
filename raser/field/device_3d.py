#!/usr/bin/env python3
# -*- encoding: utf-8 -*-


import devsim
from . import diode_element_physics
from .build_device import Detector
import sys
import math
sys.path.append("..")
import matplotlib
import os
import devsim
import matplotlib.pyplot

if not (os.path.exists("./output/pixel")):
    os.mkdir("./output/pixel")

simname="3d_pixel"
device=simname
region=simname




def main():
    Pixel3D = Detector(simname, 3)

    diode_element_physics.setMaterialParameters(device, region)

    diode_element_physics.createSolution(device, region, "Potential")

    


    diode_element_physics.createPotentialOnly(device, region)


    diode_element_physics.createPotentialOnlyContact(device, region, "top")
    diode_element_physics.createPotentialOnlyContact(device, region, "bot")

    ####
    #### Initial DC solution
    ####
    devsim.solve(type="dc", absolute_error=1.0, relative_error=1e-12, maximum_iterations=30)

    devsim.write_devices(file="dio2_element_2d_potentialonly.flps", type="floops")

    ####
    #### drift diffusion
    ####
    diode_element_physics.createSolution(device, region, "Electrons")
    diode_element_physics.createSolution(device, region, "Holes")

    ####
    #### create initial guess from dc only solution
    ####
    devsim.set_node_values(device=device, region=region, name="Electrons", init_from="IntrinsicElectrons")
    devsim.set_node_values(device=device, region=region, name="Holes",     init_from="IntrinsicHoles")

    diode_element_physics.createDriftDiffusion(device, region)

    diode_element_physics.createDriftDiffusionAtContact(device, region, "top")
    diode_element_physics.createDriftDiffusionAtContact(device, region, "bot")



    devsim.set_parameter(device=device, region=region, name="top", value=0.0)



    devsim.circuit_element(name="V1", n1=1,         n2=0, value=1.0, acreal=1.0)
    devsim.circuit_element(name="R1", n1="top", n2=1, value=1e3)


    v=0
    while v < 5:
    
        devsim.set_parameter(device=device, region=region, name="topbias", value=0-v)
        devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=1500)
        diode_element_physics.printCurrents(device, "top", 0-v)
        diode_element_physics.printCurrents(device, "bot", 0.0)
        v += 0.1

        devsim.write_devices(file="./output/pixel/{0}_{1}dd.dat".format(type,v), type="floops")
        devsim.write_devices(file="./output/pixel/{0}_{1}_2d_dd".format(type,v), type="tecplot")

if __name__ == "__main__":
    main()      