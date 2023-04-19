#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import devsim
import os
import sys
from raser import Node
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

def SetDoping(device, region, bulk_doping="5.2e13"):
    '''
      Doping
    '''
    Node.CreateNodeModel(device, region, "Acceptors", "1.0e19*step(1e-4-x)")
    Node.CreateNodeModel(device, region, "Donors",    "%s*step(x-1e-4)"%bulk_doping)
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

    device="1D_NJU_PIN"
    region="1D_NJU_PIN"

    Create1DMesh(device=device, region=region)
    SetDoping(device=device, region=region)
    Draw_Doping(device=device, region=region, path="./output/devsim/nju_pin_doping.png")

if __name__ == '__main__':
    main()
