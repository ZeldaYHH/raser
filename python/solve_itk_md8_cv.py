#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import devsim 
import os
import sys

from raser import Physics
from raser import Node
from raser import Initial

import itk_md8_mesh

import matplotlib
#matplotlib.use('Agg') 
import matplotlib.pyplot
import csv
import math

if not (os.path.exists("./output/devsim")):
    os.makedirs("./output/devsim")

device="1D_ITK_MD8"
region="1D_ITK_MD8"

# Area factor
# 1D 1cm*1cm
# DUT 0.8cm* 0.8cm
area_factor = 1.0/(0.8*0.8)

itk_md8_mesh.Create1DMesh(device=device, region=region)
itk_md8_mesh.SetDoping(device=device, region=region)
itk_md8_mesh.Draw_Doping(device=device, region=region, path="./output/devsim/itk_md8_doping.png")

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

f = open("./output/devsim/itk_md8_reverse_cv.csv", "w")
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
    ssac_top_cap.append(abs(cap*(1e12))/area_factor)

    writer.writerow([0-reverse_v,cap*(1e12)/area_factor])

f.close()
devsim.close_db()

fig=matplotlib.pyplot.figure(num=4,figsize=(4,4))
matplotlib.pyplot.plot(ssac_voltage, ssac_top_cap)
matplotlib.pyplot.xlabel('Voltage (V)')
matplotlib.pyplot.ylabel('Capacitance (pF)')
matplotlib.pyplot.savefig("./output/devsim/itk_md8_reverse_cv.png")

