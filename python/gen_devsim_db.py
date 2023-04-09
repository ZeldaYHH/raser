#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
import devsim
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from array import array

if not (os.path.exists("./output/devsim")):
    os.makedirs("./output/devsim")


def CreateDataBase(filename):
    devsim.create_db(filename=filename)
    print("The SICAR database is created.")



def CreateGlobalConstant():
    # define global constant
    q = 1.60217646e-19 # coul
    k = 1.3806503e-23  # J/K
    eps_0 = 8.85e-14   # F/cm^2
    T0 = 300.0         # K
    devsim.add_db_entry(material="global",   parameter="q",       value=q,          unit="coul",     description="Unit Charge")
    devsim.add_db_entry(material="global",   parameter="k",       value=k,          unit="J/K",      description="Boltzmann Constant")
    devsim.add_db_entry(material="global",   parameter="eps_0",   value=eps_0,      unit="F/cm^2",   description="Absolute Dielectric Constant")
    devsim.add_db_entry(material="global",   parameter="T0",      value=T0,         unit="K",        description="T0")
    devsim.add_db_entry(material="global",   parameter="k_T0",    value=k*T0,       unit="J",        description="k*T0")
    devsim.add_db_entry(material="global",   parameter="V_T0",    value=k*T0/q,     unit="J/coul",   description="k*T0/q")

    T = 300.0         # K
    devsim.add_db_entry(material="global",   parameter="T",    value=T,     unit="K",   description="T")



def CreateSiliconCarbideConstant():
    # define SiliconCarbide parameters
    # material
    devsim.add_db_entry(material="SiliconCarbide",   parameter="eps",    value=9.76,      unit="1",         description="Dielectric Constant")
    devsim.add_db_entry(material="SiliconCarbide",   parameter="n_i",    value=3.89e-9,   unit="/cm^3",     description="Intrinsic Electron Concentration")
    # mobility
    devsim.add_db_entry(material="SiliconCarbide",   parameter="mu_n",   value=1100,      unit="cm^2/Vs",   description="Constant Mobility of Electron")
    devsim.add_db_entry(material="SiliconCarbide",   parameter="mu_p",   value=114,       unit="cm^2/Vs",   description="Constant Mobility of Hole")
    # SRH
    devsim.add_db_entry(material="SiliconCarbide",   parameter="n1",     value=3.89e-9,   unit="/cm^3",     description="n1")
    devsim.add_db_entry(material="SiliconCarbide",   parameter="p1",     value=3.89e-9,   unit="/cm^3",     description="p1")
    devsim.add_db_entry(material="SiliconCarbide",   parameter="tau_n",  value=2.5e-6,    unit="s",         description="Constant SRH Lifetime of Electron")
    devsim.add_db_entry(material="SiliconCarbide",   parameter="tau_p",  value=0.5e-6,    unit="s",         description="Constant SRH Lifetime of Hole")


def CreateSiliconConstant():
    # define SiliconCarbide parameters
    # material
    devsim.add_db_entry(material="Silicon",   parameter="eps",    value=11.9,      unit="1",         description="Dielectric Constant")
    devsim.add_db_entry(material="Silicon",   parameter="n_i",    value=1.02e10,   unit="/cm^3",     description="Intrinsic Electron Concentration")
    # mobility
    devsim.add_db_entry(material="Silicon",   parameter="mu_n",   value=1450,      unit="cm^2/Vs",   description="Constant Mobility of Electron")
    devsim.add_db_entry(material="Silicon",   parameter="mu_p",   value=500,       unit="cm^2/Vs",   description="Constant Mobility of Hole")
    # SRH
    devsim.add_db_entry(material="Silicon",   parameter="n1",     value=1.02e10,   unit="/cm^3",     description="n1")
    devsim.add_db_entry(material="Silicon",   parameter="p1",     value=1.02e10,   unit="/cm^3",     description="p1")
    devsim.add_db_entry(material="Silicon",   parameter="tau_n",  value=5e-6,    unit="s",         description="Constant SRH Lifetime of Electron")
    devsim.add_db_entry(material="Silicon",   parameter="tau_p",  value=5e-6,    unit="s",         description="Constant SRH Lifetime of Hole")


