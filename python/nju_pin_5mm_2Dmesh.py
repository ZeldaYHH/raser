import devsim
import os
import sys
from raser import Node
import matplotlib
import matplotlib.pyplot

#NJU PIN 5mm*5mm 2D
def main():
    if not (os.path.exists("./output/devsim")):
        os.makedirs("./output/devsim")

    device="2D_NJU_PIN"
    region="2D_NJU_PIN"

    Create1DMesh(device=device, region=region)
    SetDoping(device=device, region=region)
    #Draw_Doping(device=device, region=region, path="./output/1d_nju_pin_doping.png")
    devsim.write_devices(file="nju_pin_5mm_2D",device=device,type="vtk")

def Create2DMesh(device,region):
    #meshing
    devsim.create_2d_mesh(mesh="pin")
    devsim.add_2d_mesh_line(mesh="pin",dir="x",pos=0,ps=1e-6)
    devsim.add_2d_mesh_line(mesh="pin",dir="x",pos=1e-4,ps=1e-5)
    devsim.add_2d_mesh_line(mesh="pin",dir="x",pos=1e-2,ps=1e-4)
    devsim.add_2d_mesh_line(mesh="pin",dir="y",pos=0,ps=1e-3)
    devsim.add_2d_mesh_line(mesh="pin",dir="y",pos=0.5,ps=1e-3)
    devsim.add_2d_region(mesh="pin",region=region,material="SiliconCarbide",xl=0,xh=1e-2,yl=0,yh=0.5)
    devsim.add_2d_contact(name="top",material="metal",mesh="pin",region=region,xl=0,xh=0)
    devsim.add_2d_contact(name="top",material="metal",mesh="pin",region=region,xl=1e-2,xh=1e-2) 
    devsim.finalize_mesh(mesh="pin")
    devsim.creat_device(mesh="pin",device=device)

def SetDoping(device,region):
    #Doping
    CreateNodeModel(device,region,"Acceptors","1.0e19*step(1e-4-x)")
    CreateNodeModel(device,region,"Donors","5.2e13*step(x-1e-4)")
    CreateNodeModel(device,region,"NetDoping","Donors-Acceptors")