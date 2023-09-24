#!/usr/bin/env python3
# -*- encoding: utf-8 -*-


import devsim
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from readjson import Setting
from field import node
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot
import math


#  MD8
# 0.8cm*0.8cm
args = ["det_name=ITk-Si-strip","parfile=paras/setting.json"]
dset = Setting(args)
det_dic = dset.detector    
#doping=str(det_dic['doping'])+"e12"
doping=str(det_dic['doping'])

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
    devsim.add_1d_mesh_line(mesh="dio", pos=305*1e-4, ps=1e-4, tag="bot")

    # devsim.add_1d_mesh_line(mesh="dio", pos=0, ps=1e-5, tag="top")
    # devsim.add_1d_mesh_line(mesh="dio", pos=(0.5e-4)-(0.25e-4), ps=1e-5, tag="jun_up")
    # devsim.add_1d_mesh_line(mesh="dio", pos=0.5e-4, ps=1e-5, tag="mid")
    # devsim.add_1d_mesh_line(mesh="dio", pos=(0.5e-4)+(3e-4), ps=1e-5, tag="jun_down")
    # devsim.add_1d_mesh_line(mesh="dio", pos=305*1e-4, ps=1e-4, tag="bot")
    
    devsim.add_1d_contact  (mesh="dio", name="top", tag="top", material="metal")
    devsim.add_1d_contact  (mesh="dio", name="bot", tag="bot", material="metal")
    devsim.add_1d_region   (mesh="dio", material="Silicon", region=region, tag1="top", tag2="bot")
    devsim.finalize_mesh(mesh="dio")
    devsim.create_device(mesh="dio", device=device)



def SetDoping_old(device, region, bulk_doping=doping):#default doping 4.7e12
    '''
      Doping
    '''
    #node.CreateNodeModel(device, region, "Donors", "5.0e15*step(1e-4-x)")
    node.CreateNodeModel(device, region, "Donors", "1.0e19*step(1e-4-x)")
    #node.CreateNodeModel(device, region, "Donors", "1.0e19*step(0.5e-4-x)")
    node.CreateNodeModel(device, region, "Acceptors",    "%s*step(x-1e-4)"%bulk_doping)
    node.CreateNodeModel(device, region, "NetDoping", "Donors-Acceptors")
    devsim.edge_from_node_model(device=device,region=region,node_model="Acceptors")
    devsim.edge_from_node_model(device=device,region=region,node_model="NetDoping")
    devsim.edge_from_node_model(device=device,region=region,node_model="Donors")


def SetDoping(device, region, bulk_doping=doping, backthickness="304.9", back_doping="1e17"):#default doping 4.7e12
    '''
      Doping
    '''
    #node.CreateNodeModel(device, region, "Donors", "5.0e15*step(1e-4-x)")
    node.CreateNodeModel(device, region, "Donors", "1.0e19*step(1e-4-x)")
    node.CreateNodeModel(device, region, "Acceptors",    "step(%s*1e-4-x)*%s*step(x-1e-4)+%s*step(x-%s*1e-4)"%(backthickness,bulk_doping,back_doping,backthickness))
    #node.CreateNodeModel(device, region, "Acceptors",    "step(303*1e-4-x)*%s*step(x-1e-4)+1e16*step(x-303*1e-4)"%bulk_doping)
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
    

    device="1D_ITK_MD8"
    region="1D_ITK_MD8"
    if not (os.path.exists("./output/devsim/"+device+"_"+doping)):
        os.makedirs("./output/devsim/"+device+"_"+doping)


    Create1DMesh(device=device, region=region)
    SetDoping(device=device, region=region, bulk_doping=doping) 
    Draw_Doping(device=device, region=region, path="./output/devsim/1D_ITK_MD8_"+doping+".png")

if __name__ == '__main__':
    main()