'''
Doping & ElectricFiled Dependence Mobility of SiliconCarbide
Ref DOI: 
'''
# mu_n   = 1100
# mu_p   = 114
# NetDoping = 5.2e13
# 
# n_alpha = 0.34
# n_ulp = 124.0 * math.pow(T / 300.0, -2.0)
# n_uminp = 15.9
# n_Crefp = 1.76e19
# n_betap = 1.213 * math.pow(T / 300.0, 0.17)
# n_vsatp = 2e7 * math.pow(T / 300.0, 0.52)
# n_lfm = n_uminp + n_ulp/(1.0 + math.pow(NetDoping / n_Crefp, n_alpha))
# n_hfm = n_lfm / (math.pow(1.0 + math.pow(n_lfm * E / n_vsatp, n_betap), 1.0 / n_betap))
# p_alpha = 0.61
# p_ulp = 947.0 * math.pow(T / 300.0, -2)
# p_Crefp = 1.94e19
# p_betap = 1.0 * math.pow(T / 300.0, 0.66)
# p_vsatp = 2e7 * math.pow(T / 300.0, 0.87)
# p_lfm = p_ulp/ (1.0 + math.pow(NetDoping / p_Crefp, p_alpha))
# p_hfm = p_lfm / (math.pow(1.0 + math.pow(p_lfm * E / p_vsatp, p_betap), 1.0/p_betap))


