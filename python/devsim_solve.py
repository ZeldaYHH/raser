#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import devsim 
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from raser import Physics
from raser import Node
from raser import Initial
from raser import Setting

import nju_pin_5mm_5mm_mesh
import hpk_pin_5mm_5mm_mesh
import sicar1_lgad_mesh
import itk_md8_mesh

import matplotlib
#matplotlib.use('Agg') 
import matplotlib.pyplot
import csv
import math
gaindoping = sys.argv[1]
bulkdoping = sys.argv[2]
#bulk_thickness = sys.argv[1]
if not (os.path.exists("./output/devsim")):
    os.makedirs("./output/devsim")

# Area factor
# 1D 1cm*1cm
# DUT 5mm* 5mm
area_factor = 4.0
ITK_MD8_doping="eee"

def main():
    devsim.open_db(filename="./output/devsim/SICARDB", permission="readonly")
    para_dict = set_para(sys.argv[1:])

    if "device" in para_dict:
        device=para_dict["device"]
        region=para_dict["device"]
    else:
        raise KeyError

    if "v_max" in para_dict:
        v_max = float(para_dict["v_max"])
    else:
        raise ValueError

    if "Rirr" in para_dict:
        device = "1D_ITK_MD8"
        region = "1D_ITK_MD8"
        itk_md8_mesh.Create1DMesh(device=device, region=region)
        Rirrad=para_dict["Rirr"]
        itk_md8_mesh.SetDoping(device=device, region=region)
        extend_set()
        initial_solution_Rirr(device,region,para_dict,Rirr=Rirrad)
        solve_iv_Rirr(device,region,Rirrad,v_max,para_dict)
        return 0

    if "backdopingtest" in para_dict:
        device = "1D_ITK_MD8"
        region = "1D_ITK_MD8"
        itk_md8_mesh.Create1DMesh(device=device, region=region)
        backthickness=para_dict["backthickness"]
        back_doping=para_dict["backdopingtest"]
        itk_md8_mesh.SetDoping(device=device, region=region,backthickness=backthickness, back_doping=back_doping)
        extend_set()
        initial_solution(device,region,para_dict)
        solve_iv_backtest(device,region,v_max,para_dict,backthickness,back_doping)
        return 0



    
    set_mesh(device,region)
    extend_set()
    initial_solution(device,region,para_dict)

    if "defect" in para_dict:
        set_defect(para_dict)



            
    if "IV" in para_dict:
        solve_iv(device,region,v_max,para_dict)
    if "CV" in para_dict:
        solve_cv(device,region,v_max,para_dict,frequency=1e3)


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
    elif device == "1D_HPK_PIN":
        device_mesh = hpk_pin_5mm_5mm_mesh
    elif device == "1D_ITK_MD8":
        device_mesh = itk_md8_mesh
    device_mesh.Create1DMesh(device=device, region=region)
    device_mesh.SetDoping(device=device, region=region)
    device_mesh.Draw_Doping(device=device, region=region, path="./output/devsim/1D_SICAR1_LGAD_gaindoping_{0}_bulkdoping_{1}.png".format(gaindoping,bulkdoping))
    #device_mesh.Draw_Doping(device=device, region=region, path="./output/devsim/1D_SICAR1_LGAD_bulk_thickness_{0}.png".format(bulk_thickness))
def extend_set():
    devsim.set_parameter(name = "extended_solver", value=True)
    devsim.set_parameter(name = "extended_model", value=True)
    devsim.set_parameter(name = "extended_equation", value=True)
    devsim.circuit_element(name="V1", n1=Physics.GetContactBiasName("top"), n2=0, value=0.0, acreal=1.0, acimag=0.0)

