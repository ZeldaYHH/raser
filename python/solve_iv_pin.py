#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import devsim 
import os
import sys
import math

from raser import Physics
from raser import Node
from raser import Initial


import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot
import csv
import numpy as np


import nju_pin_5mm_5mm_mesh

if not (os.path.exists("./output/devsim")):
    os.makedirs("./output/devsim")

device="1D_NJU_PIN"
region="1D_NJU_PIN"

# Area factor
# 1D 1cm*1cm
# DUT 5mm* 5mm
area_factor = 4.0

nju_pin_5mm_5mm_mesh.Create1DMesh(device=device, region=region)
nju_pin_5mm_5mm_mesh.SetDoping(device=device, region=region)
nju_pin_5mm_5mm_mesh.Draw_Doping(device=device, region=region, path="./output/devsim/nju_pin_doping.png")

devsim.open_db(filename="./output/devsim/SICARDB", permission="readonly")

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
devsim.set_parameter(device=device,region=region,name="N_t1",value=2e15)#density of Z1/2,4.1e13 from paper
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
Initial.InitialSolution(device, region)
devsim.solve(type="dc", absolute_error=1.0, relative_error=1e-10, maximum_iterations=50)

### Drift diffusion simulation at equilibrium
Initial.DriftDiffusionInitialSolution(device, region)
devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-7, maximum_iterations=50)

#### Ramp the bias to Reverse
reverse_v = 0.0
reverse_voltage = []
reverse_top_current = []
reverse_bot_current = []

reverse_voltage.append(0.)
reverse_top_current.append(0.)

f = open("./output/devsim/nju_pin_reverse_iv.csv", "w")
header = ["Voltage","Current"]
writer = csv.writer(f)
writer.writerow(header)

#devsim.delete_node_model(device=device, region=region, name="IntrinsicElectrons")
#devsim.delete_node_model(device=device, region=region, name="IntrinsicHoles")

fig1=matplotlib.pyplot.figure()
ax1 = fig1.add_subplot(111)

while reverse_v < 800.0:

    devsim.set_parameter(device=device, name=Physics.GetContactBiasName("top"), value=0-reverse_v)
    try:
        devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-7, maximum_iterations=50)
    except devsim.error as msg:
        if msg=="Convergence failure!":
            raise
    Physics.PrintCurrents(device, "top")
    Physics.PrintCurrents(device, "bot")
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

matplotlib.pyplot.xlabel('Depth [cm]')
matplotlib.pyplot.ylabel('E (V/cm)')
matplotlib.pyplot.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
ax1.legend(loc='upper right')
fig1.show()
fig1.savefig("./output/devsim/nju_pin_reverse_electricfield.png")

f.close()
devsim.close_db()

#print(reverse_voltage)
#print(reverse_top_current)

fig2=matplotlib.pyplot.figure()
ax2 = fig2.add_subplot(111)
matplotlib.pyplot.semilogy(reverse_voltage, reverse_top_current)
matplotlib.pyplot.xlabel('Voltage (V)')
matplotlib.pyplot.ylabel('Current (A)')
#matplotlib.pyplot.axis([min(reverse_voltage), max(reverse_voltage), 1e-9, 1e-2])
fig2.savefig("./output/devsim/nju_pin_reverse_iv.png")
