#!/usr/bin/env python3
# -*- encoding: utf-8 -*-


import sys
sys.path.append("..")
from raser import Node
import matplotlib
import os
import devsim
import matplotlib.pyplot
#此处初始化器件，注意初始化器件
def Create3DSICARFromGmesh(device, region):
    devsim.create_gmsh_mesh (file="3d_pin.msh", mesh="3d_pin")
    devsim.add_gmsh_region  (mesh="3d_pin" ,  gmsh_name="bulk",    region=region, material="SiliconCarbide")
    devsim.add_gmsh_contact (mesh="3d_pin" ,  gmsh_name="top",    region=region, material="metal", name="top")
    devsim.add_gmsh_contact  (mesh="3d_pin" ,  gmsh_name="bot",    region=region, material="metal" ,name="bot")
    devsim.finalize_mesh    (mesh="3d_pin")
    devsim.create_device    (mesh="3d_pin", device=device)

#此处定义掺杂
def SetDoping(device, region):
    Node.CreateNodeModel(device, region, "bulk",   "5.2e13")
    Node.CreateNodeModel(device, region, "top", "5.2e13")
    Node.CreateNodeModel(device, region, "bot",   "5.2e13")
    Node.CreateNodeModel(device, region, "NetDoping", "top-bot-bulk")

#此处可视化
def Draw_Doping(device, region, path):

    fig1=matplotlib.pyplot.figure(num=1,figsize=(4,4))

    x=devsim.get_node_model_values(device=device, region=region, name="z")
    fields = ("top", "bot","bulk")

    for i in fields:
        y=devsim.get_node_model_values(device=device, region=region, name=i)
        matplotlib.pyplot.semilogy(x, y)

    matplotlib.pyplot.xlabel('z (cm)')
    matplotlib.pyplot.ylabel('Density (#/cm^3)')
    matplotlib.pyplot.legend(fields)
    matplotlib.pyplot.savefig(path)



def main():
    if not (os.path.exists("./output")):
        os.mkdir("./output")
    device="3d_pin"
    region="3d_pin"

    Create3DSICARFromGmesh(device=device, region=region)
    SetDoping(device=device, region=region)
    Draw_Doping(device=device, region=region, path="./output/3d_pin_doping.png")
    devsim.write_devices(file="3d_pin_doping.dat",type="tecplot")


if __name__ == '__main__':
    main()
