#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import devsim 
import os
import math
import sys
sys.path.append("..")

from . import physics_drift_diffusion
from . import model_create
from . import initial

from .build_device import Detector

import matplotlib
import matplotlib.pyplot
import csv
import numpy as np

if not (os.path.exists("./output/devsim")):
    os.makedir("./output/devsim")

device="1D_NJU_PIN"
region="1D_NJU_PIN"

# Area factor
# 1D 1cm*1cm
# DUT 5mm* 5mm
area_factor = 4.0

MyDetector = Detector("NJU-PIN", 1)

devsim.open_db(filename="./output/field/SICARDB.db", permission="readonly")


#add defect parameters
N_c=3.25e15 #effective density of states in conduction band
N_v=4.8e15 #effective density of states in valence band
k=1.3806503e-23 
T0=300
#Z1/2
E_t11=-0.67*1.6e-19 #J
E_t12=-2.56*1.6e-19
n_11=N_c*math.exp(E_t11/(k*T0))
p_11=N_v*math.exp(E_t12/(k*T0))
devsim.set_parameter(device=device,region=region,name="N_t1",value=0)#density of Z1/2,4.1e13 from paper
devsim.set_parameter(device=device,region=region,name="r_n1",value=2e-7)#electron capture constant of Z1/2
devsim.set_parameter(device=device,region=region,name="r_p1",value=3e-7)#hole capture constant of Z1/2
devsim.set_parameter(device=device,region=region,name="E_t11",value=E_t11)#Z1/2 Et-Ec
devsim.set_parameter(device=device,region=region,name="E_t12",value=E_t12)#Z1/2 -(Et-Ev)
devsim.set_parameter(device=device,region=region,name="n_11",value=n_11)#n1 of Z1/2
devsim.set_parameter(device=device,region=region,name="p_11",value=p_11)#p1 of Z1/2
#EH6/7
E_t21=-1.65*1.6e-19 #J
E_t22=-1.58*1.6e-19
n_12=N_c*math.exp(E_t21/(k*T0))
p_12=N_v*math.exp(E_t22/(k*T0))
devsim.set_parameter(device=device,region=region,name="N_t2",value=0)#density of EH6/7,3.9e13 from paper
devsim.set_parameter(device=device,region=region,name="r_n2",value=2.4e-7)#electron capture constant of EH6/7
devsim.set_parameter(device=device,region=region,name="r_p2",value=5e-11)#hole capture constant of EH6/7
devsim.set_parameter(device=device,region=region,name="E_t21",value=E_t21)#EH6/7 Et-Ec
devsim.set_parameter(device=device,region=region,name="E_t22",value=E_t22)#EH6/7 -(Et-Ev)
devsim.set_parameter(device=device,region=region,name="n_12",value=n_12)#n1 of EH6/7
devsim.set_parameter(device=device,region=region,name="p_12",value=p_12)#p1 of EH6/7

# Extended precision
devsim.set_parameter(name = "extended_solver", value=True)
devsim.set_parameter(name = "extended_model", value=True)
devsim.set_parameter(name = "extended_equation", value=True)

# Initial DC solution
initial.InitialSolution(device, region)
devsim.solve(type="dc", absolute_error=1.0, relative_error=1e-10, maximum_iterations=30)

### Drift diffusion simulation at equilibrium
initial.DriftDiffusionInitialSolution(device, region)
devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=30)

#set paramater of Nt and sigma
list_Nt = [1e12, 1e13, 1e14, 1e15, 1e16, 1e17]
list_sigman = [3e-12, 3e-13, 3e-14, 3e-15, 3e-16, 3e-17]
#list_sigmap = [2e-12, 2e-13, 2e-14, 2e-15, 2e-16, 2e-17]

i = int(sys.argv[1])
print(i)
if (i<=3):
    N_t=list_Nt[i+1]
    sigma_n=3e-12
    sigma_p=2e-12
    devsim.add_db_entry(material="global",   parameter="sigma_n",     value=sigma_n,   unit="s/cm^2",     description="sigma_n")
    devsim.add_db_entry(material="global",   parameter="sigma_p",     value=sigma_p,   unit="s/cm^2",     description="sigma_p")
    devsim.add_db_entry(material="global",   parameter="N_t",     value=N_t,   unit="cm^(-3)",     description="N_t")
