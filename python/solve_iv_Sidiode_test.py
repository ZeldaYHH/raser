#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import devsim 
import os
import sys
import math
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from raser import Physics
from raser import Node
from raser import Initial
from raser import Setting
from array import array

import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot
import csv
import numpy as np


import itk_md8_mesh

if not (os.path.exists("./output/devsim")):
    os.makedirs("./output/devsim")

device="1D_ITK_MD8"
region="1D_ITK_MD8"

def create1DMeshtest(device, region):
    devsim.create_1d_mesh(mesh="dio")
    devsim.add_1d_mesh_line(mesh="dio", pos=0, ps=1e-7, tag="top")
    devsim.add_1d_mesh_line(mesh="dio", pos=0.5e-5, ps=1e-9, tag="mid")
    devsim.add_1d_mesh_line(mesh="dio", pos=1e-5, ps=1e-7, tag="bot")
    devsim.add_1d_contact (mesh="dio", name="top", tag="top", material="metal")
    devsim.add_1d_contact (mesh="dio", name="bot", tag="bot", material="metal")
    devsim.add_1d_region (mesh="dio", material="Silicon", region=region, tag1="top", tag2="bot")
    devsim.finalize_mesh(mesh="dio")
    devsim.create_device(mesh="dio", device=device)


def SetNetDoping_devsim(device, region):
    '''
      NetDoping
    '''
    Node.CreateNodeModel(device, region, "Acceptors", "1.0e18*step(0.5e-5-x)")
    Node.CreateNodeModel(device, region, "Donors",    "1.0e18*step(x-0.5e-5)")
    Node.CreateNodeModel(device, region, "NetDoping", "Donors-Acceptors")
    devsim.print_node_values(device=device, region=region, name="NetDoping")

#createMesh(device, region)

def SetDopingtest(device, region, donor_doping,bulk_doping=4.7e12):#default doping 4.7e12
    '''
      Doping
    '''
    Node.CreateNodeModel(device, region, "Donors", "%s*step(1e-4-x)"%donor_doping)
    #Node.CreateNodeModel(device, region, "Donors", "1.0e19*step(1e-4-x)")
    #Node.CreateNodeModel(device, region, "Donors", "1.0e19*step(0.5e-4-x)")
    Node.CreateNodeModel(device, region, "Acceptors",    "%s*step(x-1e-4)"%bulk_doping)
    Node.CreateNodeModel(device, region, "NetDoping", "Donors-Acceptors")
    devsim.edge_from_node_model(device=device,region=region,node_model="Acceptors")
    devsim.edge_from_node_model(device=device,region=region,node_model="NetDoping")
    devsim.edge_from_node_model(device=device,region=region,node_model="Donors")


# itk_md8_mesh.Create1DMesh(device=device, region=region)
# itk_md8_mesh.SetDoping(device=device, region=region)
# itk_md8_mesh.Draw_Doping(device=device, region=region, path="./output/devsim/testmd8_doping.png")

create1DMeshtest(device=device, region=region)
SetNetDoping_devsim(device=device, region=region)


def CreateSiliconConstant():
    #global
    #q = 1.60217646e-19 # coul
    q = 1.6e-19 # coul
    k = 1.3806503e-23  # J/K
    eps_0 = 8.85e-14   # F/cm^2
    T0 = 300.0         # K
    devsim.add_db_entry(material="global",   parameter="q",       value=q,          unit="coul",     description="Unit Charge")
    devsim.add_db_entry(material="global",   parameter="k",       value=k,          unit="J/K",      description="Boltzmann Constant")
    devsim.add_db_entry(material="global",   parameter="eps_0",   value=eps_0,      unit="F/cm^2",   description="Absolute Dielectric Constant")
    devsim.add_db_entry(material="global",   parameter="T0",      value=T0,         unit="K",        description="T0")
    devsim.add_db_entry(material="global",   parameter="k_T0",    value=k*T0,       unit="J",        description="k*T0")
    devsim.add_db_entry(material="global",   parameter="V_T0",    value=k*T0/q,     unit="J/coul",   description="k*T0/q")

    # define Silicon parameters
    N_c=2.8e19
    N_v=1.1e19
    #N_c=2.86e19
    #N_v=2.66e19
    devsim.add_db_entry(material="Silicon",parameter="N_c",value=N_c, unit="/cm^3", description="effective density of states in conduction band")
    devsim.add_db_entry(material="Silicon",parameter="N_v",value=N_v, unit="/cm^3", description="effective density of states in valence band")
    E_g=1.12*1.6*1e-19
    devsim.add_db_entry(material="Silicon",   parameter="E_g",    value=E_g,       unit="J",         description="E_g")
    # material
    devsim.add_db_entry(material="Silicon",   parameter="eps",    value=11.1,      unit="1",         description="Dielectric Constant")
    devsim.add_db_entry(material="Silicon",   parameter="n_i",    value=1.0e10,   unit="/cm^3",     description="Intrinsic Electron Concentration")
    #devsim.add_db_entry(material="Silicon",   parameter="n_i",    value=1.45e10,   unit="/cm^3",     description="Intrinsic Electron Concentration")
    #devsim.add_db_entry(material="Silicon",   parameter="n_i",    value=9.65e9,   unit="/cm^3",     description="Intrinsic Electron Concentration")
    # mobility
    devsim.add_db_entry(material="Silicon",   parameter="mu_n",   value=400,      unit="cm^2/Vs",   description="Constant Mobility of Electron")
    devsim.add_db_entry(material="Silicon",   parameter="mu_p",   value=200,       unit="cm^2/Vs",   description="Constant Mobility of Hole")

    #devsim.add_db_entry(material="Silicon",   parameter="mu_n",   value=1450,      unit="cm^2/Vs",   description="Constant Mobility of Electron")
    #devsim.add_db_entry(material="Silicon",   parameter="mu_p",   value=500,       unit="cm^2/Vs",   description="Constant Mobility of Hole")
