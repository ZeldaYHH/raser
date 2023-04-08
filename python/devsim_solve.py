#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import devsim 
import os
import sys

from raser import Physics
from raser import Node
from raser import Initial

import nju_pin_5mm_5mm_mesh
import sicar1_lgad_mesh

import matplotlib
#matplotlib.use('Agg') 
import matplotlib.pyplot
import csv
import math

if not (os.path.exists("./output/devsim")):
    os.makedirs("./output/devsim")

# Area factor
# 1D 1cm*1cm
# DUT 5mm* 5mm
area_factor = 4.0

def main():
    devsim.open_db(filename="./output/devsim/SICARDB", permission="readonly")
    para_dict = set_para(sys.argv[1:])
    if "device" in para_dict:
        device=para_dict["device"]
        region=para_dict["device"]
    else:
        raise KeyError
    
    set_mesh(device,region)
    extend_set()
    initial_solution(device,region,para_dict)

    if "defect" in para_dict:
        set_defect(para_dict)

    if "v_max" in para_dict:
        v_max = float(para_dict["v_max"])
    else:
        raise ValueError

    if "IV" in para_dict:
        solve_iv(device,region,v_max,para_dict)
    if "CV" in para_dict:
        solve_cv(device,region,v_max,para_dict)

def set_para(para_list):
    para_dict={}
    for para in para_list:
        # device=1D_NJU_PIN 
        # IV=True CV=True 
        # defect=True irradiation=True (Default to be False, "False"==True)
        # v_max=800 v_step=1
        key,_,value=para.rpartition('=')
        para_dict[key]=value
    return para_dict

def set_mesh(device,region):
    if device == "1D_NJU_PIN":
        device_mesh = nju_pin_5mm_5mm_mesh
    elif device == "1D_SICAR1_LGAD":
        device_mesh = sicar1_lgad_mesh
    device_mesh.Create1DMesh(device=device, region=region)
    device_mesh.SetDoping(device=device, region=region)
    device_mesh.Draw_Doping(device=device, region=region, path="./output/devsim/{}_doping.png".format(device))

def extend_set():
    devsim.set_parameter(name = "extended_solver", value=True)
    devsim.set_parameter(name = "extended_model", value=True)
    devsim.set_parameter(name = "extended_equation", value=True)
    devsim.circuit_element(name="V1", n1=Physics.GetContactBiasName("top"), n2=0, value=0.0, acreal=1.0, acimag=0.0)

def initial_solution(device,region,para_dict):
    # Initial DC solution
    Initial.InitialSolution(device, region, circuit_contacts="top")
    devsim.solve(type="dc", absolute_error=1.0, relative_error=1e-10, maximum_iterations=50)

    ### Drift diffusion simulation at equilibrium
    Initial.DriftDiffusionInitialSolution(device, region, circuit_contacts="top")
    devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=50)

    if "irradiation" in para_dict:
        Initial.DriftDiffusionInitialSolutionIrradiated(device, region, circuit_contacts="top")
        devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-5, maximum_iterations=200)

def set_defect(paras):
    #Z_1/2
    devsim.add_db_entry(material="global",   parameter="sigma_n",     value=float(paras["sigma_n"]),   unit="s/cm^2",     description="sigma_n")
    devsim.add_db_entry(material="global",   parameter="sigma_p",     value=float(paras["sigma_p"]),   unit="s/cm^2",     description="sigma_p")
    devsim.add_db_entry(material="global",   parameter="N_t",     value=float(paras["N_t"]),   unit="cm^(-3)",     description="N_t")
    #EH_6/7
    devsim.add_db_entry(material="global",   parameter="sigma_n_HS6",     value=float(paras["sigma_n_HS6"]),   unit="s/cm^2",     description="sigma_n_HS6")
    devsim.add_db_entry(material="global",   parameter="sigma_p_HS6",     value=float(paras["sigma_p_HS6"]),   unit="s/cm^2",     description="sigma_p_HS6")
    devsim.add_db_entry(material="global",   parameter="N_t_HS6",     value=float(paras["N_t_HS6"]),   unit="cm^(-3)",     description="N_t_HS6")