elif (3<i<9):
    N_t=1e12
    sigma_n=list_sigman[i-4]
    sigma_p=2e-12
    devsim.add_db_entry(material="global",   parameter="sigma_n",     value=sigma_n,   unit="s/cm^2",     description="sigma_n")
    devsim.add_db_entry(material="global",   parameter="sigma_p",     value=sigma_p,   unit="s/cm^2",     description="sigma_p")
    devsim.add_db_entry(material="global",   parameter="N_t",     value=N_t,   unit="cm^(-3)",     description="N_t")
elif (8<i<14):
    N_t_HS6=list_Nt[i-8]
    sigma_n_HS6=2e-17
    sigma_p_HS6=3e-17
    devsim.add_db_entry(material="global",   parameter="sigma_n_HS6",     value=sigma_n_HS6,   unit="s/cm^2",     description="sigma_n_HS6")
    devsim.add_db_entry(material="global",   parameter="sigma_p_HS6",     value=sigma_p_HS6,   unit="s/cm^2",     description="sigma_p_HS6")
    devsim.add_db_entry(material="global",   parameter="N_t_HS6",     value=N_t_HS6,   unit="cm^(-3)",     description="N_t_HS6")
else :
    N_t_HS6=1e13
    sigma_n_HS6=list_sigman[i-14]
    sigma_p_HS6=2e-16
    devsim.add_db_entry(material="global",   parameter="sigma_n_HS6",     value=sigma_n_HS6,   unit="s/cm^2",     description="sigma_n_HS6")
    devsim.add_db_entry(material="global",   parameter="sigma_p_HS6",     value=sigma_p_HS6,   unit="s/cm^2",     description="sigma_p_HS6")
    devsim.add_db_entry(material="global",   parameter="N_t_HS6",     value=N_t_HS6,   unit="cm^(-3)",     description="N_t_HS6")


reverse_v = 0.0
reverse_voltage = []
reverse_top_current = []    
reverse_bot_current = []

reverse_voltage.append(0.)
reverse_top_current.append(0.)

#devsim.delete_node_model(device=device, region=region, name="IntrinsicElectrons")
#devsim.delete_node_model(device=device, region=region, name="IntrinsicHoles")

f = open("./output/devsim/nju_pin_reverse_iv%d.csv"%i, "w" )
header = ["Voltage","Current"]
writer = csv.writer(f)
writer.writerow(header)

while reverse_v < 800.0:
    devsim.set_parameter(device=device, name=physics_drift_diffusion.GetContactBiasName("top"), value=0-reverse_v)
    devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=30)
    physics_drift_diffusion.PrintCurrents(device, "top")
    physics_drift_diffusion.PrintCurrents(device, "bot")
    reverse_top_electron_current= devsim.get_contact_current(device=device, contact="top", equation="ElectronContinuityEquation")
    reverse_top_hole_current    = devsim.get_contact_current(device=device, contact="top", equation="HoleContinuityEquation")
    reverse_top_total_current   = reverse_top_electron_current + reverse_top_hole_current       
    reverse_voltage.append(0-reverse_v)
    reverse_top_current.append(abs(reverse_top_total_current))
    writer.writerow([0-reverse_v,abs(reverse_top_total_current/area_factor)])

    if(reverse_v%100.0==0):
        devsim.edge_average_model(device=device, region=region, node_model="x", edge_model="xmid")
        x = devsim.get_edge_model_values(device=device, region=region, name="xmid") # get x-node values
        y = devsim.get_edge_model_values(device=device, region=region, name="ElectricField") # get y-node values
        matplotlib.pyplot.plot(x,y,label="%s"%(str(reverse_v)))
        #break
    reverse_v += 1
f.close()
'''
fig1=matplotlib.pyplot.figure()
ax1 = fig1.add_subplot(111)
matplotlib.pyplot.xlabel('Depth [cm]')
matplotlib.pyplot.ylabel('E (V/cm)')
matplotlib.pyplot.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
ax1.legend(loc='upper right')
fig1.show()
fig1.savefig("./output/devsim/nju_pin_reverse_electricfield%d.png"%i)
'''
print(reverse_voltage)
print(reverse_top_current)
'''
fig2=matplotlib.pyplot.figure()
ax2 = fig2.add_subplot(111)
matplotlib.pyplot.semilogy(reverse_voltage, reverse_top_current)
matplotlib.pyplot.xlabel('Voltage (V)')
matplotlib.pyplot.ylabel('Current (A)')
matplotlib.pyplot.axis([min(reverse_voltage), max(reverse_voltage), 1e-9, 1e-2])
fig2.savefig("./output/devsim/nju_pin_reverse_iv%d.png"%i)
'''
devsim.close_db() 
