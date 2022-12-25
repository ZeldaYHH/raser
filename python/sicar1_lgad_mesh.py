#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import devsim
import os
import sys
from raser import Node
import matplotlib
import matplotlib.pyplot

# 1D SICAR1 LGAD



def CreateMesh(device, region):
    '''
      Meshing
    '''
    devsim.create_1d_mesh(mesh="lgad")
    devsim.add_1d_mesh_line(mesh="lgad", pos=0, ps=5e-6, tag="top")
    devsim.add_1d_mesh_line(mesh="lgad", pos=(3e-5)-(1e-5), ps=1e-6, tag="jun_up")
    devsim.add_1d_mesh_line(mesh="lgad", pos=3e-5, ps=1e-6, tag="mid")
    devsim.add_1d_mesh_line(mesh="lgad", pos=(3e-5)+(2e-4), ps=5e-6, tag="jun_down")
    devsim.add_1d_mesh_line(mesh="lgad", pos=66.3e-4, ps=0.5e-4, tag="bot")
    devsim.add_1d_contact  (mesh="lgad", name="top", tag="top", material="metal")
    devsim.add_1d_contact  (mesh="lgad", name="bot", tag="bot", material="metal")
    devsim.add_1d_region   (mesh="lgad", material="SiliconCarbide", region=region, tag1="top", tag2="bot")
    devsim.finalize_mesh(mesh="lgad")
    devsim.create_device(mesh="lgad", device=device)



def SetDoping(device, region):
    '''
      Doping
    '''
    #Node.CreateNodeModel(device, region, "Acceptors", "2.0e19*step(3e-5-x)")      
    #Node.CreateNodeModel(device, region, "Donors",    "1.0e17*( step((1.3e-4)-x) -step((3e-5)-x) ) + 1.0e14*( step((51.3e-4)-x) - step((1.3e-4)-x) ) + 1.0e18*( step((56.3e-4)-x) - step((51.3e-4)-x) )+ 1.0e19*( step((66.3e-4)-x) - step((56.3e-4)-x) )")

    Node.CreateNodeModel(device, region, "Acceptors", "2.0e19*step(3e-5-x)")      
    Node.CreateNodeModel(device, region, "Donors",    "1.48e17*( step((1.3e-4)-x) -step((3e-5)-x) ) + 1.0e14*( step((51.3e-4)-x) - step((1.3e-4)-x) ) + 1.0e18*( step((56.3e-4)-x) - step((51.3e-4)-x) )+ 2.0e18*( step((66.3e-4)-x) - step((56.3e-4)-x) )")

    #Node.CreateNodeModel(device, region, "Acceptors", "1.63e19*step(3e-5-x)")      
    #Node.CreateNodeModel(device, region, "Donors",    "1.04e17*( step((1.3e-4)-x) -step((3e-5)-x) ) + 2.203e14*( step((54.3e-4)-x) - step((1.3e-4)-x) ) + 1.21e18*( step((59.3e-4)-x) - step((54.3e-4)-x) )+ 2.0e18*( step((69.3e-4)-x) - step((59.3e-4)-x) )")

    Node.CreateNodeModel(device, region, "NetDoping", "Donors-Acceptors")



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
        os.mkdir("./output/devsim")

    device="1D_SICAR1_LGAD"
    region="1D_SICAR1_LGAD"

    CreateMesh(device=device, region=region)
    SetDoping(device=device, region=region)
    Draw_Doping(device=device, region=region, path="./output/devsim/sicar1_lgad_doping.png")


if __name__ == '__main__':
    main()