def initial_solution(device,region,para_dict):
    # Initial DC solution
    
    Initial.InitialSolution(device, region, circuit_contacts="top")
    devsim.solve(type="dc", absolute_error=1.0, relative_error=1e-10, maximum_iterations=50)


    if "irradiation" in para_dict:
        if device == "1D_ITK_MD8":
            Initial.DriftDiffusionInitialSolutionSiIrradiated(device, region, circuit_contacts="top")
            devsim.set_parameter(device=device, name=Physics.GetContactBiasName("top"), value=0)

        else:
            Initial.DriftDiffusionInitialSolutionIrradiated(device, region, circuit_contacts="top")
    else:
    ### Drift diffusion simulation at equilibrium
        Initial.DriftDiffusionInitialSolution(device, region, circuit_contacts="top")
        devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=50)
    """names        = ["E30K"   , "V3"      , "Ip"      , "H220"    , "CiOi"    ]
        g_ints       = [0.0497   , 0.6447    , 0.4335    , 0.5978    , 0.3780    ]
        for Neutron_eq in range(int(2e11),int(5e11),int(1e11)):
            for name, g_int in zip(names, g_ints):
                N_t_irr = g_int*Neutron_eq
                devsim.add_db_entry(material="global",   parameter="N_t_irr_"+name,     value=N_t_irr,   unit="cm^(-3)",     description="N_t_"+name)
            devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-5, maximum_iterations=400)
            print("Neutron_eq="+str(Neutron_eq))"""
    devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-5, maximum_iterations=400,maximum_divergence=300)
        
def initial_solution_Rirr(device,region,para_dict,Rirr=None):
    # Initial DC solution
    
    Initial.InitialSolution(device, region, circuit_contacts="top")
    devsim.solve(type="dc", absolute_error=1.0, relative_error=1e-10, maximum_iterations=50)


    if "irradiation" in para_dict:
        if device == "1D_ITK_MD8":
            Initial.DriftDiffusionInitialSolutionSiIrradiated(device, region, Rirr,circuit_contacts="top")
            #devsim.set_parameter(device=device, name=Physics.GetContactBiasName("top"), value=0)
            GGGddd=devsim.get_node_model_values(device=device, region=region, name="ElectronGeneration")
            GGGaaa=devsim.get_node_model_values(device=device, region=region, name="HoleGeneration")
            # print("Gd="+str(GGGddd)+"\n")
            # print("Ga="+str(GGGaaa)+"\n")
        else:
            Initial.DriftDiffusionInitialSolutionIrradiated(device, region, circuit_contacts="top")
    else:
    ### Drift diffusion simulation at equilibrium
        Initial.DriftDiffusionInitialSolution(device, region, circuit_contacts="top")
        GGGddd=devsim.get_node_model_values(device=device, region=region, name="ElectronGeneration")
        GGGaaa=devsim.get_node_model_values(device=device, region=region, name="HoleGeneration")
        # print("Gd="+str(GGGddd)+"\n")
        # print("Ga="+str(GGGaaa)+"\n")
        devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=50)
    devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-5, maximum_iterations=50,maximum_divergence=50)
 

        
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
    global area_factor
    condition = ""
    if "irradiation" in para_dict:
        condition += "_irradiation"
    if "defect" in para_dict:
        condition += "_defect"
        for key in ["N_t","sigma_n","sigma_p","N_t_HS6","sigma_n_HS6","sigma_p_HS6"]:
            condition += "_{}={}".format(key,para_dict[key])
    reverse_v = 0.0
    reverse_voltage = []
    reverse_top_current = []
    reverse_bot_current = []

    v_max_field=v_max

    f_iv = open("./output/devsim/{}_reverse_iv_gaindoping_{}_bulkdoping_{}.csv".format(device+condition,gaindoping,bulkdoping), "w")
    header_iv = ["Voltage","Current"]
    writer_iv = csv.writer(f_iv)
    writer_iv.writerow(header_iv)

    #devsim.delete_node_model(device=device, region=region, name="IntrinsicElectrons")
    #devsim.delete_node_model(device=device, region=region, name="IntrinsicHoles")
    
    if device == "1D_ITK_MD8":
        
        args111 = ["det_name=ITk-Si-strip","parfile=paras/setting.json"]
        dset111 = Setting(args111)
        det_dic111 = dset111.detector    
        doping1=det_dic111['doping']
        ITK_MD8_doping=doping1
        area_factor = 1.0/(0.8*0.8)
