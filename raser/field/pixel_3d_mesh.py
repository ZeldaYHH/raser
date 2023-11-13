import devsim
import sys
sys.path.append("..")
from . import node_in_2d
import matplotlib
import os

def Create3DSICARFromGmesh(device, region):
    #this reads in the gmsh format
    devsim.create_gmsh_mesh (mesh="pin", file="./output/parainprogram/pixel.msh")
    devsim.add_gmsh_region  (mesh="pin", gmsh_name="bulk",    region=region, material="SiliconCarbide")
    devsim.add_gmsh_contact (mesh="pin", gmsh_name="top",    region=region, material="metal", name="top")
    devsim.add_gmsh_contact (mesh="pin", gmsh_name="bot", region=region, material="metal", name="bot")
    devsim.finalize_mesh    (mesh="pin")
    devsim.create_device    (mesh="pin", device=device)



def SetDoping(device, region):
    node_in_2d.CreateNodeModel(device, region, "Donors", "1.0e17*step(1e-8-z)")      
    node_in_2d.CreateNodeModel(device, region, "Acceptors",    "1e15*step(z-1e-8)")
    node_in_2d.CreateNodeModel(device, region, "NetDoping", "Acceptors-Donors")


def Draw_Doping(device, region, path):

    fig1=matplotlib.pyplot.figure(num=1,figsize=(4,4))

    x=devsim.get_node_model_values(device=device, region=region, name="z")
    fields = ("Donors", "Acceptors")

    for i in fields:
        y=devsim.get_node_model_values(device=device, region=region, name=i)
        matplotlib.pyplot.semilogy(x, y)
    
    matplotlib.pyplot.xlabel('x (cm)')
    matplotlib.pyplot.ylabel('Density (#/cm^3)')
    matplotlib.pyplot.legend(fields)
    matplotlib.pyplot.savefig(path)



def main():
    if not (os.path.exists("./output/pixel")):
        os.mkdir("./output/pixel")

    device="MyDevice"
    region="MyRegion"

    Create3DSICARFromGmesh(device=device, region=region)
    SetDoping(device=device, region=region)
    Draw_Doping(device=device, region=region, path="./output/pixel/pixel_doping.png")
    devsim.write_devices(file="./output/pixel/pixel.dat",type="tecplot")


if __name__ == '__main__':
    main()
