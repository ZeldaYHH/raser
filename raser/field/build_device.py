#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import devsim
from . import model_create

from util.output import output
import json
import os

import matplotlib.pyplot

class Detector:
    """
    Description:
    ---------
        Different types detectors parameters assignment.
    Parameters:
    ---------
    device_name : string
        name the device and define the device by device.json 
    dimension : int
        the dimension of devsim mesh
    Modify:
    ---------
        2023/12/03
    """ 
    def __init__(self, device_name):
        self.device = device_name
        self.region = device_name
        device_json = "./setting/detector/" + device_name + ".json"
        with open(device_json) as f:
            self.device_dict = json.load(f)

        self.dimension = self.device_dict['default_dimension']
        if self.dimension == 1:
            self.create1DMesh()
        elif self.dimension == 2:
            self.create2DMesh()
        elif self.dimension == 3:
            self.createGmshMesh()
        else:
            raise ValueError(self.dimension)

        self.setDoping()

        path = output(__file__, device_name)
        self.drawDoping(path)
        devsim.write_devices(file=os.path.join(path, device_name+".dat"),type="tecplot")

    def create1DMesh(self):
        mesh_name = self.device
        devsim.create_1d_mesh(mesh=mesh_name)
        mesh = self.device_dict["mesh"]["1D_mesh"]
        for mesh_line in mesh["mesh_line"]:
            devsim.add_1d_mesh_line(mesh=mesh_name, **mesh_line)
        for region in mesh["region"]:
            devsim.add_1d_region   (mesh=mesh_name, **region)
        for contact in mesh["contact"]:
            devsim.add_1d_contact  (mesh=mesh_name, **contact)
        devsim.finalize_mesh(mesh=mesh_name)
        devsim.create_device(mesh=mesh_name, device=mesh_name)

    def create2DMesh(self):
        mesh_name = self.device
        devsim.create_2d_mesh(mesh=mesh_name)
        mesh = self.device_dict["mesh"]["2D_mesh"]
        for mesh_line in mesh["mesh_line"]:
            devsim.add_2d_mesh_line(mesh=mesh_name, **mesh_line)
        for region in mesh["region"]:
            # Must define material regions before air regions when material borders not clarified!
            devsim.add_2d_region   (mesh=mesh_name, **region)
        for contact in mesh["contact"]:
            devsim.add_2d_contact  (mesh=mesh_name, **contact)
        devsim.finalize_mesh(mesh=mesh_name)
        devsim.create_device(mesh=mesh_name, device=mesh_name)

    def createGmshMesh(self):
        mesh_name = self.device
        devsim.create_gmsh_mesh (mesh=mesh_name, file=mesh['file'])
        mesh = self.device_dict["mesh"]["gmsh_mesh"]
        for region in mesh["region"]:
            devsim.add_gmsh_region   (mesh=mesh_name, **region)
        for contact in mesh["contact"]:
            devsim.add_gmsh_contact  (mesh=mesh_name, **contact)
        devsim.finalize_mesh(mesh=mesh_name)
        devsim.create_device(mesh=mesh_name, device=mesh_name)

    def setDoping(self):
        '''
        Doping
        '''
        model_create.CreateNodeModel(self.device, self.region, "Acceptors", self.device_dict['doping']['Acceptors'])      
        model_create.CreateNodeModel(self.device, self.region, "Donors",    self.device_dict['doping']['Donors'])
        model_create.CreateNodeModel(self.device, self.region, "NetDoping", "Donors-Acceptors")
        devsim.edge_from_node_model(device=self.device, region=self.region, node_model="Acceptors")
        devsim.edge_from_node_model(device=self.device, region=self.region, node_model="NetDoping")
        devsim.edge_from_node_model(device=self.device, region=self.region, node_model="Donors")

    def drawDoping(self, path):
        fig1=matplotlib.pyplot.figure(num=1,figsize=(4,4))
        x=devsim.get_node_model_values(device=self.device, region=self.region, name="x")
        fields = ("Donors", "Acceptors")

        for i in fields:
            y=devsim.get_node_model_values(device=self.device, region=self.region, name=i)
            matplotlib.pyplot.semilogy(x, y)
        
        matplotlib.pyplot.xlabel('x (cm)')
        matplotlib.pyplot.ylabel('Density (#/cm^3)')
        matplotlib.pyplot.legend(fields)
        matplotlib.pyplot.savefig(os.path.join(path, "Doping"))


if __name__ == "__main__":
    import sys
    Detector(sys.argv[1])