#        f_md8iv = open("./output/devsim/"+device+"_"+"irr_new"+"/"+device+condition+"1e11neq_reverse_iv.csv", "w")
        f_md8iv = open("./output/devsim/withback"+device+"_"+"3.2e12"+"/test0.1um1e17"+device+condition+"3.2e12_reverse_iv.csv", "w")
        header_md8iv = ["Voltage","Current"]
        writer_md8iv = csv.writer(f_md8iv)
        writer_md8iv.writerow(header_md8iv)
        devsim.set_parameter(device=device,   name="tau_n",  value=3e-2)
        devsim.set_parameter(device=device,   name="tau_p",  value=3e-2)



    positions_mid = []
    intensities = []
    bias_voltages = []

    positions = []
    electrons = []
    holes = []

    while reverse_v < v_max:
        reverse_top_total_current = solve_iv_single_point(device,region,reverse_v)
        reverse_top_current.append(abs(reverse_top_total_current))

        writer_iv.writerow([0-reverse_v,abs(reverse_top_total_current/area_factor)])
        if device == "1D_ITK_MD8":
            writer_md8iv.writerow([reverse_v,abs(reverse_top_total_current/area_factor)])        


        voltage_step = 100
        if(reverse_v%voltage_step==0.0 and reverse_v<=v_max_field):
            devsim.edge_average_model(device=device, region=region, node_model="x", edge_model="xmid")
            x_mid = devsim.get_edge_model_values(device=device, region=region, name="xmid") # get x-node values 
            E = devsim.get_edge_model_values(device=device, region=region, name="ElectricField") # get y-node values
            V = reverse_v

            x = devsim.get_node_model_values(device=device, region=region, name="x") # get x-node values 
            n = devsim.get_node_model_values(device=device, region=region, name="Electrons")
            p = devsim.get_node_model_values(device=device, region=region, name="Holes")

            positions_mid.append(x_mid)
            intensities.append(E)
            bias_voltages.append(V)

            positions.append(x)
            electrons.append(n)
            holes.append(p)


        if device == "1D_ITK_MD8":
            reverse_voltage.append(reverse_v)
        else:
            reverse_voltage.append(0-reverse_v)
        reverse_v += 1


    f_iv.close()
    if device == "1D_ITK_MD8":
        f_md8iv.close()
    devsim.close_db()

    draw_iv(reverse_voltage, reverse_top_current, device, condition)
    draw_ele_field(device, positions_mid, intensities, bias_voltages, condition)
    draw_electrons(device, positions, electrons, bias_voltages, condition)
    draw_holes(device, positions, holes, bias_voltages, condition)
    save_ele_field(device, positions, intensities, bias_voltages, condition)


def solve_iv_backtest(device,region,v_max,para_dict,backthickness,back_doping):
    global area_factor
    condition = ""
    if "irradiation" in para_dict:
        condition += "_irradiation"
    if "defect" in para_dict:
        condition += "_defect"
        for key in ["N_t","sigma_n","sigma_p","N_t_HS6","sigma_n_HS6","sigma_p_HS6"]:
            condition += "_{}={}".format(key,para_dict[key])
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
    
    if device == "1D_ITK_MD8":
        
        args111 = ["det_name=ITk-Si-strip","parfile=paras/setting.json"]
        dset111 = Setting(args111)
        det_dic111 = dset111.detector    
        doping1=det_dic111['doping']
        ITK_MD8_doping=doping1
        area_factor = 1.0/(0.8*0.8)
