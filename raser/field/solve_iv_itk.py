#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import devsim 
import os
import sys
import math
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from . import physics
from . import node
from . import initial
from util.read_json import Setting


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

# Area factor
# 1D 1cm*1cm
# DUT 5mm* 5mm
area_factor = 1/(0.8*0.8)

print()

itk_md8_mesh.Create1DMesh(device=device, region=region)
itk_md8_mesh.SetDoping(device=device, region=region)
itk_md8_mesh.Draw_Doping(device=device, region=region, path="./output/devsim/itk_md8_doping.png")

devsim.open_db(filename="./output/devsim/SICARDB", permission="readonly")

# Extended precision
devsim.set_parameter(name = "extended_solver", value=True)
devsim.set_parameter(name = "extended_model", value=True)
devsim.set_parameter(name = "extended_equation", value=True)

# Initial DC solution

args111 = ["det_name=ITk-Si-strip","parfile=paras/setting.json"]
dset111 = Setting(args111)
det_dic111 = dset111.detector    
doping1=str(det_dic111['doping'])

sign1=sys.argv[1]
constant1=sys.argv[2]
ITK_MD8_doping=doping1
area_factor = 1.0/(0.8*0.8)
if not (os.path.exists("./output/devsim/"+device+"_"+ITK_MD8_doping+sign1+constant1+"/")):
    os.makedirs("./output/devsim/"+device+"_"+ITK_MD8_doping+sign1+constant1+"/")
f_md8iv = open("./output/devsim/"+device+"_"+ITK_MD8_doping+sign1+constant1+"/"+device+"_reverse_iv.csv", "w")
header_md8iv = ["Voltage","Current"]
writer_md8iv = csv.writer(f_md8iv)
writer_md8iv.writerow(header_md8iv)

initial.InitialSolution(device, region)
devsim.solve(type="dc", absolute_error=1.0, relative_error=1e-10, maximum_iterations=50)

### Drift diffusion simulation at equilibrium
if sign1=="plus":
    constant="+"+constant1
if sign1=="minus":
    constant="-"+constant1

initial.DriftDiffusionInitialSolution(device, region,constant)
devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=50)

#### Ramp the bias to Reverse
reverse_v = 0.0
reverse_voltage = []
reverse_top_current = []
reverse_bot_current = []

reverse_voltage.append(0.)
reverse_top_current.append(0.)

f = open("./output/devsim/ITK_MD8_reverse_iv.csv", "w")
header = ["Voltage","Current"]
writer = csv.writer(f)
writer.writerow(header)

#devsim.delete_node_model(device=device, region=region, name="IntrinsicElectrons")
#devsim.delete_node_model(device=device, region=region, name="IntrinsicHoles")

fig1=matplotlib.pyplot.figure()
ax1 = fig1.add_subplot(111)

while reverse_v < 700.0:

    devsim.set_parameter(device=device, name=physics.GetContactBiasName("top"), value=reverse_v)
    #devsim.set_parameter(device=device, name=physics.GetContactBiasName("top"), value=0-reverse_v)
    try:
        devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=50)
    except devsim.error as msg:
        if msg=="Convergence failure!":
            raise
    physics.PrintCurrents(device, "top")
    physics.PrintCurrents(device, "bot")
    reverse_top_electron_current= devsim.get_contact_current(device=device, contact="top", equation="ElectronContinuityEquation")
    reverse_top_hole_current    = devsim.get_contact_current(device=device, contact="top", equation="HoleContinuityEquation")
    reverse_top_total_current   = reverse_top_electron_current + reverse_top_hole_current       
    reverse_voltage.append(reverse_v)
    #reverse_voltage.append(0-reverse_v)
    reverse_top_current.append(abs(reverse_top_total_current))
    writer.writerow([reverse_v,abs(reverse_top_total_current/area_factor)])
    writer_md8iv.writerow([reverse_v,abs(reverse_top_total_current/area_factor)])
    #writer.writerow([0-reverse_v,abs(reverse_top_total_current/area_factor)])
    #writer_md8iv.writerow([0-reverse_v,abs(reverse_top_total_current/area_factor)]) 
    
    if(reverse_v%50.0==0):
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
fig1.savefig("./output/devsim/ITK_MD8_reverse_electricfield.png")
f_md8iv.close()
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
fig2.savefig("./output/devsim/ITK_MD8_reverse_iv.png")
