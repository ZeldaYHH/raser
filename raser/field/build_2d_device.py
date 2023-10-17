#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import numpy as np
import pickle
import ROOT
import devsim
import  physics_2d
import node_in_2d


def Create2DMesh(device,region,simname):
    if simname=="sicar1.1.6":
        devsim.create_2d_mesh  (mesh="Sicar")
        
        devsim.add_2d_mesh_line(mesh="Sicar", dir="x", pos=0     , ps=2.5e-5)
        devsim.add_2d_mesh_line(mesh="Sicar", dir="x", pos=66.3e-4  , ps=2.5e-5)

        
        devsim.add_2d_mesh_line(mesh="Sicar", dir="y", pos=0     , ps=2.5e-5)
        devsim.add_2d_mesh_line(mesh="Sicar", dir="y", pos=1e-4 , ps=2.5e-5)
        devsim.add_2d_mesh_line(mesh="Sicar", dir="x", pos=0.3e-4     , ps=1e-5)
        devsim.add_2d_mesh_line(mesh="Sicar", dir="x", pos=1.3e-4  , ps=1e-5)
        devsim.add_2d_mesh_line(mesh="Sicar", dir="x", pos=51.3e-4  , ps=1e-5)
        devsim.add_2d_mesh_line(mesh="Sicar", dir="x", pos=56.3e-4  , ps=1e-5)
        devsim.add_2d_mesh_line(mesh="Sicar", dir="x", pos=-1e-4   , ps=2.5e-5)
        devsim.add_2d_mesh_line(mesh="Sicar", dir="x", pos=67.3e-4, ps=2.5e-5)
        devsim.add_2d_region   (mesh="Sicar", material="SiliconCarbide", region=region)
        devsim.add_2d_region   (mesh="Sicar", material="air", region="air1", xl=-1e-4,  xh=0)
        devsim.add_2d_region   (mesh="Sicar", material="air", region="air2", xl=67.3e-4, xh=66.3e-4)
        devsim.add_2d_contact  (mesh="Sicar", name="top", region=region, xl=0, xh=0, bloat=1e-5, material="metal")
        devsim.add_2d_contact  (mesh="Sicar", name="bot", region=region, xl=66.3e-4,   xh=66.3e-4, bloat=1e-5, material="metal")

        devsim.finalize_mesh   (mesh="Sicar")
        devsim.create_device   (mesh="Sicar", device=device)
    elif simname=="NJUPIN":
        devsim.create_2d_mesh  (mesh="NJUPIN")
        devsim.add_2d_mesh_line(mesh="NJUPIN", dir="y", pos=0     , ps=1e-4)
        devsim.add_2d_mesh_line(mesh="NJUPIN", dir="y", pos=10e-4 , ps=1e-4)        
        devsim.add_2d_mesh_line(mesh="NJUPIN", dir="x", pos=0     , ps=1e-4)
        devsim.add_2d_mesh_line(mesh="NJUPIN", dir="x", pos=10e-4  , ps=1e-4)
        devsim.add_2d_mesh_line(mesh="NJUPIN", dir="x", pos=1e-4    , ps=1e-6)
        devsim.add_2d_mesh_line(mesh="NJUPIN", dir="x", pos=-1e-5     , ps=1e-5)
        devsim.add_2d_mesh_line(mesh="NJUPIN", dir="x", pos=10.1e-4     , ps=1e-5)
        devsim.add_2d_region   (mesh="NJUPIN", material="SiliconCarbide", region=region)
        devsim.add_2d_region   (mesh="NJUPIN", material="air", region="air1", xl=-1e-5,  xh=0)
        devsim.add_2d_region   (mesh="NJUPIN", material="air", region="air2", xl=10.1e-4, xh=10e-4)
        devsim.add_2d_contact  (mesh="NJUPIN", name="top", region=region, xl=0, xh=0, bloat=1e-5, material="metal")
        devsim.add_2d_contact  (mesh="NJUPIN", name="bot", region=region, xl=10e-4,   xh=10e-4, bloat=1e-5, material="metal")

        devsim.finalize_mesh   (mesh="NJUPIN")
        devsim.create_device   (mesh="NJUPIN", device=device)
    elif simname=="NJUPIN_defect":
        devsim.create_2d_mesh  (mesh="NJUPIN")
        devsim.add_2d_mesh_line(mesh="NJUPIN", dir="y", pos=0     , ps=1e-4)
        devsim.add_2d_mesh_line(mesh="NJUPIN", dir="y", pos=10e-4 , ps=1e-4)        
        devsim.add_2d_mesh_line(mesh="NJUPIN", dir="x", pos=0     , ps=1e-4)
        devsim.add_2d_mesh_line(mesh="NJUPIN", dir="x", pos=10e-4  , ps=1e-4)
        devsim.add_2d_mesh_line(mesh="NJUPIN", dir="x", pos=1e-4     , ps=1e-6)
        devsim.add_2d_mesh_line(mesh="NJUPIN", dir="x", pos=-1e-5     , ps=1e-5)
        devsim.add_2d_mesh_line(mesh="NJUPIN", dir="x", pos=10.1e-4     , ps=1e-5)
        devsim.add_2d_region   (mesh="NJUPIN", material="SiliconCarbide", region=region)
        devsim.add_2d_region   (mesh="NJUPIN", material="air", region="air1", xl=-1e-5,  xh=0)
        devsim.add_2d_region   (mesh="NJUPIN", material="air", region="air2", xl=10.1e-4, xh=10e-4)
        #devsim.add_2d_region   (mesh="NJUPIN", material="air", region="air3", xl=2e-6, xh=1e-6,yl=3e-4,yh=2e-4)
        devsim.add_2d_contact  (mesh="NJUPIN", name="top", region=region, xl=0, xh=0, bloat=1e-5, material="metal")
        devsim.add_2d_contact  (mesh="NJUPIN", name="bot", region=region, xl=10e-4,   xh=10e-4, bloat=1e-5, material="metal")

        devsim.finalize_mesh   (mesh="NJUPIN")
        devsim.create_device   (mesh="NJUPIN", device=device)
    elif simname=="3d_pixel":
        devsim.create_gmsh_mesh (mesh="pin", file="./output/parainprogram/pixel.msh")
        devsim.add_gmsh_region  (mesh="pin", gmsh_name="bulk",    region=region, material="SiliconCarbide")
        devsim.add_gmsh_contact (mesh="pin", gmsh_name="top",    region=region, material="metal", name="top")
        devsim.add_gmsh_contact (mesh="pin", gmsh_name="bot", region=region, material="metal", name="bot")
        devsim.finalize_mesh    (mesh="pin")
        devsim.create_device    (mesh="pin", device=device)