#        f_md8iv = open("./output/devsim/"+device+"_"+"irr_new"+"/"+device+condition+"1e11neq_reverse_iv.csv", "w")
        f_md8iv = open("./output/devsim/withback"+device+"_"+"3.2e12"+"/"+backthickness+"umstop"+back_doping+device+condition+"3.2e12_reverse_iv.csv", "w")
        header_md8iv = ["Voltage","Current"]
        writer_md8iv = csv.writer(f_md8iv)
        writer_md8iv.writerow(header_md8iv)
        devsim.set_parameter(device=device,   name="tau_n",  value=3e-2)
        devsim.set_parameter(device=device,   name="tau_p",  value=3e-2)



    positions_mid = []
    intensities = []
    bias_voltages = []

    positions = []
    electrons = []
    holes = []

    while reverse_v < v_max:
        reverse_top_total_current = solve_iv_single_point(device,region,reverse_v)
        reverse_top_current.append(abs(reverse_top_total_current))

        writer_iv.writerow([0-reverse_v,abs(reverse_top_total_current/area_factor)])
        if device == "1D_ITK_MD8":
            writer_md8iv.writerow([reverse_v,abs(reverse_top_total_current/area_factor)])        


        voltage_step = 100
        if(reverse_v%voltage_step==0.0 and reverse_v<=v_max_field):
            devsim.edge_average_model(device=device, region=region, node_model="x", edge_model="xmid")
            x_mid = devsim.get_edge_model_values(device=device, region=region, name="xmid") # get x-node values 
            E = devsim.get_edge_model_values(device=device, region=region, name="ElectricField") # get y-node values
            V = reverse_v

            x = devsim.get_node_model_values(device=device, region=region, name="x") # get x-node values 
            n = devsim.get_node_model_values(device=device, region=region, name="Electrons")
            p = devsim.get_node_model_values(device=device, region=region, name="Holes")

            positions_mid.append(x_mid)
            intensities.append(E)
            bias_voltages.append(V)

            positions.append(x)
            electrons.append(n)
            holes.append(p)


        if device == "1D_ITK_MD8":
            reverse_voltage.append(reverse_v)
        else:
            reverse_voltage.append(0-reverse_v)
        reverse_v += 1


    f_iv.close()
    if device == "1D_ITK_MD8":
        f_md8iv.close()
    devsim.close_db()

    draw_iv(reverse_voltage, reverse_top_current, device, condition)
    draw_ele_field(device, positions_mid, intensities, bias_voltages, condition)
    draw_electrons(device, positions, electrons, bias_voltages, condition)
    draw_holes(device, positions, holes, bias_voltages, condition)
    save_ele_field(device, positions, intensities, bias_voltages, condition)


def solve_iv_Rirr(device,region,Rirr,v_max,para_dict):
    global area_factor
    condition = ""
    if "irradiation" in para_dict:
        condition += "_irradiation"
    if "defect" in para_dict:
        condition += "_defect"
        for key in ["N_t","sigma_n","sigma_p","N_t_HS6","sigma_n_HS6","sigma_p_HS6"]:
            condition += "_{}={}".format(key,para_dict[key])
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
    
    if device == "1D_ITK_MD8":
        
        args111 = ["det_name=ITk-Si-strip","parfile=paras/setting.json"]
        dset111 = Setting(args111)
        det_dic111 = dset111.detector    
        doping1=det_dic111['doping']
        ITK_MD8_doping=doping1
        area_factor = 1.0/(0.8*0.8)
        f_md8iv = open("./output/devsim/"+device+"_"+"irr_new"+"/"+device+condition+"_reverse_iv_"+Rirr+".csv", "w")
        header_md8iv = ["Voltage","Current"]
        writer_md8iv = csv.writer(f_md8iv)
        writer_md8iv.writerow(header_md8iv)


    positions_mid = []
    intensities = []
    bias_voltages = []

    positions = []
    electrons = []
    holes = []

    while reverse_v < v_max:
        reverse_top_total_current = solve_iv_single_point(device,region,reverse_v)
        reverse_top_current.append(abs(reverse_top_total_current))

        writer_iv.writerow([0-reverse_v,abs(reverse_top_total_current/area_factor)])
        if device == "1D_ITK_MD8":
            writer_md8iv.writerow([reverse_v,abs(reverse_top_total_current/area_factor)])        


        voltage_step = 100
        if(reverse_v%voltage_step==0.0 and reverse_v<=v_max_field):
            devsim.edge_average_model(device=device, region=region, node_model="x", edge_model="xmid")
            x_mid = devsim.get_edge_model_values(device=device, region=region, name="xmid") # get x-node values 
            E = devsim.get_edge_model_values(device=device, region=region, name="ElectricField") # get y-node values
            V = reverse_v

            x = devsim.get_node_model_values(device=device, region=region, name="x") # get x-node values 
            n = devsim.get_node_model_values(device=device, region=region, name="Electrons")
            p = devsim.get_node_model_values(device=device, region=region, name="Holes")

            positions_mid.append(x_mid)
            intensities.append(E)
            bias_voltages.append(V)

            positions.append(x)
            electrons.append(n)
            holes.append(p)


        if device == "1D_ITK_MD8":
            reverse_voltage.append(reverse_v)
        else:
            reverse_voltage.append(0-reverse_v)
        reverse_v += 1


    f_iv.close()
    if device == "1D_ITK_MD8":
        f_md8iv.close()
    devsim.close_db()

    draw_iv(reverse_voltage, reverse_top_current, device, condition)
    draw_ele_field(device, positions_mid, intensities, bias_voltages, condition)
    draw_electrons(device, positions, electrons, bias_voltages, condition)
    draw_holes(device, positions, holes, bias_voltages, condition)
    save_ele_field(device, positions, intensities, bias_voltages, condition)



