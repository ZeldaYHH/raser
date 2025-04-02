import os
import pickle

import devsim
import numpy as np

from . import devsim_draw
from .create_parameter import create_parameter, delete_init
from util.output import create_path

def milestone_save_1D(device, region, v, path, is_tcad):
    if is_tcad:
        U = "ElectrostaticPotential"
        # TODO: replace E with (ElectricField_0**2 + ElectricField_1**2)**0.5
        E = "ElectricField_0"
        Doping = "DopingConcentration"
        PNC = "SpaceCharge"
        e = "eDensity"
        h = "hDensity"
        # TODO: add irradiation defect assisted recombination
        trap_n = "eGapStatesRecombination"
        trap_p = "hGapStatesRecombination"
        geometry_scale = 1e-4 # TCAD uses um
    else:
        U = "Potential"
        E = "ElectricField"
        Doping = "NetDoping"
        PNC = "PotentialNodeCharge"
        e = "Electrons"
        h = "Holes"
        trap_n = "TrappingRate_n"
        trap_p = "TrappingRate_p"  
        geometry_scale = 1 # Devsim uses cm

    x = geometry_scale*np.array(devsim.get_node_model_values(device=device, region=region, name="x"))
    Potential = np.array(devsim.get_node_model_values(device=device, region=region, name=U)) # get the potential dat
    NetDoping= np.array(devsim.get_node_model_values(device=device, region=region, name=Doping))
    PotentialNodeCharge = np.array(devsim.get_node_model_values(device=device, region=region, name=PNC))
    Electrons = np.array(devsim.get_node_model_values(device=device, region=region, name=e))
    Holes = np.array(devsim.get_node_model_values(device=device, region=region, name=h))
    TrappingRate_n = np.array(devsim.get_node_model_values(device=device, region=region, name=trap_n))
    TrappingRate_p = np.array(devsim.get_node_model_values(device=device, region=region, name=trap_p))

    devsim_draw.draw1D(x,Potential,"Potential","Depth[cm]","Potential[V]", v, path)
    devsim_draw.draw1D(x,TrappingRate_n,"Electron Trapping Rate","Depth[cm]","Trapping Rate[s]", v, path)
    devsim_draw.draw1D(x,TrappingRate_p,"Hole Trapping Rate","Depth[cm]","Trapping Rate[s]", v, path)

    if is_tcad:
        ElectricField = devsim.get_node_model_values(device=device, region=region, name=E)
        devsim_draw.draw1D(x,ElectricField,"Electric Field","Depth[cm]","Electric Field[V/cm]", v, path)
    else:
        devsim.edge_average_model(device=device, region=region, node_model="x", edge_model="xmid")
        x_mid = devsim.get_edge_model_values(device=device, region=region, name="xmid") # get x-node values 
        ElectricField = devsim.get_edge_model_values(device=device, region=region, name=E) # get y-node values
        devsim_draw.draw1D(x_mid,ElectricField,"Electric Field","Depth[cm]","Electric Field[V/cm]", v, path)

    metadata = {}
    metadata['voltage'] = v
    metadata['dimension'] = 1

    names = ['Potential', 'TrappingRate_p', 'TrappingRate_n']
    if v == 0 or is_tcad:
        names.append('NetDoping')

    for name in names: # scalar field on mesh point (instead of on edge)
        with open(os.path.join(path, "{}_{}V.pkl".format(name,v)),'wb') as file:
            data = {}
            data['values'] = eval(name) # refer to the object with given name
            data['points'] = x
            data['metadata'] = metadata
            pickle.dump(data, file)

def milestone_save_wf_1D(device, region, v, path, contact, is_tcad):
    save_wf_path = os.path.join(path, contact)
    create_path(save_wf_path)
    
    x = np.array(devsim.get_node_model_values(device=device, region=region, name="x")) # get x-node values
    Potential = np.array(devsim.get_node_model_values(device=device, region=region, name="Potential")) # get the potential data

    devsim.edge_average_model(device=device, region=region, node_model="x", edge_model="xmid")
    ElectricField=np.array(devsim.get_edge_model_values(device=device, region=region, name="ElectricField"))
    x_mid = np.array(devsim.get_edge_model_values(device=device, region=region, name="xmid")) 

    devsim_draw.draw1D(x,Potential,"Weighting Potential","Depth[um]","Weighting Potential", v, save_wf_path)
    devsim_draw.draw1D(x_mid,ElectricField,"Weighting Field","Depth[um]","Weighting Field[1/cm]",v, save_wf_path)

    metadata = {}
    metadata['voltage'] = v
    metadata['dimension'] = 1
    
    for name in ['Potential']: # scalar field on mesh point (instead of on edge)
        with open(os.path.join(save_wf_path, "{}_{}V.pkl".format(name,v)),'wb') as file:
            data = {}
            data['values'] = eval(name) # refer to the object with given name
            data['points'] = x
            data['metadata'] = metadata
            pickle.dump(data, file)

