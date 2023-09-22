#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import devsim 
import os
import sys
sys.path.append("..")

import sys
import csv
from field import node
from field import physics
sys.path.append("..")
import matplotlib.pyplot
import physics2dcv
import math
import Sicar11

if not (os.path.exists("./output")):
    os.mkdir("./output")

if not (os.path.exists("./output/reverse")):
    os.mkdir("./output/reverse")

device="MyDevice"
region="MyDevice"

q=1.6e-19
k=1.3806503e-23
eps=8.85e-14
T=300

'''
pn_2D.Create2DMesh(device=device, region=region)
pn_2D.SetDoping(device=device, region=region)

'''

Sicar11.Create2DMesh(device=device, region=region)
Sicar11.SetDoping(device=device, region=region)
#Sicar11.Draw_Doping(device=device, region=region, path="./output/2d_pn_doping.png")

physics2dcv.SetMaterialParameters(device,region)
devsim.open_db(filename="./output/devsim/SICARDB", permission="readonly")



physics2dcv.SetMaterialParameters(device, region)

###
### Create the Potential solution variable
###

devsim.node_solution(device=device, region=region, name="Potential")
#devsim.add_circuit_node(name="V1", variable_update="log_damp")
###
### Creates the Potential@n0 and Potential@n1 edge model
###
devsim.edge_from_node_model(device=device, region=region, node_model="Potential")

###
### Electric field on each edge, as well as its derivatives with respect to
### the potential at each node
###
devsim.edge_model(device=device, region=region, name="ElectricField",
                  equation="(Potential@n0 - Potential@n1)*EdgeInverseLength")

devsim.edge_model(device=device, region=region, name="ElectricField:Potential@n0",
                  equation="EdgeInverseLength")

devsim.edge_model(device=device, region=region, name="ElectricField:Potential@n1",
                  equation="-EdgeInverseLength")

###
### Model the D Field
###
devsim.element_model(device=device, region=region, name="DField",
                  equation="Permittivity*ElectricField")

devsim.element_model(device=device, region=region, name="DField:Potential@en0",
                  equation="diff(Permittivity*ElectricField, Potential@n0)")

devsim.element_model(device=device, region=region, name="DField:Potential@en1",
                  equation="-DField:Potential@en0")

devsim.element_model(device=device, region=region, name="DField:Potential@en2",
                  equation="0")

###
### Create the bulk equation
###
devsim.equation(device=device, region=region, name="PotentialEquation", variable_name="Potential",
                element_model="DField", variable_update="default")

# the Pcontactbias is a circuit node, and we want to prevent it from being overridden by a parameter
devsim.set_parameter(device=device, region=region, name="Ncontactbias", value=0.0)

for name, equation in (
    ("Pcontactnode_model", "Potential - Pcontactbias"),
  ("Pcontactnode_model:Potential", "1"),
  ("Pcontactnode_model:Pcontactbias", "-1"),
  ("Ncontactnode_model", "Potential - Ncontactbias"),
  ("Ncontactnode_model:Potential", "1"),
):
    devsim.node_model(device=device, region=region, name=name, equation=equation)
# attached to circuit node
devsim.contact_equation(device=device, contact="Pcontact", name="PotentialEquation",
                        node_model="Pcontactnode_model", element_charge_model="DField", circuit_node="Pcontactbias")
# attached to ground
devsim.contact_equation(device=device, contact="Ncontact", name="PotentialEquation",
                        node_model="Ncontactnode_model", element_charge_model="DField")



#新加的代码

def CreateSolution(device, region, name):
    '''
      Creates solution variables
      As well as their entries on each edge
    '''
    devsim.node_solution(name=name, device=device, region=region)
    devsim.edge_from_node_model(node_model=name, device=device, region=region)



def DriftDiffusionInitialSolution(device, region, circuit_contacts=None):
    ####
    #### drift diffusion solution variables
    ####
    CreateSolution(device, region, "Electrons")
    CreateSolution(device, region, "Holes")

    ####
    #### create initial guess from dc only solution
    ####
    devsim.set_node_values(device=device, region=region, name="Electrons", init_from="IntrinsicElectrons")
    devsim.set_node_values(device=device, region=region, name="Holes",     init_from="IntrinsicHoles")
    #devsim.set_node_values(device=device, region=region, name="Electrons", init_from="InitialElectron")
    #devsim.set_node_values(device=device, region=region, name="Holes",     init_from="InitialHole")

    ###
    ### Set up equations
    ###
    physics.CreateSiliconDriftDiffusion(device, region)
    for i in devsim.get_contact_list(device=device):
        if circuit_contacts and i in circuit_contacts:
            physics.CreateSiliconDriftDiffusionAtContact(device, region, i, True)
        else:
            physics.CreateSiliconDriftDiffusionAtContact(device, region, i)









#
# Voltage source
#



devsim.circuit_element(name="V1", n1=1,         n2=0, value=1,acreal=1)
devsim.circuit_element(name="R1", n1="Pcontactbias", n2=1, value=1e3)


devsim.solve(type="dc", absolute_error=1.0, relative_error=1e-10, maximum_iterations=30)
#####TODO:change acreal ,but now acreal can't be changed.
v=0
ssac_voltage = []
ssac_Pcontact_cap = []

f = open("./output/sicar1_lgad_reverse_cv.csv", "w")
header = ["Voltage","Capacitance"]
writer = csv.writer(f)
writer.writerow(header)


while v<400:
    print(v)
    devsim.circuit_alter(name="V1",value=v)
    devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=30)
    print(devsim.get_contact_charge(device=device, contact="Pcontact", equation="PotentialEquation"))
    print(devsim.get_contact_charge(device=device, contact="Ncontact", equation="PotentialEquation"))
    devsim.solve(type="ac",frequency=1e12)
    cap=devsim.get_circuit_node_value(node="V1.I", solution="ssac_imag")/ (-2*math.pi)
    print("capacitance {0} {1}".format(v, cap))
    v += 1.0
    ssac_voltage.append(0-v)
    ssac_Pcontact_cap.append(cap*(1e12))

    writer.writerow([0-v,cap*(1e12)])

f.close()

fig=matplotlib.pyplot.figure(num=4,figsize=(4,4))
matplotlib.pyplot.plot(ssac_voltage, ssac_Pcontact_cap)
matplotlib.pyplot.xlabel('Voltage (V)')
matplotlib.pyplot.ylabel('Capacitance (pF)')
#matplotlib.pyplot.axis([-200, 0, 0, 20])
matplotlib.pyplot.savefig("./output/sicar1_lgad_reverse_cv.png")

