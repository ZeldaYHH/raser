#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import numpy as np
import pickle
import ROOT
import devsim
import  physics2D
#####
# dio1
#
# Make doping a step function
# print dat to text file for viewing in grace
# verify currents analytically
# in dio2 add recombination
# TODO: use CreateMesh and update regressions

def Create2DMesh(device, region):
    devsim.create_2d_mesh  (mesh="dog")
    devsim.add_2d_mesh_line (mesh="dog", dir="x",pos=0, ps=1e-4)
    devsim.add_2d_mesh_line (mesh="dog", dir="x",pos=(1e-4)-(0.5e-4), ps=1e-5)
    devsim.add_2d_mesh_line (mesh="dog", dir="x",pos=1e-4, ps=1e-5)
    devsim.add_2d_mesh_line (mesh="dog", dir="x",pos=(1e-4)+(3e-4), ps=1e-5)
    devsim.add_2d_mesh_line (mesh="dog", dir="x",pos=100*1e-4, ps=1e-4)
    devsim.add_2d_mesh_line(mesh="dog", dir="y", pos=0     , ps=1e-4)
    devsim.add_2d_mesh_line(mesh="dog", dir="y", pos=1e-2  , ps=1e-4)
    devsim.add_2d_mesh_line(mesh="dog", dir="x", pos=-1e-5   , ps=1e-4)
    devsim.add_2d_mesh_line(mesh="dog", dir="x", pos=1.001e-2, ps=1e-4)

    devsim.add_2d_region   (mesh="dog", material="SiC", region=region)
    devsim.add_2d_region   (mesh="dog", material="air", region="air1", xl=-1e-5,  xh=0)
    devsim.add_2d_region   (mesh="dog", material="air", region="air2", xl=1.0e-2, xh=1.01e-2)

    devsim.add_2d_contact  (mesh="dog", name="top", region=region,  xl=0, xh=0, bloat=1e-5, material="metal")
    devsim.add_2d_contact  (mesh="dog", name="bot", region=region, xl=1e-2,   xh=1e-2, bloat=1e-8, material="metal")

    devsim.finalize_mesh   (mesh="dog")
    devsim.create_device   (mesh="dog", device=device)





def SetParameters(device, region):
    '''
      Set parameters for 300 K
    '''
    physics2D.SetSiliconParameters(device, region, 300)


def SetNetDoping(device, region,type1):
    
    if type1=="PNjuction":
        physics2D.CreateNodeModel(device, region, "Acceptors", "1.0e19*step(0.3e-4-x)")
        physics2D.CreateNodeModel(device, region, "Donors",    "7.96e13*( step((1.3e-4)-x) -step((3e-5)-x) ) + 5.6e12*( step((1e-2)-x) - step((1.3e-4)-x) ) ")
        physics2D.CreateNodeModel(device, region, "NetDoping", "Donors-Acceptors")
        devsim.edge_from_node_model(device=device,region=region,node_model="Acceptors")
        devsim.edge_from_node_model(device=device,region=region,node_model="NetDoping")
        devsim.edge_from_node_model(device=device,region=region,node_model="Donors")
    elif type1 =="PNwithGainlayer":
        physics2D.CreateNodeModel(device, region, "Acceptors", "2.0e19*step(3e-5-x)")
        physics2D.CreateNodeModel(device, region, "Donors",    "1.0e17*( step((1.3e-4)-x) -step((3e-5)-x) ) + 1.0e14*( step((51.3e-4)-x) - step((1.3e-4)-x) ) + 1.0e18*( step((56.3e-4)-x) - step((51.3e-4)-x) )+ 1.0e19*( step((66.3e-4)-x) - step((56.3e-4)-x) )")
        physics2D.CreateNodeModel(device, region, "NetDoping", "Donors-Acceptors")
        devsim.edge_from_node_model(device=device,region=region,node_model="Acceptors")
        devsim.edge_from_node_model(device=device,region=region,node_model="NetDoping")
        devsim.edge_from_node_model(device=device,region=region,node_model="Donors")
       
    
def InitialSolution(device, region, circuit_contacts=None):
    # Create Potential, Potential@n0, Potential@n1
    physics2D.CreateSolution(device, region, "Potential")

    # Create potential only physical models
    physics2D.CreateSiliconPotentialOnly(device, region)


    # Set up the contacts applying a bias
    for i in devsim.get_contact_list(device=device):
        if circuit_contacts and i in circuit_contacts:
            physics2D.CreateSiliconPotentialOnlyContact(device, region, i, True)
        else:
            ###print "FIX THIS"
            ### it is more correct for the bias to be 0, and it looks like there is side effects
            devsim.set_parameter(device=device, name=physics2D.GetContactBiasName(i), value=0.0)
            physics2D.CreateSiliconPotentialOnlyContact(device, region, i)


def DriftDiffusionInitialSolution(device, region, circuit_contacts=None):
    ####
    #### drift diffusion solution variables
    ####
    physics2D.CreateSolution(device, region, "Electrons")
    physics2D.CreateSolution(device, region, "Holes")

    ####
    #### create initial guess from dc only solution
    ####
    devsim.set_node_values(device=device, region=region, name="Electrons", init_from="IntrinsicElectrons")
    devsim.set_node_values(device=device, region=region, name="Holes",     init_from="IntrinsicHoles")

    ###
    ### Set up equations
    ###
    physics2D.CreateSiliconDriftDiffusion(device, region)
    for i in devsim.get_contact_list(device=device):
        if circuit_contacts and i in circuit_contacts:
            physics2D.CreateSiliconDriftDiffusionAtContact(device, region, i, True)
        else:
            physics2D.CreateSiliconDriftDiffusionAtContact(device, region, i)


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