def solve_iv(device,region,v_max,para_dict):
    condition = ""
    if "irradiation" in para_dict:
        condition += "_irradiation"
    if "defect" in para_dict:
        condition += "_defect"
        for key in ["N_t","sigma_n","sigma_p","N_t_HS6","sigma_n_HS6","sigma_p_HS6"]:
            condition += "{}={}".format(key,para_dict[key])
    reverse_v = 0.0
    reverse_voltage = []
    reverse_top_current = []
    reverse_bot_current = []

    v_max_field=v_max

    f_iv = open("./output/devsim/{}_reverse_iv.csv".format(device+condition), "w")
    header_iv = ["Voltage","Current"]
    writer_iv = csv.writer(f_iv)
    writer_iv.writerow(header_iv)

    #devsim.delete_node_model(device=device, region=region, name="IntrinsicElectrons")
    #devsim.delete_node_model(device=device, region=region, name="IntrinsicHoles")

    positions = []
    intensities = []
    bias_voltages = []

    while reverse_v < v_max:
        reverse_top_total_current = solve_iv_single_point(device,region,reverse_v)
        reverse_top_current.append(abs(reverse_top_total_current))

        writer_iv.writerow([0-reverse_v,abs(reverse_top_total_current/area_factor)])

        if(reverse_v%100.0==0 and reverse_v<v_max_field):
            devsim.edge_average_model(device=device, region=region, node_model="x", edge_model="xmid")
            x = devsim.get_edge_model_values(device=device, region=region, name="xmid") # get x-node values 
            E = devsim.get_edge_model_values(device=device, region=region, name="ElectricField") # get y-node values
            V = reverse_v
            positions.append(x)
            intensities.append(E)
            bias_voltages.append(V)

        reverse_voltage.append(0-reverse_v)
        reverse_v += 1

        # breakdown
        if(abs(reverse_top_total_current/area_factor) > 1e3): break

    f_iv.close()
    devsim.close_db()

    draw_iv(reverse_voltage, reverse_top_current, device, condition)
    draw_ele_field(device, positions,intensities, bias_voltages,condition)

def solve_cv(device,region,v_max,para_dict):
    condition = ""
    if "irradiation" in para_dict:
        condition += "_irradiation"
    if "defect" in para_dict:
        condition += "_defect"
        for key in ["N_t","sigma_n","sigma_p","N_t_HS6","sigma_n_HS6","sigma_p_HS6"]:
            condition += "{}={}".format(key,para_dict[key])
    reverse_v = 0.0
    reverse_voltage = []
    ssac_top_cap = []

    f_cv = open("./output/devsim/{}_reverse_cv.csv".format(device+condition), "w")
    header_cv = ["Voltage","Capacitance"]
    writer_cv = csv.writer(f_cv)
    writer_cv.writerow(header_cv)

    while reverse_v < v_max:
        capacitance = solve_cv_single_point(device,region,reverse_v)
        ssac_top_cap.append(capacitance*(1e12)/area_factor)

        writer_cv.writerow([0-reverse_v,capacitance*(1e12)/area_factor])
        reverse_voltage.append(0-reverse_v)
        reverse_v += 1

    f_cv.close()
    devsim.close_db()
    draw_cv(reverse_voltage, ssac_top_cap, device,condition)

def solve_iv_single_point(device,region,reverse_v):
    devsim.set_parameter(device=device, name=Physics.GetContactBiasName("top"), value=0-reverse_v)
    devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-5, maximum_iterations=200)
    Physics.PrintCurrents(device, "top")
    Physics.PrintCurrents(device, "bot")
    reverse_top_electron_current= devsim.get_contact_current(device=device, contact="top", equation="ElectronContinuityEquation")
    reverse_top_hole_current    = devsim.get_contact_current(device=device, contact="top", equation="HoleContinuityEquation")
    reverse_top_total_current   = reverse_top_electron_current + reverse_top_hole_current

    return reverse_top_total_current

def solve_cv_single_point(device,region,reverse_v):
    devsim.circuit_alter(name="V1", value=0-reverse_v)
    devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-5, maximum_iterations=200)
    Physics.PrintCurrents(device, "bot")
    devsim.solve(type="ac", frequency=1.0)
    cap=devsim.get_circuit_node_value(node="V1.I", solution="ssac_imag")/ (-2*math.pi)
    print("capacitance {0} {1}".format(reverse_v, cap))
    return cap

def draw_iv(V,I,device,condition):
    fig2=matplotlib.pyplot.figure()
    matplotlib.pyplot.semilogy(V,I)
    matplotlib.pyplot.xlabel('Voltage (V)')
    matplotlib.pyplot.ylabel('Current (A)')
    #matplotlib.pyplot.axis([min(reverse_voltage), max(reverse_voltage), 1e-9, 1e-2])
    fig2.savefig("./output/devsim/{}_reverse_iv.png".format(device+condition))

def draw_cv(V,C,device,condition):
    fig3=matplotlib.pyplot.figure(num=4,figsize=(4,4))
    matplotlib.pyplot.plot(V, C)
    matplotlib.pyplot.xlabel('Voltage (V)')
    matplotlib.pyplot.ylabel('Capacitance (pF)')
    #matplotlib.pyplot.axis([-200, 0, 0, 20])
    fig3.savefig("./output/devsim/{}_reverse_cv.png".format(device+condition))

def draw_ele_field(device, positions,intensities, bias_voltages,condition):
    fig1=matplotlib.pyplot.figure()
    ax1 = fig1.add_subplot(111)
    for (x,E,V) in zip(positions,intensities, bias_voltages):
        matplotlib.pyplot.plot(x,E,label="%s"%(str(V)))
    matplotlib.pyplot.xlabel('Depth [cm]')
    matplotlib.pyplot.ylabel('E (V/cm)')
    matplotlib.pyplot.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
    ax1.legend(loc='upper right')
    if device == "1D_SICAR1_LGAD":
        ax1.set_xlim(0,5e-4)
    fig1.show()
    fig1.savefig("./output/devsim/{}_reverse_electricfield.png".format(device+condition))

if __name__ == "__main__":
    main()