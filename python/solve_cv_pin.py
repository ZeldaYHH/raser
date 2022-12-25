#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import devsim 
import os
import sys

from raser import Physics
from raser import Node
from raser import Initial

import nju_pin_5mm_5mm_mesh

import matplotlib
#matplotlib.use('Agg') 
import matplotlib.pyplot
import csv
import math

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

# Extended precision
devsim.set_parameter(name = "extended_solver", value=True)
devsim.set_parameter(name = "extended_model", value=True)
devsim.set_parameter(name = "extended_equation", value=True)
devsim.circuit_element(name="V1", n1=Physics.GetContactBiasName("top"), n2=0, value=0.0, acreal=1.0, acimag=0.0)

# Initial DC solution
Initial.InitialSolution(device, region, circuit_contacts="top")
devsim.solve(type="dc", absolute_error=1.0, relative_error=1e-10, maximum_iterations=30)

### Drift diffusion simulation at equilibrium
Initial.DriftDiffusionInitialSolution(device, region, circuit_contacts=["top"])
devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=30)

#### Ramp the bias to Reverse
reverse_v=0.0
ssac_voltage = []
ssac_top_cap = []

f = open("./output/devsim/nju_pin_reverse_cv.csv", "w")
header = ["Voltage","Capacitance"]
writer = csv.writer(f)
writer.writerow(header)

while reverse_v < 400.0: 
    devsim.circuit_alter(name="V1", value=0-reverse_v)
    devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=30)
    #TODO: get out circuit information
    Physics.PrintCurrents(device, "bot")
    devsim.solve(type="ac", frequency=1.0)
    cap=devsim.get_circuit_node_value(node="V1.I", solution="ssac_imag")/ (-2*math.pi)
    print("capacitance {0} {1}".format(reverse_v, cap))
    reverse_v += 1.0

    ssac_voltage.append(0-reverse_v)
    ssac_top_cap.append(cap*(1e12)/area_factor)

    writer.writerow([0-reverse_v,cap*(1e12)/area_factor])

f.close()
devsim.close_db()

fig=matplotlib.pyplot.figure(num=4,figsize=(4,4))
matplotlib.pyplot.plot(ssac_voltage, ssac_top_cap)
matplotlib.pyplot.xlabel('Voltage (V)')
matplotlib.pyplot.ylabel('Capacitance (pF)')
#matplotlib.pyplot.axis([-200, 0, 0, 20])
matplotlib.pyplot.savefig("./output/devsim/nju_pin_reverse_cv.png")
#write_devices(file="diode_1d.dat", type="tecplot")
