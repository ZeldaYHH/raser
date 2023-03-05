import devsim 
import os
import math
import sys
sys.path.append("..")

from sicar import Physics
from sicar import Node
from sicar import Initial

import matplotlib
import matplotlib.pyplot
import csv
import numpy as np


import nju_pin_5mm_5mm_mesh

if not (os.path.exists("./output")):
    os.mkdir("./output")

device="1D_NJU_PIN"
region="1D_NJU_PIN"

# Area factor
# 1D 1cm*1cm
# DUT 5mm* 5mm
area_factor = 4.0

nju_pin_5mm_5mm_mesh.CreateMesh(device=device, region=region)
nju_pin_5mm_5mm_mesh.SetDoping(device=device, region=region)
nju_pin_5mm_5mm_mesh.Draw_Doping(device=device, region=region, path="./output/nju_pin_doping.png")

devsim.open_db(filename="../sicar/SICARDB", permission="readonly")

# Extended precision
devsim.set_parameter(name = "extended_solver", value=True)
devsim.set_parameter(name = "extended_model", value=True)
devsim.set_parameter(name = "extended_equation", value=True)

# Initial DC solution
Initial.InitialSolution(device, region)
devsim.solve(type="dc", absolute_error=1.0, relative_error=1e-10, maximum_iterations=30)

### Drift diffusion simulation at equilibrium
Initial.DriftDiffusionInitialSolution(device, region)
devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-7, maximum_iterations=30)

#set paramater of Z1/2
list_Nt = [1e12, 1e13, 1e14, 1e15, 1e16, 1e17]
#list_sigman = [3e-12, 3e-13, 3e-14, 3e-15, 3e-16, 3e-17]
#list_sigmap = [2e-12, 2e-13, 2e-14, 2e-15, 2e-16, 2e-17]
para_n=0
para_p=0
para_N=0
#sigma_n=list_sigman[para_n]
#sigma_p=list_sigman[para_p]
sigma_n=3e-12
sigma_p=2e-12
N_t=list_Nt[para_N]
devsim.add_db_entry(material="global",   parameter="sigma_n",     value=sigma_n,   unit="s/cm^2",     description="sigma_n")
devsim.add_db_entry(material="global",   parameter="sigma_p",     value=sigma_p,   unit="s/cm^2",     description="sigma_p")
devsim.add_db_entry(material="global",   parameter="N_t",     value=N_t,   unit="cm^(-3)",     description="N_t")
v_T=1e7
devsim.add_db_entry(material="global",   parameter="v_T",     value=v_T,   unit="cm/s",     description="v_T")

while para_N < 6.0:
    #### Ramp the bias to Reverse
    reverse_v = 0.0
    reverse_voltage = []
    reverse_top_current = []    
    reverse_bot_current = []

    reverse_voltage.append(0.)
    reverse_top_current.append(0.)

    #devsim.delete_node_model(device=device, region=region, name="IntrinsicElectrons")
    #devsim.delete_node_model(device=device, region=region, name="IntrinsicHoles")


    f = open("./output/nju_pin_reverse_iv%d.csv"%para_N, "w" )
    header = ["Voltage","Current"]
    writer = csv.writer(f)
    writer.writerow(header)
    #fig1=matplotlib.pyplot.figure()
    #ax1 = fig1.add_subplot(111)
    while reverse_v < 800.0:
        devsim.set_parameter(device=device, name=Physics.GetContactBiasName("top"), value=0-reverse_v)
        devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=30)
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
 

    #matplotlib.pyplot.xlabel('Depth [cm]')
    #matplotlib.pyplot.ylabel('E (V/cm)')
    #matplotlib.pyplot.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
    #ax1.legend(loc='upper right')
    #fig1.show()
    #fig1.savefig("./output/nju_pin_reverse_electricfield%d.png"%para_N)

    f.close()
    devsim.close_db() 
    
 #print(reverse_voltage)
 #print(reverse_top_current)

    #fig2=matplotlib.pyplot.figure()
    #ax2 = fig2.add_subplot(111)
    #matplotlib.pyplot.semilogy(reverse_voltage, reverse_top_current)
    #matplotlib.pyplot.xlabel('Voltage (V)')
    #matplotlib.pyplot.ylabel('Current (A)')
 #matplotlib.pyplot.axis([min(reverse_voltage), max(reverse_voltage), 1e-9, 1e-2])
    #fig2.savefig("./output/nju_pin_reverse_iv%d.png"%para_N)
    
    para_N += 1
