#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import numpy as np
import pickle
import ROOT
import devsim

from . import physics
from . import node

from . import physics_2d
from . import node_in_2d

def Create1DMesh(device, region, device_dict):
    devsim.create_1d_mesh(mesh=device)
    mesh = device_dict["mesh"]["1D_mesh"]
    for mesh_line in mesh["mesh_line"]:
        devsim.add_1d_mesh_line(mesh=device, **mesh_line)
    for region in mesh["region"]:
        devsim.add_1d_region   (mesh=device, **region)
    for contact in mesh["contact"]:
        devsim.add_1d_contact  (mesh=device, **contact)
    devsim.finalize_mesh(mesh=device)
    devsim.create_device(mesh=device, device=device)

def Create2DMesh(device, region, device_dict):
    devsim.create_2d_mesh(mesh=device)
    mesh = device_dict["mesh"]["2D_mesh"]
    for mesh_line in mesh["mesh_line"]:
        devsim.add_2d_mesh_line(mesh=device, **mesh_line)
    for region in mesh["region"]:
        devsim.add_2d_region   (mesh=device, **region)
    for contact in mesh["contact"]:
        devsim.add_2d_contact  (mesh=device, **contact)
    devsim.finalize_mesh(mesh=device)
    devsim.create_device(mesh=device, device=device)

def CreateGmshMesh(device, region, device_dict):
    mesh = device_dict["mesh"]["gmsh_mesh"]
    devsim.create_gmsh_mesh (mesh=device, file=mesh['file'])
    for region in mesh["region"]:
        devsim.add_2d_region   (mesh=device, **region)
    for contact in mesh["contact"]:
        devsim.add_2d_contact  (mesh=device, **contact)
    devsim.finalize_mesh    (mesh=device)
    devsim.create_device    (mesh=device, device=device)

def SetDoping(device, region, device_dict):
    '''
      Doping
    '''
    node.CreateNodeModel(device, region, "Acceptors", device_dict['doping']['Acceptors'])      
    node.CreateNodeModel(device, region, "Donors",    device_dict['doping']['Donors'])
    node.CreateNodeModel(device, region, "NetDoping", "Donors-Acceptors")
    devsim.edge_from_node_model(device=device,region=region,node_model="Acceptors")
    devsim.edge_from_node_model(device=device,region=region,node_model="NetDoping")
    devsim.edge_from_node_model(device=device,region=region,node_model="Donors")

def DrawDoping(device, region, path):
    import matplotlib.pyplot
    import os
    fig1=matplotlib.pyplot.figure(num=1,figsize=(4,4))
    x=devsim.get_node_model_values(device=device, region=region, name="x")
    fields = ("Donors", "Acceptors")

    for i in fields:
        y=devsim.get_node_model_values(device=device, region=region, name=i)
        matplotlib.pyplot.semilogy(x, y)
    
    matplotlib.pyplot.xlabel('x (cm)')
    matplotlib.pyplot.ylabel('Density (#/cm^3)')
    matplotlib.pyplot.legend(fields)
    matplotlib.pyplot.savefig(os.path.join(path, "Doping"))

def main(device):
    from util.output import output
    import json
    import os
    region = device
    device_json = "./setting/detector/"+device+".json"
    with open(device_json) as f:
        device_dict = json.load(f)

    Create2DMesh(device, region, device_dict)
    SetDoping(device, region, device_dict)
    path = output(__file__, device)
    DrawDoping(device=device, region=region, path=path)
    devsim.write_devices(file=os.path.join(path,device+".dat"),type="tecplot")

if __name__ == "__main__":
    import sys
    main(sys.argv[1])