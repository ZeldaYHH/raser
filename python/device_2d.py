#!/usr/bin/env python3
# -*- encoding: utf-8 -*-


import devsim
import python.diode_element_physics as diode_element_physics
import sys
import math
sys.path.append("..")
import matplotlib
import os
import devsim
import matplotlib.pyplot

if not (os.path.exists("./output/testdiode")):
    os.mkdir("./output/testdiode")



type=sys.argv[1]

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

    devsim.add_2d_contact  (mesh="dog", name="top", region=region, yl=0.8e-5, yh=1e-5, xl=0, xh=0, bloat=1e-10, material="metal")
    devsim.add_2d_contact  (mesh="dog", name="bot", region=region, xl=1e-5,   xh=1e-5, bloat=1e-10, material="metal")

    devsim.finalize_mesh   (mesh="dog")
    devsim.create_device   (mesh="dog", device=device)



device="MyDevice"
region="MyRegion"

createMesh(device,region)


diode_element_physics.setMaterialParameters(device, region)

diode_element_physics.createSolution(device, region, "Potential")

####
#### NetDoping
####

def NetDoping(device=device, region=region):
    if type=="PNjuction":

        for name, equation in (
        ("Acceptors", "2.0e19*step(0.3e-7-x)"),
        ("Donors",    "1.0e18*step(x-(3e-8))"),
        ("NetDoping", "Donors-Acceptors"),
        ):
            devsim.node_model(device=device, region=region, name=name, equation=equation)
    elif type=="PNwithGainlayer":
        for name, equation in (
        ("Acceptors", "2.0e20*step(0.3e-7-x)"),
        ("Donors",    "1.80e17*( step((1.3e-7)-x) -step((3e-8)-x) ) + 1.0e14*( step((51.3e-7)-x) - step((1.3e-7)-x) ) + 1.0e18*( step((56.3e-7)-x) - step((51.3e-7)-x) )+ 2.0e18*( step((66.3e-7)-x) - step((56.3e-7)-x) )"),
        ("NetDoping", "Donors-Acceptors"),
        ):
            devsim.node_model(device=device, region=region, name=name, equation=equation)

NetDoping(device,region)


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
while v < 7:
   
    devsim.set_parameter(device=device, region=region, name="topbias", value=0-v)
    devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=1500)
    diode_element_physics.printCurrents(device, "top", 0-v)
    diode_element_physics.printCurrents(device, "bot", 0.0)
    v += 0.1

    devsim.write_devices(file="./output/testdiode/{0}_{1}dd.dat".format(type,v), type="floops")
    devsim.write_devices(file="./output/testdiode/{0}_{1}_2d_dd".format(type,v), type="tecplot")

print("This is simple pn juction with 2diffrent doping,please download .dd file and use tecplot to check")