def CreateHatakeyamaImpact():
    '''
    The Hatakeyama avalanche model describes the anisotropic behavior in 4H-SiC power devices. The impact ionization coefficient is obtainedaccording to the Chynoweth law.
    Ref DOI: https://onlinelibrary.wiley.com/doi/abs/10.1002/pssa.200925213
    '''
    T = 300 #K

    hbarOmega = 0.19 # eV
    _theta =1 # 1
    T0 = 300.0 # K
    k_T0_ev = 0.0257 # eV
    
    n_a_0001 = 1.76e8 # cm-1
    n_a_1120 = 2.10e7 # cm-1
    n_b_0001 = 3.30e7 # V/cm 
    n_b_1120 = 1.70e7 # V/cm

    p_a_0001 = 3.41e8 # cm-1
    p_a_1120 = 2.96e7 # cm-1
    p_b_0001 = 2.50e7 # V/cm 
    p_b_1120 = 1.60e7 # V/cm 

    #gamma = math.tanh(hbarOmega/(2*k_T0_ev))/math.tanh(hbarOmega/(2*k_T0_ev*T/T0))
    gamma = 1

    # only consider the <0001> direction multiplication, no anisotropy now!
    n_a = n_a_0001
    n_b = n_b_0001
    p_a = p_a_0001
    p_b = p_b_0001

    devsim.add_db_entry(material="SiliconCarbide",   parameter="gamma",  value=gamma,   unit="1",     description="gamma for Hatakeyama Avalanche Model")
    #devsim.add_db_entry(material="SiliconCarbide",   parameter="n_a",  value=n_a,   unit="cm-1",     description="n_a for Hatakeyama Avalanche Model")
    #devsim.add_db_entry(material="SiliconCarbide",   parameter="n_b",  value=n_b,   unit="V/cm",     description="n_b for Hatakeyama Avalanche Model")
    #devsim.add_db_entry(material="SiliconCarbide",   parameter="p_a",  value=p_a,   unit="cm-1",     description="p_a for Hatakeyama Avalanche Model")
    #devsim.add_db_entry(material="SiliconCarbide",   parameter="p_b",  value=p_b,   unit="V/cm",     description="p_b for Hatakeyama Avalanche Model")
    devsim.add_db_entry(material="SiliconCarbide",   parameter="cutoff_angle",  value=4,   unit="degree",     description="cutoff_angle for Hatakeyama Avalanche Model")
    devsim.add_db_entry(material="SiliconCarbide",   parameter="n_a_0001",  value=n_a_0001,   unit="cm-1",     description="n_a for Hatakeyama Avalanche Model")
    devsim.add_db_entry(material="SiliconCarbide",   parameter="n_b_0001",  value=n_b_0001,   unit="V/cm",     description="n_b for Hatakeyama Avalanche Model")
    devsim.add_db_entry(material="SiliconCarbide",   parameter="p_a_0001",  value=p_a_0001,   unit="cm-1",     description="p_a for Hatakeyama Avalanche Model")
    devsim.add_db_entry(material="SiliconCarbide",   parameter="p_b_0001",  value=p_b_0001,   unit="V/cm",     description="p_b for Hatakeyama Avalanche Model")

    devsim.add_db_entry(material="SiliconCarbide",   parameter="n_a_1120",  value=n_a_1120,   unit="cm-1",     description="n_a for Hatakeyama Avalanche Model")
    devsim.add_db_entry(material="SiliconCarbide",   parameter="n_b_1120",  value=n_b_1120,   unit="V/cm",     description="n_b for Hatakeyama Avalanche Model")
    devsim.add_db_entry(material="SiliconCarbide",   parameter="p_a_1120",  value=p_a_1120,   unit="cm-1",     description="p_a for Hatakeyama Avalanche Model")
    devsim.add_db_entry(material="SiliconCarbide",   parameter="p_b_1120",  value=p_b_1120,   unit="V/cm",     description="p_b for Hatakeyama Avalanche Model")


    def cal_impact_coefficient(electric_field):
        n_coeff = gamma*n_a*math.exp(-(gamma*n_b/electric_field))
        p_coeff = gamma*p_a*math.exp(-(gamma*p_b/electric_field))
        return n_coeff,p_coeff


    high_field = 1e7 # V/cm
    field_step = high_field/1000.0

    x_field = array( 'd' )
    x_inversefield = array( 'd' )

    y_sic_electron_multi_coeff = array( 'd' )
    y_sic_hole_multi_coeff = array( 'd' )

    tmp_field = 0.
    tmp_sic_electron_multi_coeff = 0.
    tmp_sic_hole_multi_coeff = 0.

    for i in range(1000):
        tmp_field = tmp_field + field_step # V/cm
        tmp_inversefield = 1e6/tmp_field
        tmp_sic_electron_multi_coeff,tmp_sic_hole_multi_coeff = cal_impact_coefficient(tmp_field)

        x_field.append(tmp_field)
        x_inversefield.append(tmp_inversefield)
        y_sic_electron_multi_coeff.append(tmp_sic_electron_multi_coeff)
        y_sic_hole_multi_coeff.append(tmp_sic_hole_multi_coeff)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x_field,y_sic_electron_multi_coeff,label="electron")
    ax.plot(x_field,y_sic_hole_multi_coeff,label="hole")
    ax.set_xlim(2e5,1e7)
    ax.set_ylim(1e-1,4e6)
    ax.legend(loc='upper left')
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("ElectricField  [V/cm]")
    plt.ylabel("Impact Coefficient [cm-1]")
    plt.title("Hatakeyama Impact Model")
    plt.grid(True,ls = '--',which="both")
    fig.show()
    fig.savefig("./output/devsim/HatakeyamaImpactModel.png")