def SetParameters(device, region):
    '''
      Set parameters for 300 K
    '''
    physics_2d.SetSiliconParameters(device, region, 300)


def SetNetDoping(device, region,simname):
    
    if simname=="sicar1.1.6":
        node_in_2d.CreateNodeModel(device, region, "Acceptors", "2.0e19*step(3e-5-x)")
        node_in_2d.CreateNodeModel(device, region, "Donors",    "1.0e17*( step((1.3e-4)-x) -step((3e-5)-x) ) + 1.0e14*( step((51.3e-4)-x) - step((1.3e-4)-x) ) + 1.0e18*( step((56.3e-4)-x) - step((51.3e-4)-x) )+ 1.0e19*( step((66.3e-4)-x) - step((56.3e-4)-x) )")
        node_in_2d.CreateNodeModel(device, region, "NetDoping", "Donors-Acceptors")
    elif simname =="PNwithGainlayer":
        node_in_2d.CreateNodeModel(device, region, "Acceptors", "2.0e19*step(3e-5-x)")
        node_in_2d.CreateNodeModel(device, region, "Donors",    "1.0e17*( step((1.3e-4)-x) -step((3e-5)-x) ) + 1.0e14*( step((51.3e-4)-x) - step((1.3e-4)-x) ) + 1.0e18*( step((56.3e-4)-x) - step((51.3e-4)-x) )+ 1.0e19*( step((66.3e-4)-x) - step((56.3e-4)-x) )")
        node_in_2d.CreateNodeModel(device, region, "NetDoping", "Donors-Acceptors")
        devsim.edge_from_node_model(device=device,region=region,node_model="Acceptors")
        devsim.edge_from_node_model(device=device,region=region,node_model="NetDoping")
        devsim.edge_from_node_model(device=device,region=region,node_model="Donors")
    elif simname=="NJUPIN":
        node_in_2d.CreateNodeModel(device,region,"Acceptors", "1.0e18*step((1e-4)-x)")
        node_in_2d.CreateNodeModel(device,region,"Donors",    "5.2e15*step(x-(1e-4))")
        node_in_2d.CreateNodeModel(device,region,"NetDoping",  "Donors-Acceptors")
    elif simname=="NJUPIN_defect":
        node_in_2d.CreateNodeModel(device,region,"Acceptors", "1e19*step(1e-6-x)")
        node_in_2d.CreateNodeModel(device,region,"Donors",     "5.2e10*step(x-1e-6)")
        node_in_2d.CreateNodeModel(device,region,"NetDoping",  "Donors-Acceptors")
    elif simname=="3d_pixel":
        node_in_2d.CreateNodeModel(device, region, "Acceptors", "1.0e19*step(1e-8-z)")      
        node_in_2d.CreateNodeModel(device, region, "Donors",    "5.2e13*step(z-1e-8)")
        node_in_2d.CreateNodeModel(device, region, "NetDoping", "Donors-Acceptors")
    