def solve_cv(device,region,v_max,para_dict,frequency):
    condition = ""
    if "irradiation" in para_dict:
        condition += "_irradiation"
    if "defect" in para_dict:
        condition += "_defect"
        for key in ["N_t","sigma_n","sigma_p","N_t_HS6","sigma_n_HS6","sigma_p_HS6"]:
            condition += "_{}={}".format(key,para_dict[key])
    reverse_v = 0.0
    reverse_voltage = []
    ssac_top_cap = []

    f_cv = open("./output/devsim/{}_reverse_cv_gaindoping_{}_bulkdoping_{}.csv".format(device+condition,gaindoping,bulkdoping), "w")
    header_cv = ["Voltage","Capacitance"]
    writer_cv = csv.writer(f_cv)
    writer_cv.writerow(header_cv)

    while reverse_v < v_max:
        capacitance = solve_cv_single_point(device,region,reverse_v,frequency)
        ssac_top_cap.append(capacitance*(1e12)/area_factor)

        writer_cv.writerow([0-reverse_v,capacitance*(1e12)/area_factor])
        reverse_voltage.append(0-reverse_v)
        reverse_v += 1

    f_cv.close()
    devsim.close_db()
    draw_cv(reverse_voltage, ssac_top_cap, device,condition)

def solve_iv_single_point(device,region,reverse_v):
    if device == "1D_ITK_MD8":
        devsim.set_parameter(device=device, name=Physics.GetContactBiasName("top"), value=reverse_v)
    else:
        devsim.set_parameter(device=device, name=Physics.GetContactBiasName("top"), value=0-reverse_v)
    devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-5, maximum_iterations=100,maximum_divergence=50)
    # try:
    #     devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-5, maximum_iterations=200,maximum_divergence=50)
    # except devsim.error as msg:
    #     if msg=="Convergence failure!":
    #         raise
    Physics.PrintCurrents(device, "top")
    Physics.PrintCurrents(device, "bot")
    reverse_top_electron_current= devsim.get_contact_current(device=device, contact="top", equation="ElectronContinuityEquation")
    reverse_top_hole_current    = devsim.get_contact_current(device=device, contact="top", equation="HoleContinuityEquation")
    reverse_top_total_current   = reverse_top_electron_current + reverse_top_hole_current

    return reverse_top_total_current

def solve_cv_single_point(device,region,reverse_v,frequency):
    devsim.circuit_alter(name="V1", value=0-reverse_v)
    devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-5, maximum_iterations=200)
    Physics.PrintCurrents(device, "bot")
    devsim.solve(type="ac", frequency=frequency)
    cap=devsim.get_circuit_node_value(node="V1.I", solution="ssac_imag")/ (-2*math.pi*frequency)
    print("capacitance {0} {1}".format(reverse_v, cap))
    return cap