def milestone_save_2D(device, region, v, path, is_tcad):
    if is_tcad:
        U = "ElectrostaticPotential"
        # TODO: replace E with (ElectricField_0**2 + ElectricField_1**2)**0.5
        E = "ElectricField_0"
        Doping = "DopingConcentration"
        PNC = "SpaceCharge"
        e = "eDensity"
        h = "hDensity"
        # TODO: add irradiation defect assisted recombination
        trap_n = "eGapStatesRecombination"
        trap_p = "hGapStatesRecombination"
        geometry_scale = 1e-4 # TCAD uses um
    else:
        U = "Potential"
        E = "ElectricField"
        Doping = "NetDoping"
        PNC = "PotentialNodeCharge"
        e = "Electrons"
        h = "Holes"
        trap_n = "TrappingRate_n"
        trap_p = "TrappingRate_p"  
        geometry_scale = 1 # Devsim uses cm

    x = geometry_scale*np.array(devsim.get_node_model_values(device=device, region=region, name="x")) # get x-node values
    y = geometry_scale*np.array(devsim.get_node_model_values(device=device, region=region, name="y")) # get y-node values
    Potential = np.array(devsim.get_node_model_values(device=device, region=region, name=U)) # get the potential data
    TrappingRate_n = np.array(devsim.get_node_model_values(device=device, region=region, name=trap_n))
    TrappingRate_p = np.array(devsim.get_node_model_values(device=device, region=region, name=trap_p))
    NetDoping= np.array(devsim.get_node_model_values(device=device, region=region, name=Doping))

    devsim_draw.draw2D(x,y,Potential,"Potential",v,path)
    devsim_draw.draw2D(x,y,TrappingRate_n,"TrappingRate_n",v,path)
    devsim_draw.draw2D(x,y,TrappingRate_p,"TrappingRate_p",v,path)

    if is_tcad:
        ElectricField = np.array(devsim.get_node_model_values(device=device, region=region, name=E))
        devsim_draw.draw2D(x,y,ElectricField,"Electric Field", v,path)
    else:
        devsim.element_from_edge_model(edge_model=E,   device=device, region=region)
        devsim.edge_average_model(device=device, region=region, node_model="x", edge_model="xmid")
        devsim.edge_average_model(device=device, region=region, node_model="y", edge_model="ymid")
        x_mid = np.array(devsim.get_edge_model_values(device=device, region=region, name="xmid")) 
        y_mid = np.array(devsim.get_edge_model_values(device=device, region=region, name="ymid")) 
        ElectricField = devsim.get_edge_model_values(device=device, region=region, name=E)
        devsim_draw.draw2D(x_mid,y_mid,ElectricField,"Electric Field",v,path)

    metadata = {}
    metadata['voltage'] = v
    metadata['dimension'] = 2

    names = ['Potential', 'TrappingRate_p', 'TrappingRate_n']
    if v == 0 or is_tcad:
        names.append('NetDoping')

    for name in names: # scalar field on mesh point (instead of on edge)
        with open(os.path.join(path, "{}_{}V.pkl".format(name,v)),'wb') as file:
            data = {}
            data['values'] = eval(name) # refer to the object with given name
            merged_list = [x, y]
            transposed_list = list(map(list, zip(*merged_list)))
            data['points'] = transposed_list
            data['metadata'] = metadata
            pickle.dump(data, file)


def milestone_save_wf_2D(device, region, v, path, contact, is_tcad):
    save_wf_path = os.path.join(path,contact)
    create_path(save_wf_path)

    x = np.array(devsim.get_node_model_values(device=device, region=region, name="x")) # get x-node values
    y = np.array(devsim.get_node_model_values(device=device, region=region, name="y")) # get y-node values
    Potential = np.array(devsim.get_node_model_values(device=device, region=region, name="Potential")) # get the potential data

    devsim.element_from_edge_model(edge_model="ElectricField",   device=device, region=region)
    devsim.edge_average_model(device=device, region=region, node_model="x", edge_model="xmid")
    devsim.edge_average_model(device=device, region=region, node_model="y", edge_model="ymid")
    ElectricField=np.array(devsim.get_edge_model_values(device=device, region=region, name="ElectricField"))
    x_mid = np.array(devsim.get_edge_model_values(device=device, region=region, name="xmid")) 
    y_mid = np.array(devsim.get_edge_model_values(device=device, region=region, name="ymid")) 

    devsim_draw.draw2D(x, y, Potential, "Potential", v, save_wf_path)
    devsim_draw.draw2D(x_mid, y_mid, ElectricField, "ElectricField", v, save_wf_path)

    metadata = {}
    metadata['voltage'] = v
    metadata['dimension'] = 2

    for name in ['Potential']: # scalar field on mesh point (instead of on edge)
        with open(os.path.join(save_wf_path, "{}_{}V.pkl".format(name,v)),'wb') as file:
            data = {}
            data['values'] = eval(name) # refer to the object with given name
            merged_list = [x, y]
            transposed_list = list(map(list, zip(*merged_list)))
            data['points'] = transposed_list
            data['metadata'] = metadata
            pickle.dump(data, file)

def milestone_save_3D(device, region, v, path, is_tcad):
    # not finished
    pass

def milestone_save_wf_3D(device, region, v, path, contact, is_tcad):
    # not finished
    pass

def save_milestone(device, region, v, path, dimension, contact, is_wf, is_tcad = False):
    if dimension ==1 :
        if is_wf == True:
            milestone_save_wf_1D(device, region, v, path, contact, is_tcad)
        elif is_wf == False:
            milestone_save_1D(device, region, v, path, is_tcad)
        else:
            print("==========RASER info ==========\nis_wf only has 2 values, True or False\n==========Error=========")
    if dimension == 2:
        if is_wf == True:
            milestone_save_wf_2D(device, region, v, path, contact, is_tcad)
        elif is_wf == False:
            milestone_save_2D(device, region, v, path, is_tcad)
        else:
            print("==========RASER info ==========\nis_wf only has 2 values, True or False\n==========Error=========")
    if dimension == 3:
        if is_wf == True:
            milestone_save_wf_3D(device, region, v, path, contact, is_tcad)
        elif is_wf == False:
            milestone_save_3D(device, region, v, path, is_tcad)
        else:
            print("==========RASER info ==========\nis_wf only has 2 values, True or False\n==========Error=========")

