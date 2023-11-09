#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import devsim
import os
import sys
from . import node
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot
import math

# NJU PIN 5mm*5mm 

# 1d
def Create1DMesh(device, region):
    '''
      Meshing
    '''
    devsim.create_1d_mesh(mesh="dio")
    devsim.add_1d_mesh_line(mesh="dio", pos=0, ps=1e-4, tag="top")
    devsim.add_1d_mesh_line(mesh="dio", pos=(1e-4)-(0.5e-4), ps=1e-5, tag="jun_up")
    devsim.add_1d_mesh_line(mesh="dio", pos=1e-4, ps=1e-5, tag="mid")
    devsim.add_1d_mesh_line(mesh="dio", pos=(1e-4)+(3e-4), ps=1e-5, tag="jun_down")
    devsim.add_1d_mesh_line(mesh="dio", pos=100*1e-4, ps=1e-4, tag="bot")
    devsim.add_1d_contact  (mesh="dio", name="top", tag="top", material="metal")
    devsim.add_1d_contact  (mesh="dio", name="bot", tag="bot", material="metal")
    devsim.add_1d_region   (mesh="dio", material="SiliconCarbide", region=region, tag1="top", tag2="bot")
    devsim.finalize_mesh(mesh="dio")
    devsim.create_device(mesh="dio", device=device)

def SetDoping(device, region, bulk_doping="5.2e13"):
    '''
      Doping
    '''
    node.CreateNodeModel(device, region, "Acceptors", "1.0e19*step(1e-4-x)")
    node.CreateNodeModel(device, region, "Donors",    "%s*step(x-1e-4)"%bulk_doping)
    node.CreateNodeModel(device, region, "NetDoping", "Donors-Acceptors")
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

    device="1D_NJU_PIN"
    region="1D_NJU_PIN"

    Create1DMesh(device=device, region=region)
    SetDoping(device=device, region=region)
    Draw_Doping(device=device, region=region, path="./output/devsim/1D_NJU_PIN_doping.png")

if __name__ == '__main__':
    main()
