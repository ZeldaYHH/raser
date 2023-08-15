#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import devsim
import os
import sys
from raser import Node
import matplotlib
import matplotlib.pyplot
import math
gaindoping = sys.argv[1]
bulkdoping = sys.argv[2]
#bulk_thickness = sys.argv[1]
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

    #Node.CreateNodeModel(device, region, "Acceptors", "2.0e19*step(3e-5-x)")      
    #Node.CreateNodeModel(device, region, "Donors",    "8.0e16*(step((1.3e-4)-x) -step((3e-5)-x) ) + 5.6e14*( step(({0}+1.3e-4)-x) - step((1.3e-4)-x) ) + 1.0e18*( step(({0}+6.3e-4)-x) - step(({0}+1.3e-4)-x) )+ 2.0e18*( step(({0}+16.3e-4)-x) - step(({0}+6.3e-4)-x) )".format(bulk_thickness))

    Node.CreateNodeModel(device, region, "Acceptors", "2.0e19*step(3e-5-x)")      
    Node.CreateNodeModel(device, region, "Donors",    "{0}*( step((1.3e-4)-x) -step((3e-5)-x) ) + {1}*( step((51.3e-4)-x) - step((1.3e-4)-x) ) + 1.0e18*( step((56.3e-4)-x) - step((51.3e-4)-x) )+ 2.0e18*( step((66.3e-4)-x) - step((56.3e-4)-x) )".format(gaindoping,bulkdoping))

    #Node.CreateNodeModel(device, region, "Acceptors", "1.63e19*step(3e-5-x)")      
    #Node.CreateNodeModel(device, region, "Donors",    "1.04e17*( step((1.3e-4)-x) -step((3e-5)-x) ) + 2.203e14*( step((54.3e-4)-x) - step((1.3e-4)-x) ) + 1.21e18*( step((59.3e-4)-x) - step((54.3e-4)-x) )+ 2.0e18*( step((69.3e-4)-x) - step((59.3e-4)-x) )")

    Node.CreateNodeModel(device, region, "NetDoping", "Donors-Acceptors")
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
    Draw_Doping(device=device, region=region, path="./output/devsim/1D_SICAR1_LGAD_gaindoping_{}_bulkdoping_{}.png".format(gaindoping,bulkdoping))
    #Draw_Doping(device=device, region=region, path="./output/devsim/1D_SICAR1_LGAD_bulk_thickness_{0}.png".format(bulk_thickness))

if __name__ == '__main__':
    main()