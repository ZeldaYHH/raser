#!/usr/bin/env python3
# -*- encoding: utf-8 -*-


import sys
import csv
from raser import Node
from raser import Physics
sys.path.append("..")
import matplotlib
import os
import devsim
import matplotlib.pyplot
import math

def Create2DMesh(device,region):
    devsim.create_2d_mesh  (mesh="Sicar")
    #宽0.01cm
    devsim.add_2d_mesh_line(mesh="Sicar", dir="x", pos=0     , ps=1e-3)
    devsim.add_2d_mesh_line(mesh="Sicar", dir="x", pos=1e-2  , ps=1e-4)

    #长0.5cm
    devsim.add_2d_mesh_line(mesh="Sicar", dir="y", pos=0     , ps=0.01)
    devsim.add_2d_mesh_line(mesh="Sicar", dir="y", pos=0.5 , ps=0.01)

    #划分各个区域
    #0-0.3um P++
    devsim.add_2d_mesh_line(mesh="Sicar", dir="x", pos=0.3e-4     , ps=1e-4)
    #0.3e-5-1.3um N+
    devsim.add_2d_mesh_line(mesh="Sicar", dir="x", pos=1.3e-4  , ps=1e-4)
    #1.3-51.3um n-
    devsim.add_2d_mesh_line(mesh="Sicar", dir="x", pos=51.3e-4  , ps=1e-4)
    #51.3um-56.3um nbuffer
    devsim.add_2d_mesh_line(mesh="Sicar", dir="x", pos=56.3e-4  , ps=1e-4)

    devsim.add_2d_mesh_line(mesh="Sicar", dir="x", pos=-1e-4   , ps=1e-4)
    devsim.add_2d_mesh_line(mesh="Sicar", dir="x", pos=1.01e-2, ps=1e-4)

    devsim.add_2d_region   (mesh="Sicar", material="SiliconCarbide", region=region)
    devsim.add_2d_region   (mesh="Sicar", material="SiliconCarbide", region="air1", xl=-1e-4,  xh=0)
    devsim.add_2d_region   (mesh="Sicar", material="SiliconCarbide", region="air2", xl=1.01e-2, xh=1e-2)

    devsim.add_2d_contact  (mesh="Sicar", name="Pcontact", region=region, yl=0, yh=0.5, xl=0, xh=0, bloat=1e-6, material="metal")
    devsim.add_2d_contact  (mesh="Sicar", name="Ncontact", region=region, xl=1e-2,   xh=1e-2, bloat=1e-6, material="metal")

    devsim.finalize_mesh   (mesh="Sicar")
    devsim.create_device   (mesh="Sicar", device=device)
    devsim.write_devices(file="./output/devsim/Sicar1_1.dat",device=device,type="tecplot")


def SetDoping(device,region):
    Node.CreateNodeModel(device,region, "Acceptors", "2.0e19*step(0.3e-4-x)")
    Node.CreateNodeModel(device, region, "Donors",    "1.40e17*( step((1.3e-4)-x) -step((3e-5)-x) ) + 1.0e14*( step((51.3e-4)-x) - step((1.3e-4)-x) ) + 1.0e18*( step((56.3e-4)-x) - step((51.3e-4)-x) )+ 2.0e18*( step((66.3e-4)-x) - step((56.3e-4)-x) )")
    Node.CreateNodeModel(device, region, "NetDoping","Donors-Acceptors")
    devsim.edge_from_node_model(device=device,region=region,node_model="Acceptors")
    devsim.edge_from_node_model(device=device,region=region,node_model="NetDoping")
    devsim.edge_from_node_model(device=device,region=region,node_model="Donors")


def Draw_Doping(device, region, path):

    fig1=matplotlib.pyplot.figure(num=1,figsize=(4,4))

    x=devsim.get_node_model_values(device=device, region=region, name="x")
    fields = ("Donors", "Acceptors")

    for i in fields:
        y=devsim.get_node_model_values(device=device, region=region, name=i)
        matplotlib.pyplot.semilogy(x, y)
    
    matplotlib.pyplot.xlabel('x (cm)')
    matplotlib.pyplot.ylabel('Density (#/cm^3)')
    matplotlib.pyplot.legend(fields)
    matplotlib.pyplot.savefig(path)

def main():
    if not (os.path.exists("./output/devsim")):
        os.makedirs("./output/devsim")

    device="MyDevice"
    region="MyDevice"
    Create2DMesh(device=device, region=region)
    #createMesh(device=device, region=region)
    SetDoping(device=device, region=region)
    Draw_Doping(device=device, region=region, path="./output/devsim/2DSicar1_1.png")