#    devsim.add_db_entry(material="Silicon",   parameter="mu_p",   value=505,       unit="cm^2/Vs",   description="Constant Mobility of Hole")

    # SRH
    devsim.add_db_entry(material="Silicon",   parameter="n1",     value=1.0e10,   unit="/cm^3",     description="n1")
    devsim.add_db_entry(material="Silicon",   parameter="p1",     value=1.0e10,   unit="/cm^3",     description="p1")
    #devsim.add_db_entry(material="Silicon",   parameter="tau_n",  value=5e-6,    unit="s",         description="Constant SRH Lifetime of Electron")
    #devsim.add_db_entry(material="Silicon",   parameter="tau_p",  value=5e-6,    unit="s",         description="Constant SRH Lifetime of Hole")
    #devsim.add_db_entry(material="Silicon",   parameter="tau_n",  value=5e-3,    unit="s",         description="Constant SRH Lifetime of Electron")
    #devsim.add_db_entry(material="Silicon",   parameter="tau_p",  value=5e-3,    unit="s",         description="Constant SRH Lifetime of Hole")
    #devsim.add_db_entry(material="Silicon",   parameter="tau_n",  value=3e-2,    unit="s",         description="Constant SRH Lifetime of Electron")
    #devsim.add_db_entry(material="Silicon",   parameter="tau_p",  value=3e-2,    unit="s",         description="Constant SRH Lifetime of Hole")
    #devsim.add_db_entry(material="Silicon",   parameter="tau_n",  value=1.3e-4,    unit="s",         description="Constant SRH Lifetime of Electron")
    #devsim.add_db_entry(material="Silicon",   parameter="tau_p",  value=1.3e-4,    unit="s",         description="Constant SRH Lifetime of Hole")
    devsim.add_db_entry(material="Silicon",   parameter="tau_n",  value=1e-8,    unit="s",         description="Constant SRH Lifetime of Electron")
    devsim.add_db_entry(material="Silicon",   parameter="tau_p",  value=1e-8,    unit="s",         description="Constant SRH Lifetime of Hole")


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

    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # ax.plot(x_field,y_sic_electron_multi_coeff,label="electron")
    # ax.plot(x_field,y_sic_hole_multi_coeff,label="hole")
    # ax.set_xlim(1.5e5,5e6)
    # ax.set_ylim(1e-1,4e6)
    # ax.legend(loc='upper left')
    # plt.xscale("log")
    # plt.yscale("log")
    # plt.xlabel("ElectricField  [V/cm]")
    # plt.ylabel("Impact Coefficient [cm-1]")
    # plt.title("van Ovenstraeten Impact Model")
    # plt.grid(True,ls = '--',which="both")
    # fig.show()
    # fig.savefig("./output/devsim/VanOvenstraetenModel.png")



CreateSiliconConstant()
CreateVanOvenstraetenImpact()
#devsim.set_parameter(device=device, region=region, name="taun", value=1e-8)
#devsim.set_parameter(device=device, region=region, name="taup", value=1e-8)

#Node.CreateNodeModel(device, region, "Acceptors", "1.0e18*step(0.5e-5-x)")
#Node.CreateNodeModel(device, region, "Donors", "1.0e18*step(x-0.5e-5)")
#Node.CreateNodeModel(device, region, "NetDoping", "Donors-Acceptors")
#devsim.print_node_values(device=device, region=region, name="NetDoping")