def draw_iv(V,I,device,condition):
    fig2=matplotlib.pyplot.figure()
    matplotlib.pyplot.semilogy(V,I)
    matplotlib.pyplot.xlabel('Voltage (V)')
    matplotlib.pyplot.ylabel('Current (A)')
    #matplotlib.pyplot.axis([min(reverse_voltage), max(reverse_voltage), 1e-9, 1e-2])
    #if device == "1D_ITK_MD8":
    #    fig2.savefig("./output/devsim/{device}_{ITK_MD8_doping}/{device}_{condition}_reverse_iv.png".format(device=device,ITK_MD8_doping=ITK_MD8_doping,condition=condition))
    fig2.savefig("./output/devsim/{0}_reverse_iv_gain_doping_{1}_bulk_{2}.png".format(device+condition,gaindoping,bulkdoping))
    fig2.clear()

def draw_cv(V,C,device,condition):
    fig3=matplotlib.pyplot.figure(num=4,figsize=(4,4))
    matplotlib.pyplot.plot(V, C)
    matplotlib.pyplot.xlabel('Voltage (V)')
    matplotlib.pyplot.ylabel('Capacitance (pF)')
    #matplotlib.pyplot.axis([-200, 0, 0, 20])
    fig3.savefig("./output/devsim/{0}_reverse_cv_gain_doping_{1}_bulk_{2}.png".format(device+condition,gaindoping,bulkdoping))
    fig3.clear()

    fig4=matplotlib.pyplot.figure(num=4,figsize=(4,4))
    C_minus2 = []
    for c in C:
        C_minus2.append(1/c**2)
    matplotlib.pyplot.plot(V, C_minus2)
    matplotlib.pyplot.xlabel('Voltage (V)')
    matplotlib.pyplot.ylabel('1/C^2 (pF^{-2})')
    #matplotlib.pyplot.axis([-200, 0, 0, 20])
    fig4.savefig("./output/devsim/{}_reverse_c^-2v.png".format(device+condition))
    fig4.clear()

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
    fig1.clear()

def draw_electrons(device, positions, electrons, bias_voltages, condition):
    fig1=matplotlib.pyplot.figure()
    ax1 = fig1.add_subplot(111)
    for (x,n,V) in zip(positions, electrons, bias_voltages):
        matplotlib.pyplot.plot(x,n,label="%s"%(str(V)))
    matplotlib.pyplot.xlabel('Depth [cm]')
    matplotlib.pyplot.ylabel('Electron Density [cm^{-3}]')
    matplotlib.pyplot.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
    ax1.legend(loc='upper right')
    if device == "1D_SICAR1_LGAD":
        ax1.set_xlim(0,5e-4)
    fig1.show()
    fig1.savefig("./output/devsim/{}_reverse_electrons.png".format(device+condition))
    fig1.clear()

def draw_holes(device, positions, holes, bias_voltages, condition):
    fig1=matplotlib.pyplot.figure()
    ax1 = fig1.add_subplot(111)
    for (x,p,V) in zip(positions, holes, bias_voltages):
        matplotlib.pyplot.plot(x,p,label="%s"%(str(V)))
    matplotlib.pyplot.xlabel('Depth [cm]')
    matplotlib.pyplot.ylabel('Hole Density [cm^{-3}]')
    matplotlib.pyplot.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
    ax1.legend(loc='upper right')
    if device == "1D_SICAR1_LGAD":
        ax1.set_xlim(0,5e-4)
    fig1.show()
    fig1.savefig("./output/devsim/{}_reverse_holes.png".format(device+condition))
    fig1.clear()

def save_ele_field(device, positions,intensities, bias_voltages,condition):
    if not (os.path.exists("./output/devsim/{}/".format(device+condition))):
        os.makedirs("./output/devsim/{}/".format(device+condition))
    for (x,E,V) in zip(positions,intensities, bias_voltages):
        header_iv = ["Depth [cm]","E (V/cm)"]
        f=open("./output/devsim/{}/".format(device+condition)+str(V)+'V_x_E.csv','w')
        writer_E = csv.writer(f)
        writer_E.writerow(header_iv)
        for (per_x,per_E) in zip(x,E):
            writer_E.writerow([float(per_x),float(per_E)])

if __name__ == "__main__":
    main()