#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

'''
Description:  physics_avalanche.py
@Date       : 2022/10/25 16:40:46
@Author     : Tao Yang
@version    : 1.0
'''

import devsim
from .model_create import *
import math

def CreateImpactGeneration(device, region, custom_ion_n='', custom_ion_p=''):

    # if not InEdgeModelList(device, region, "ElectricField"):
    #     CreateEdgeModel(device, region, "ElectricField", "(Potential@n0-Potential@n1)*EdgeInverseLength")
    #     CreateEdgeModelDerivatives(device, region, "ElectricField", "(Potential@n0-Potential@n1)*EdgeInverseLength", "Potential")

    material = devsim.get_material(device=device, region=region)
    if material == 'Silicon':
        Ion_coeff_n, Ion_coeff_p = CreateImpactModel_vanOvenstraeten(device, region)
    elif material == 'SiliconCarbide':
        Ion_coeff_n, Ion_coeff_p = CreateImpactModel_Hatakeyama(device, region)
    else:
        Ion_coeff_n, Ion_coeff_p = custom_ion_n, custom_ion_p

    if Ion_coeff_n == '' or Ion_coeff_p =='':
        raise ValueError(Ion_coeff_n, Ion_coeff_p)

    #Ion_coeff_n  = "gamma * n_a * exp( - gamma * n_b / (ElectricField))"
    #Ion_coeff_p  = "gamma * p_a * exp( - gamma * p_b / (ElectricField))"
    Ion_coeff_rate = "(Ion_coeff_n*(abs(ElectronCurrent))+Ion_coeff_p*(abs(HoleCurrent)))/q"

    CreateEdgeModel(device, region, "Ion_coeff_n", Ion_coeff_n)
    CreateEdgeModelDerivatives(device, region, "Ion_coeff_n", Ion_coeff_n, "Potential")
    #CreateEdgeModelDerivatives(device, region, "Ion_coeff_n", Ion_coeff_n, "Electrons")
    #CreateEdgeModelDerivatives(device, region, "Ion_coeff_n", Ion_coeff_n, "Holes")
    CreateEdgeModel(device, region, "Ion_coeff_p", Ion_coeff_p)
    CreateEdgeModelDerivatives(device, region, "Ion_coeff_p", Ion_coeff_p, "Potential")
    #CreateEdgeModelDerivatives(device, region, "Ion_coeff_p", Ion_coeff_p, "Electrons")
    #CreateEdgeModelDerivatives(device, region, "Ion_coeff_p", Ion_coeff_p, "Holes")
    #CreateEdgeModel(device, region, "Ion_coeff_rate", Ion_coeff_rate)
    #CreateEdgeModelDerivatives(device, region, "Ion_coeff_rate", Ion_coeff_rate, "Potential")
    
    
    ImpactGen_n = "+q*%s"%(Ion_coeff_rate)
    ImpactGen_p = "-q*%s"%(Ion_coeff_rate)

    CreateEdgeModel(device, region, "ImpactGen_n", ImpactGen_n)
    CreateEdgeModelDerivatives(device, region, "ImpactGen_n", ImpactGen_n, "Potential")
    CreateEdgeModelDerivatives(device, region, "ImpactGen_n", ImpactGen_n, "Electrons")
    CreateEdgeModelDerivatives(device, region, "ImpactGen_n", ImpactGen_n, "Holes")
    
    CreateEdgeModel(device, region, "ImpactGen_p", ImpactGen_p)
    CreateEdgeModelDerivatives(device, region, "ImpactGen_p", ImpactGen_p, "Potential")
    CreateEdgeModelDerivatives(device, region, "ImpactGen_p", ImpactGen_p, "Electrons")
    CreateEdgeModelDerivatives(device, region, "ImpactGen_p", ImpactGen_p, "Holes")
    #devsim.edge_model(device=device,region=region,name="ImpactGen_p:Potential",equation="-ImpactGen_n:Potential")

def CreateImpactModel_vanOvenstraeten(device, region):
    """
    van Ovenstraeten Model
    """

    Ion_coeff_n  = "ifelse(abs(ElectricField)>1.75e4, (ifelse(abs(ElectricField)>4e5, gamma * n_a_high * exp( - gamma * n_b_high / (abs(ElectricField)+1)),  gamma * n_a_low * exp( - gamma * n_b_low / (abs(ElectricField)+1)))), 1)"
    Ion_coeff_p  = "ifelse(abs(ElectricField)>1.75e4, (ifelse(abs(ElectricField)>4e5, gamma * p_a_high * exp( - gamma * p_b_high / (abs(ElectricField)+1)),  gamma * p_a_low * exp( - gamma * p_b_low / (abs(ElectricField)+1)))), 1)"

    return Ion_coeff_n, Ion_coeff_p