#### Create potential only physical models
####
Node.CreateSolution(device, region, "Potential")
Physics.CreateSiliconPotentialOnly(device, region)
####
#### Set up the contacts applying a bias
####
for i in devsim.get_contact_list(device=device):
    devsim.set_parameter(device=device, name=Physics.GetContactBiasName(i), value=0.0)
    Physics.CreateSiliconPotentialOnlyContact(device, region, i)


# Extended precision
# devsim.set_parameter(name = "extended_solver", value=True)
# devsim.set_parameter(name = "extended_model", value=True)
# devsim.set_parameter(name = "extended_equation", value=True)



#Initial.InitialSolution(device, region)
devsim.solve(type="dc", absolute_error=1.0, relative_error=1e-10, maximum_iterations=50)

### Drift diffusion simulation at equilibrium
Node.CreateSolution(device, region, "Electrons")
Node.CreateSolution(device, region, "Holes")

#### create initial guess from dc only solution
####
devsim.set_node_values(device=device, region=region,name="Electrons", init_from="IntrinsicElectrons")
devsim.set_node_values(device=device, region=region,name="Holes", init_from="IntrinsicHoles")
###
### Set up equations
###
Physics.CreateSiDriftDiffusion(device, region)
for i in devsim.get_contact_list(device=device):
    Physics.CreateSiDriftDiffusionAtContact(device, region, i)



#Initial.DriftDiffusionInitialSolution(device, region,constant)
devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=50)

#### Ramp the bias to Reverse
reverse_v = 0.0
reverse_voltage = []
reverse_top_current = []
reverse_bot_current = []

reverse_voltage.append(0.)
reverse_top_current.append(0.)

f = open("./output/devsim/Sidiode_test_reverse_iv.csv", "w")
header = ["Voltage","Current"]
writer = csv.writer(f)
writer.writerow(header)

#devsim.delete_node_model(device=device, region=region, name="IntrinsicElectrons")
#devsim.delete_node_model(device=device, region=region, name="IntrinsicHoles")

fig1=matplotlib.pyplot.figure()
ax1 = fig1.add_subplot(111)

while reverse_v < 0.51:

    devsim.set_parameter(device=device, name=Physics.GetContactBiasName("top"), value=reverse_v)
    #devsim.set_parameter(device=device, name=Physics.GetContactBiasName("top"), value=0-reverse_v)
    try:
        devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=50)
    except devsim.error as msg:
        if msg=="Convergence failure!":
            raise
    Physics.PrintCurrents(device, "top")
    Physics.PrintCurrents(device, "bot")
    reverse_top_electron_current= devsim.get_contact_current(device=device, contact="top", equation="ElectronContinuityEquation")
    reverse_top_hole_current    = devsim.get_contact_current(device=device, contact="top", equation="HoleContinuityEquation")
    reverse_top_total_current   = reverse_top_electron_current + reverse_top_hole_current       
    reverse_voltage.append(reverse_v)
    #reverse_voltage.append(0-reverse_v)
    reverse_top_current.append(abs(reverse_top_total_current))
    writer.writerow([reverse_v,abs(reverse_top_total_current)])
    #writer.writerow([0-reverse_v,abs(reverse_top_total_current/area_factor)])
    #writer_md8iv.writerow([0-reverse_v,abs(reverse_top_total_current/area_factor)]) 
    
    if(reverse_v==0.5):
        devsim.edge_average_model(device=device, region=region, node_model="x", edge_model="xmid")
        x = devsim.get_edge_model_values(device=device, region=region, name="xmid") # get x-node values
        y = devsim.get_edge_model_values(device=device, region=region, name="ElectricField") # get y-node values
        matplotlib.pyplot.plot(x,y,label="%s"%(str(reverse_v)))

        #break

    reverse_v += 0.1

matplotlib.pyplot.xlabel('Depth [cm]')
matplotlib.pyplot.ylabel('E (V/cm)')
matplotlib.pyplot.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
ax1.legend(loc='upper right')
fig1.show()
fig1.savefig("./output/devsim/Sidiode_test_reverse_electricfield.png")

f.close()
devsim.close_db()

#print(reverse_voltage)
#print(reverse_top_current)

fig2=matplotlib.pyplot.figure()
ax2 = fig2.add_subplot(111)
matplotlib.pyplot.semilogy(reverse_voltage, reverse_top_current)
matplotlib.pyplot.xlabel('Voltage (V)')
matplotlib.pyplot.ylabel('Current (A)')
matplotlib.pyplot.axis([min(reverse_voltage), max(reverse_voltage), 1e-9, 1e-2])
fig2.savefig("./output/devsim/Sidiode_test_reverse_iv.png")
