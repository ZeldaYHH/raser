#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import numpy as np
import pickle
import ROOT
import devsim
from .model_create import *
from .physics_drift_diffusion import *

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