def CreateVanOvenstraetenImpact():
    T = 300 #K

    hbarOmega = 0.063 # eV
    E0 = 4.0e5 # V/cm
    T0 = 293.0 # K
    k_T0 = 0.0257 # eV
    gamma = math.tanh(hbarOmega/(2*k_T0))/math.tanh(hbarOmega/(2*k_T0*T/T0))

    n_a_low = 7.03e5 # cm-1
    n_a_high = 7.03e5 # cm-1

    n_b_low = 1.232e6 # cm-1
    n_b_high = 1.232e6 # cm-1

    p_a_low = 1.582e6 # cm-1
    p_a_high = 6.71e5 # cm-1

    p_b_low = 2.036e6 # cm-1
    p_b_high = 1.693e6 # cm-1

    devsim.add_db_entry(material="Silicon",   parameter="gamma",  value=gamma,   unit="1",     description="gamma for van Ovenstraeten Avalanche Model")
    devsim.add_db_entry(material="Silicon",   parameter="n_a_high",  value=n_a_high,   unit="cm-1",     description="n_a for Hatakeyyama Avalanche Model")
    devsim.add_db_entry(material="Silicon",   parameter="n_b_high",  value=n_b_high,   unit="V/cm",     description="n_b for Hatakeyyama Avalanche Model")
    devsim.add_db_entry(material="Silicon",   parameter="p_a_high",  value=p_a_high,   unit="cm-1",     description="p_a for Hatakeyyama Avalanche Model")
    devsim.add_db_entry(material="Silicon",   parameter="p_b_high",  value=p_b_high,   unit="V/cm",     description="p_b for Hatakeyyama Avalanche Model")

    devsim.add_db_entry(material="Silicon",   parameter="n_a_low",  value=n_a_low,   unit="cm-1",     description="n_a for Hatakeyyama Avalanche Model")
    devsim.add_db_entry(material="Silicon",   parameter="n_b_low",  value=n_b_low,   unit="V/cm",     description="n_b for Hatakeyyama Avalanche Model")
    devsim.add_db_entry(material="Silicon",   parameter="p_a_low",  value=p_a_low,   unit="cm-1",     description="p_a for Hatakeyyama Avalanche Model")
    devsim.add_db_entry(material="Silicon",   parameter="p_b_low",  value=p_b_low,   unit="V/cm",     description="p_b for Hatakeyyama Avalanche Model")


    def cal_impact_coefficient(electric_field):
        if(electric_field>1.75e05):
            if(electric_field>E0):
                n_coeff = gamma*n_a_high*math.exp(-(gamma*n_b_high)/electric_field)
                p_coeff = gamma*p_a_high*math.exp(-(gamma*p_b_high)/electric_field)
            else:
                n_coeff = gamma*n_a_low*math.exp(-(gamma*n_b_low)/electric_field)
                p_coeff = gamma*p_a_low*math.exp(-(gamma*p_b_low)/electric_field)
        else:
            n_coeff, p_coeff = 0. , 0.
        return n_coeff,p_coeff

    high_field = 1e7 # V/cm
    field_step = high_field/1000.0

    x_field = array( 'd' )
    x_inversefield = array( 'd' )

    y_sic_electron_multi_coeff = array( 'd' )
    y_sic_hole_multi_coeff = array( 'd' )

    tmp_field = 0.
    tmp_sic_electron_multi_coeff = 0.
    tmp_sic_hole_multi_coeff = 0.

    for i in range(1000):
        tmp_field = tmp_field + field_step # V/cm
        tmp_inversefield = 1e6/tmp_field
        tmp_sic_electron_multi_coeff,tmp_sic_hole_multi_coeff = cal_impact_coefficient(tmp_field)

        x_field.append(tmp_field)
        x_inversefield.append(tmp_inversefield)
        y_sic_electron_multi_coeff.append(tmp_sic_electron_multi_coeff)
        y_sic_hole_multi_coeff.append(tmp_sic_hole_multi_coeff)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x_field,y_sic_electron_multi_coeff,label="electron")
    ax.plot(x_field,y_sic_hole_multi_coeff,label="hole")
    ax.set_xlim(1.5e5,5e6)
    ax.set_ylim(1e-1,4e6)
    ax.legend(loc='upper left')
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("ElectricField  [V/cm]")
    plt.ylabel("Impact Coefficient [cm-1]")
    plt.title("van Ovenstraeten Impact Model")
    plt.grid(True,ls = '--',which="both")
    fig.show()
    fig.savefig("./output/devsim/VanOvenstraetenModel.png")

