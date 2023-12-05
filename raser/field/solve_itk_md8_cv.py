#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import devsim 
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from . import physics_drift_diffusion
from . import model_create
from . import initial

from .build_device import Detector

import matplotlib
import matplotlib.pyplot
import csv
import math

if not (os.path.exists("./output/devsim")):
    os.makedirs("./output/devsim")

device="ITk-md8"
region="ITk-md8"

# Area factor
# 1D 1cm*1cm
# DUT 0.8cm* 0.8cm
area_factor = 1.0/(0.76*0.76)


MyDetector = Detector("ITk-md8", 1)

devsim.open_db(filename="./output/devsim/SICARDB.db", permission="readonly")

# Extended precision
devsim.set_parameter(name = "extended_solver", value=True)
devsim.set_parameter(name = "extended_model", value=True)
devsim.set_parameter(name = "extended_equation", value=True)
devsim.circuit_element(name="V1", n1=physics_drift_diffusion.GetContactBiasName("top"), n2=0, value=0.0, acreal=1.0, acimag=0.0)

# Initial DC solution
initial.InitialSolution(device, region, circuit_contacts="top")
devsim.solve(type="dc", absolute_error=1.0, relative_error=1e-10, maximum_iterations=30)

### Drift diffusion simulation at equilibrium
initial.DriftDiffusionInitialSolution(device, region, circuit_contacts=["top"])
devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=30)

#### Ramp the bias to Reverse
reverse_v=0.0
ssac_voltage = []
ssac_top_cap = []

f = open("./output/devsim/itk_md8_reverse_cv.csv", "w")
header = ["Voltage","Capacitance^{-2}"]
writer = csv.writer(f)
writer.writerow(header)

while reverse_v < 400.0: 
    devsim.circuit_alter(name="V1", value=reverse_v)
    devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=30)
    physics_drift_diffusion.PrintCurrents(device, "bot")
    devsim.solve(type="ac", frequency=1.0)
    cap=devsim.get_circuit_node_value(node="V1.I", solution="ssac_imag")/ (-2*math.pi)
    print("capacitance {0} {1}".format(reverse_v, cap))
    reverse_v += 1.0

    ssac_voltage.append(reverse_v)

    if abs(cap*(1e12)) == 0:
        result = None
    else:
        result = (area_factor/(abs(cap*(1e12))))**2
    ssac_top_cap.append(result)

    writer.writerow([reverse_v,result])

f.close()
devsim.close_db()

fig=matplotlib.pyplot.figure(num=4,figsize=(8,8))
matplotlib.pyplot.plot(ssac_voltage, ssac_top_cap)
matplotlib.pyplot.xlabel('Voltage (V)')
matplotlib.pyplot.ylabel('Capacitance^(-2) (pF)^(-2)')
matplotlib.pyplot.savefig("./output/devsim/itk_md8_reverse_cv.png")

