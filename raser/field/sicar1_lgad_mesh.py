#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import devsim
import os
import sys
import node
import matplotlib
import matplotlib.pyplot
import math
# 1D SICAR1 LGAD

def Create1DMesh(device, region):
    '''
      Meshing
    '''
    devsim.create_1d_mesh(mesh="lgad")
    devsim.add_1d_mesh_line(mesh="lgad", pos=0, ps=5e-6, tag="top")
    devsim.add_1d_mesh_line(mesh="lgad", pos=(3e-5)-(1e-5), ps=1e-6, tag="jun_up")
    devsim.add_1d_mesh_line(mesh="lgad", pos=3e-5, ps=1e-6, tag="mid")
    devsim.add_1d_mesh_line(mesh="lgad", pos=(3e-5)+(2e-4), ps=5e-6, tag="jun_down")
    devsim.add_1d_mesh_line(mesh="lgad", pos=32.5e-4, ps=0.5e-4, tag="bot")
    devsim.add_1d_contact  (mesh="lgad", name="top", tag="top", material="metal")
    devsim.add_1d_contact  (mesh="lgad", name="bot", tag="bot", material="metal")
    devsim.add_1d_region   (mesh="lgad", material="SiliconCarbide", region=region, tag1="top", tag2="bot")
    devsim.finalize_mesh(mesh="lgad")
    devsim.create_device(mesh="lgad", device=device)

def SetDoping(device, region):
    # min
    gaindoping = 4.45e16 
    bulkdoping = 2.74e14
    # max
    # gaindoping = 6.56e16 
    # bulkdoping = 3.70e14
    '''
      Doping
    # '''
    node.CreateNodeModel(device, region, "Acceptors", "2.0e19*step(3e-5-x)")      
    node.CreateNodeModel(device, region, "Donors",    "{}*( step((1.5e-4)-x) -step((3e-5)-x) ) + {}*( step((17.5e-4)-x) - step((1.5e-4)-x) ) + 1.0e18*( step((22.5e-4)-x) - step((17.5e-4)-x) )+ 1.0e19*( step((32.5e-4)-x) - step((22.5e-4)-x) )".format(gaindoping, bulkdoping))

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

    device="1D_SICAR1_LGAD"
    region="1D_SICAR1_LGAD"

    Create1DMesh(device=device, region=region)
    SetDoping(device=device, region=region)
    Draw_Doping(device=device, region=region, path="./output/devsim/1D_SICAR1_LGAD.png")
  
if __name__ == '__main__':
    main()