def SetTrapParametersSiliconCarbide():
    #add defect parameters
    N_c=3.25e15
    N_v=4.8e15
    devsim.add_db_entry(material="SiliconCarbide",parameter="N_c",value=N_c, unit="/cm^3", description="effective density of states in conduction band")
    devsim.add_db_entry(material="SiliconCarbide",parameter="N_v",value=N_v, unit="/cm^3", description="effective density of states in conduction band")
    k=1.3806503e-23 
    T0=300
    #Z1/2
    E_t11=-0.67*1.6e-19 #J
    E_t12=-2.56*1.6e-19
    n_11=N_c*math.exp(E_t11/(k*T0))
    p_11=N_v*math.exp(E_t12/(k*T0))
    devsim.add_db_entry(material="SiliconCarbide", parameter="N_t1",value=0, unit="/cm^3", description="density of Z1/2")#4.1e13 from paper
    devsim.add_db_entry(material="SiliconCarbide", parameter="r_n1",value=2e-7, unit="cm^3/s",description="electron capture constant of Z1/2")
    devsim.add_db_entry(material="SiliconCarbide", parameter="r_p1",value=3e-7, unit="cm^3/s",description="hole capture constant of Z1/2")
    devsim.add_db_entry(material="SiliconCarbide", parameter="E_t11",value=E_t11, unit="J", description="Z1/2 Et-Ec")
    devsim.add_db_entry(material="SiliconCarbide", parameter="E_t12",value=E_t12, unit="J", description="Z1/2 -(Et-Ev)")
    devsim.add_db_entry(material="SiliconCarbide", parameter="n_11",value=n_11, unit="/cm^3", description="n1 of Z1/2")
    devsim.add_db_entry(material="SiliconCarbide", parameter="p_11",value=p_11, unit="/cm^3", description="p1 of Z1/2")
    #EH6/7
    E_t21=-1.65*1.6e-19 #J
    E_t22=-1.58*1.6e-19
    n_12=N_c*math.exp(E_t21/(k*T0))
    p_12=N_v*math.exp(E_t22/(k*T0))
    devsim.add_db_entry(material="SiliconCarbide",parameter="N_t2",value=0, unit="/cm^3", description="density of EH6/7")#3.9e13 from paper
    devsim.add_db_entry(material="SiliconCarbide",parameter="r_n2",value=2.4e-7, unit="cm^3/s", description="electron capture constant of EH6/7")
    devsim.add_db_entry(material="SiliconCarbide",parameter="r_p2",value=5e-11, unit="cm^3/s", description="hole capture constant of EH6/7")
    devsim.add_db_entry(material="SiliconCarbide",parameter="E_t21",value=E_t21, unit="J", description="EH6/7 Et-Ec")
    devsim.add_db_entry(material="SiliconCarbide",parameter="E_t22",value=E_t22, unit="J", description="EH6/7 -(Et-Ev)")
    devsim.add_db_entry(material="SiliconCarbide",parameter="n_12",value=n_12, unit="/cm^3", description="n1 of EH6/7")
    devsim.add_db_entry(material="SiliconCarbide",parameter="p_12",value=p_12, unit="/cm^3", description="p1 of EH6/7")

def SaveDataBase():
    devsim.save_db()
    print("The SICAR database is saved.")



def main():
    CreateDataBase("./output/devsim/SICARDB")
    CreateGlobalConstant()
    CreateSiliconCarbideConstant()
    CreateSiliconConstant()

    CreateHatakeyamaImpact()
    CreateVanOvenstraetenImpact()

    SetTrapParametersSiliconCarbide()
    #SetTrapParametersSilicon()
    SaveDataBase()


main()
