#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

'''
Description:  physics_tunnel.py
@Date       : 2023/03
@Author     : Zaiyi Li
@version    : 1.0
'''

import devsim
from .model_create import *

def CreateTunnel(device, region, label="Zaiyi", custom_tunnel = {}):

    if label == 'Zaiyi':
        tunnel = CreateTunnelModel_Zaiyi(device, region)
    else:
        tunnel = custom_tunnel

    if tunnel == {}:
        raise KeyError(tunnel)

def CreateTunnelModel_Zaiyi(device, region):
    R_improved="3.11*abs(ElectricField)^2.5*exp(abs(ElectricField)/3e4)"
    CreateEdgeModel(device,region,"R_improved",R_improved)
    CreateEdgeModelDerivatives(device,region,"R_improved",R_improved,"Potential")
    R_BTBT="1e21*abs(ElectricField)^2.5*exp(-0.8e7/(1+abs(ElectricField)))"
    CreateEdgeModel(device,region,"R_BTBT",R_BTBT)
    CreateEdgeModelDerivatives(device,region,"R_BTBT",R_BTBT,"Potential")
    devsim.edge_from_node_model(device=device,region=region,node_model="USRH")
    R_TAT="2*(3*3.14159)^0.5*abs(ElectricField)/3.9e4*exp((abs(ElectricField)/3.9e4)^2)*USRH@n1"
    CreateEdgeModel(device,region,"R_TAT",R_TAT)
    CreateEdgeModelDerivatives(device,region,"R_TAT",R_TAT,"Potential")
    CreateEdgeModelDerivatives(device,region,"R_TAT",R_TAT,"Electrons")
    CreateEdgeModelDerivatives(device,region,"R_TAT",R_TAT,"Holes")

    #TODO: Impact + Tunnel == edge_volume