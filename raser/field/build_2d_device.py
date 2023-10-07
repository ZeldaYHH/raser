#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import numpy as np
import pickle
import ROOT
import devsim
import  physics_2d
import node_in_2d


def Create2DMesh(device,region):
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






def SetParameters(device, region):
    '''
      Set parameters for 300 K
    '''
    physics_2d.SetSiliconParameters(device, region, 300)


def SetNetDoping(device, region,type1):
    
    if type1=="PNjuction":
        node_in_2d.CreateNodeModel(device, region, "Acceptors", "2.0e19*step(3e-5-x)")
        #node_in_2d.CreateNodeModel(device, region, "Donors",    "1.0e17*( step((1.3e-4)-x) -step(x-(3e-5)) ) ")
        #node_in_2d.CreateNodeModel(device, region, "Donors",    "1.0e14*( step((51.3e-4)-x) - step(x-(1.3e-4)) )   ")
        node_in_2d.CreateNodeModel(device, region, "Donors",    "1.0e17*( step((1.3e-4)-x) -step((3e-5)-x) ) + 1.0e14*( step((51.3e-4)-x) - step((1.3e-4)-x) ) + 1.0e18*( step((56.3e-4)-x) - step((51.3e-4)-x) )+ 1.0e19*( step((66.3e-4)-x) - step((56.3e-4)-x) )")
        node_in_2d.CreateNodeModel(device, region, "NetDoping", "Donors-Acceptors")
        #devsim.edge_from_node_model(device=device,region=region,node_model="Acceptors")
        #devsim.edge_from_node_model(device=device,region=region,node_model="NetDoping")
        #devsim.edge_from_node_model(device=device,region=region,node_model="Donors")
    elif type1 =="PNwithGainlayer":
        node_in_2d.CreateNodeModel(device, region, "Acceptors", "2.0e19*step(3e-5-x)")
        node_in_2d.CreateNodeModel(device, region, "Donors",    "1.0e17*( step((1.3e-4)-x) -step((3e-5)-x) ) + 1.0e14*( step((51.3e-4)-x) - step((1.3e-4)-x) ) + 1.0e18*( step((56.3e-4)-x) - step((51.3e-4)-x) )+ 1.0e19*( step((66.3e-4)-x) - step((56.3e-4)-x) )")
        node_in_2d.CreateNodeModel(device, region, "NetDoping", "Donors-Acceptors")
        devsim.edge_from_node_model(device=device,region=region,node_model="Acceptors")
        devsim.edge_from_node_model(device=device,region=region,node_model="NetDoping")
        devsim.edge_from_node_model(device=device,region=region,node_model="Donors")
       
    
def InitialSolution(device, region, circuit_contacts=None):
    # Create Potential, Potential@n0, Potential@n1
    node_in_2d.CreateSolution(device, region, "Potential")

    # Create potential only physical models
    physics_2d.CreateSiliconPotentialOnly(device, region)


    # Set up the contacts applying a bias
    for i in devsim.get_contact_list(device=device):
        if circuit_contacts and i in circuit_contacts:
            physics_2d.CreateSiliconPotentialOnlyContact(device, region, i, True)
        else:
            ###print "FIX THIS"
            ### it is more correct for the bias to be 0, and it looks like there is side effects
            devsim.set_parameter(device=device, name=physics_2d.GetContactBiasName(i), value=0.0)
            physics_2d.CreateSiliconPotentialOnlyContact(device, region, i)


def DriftDiffusionInitialSolution(device, region, circuit_contacts=None):
    ####
    #### drift diffusion solution variables
    ####
    node_in_2d.CreateSolution(device, region, "Electrons")
    node_in_2d.CreateSolution(device, region, "Holes")

    ####
    #### create initial guess from dc only solution
    ####
    devsim.set_node_values(device=device, region=region, name="Electrons", init_from="IntrinsicElectrons")
    devsim.set_node_values(device=device, region=region, name="Holes",     init_from="IntrinsicHoles")

    ###
    ### Set up equations
    ###
    physics_2d.CreateSiliconDriftDiffusion(device, region)
    for i in devsim.get_contact_list(device=device):
        if circuit_contacts and i in circuit_contacts:
            physics_2d.CreateSiliconDriftDiffusionAtContact(device, region, i, True)
        else:
            physics_2d.CreateSiliconDriftDiffusionAtContact(device, region, i)


def save_values(device, region):
    Holes_values = devsim.get_node_model_values(device=device, region=region, name="Holes")
    Electrons_values = devsim.get_node_model_values(device=device, region=region, name="Electrons")
    Potential_values = devsim.get_node_model_values(device=device, region=region, name="Potential")
    with open('./output/parainprogram/Holes.pkl', 'wb') as file:
        file.truncate(0)
    with open('./output/parainprogram/Holes.pkl', 'wb') as file:
        pickle.dump(Holes_values, file)
    with open('./output/parainprogram/Electrons.pkl', 'wb') as file:
        file.truncate(0)
    with open('./output/parainprogram/Electrons.pkl', 'wb') as file:
        pickle.dump(Electrons_values, file)
    with open('./output/parainprogram/Potential.pkl', 'wb') as file:
        file.truncate(0)
    with open('./output/parainprogram/Potential.pkl', 'wb') as file:
        pickle.dump(Potential_values, file)

def load_values(values):
    if values=="Holes":
        with open('./output/parainprogram/Holes.pkl', 'rb') as file:
            return pickle.load(file)
    elif values=="Electrons":
        with open('./output/parainprogram/Electrons.pkl', 'rb') as file:
            return pickle.load(file)
    elif values=="Potential":
        with open('./output/parainprogram/Potential.pkl', 'rb') as file:
            return pickle.load(file)
    
def set_values(device, region):
    for i in ("Holes","Electrons","Potential"):
        devsim.set_node_values(device=device, region=region,name=i,values=load_values(i))