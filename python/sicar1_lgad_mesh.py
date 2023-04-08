#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import devsim
import os
import sys
from raser import Node
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
    devsim.add_1d_mesh_line(mesh="lgad", pos=66.3e-4, ps=0.5e-4, tag="bot")
    devsim.add_1d_contact  (mesh="lgad", name="top", tag="top", material="metal")
    devsim.add_1d_contact  (mesh="lgad", name="bot", tag="bot", material="metal")
    devsim.add_1d_region   (mesh="lgad", material="SiliconCarbide", region=region, tag1="top", tag2="bot")
    devsim.finalize_mesh(mesh="lgad")
    devsim.create_device(mesh="lgad", device=device)

def SetTrapParameters(device,region):
    #add defect parameters
    N_c=3.25e15 #effective density of states in conduction band
    N_v=4.8e15 #effective density of states in valence band
    devsim.set_parameter(device=device,region=region,name="N_c",value=N_c)
    devsim.set_parameter(device=device,region=region,name="N_v",value=N_v)
    k=1.3806503e-23 
    T0=300
    #Z1/2
    E_t11=-0.67*1.6e-19 #J
    E_t12=-2.56*1.6e-19
    n_11=N_c*math.exp(E_t11/(k*T0))
    p_11=N_v*math.exp(E_t12/(k*T0))
    devsim.set_parameter(device=device,region=region,name="N_t1",value=0)#density of Z1/2,4.1e13 from paper
    devsim.set_parameter(device=device,region=region,name="r_n1",value=2e-7)#electron capture constant of Z1/2
    devsim.set_parameter(device=device,region=region,name="r_p1",value=3e-7)#hole capture constant of Z1/2
    devsim.set_parameter(device=device,region=region,name="E_t11",value=E_t11)#Z1/2 Et-Ec
    devsim.set_parameter(device=device,region=region,name="E_t12",value=E_t12)#Z1/2 -(Et-Ev)
    devsim.set_parameter(device=device,region=region,name="n_11",value=n_11)#n1 of Z1/2
    devsim.set_parameter(device=device,region=region,name="p_11",value=p_11)#p1 of Z1/2
    #EH6/7
    E_t21=-1.65*1.6e-19 #J
    E_t22=-1.58*1.6e-19
    n_12=N_c*math.exp(E_t21/(k*T0))
    p_12=N_v*math.exp(E_t22/(k*T0))
    devsim.set_parameter(device=device,region=region,name="N_t2",value=0)#density of EH6/7,3.9e13 from paper
    devsim.set_parameter(device=device,region=region,name="r_n2",value=2.4e-7)#electron capture constant of EH6/7
    devsim.set_parameter(device=device,region=region,name="r_p2",value=5e-11)#hole capture constant of EH6/7
    devsim.set_parameter(device=device,region=region,name="E_t21",value=E_t21)#EH6/7 Et-Ec
    devsim.set_parameter(device=device,region=region,name="E_t22",value=E_t22)#EH6/7 -(Et-Ev)
    devsim.set_parameter(device=device,region=region,name="n_12",value=n_12)#n1 of EH6/7
    devsim.set_parameter(device=device,region=region,name="p_12",value=p_12)#p1 of EH6/7

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
    devsim.edge_from_node_model(device=device,region=region,node_model="Acceptors")
    devsim.edge_from_node_model(device=device,region=region,node_model="NetDoping")
    devsim.edge_from_node_model(device=device,region=region,node_model="Donors")
    SetTrapParameters(device=device,region=region)

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
    Draw_Doping(device=device, region=region, path="./output/devsim/sicar1_lgad_doping.png")


if __name__ == '__main__':
    main()