def CreateImpactModel_Hatakeyama(device, region, cutoff_angle = 4):
    """
    Hatakeyama Model for cutoff angle of 4°
    """

    #hbarOmega = 0.19 # eV
    #k_T0_ev = 0.0257 # eV
    # gamma = math.tanh(0.19/(2*0.0257))/math.tanh(0.19/(2*0.0257*T/T0))
    
    # if not InEdgeModelList(device, region, "ElectricField"):
    #     CreateEdgeModel(device, region, "ElectricField", "(Potential@n0-Potential@n1)*EdgeInverseLength")
    #     CreateEdgeModelDerivatives(device, region, "ElectricField", "(Potential@n0-Potential@n1)*EdgeInverseLength", "Potential")

    sin_cutoff_angle = math.sin(math.radians(cutoff_angle))
    cos_cutoff_angle = math.cos(math.radians(cutoff_angle))

    if not InEdgeModelList(device, region, "ElectricField_0001"):
        CreateEdgeModel(device, region, "ElectricField_0001", "abs(ElectricField+1)*{0}".format(cos_cutoff_angle))

    if not InEdgeModelList(device, region, "ElectricField_1120"):
        CreateEdgeModel(device, region, "ElectricField_1120", "abs(ElectricField+1)*{0}".format(sin_cutoff_angle))

    if not InEdgeModelList(device, region, "n_B"):
        CreateEdgeModel(device, region, "n_B", "abs(ElectricField+1) / pow( pow( ElectricField_1120/n_b_1120 , 2) + pow( ElectricField_0001/n_b_0001 , 2) , 0.5)")

    if not InEdgeModelList(device, region, "p_B"):
        CreateEdgeModel(device, region, "p_B", "abs(ElectricField+1) / pow( pow( ElectricField_1120/p_b_1120 , 2) + pow( ElectricField_0001/p_b_0001 , 2) , 0.5)")


    if not InEdgeModelList(device, region, "n_a_aniso"):
        CreateEdgeModel(device, region, "n_a_aniso", "pow( n_a_1120, pow( n_B*ElectricField_1120/n_b_1120/abs(ElectricField+1), 2) ) * pow( n_a_0001, pow( n_B*ElectricField_0001/n_b_0001/abs(ElectricField+1), 2) )")

    if not InEdgeModelList(device, region, "p_a_aniso"):
        CreateEdgeModel(device, region, "p_a_aniso", "pow( p_a_1120, pow( p_B*ElectricField_1120/p_b_1120/abs(ElectricField+1), 2) ) * pow( p_a_0001, pow( p_B*ElectricField_0001/p_b_0001/abs(ElectricField+1), 2) )")



    if not InEdgeModelList(device, region, "n_A"):
        CreateEdgeModel(device, region, "n_A", "log(n_a_0001/n_b_1120)")

    if not InEdgeModelList(device, region, "p_A"):
        CreateEdgeModel(device, region, "p_A", "log(p_a_0001/p_b_1120)")

    if not InEdgeModelList(device, region, "n_b_aniso"):
        CreateEdgeModel(device, region, "n_b_aniso", "n_B * pow( 1-pow(n_A,2)* pow( (n_B*ElectricField_1120*ElectricField_0001)/(abs(ElectricField+1)*n_b_1120*n_b_0001), 2), 0.5)")

    if not InEdgeModelList(device, region, "p_b_aniso"):
        CreateEdgeModel(device, region, "p_b_aniso", "p_B * pow( 1-pow(p_A,2)* pow( (p_B*ElectricField_1120*ElectricField_0001)/(abs(ElectricField+1)*p_b_1120*p_b_0001), 2), 0.5)")

    gamma_str = "tanh(0.19/(2*0.0257))/tanh(0.19/(2*0.0257*T/T0))"
    Ion_coeff_n  = "ifelse(abs(ElectricField)>1e4, {0} * n_a_aniso * exp( - {1} * n_b_aniso / (abs(ElectricField)+1)), 1)".format(gamma_str,gamma_str)
    Ion_coeff_p  = "ifelse(abs(ElectricField)>1e4, {0} * p_a_aniso * exp( - {1} * p_b_aniso / (abs(ElectricField)+1)), 1)".format(gamma_str,gamma_str)

    return Ion_coeff_n, Ion_coeff_p
