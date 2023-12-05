#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import devsim 
import os
import sys
import math

from . import physics_drift_diffusion
from . import model_create
from . import initial

from .build_device import Detector

import matplotlib
import matplotlib.pyplot
import csv

if not (os.path.exists("./output/devsim")):
    os.makedirs("./output/devsim")

device="SICAR-1.1.8"
region="SICAR-1.1.8"

# Area factor
# 1D 1cm*1cm
# DUT 5mm* 5mm
area_factor = 4.0

MyDetector = Detector("SICAR-1.1.8", 1)

devsim.open_db(filename="./output/devsim/SICARDB.db", permission="readonly")
# Extended precision
# devsim.set_parameter(name='direct_solver', value='superlu')
devsim.set_parameter(name = "extended_solver", value=True)
devsim.set_parameter(name = "extended_model", value=True)
devsim.set_parameter(name = "extended_equation", value=True)

# Initial DC solution
initial.InitialSolution(device, region)
devsim.solve(type="dc", absolute_error=1.0, relative_error=1e-10, maximum_iterations=30)

### Drift diffusion simulation at equilibrium
initial.ImprovedDriftDiffusionInitialSolution(device, region)
devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=30)

#### Ramp the bias to Reverse
reverse_v = 0.0
n = 0
reverse_voltage = []
reverse_top_current = []
reverse_bot_current = []

reverse_voltage.append(0.)
reverse_top_current.append(0.)

f = open("./output/devsim/sicar1_lgad_reverse_iv.csv", "w")
header = ["Voltage","Current"]
writer = csv.writer(f)
writer.writerow(header)

#devsim.delete_node_model(device=device, region=region, name="IntrinsicElectrons")
#devsim.delete_node_model(device=device, region=region, name="IntrinsicHoles")

fig1=matplotlib.pyplot.figure()
ax1 = fig1.add_subplot(111)

while reverse_v < 4000.0:

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

    if(reverse_v%100.0==0 and reverse_v<1001):
        devsim.edge_average_model(device=device, region=region, node_model="x", edge_model="xmid")
        x = devsim.get_edge_model_values(device=device, region=region, name="xmid") # get x-node values 
        y = devsim.get_edge_model_values(device=device, region=region, name="ElectricField") # get y-node values
        matplotlib.pyplot.plot(x,y,label="%s"%(str(reverse_v)))


    reverse_v += 1

    # breakdown
    if( abs(reverse_top_total_current/area_factor) > 1e6): break

matplotlib.pyplot.xlabel('Depth [cm]')
matplotlib.pyplot.ylabel('E (V/cm)')
matplotlib.pyplot.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
ax1.legend(loc='upper right')
ax1.set_xlim(0,5e-4)
fig1.show()
fig1.savefig("./output/devsim/sicar1_lgad_reverse_electricfield.png")

f.close()
devsim.close_db()

print(reverse_voltage)
print(reverse_top_current)

fig2=matplotlib.pyplot.figure()
ax2 = fig2.add_subplot(111)
matplotlib.pyplot.semilogy(reverse_voltage, reverse_top_current)
matplotlib.pyplot.xlabel('Voltage (V)')
matplotlib.pyplot.ylabel('Current (A)')
#matplotlib.pyplot.axis([min(reverse_voltage), max(reverse_voltage), 1e-9, 1e-2])
fig2.savefig("./output/devsim/sicar1_lgad_reverse_iv.png")