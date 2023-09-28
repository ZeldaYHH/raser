#!/usr/bin/env python3
# -*- encoding: utf-8 -*-


import devsim
from . import diode_element_physics

import sys

sys.path.append("..")
import matplotlib
import os

import matplotlib.pyplot


####
#### Meshing
####
def createMesh(device, region):
    devsim.create_2d_mesh  (mesh="dog")
    devsim.add_2d_mesh_line(mesh="dog", dir="x", pos=0     , ps=1e-6)
    devsim.add_2d_mesh_line(mesh="dog", dir="x", pos=0.5e-5, ps=1e-8)
    devsim.add_2d_mesh_line(mesh="dog", dir="x", pos=1e-5  , ps=1e-6)
    devsim.add_2d_mesh_line(mesh="dog", dir="y", pos=0     , ps=1e-6)
    devsim.add_2d_mesh_line(mesh="dog", dir="y", pos=1e-5  , ps=1e-6)

    devsim.add_2d_mesh_line(mesh="dog", dir="x", pos=-1e-8   , ps=1e-8)
    devsim.add_2d_mesh_line(mesh="dog", dir="x", pos=1.001e-5, ps=1e-8)

    devsim.add_2d_region   (mesh="dog", material="Si", region=region)
    devsim.add_2d_region   (mesh="dog", material="Si", region="air1", xl=-1e-8,  xh=0)
    devsim.add_2d_region   (mesh="dog", material="Si", region="air2", xl=1.0e-5, xh=1.001e-5)

    devsim.add_2d_contact  (mesh="dog", name="top", region=region, xl=0, xh=0, bloat=1e-10, material="metal")
    devsim.add_2d_contact  (mesh="dog", name="bot", region=region, xl=1e-5,   xh=1e-5, bloat=1e-10, material="metal")

    devsim.finalize_mesh   (mesh="dog")
    devsim.create_device   (mesh="dog", device=device)


device="MyDevice"
region="MyRegion"
def main():
    createMesh(device, region)

    diode_element_physics.setMaterialParameters(device, region)

    diode_element_physics.createSolution(device, region, "Potential")

    ####
    #### NetDoping
    ####
    for name, equation in (
        ("Acceptors", "1.8e19*step(0.5e-5-x)"),
    ("Donors",    "5.2e13*step(x-0.5e-5)"),
    ("NetDoping", "Donors-Acceptors"),
    ):
        devsim.node_model(device=device, region=region, name=name, equation=equation)

    diode_element_physics.createPotentialOnly(device, region)


    diode_element_physics.createPotentialOnlyContact(device, region, "top")
    diode_element_physics.createPotentialOnlyContact(device, region, "bot")

    ####
    #### Initial DC solution
    ####
    devsim.solve(type="dc", absolute_error=1.0, relative_error=1e-12, maximum_iterations=30)


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



    devsim.set_parameter(device=device, region=region, name="topbias", value=0.0)



    v=0
    while v < 0.51:
        devsim.set_parameter(device=device, region=region, name="topbias", value=0-v)
        devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=150)
        diode_element_physics.printCurrents(device, "top", v)
        diode_element_physics.printCurrents(device, "bot", 0.0)
        v += 0.1
        if not os.path.exists('./output/testdiode'):
            os.makedirs('./output/testdiode')

        
        devsim.write_devices(file="./output/testdiode/diode_elementtest_2d_dd", type="tecplot")
if __name__ == "__main__":
    main()               
