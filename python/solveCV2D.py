#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#### Small Signal simulation
import devsim
from physics2D import *
import diode_common
import math
import sys
from array import array
import ROOT
import numpy as np
import pickle
import json
import os

device="MyDevice"
region="MyRegion"
#This requires a circuit element to integrated current
devsim.circuit_element(name="V1", n1=GetContactBiasName("top"), n2=0, value=0.0, acreal=1.0, acimag=0.0)


type1="PNjuction"
with open('./output/parainprogram/config_loop.json', 'r') as f:
    params = json.load(f)
bias_v=int(params["bias_v"])
voltage= int(params["voltage"])
devsim.set_parameter(name = "extended_solver", value=True)
devsim.set_parameter(name = "extended_model", value=True)
devsim.set_parameter(name = "extended_equation", value=True)

diode_common.Create2DMesh(device, region)

diode_common.SetParameters(device=device, region=region)

diode_common.SetNetDoping(device=device, region=region,type1=type1)



    
diode_common.InitialSolution(device, region, circuit_contacts="top")
#diode_common.InitialSolution(device, region, circuit_contacts="bot")

# Initial DC solution
devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-6, maximum_iterations=1500)


diode_common.DriftDiffusionInitialSolution(device, region, circuit_contacts=["top"])
#diode_common.DriftDiffusionInitialSolution(device, region, circuit_contacts=["bot"])
if voltage>21:
    diode_common.set_values(device,region)
    
devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-6, maximum_iterations=1500)
data = []

def loop(bias_v,voltage):
    
    while bias_v < voltage:
        
        devsim.circuit_alter(name="V1", value=0-bias_v)
        devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-3, maximum_iterations=1500)

        # TODO: 获取电路信息

        devsim.solve(type="ac", frequency=1e5)
        cap = devsim.get_circuit_node_value(node="V1.I", solution="ssac_imag") / (-2 * math.pi)
        print("capacitance {0} {1}".format(bias_v, cap))
        data.append((bias_v, cap * 1e12))
        
        if bias_v > 60 and bias_v % 10 == 0:
            if not (os.path.exists("./output/devsim/2D_SICAR/")):
                os.makedirs("./output//devsim/2D_SICAR/")
            devsim.get_node_model_values(device=device, region=region, name="Potential")

            xo = np.array(devsim.get_node_model_values(device=device, region=region, name="x")) 
            zo = np.array(devsim.get_node_model_values(device=device, region=region, name="y")) 
            potential = np.array(devsim.get_node_model_values(device=device, region=region, name="Potential")) 
            do = potential
            xn = np.unique(xo)
            zn = np.unique(zo)
            xm,zm = np.meshgrid(xn,zn)

            Dm = []
            for j in zn:
                dm = []
                for i in xn:
                    do_index=np.intersect1d(np.argwhere(xo == i),np.argwhere(zo == j))
                    dm.append(float(do[do_index]))

                Dm.append(dm)
            elefieldx = []
            elefieldy = []
            print(type(xm))
            for j in range(len(Dm)):
                elex = []
                for i in range(len(Dm[j])):
                    if i+1 == len(Dm[j]):
                        elex.append(draft)
                    else:
                        elex.append((Dm[j][i+1]-Dm[j][i]) / (xm[j][i+1]-xm[j][i]))
                        draft = (Dm[j][i+1]-Dm[j][i]) / (xm[j][i+1]-xm[j][i])
                elefieldx.append(elex)
                eley = []
                if j+1 == len(xm):
                    elefieldy.append(draft2)
                else:
                    for i in range(len(xm[j])):
                        eley.append((Dm[j+1][i]) / (zm[j+1][i]-zm[j][i]))
                        draft2 = eley
                    elefieldy.append(eley)
            pointxy = []
            elefield = [[], []]
            xypotential = [[], []]
            for j in range(len(elefieldx)):
                for i in range(len(elefieldx[0])):
                    elefield[0].append(elefieldx[j][i])
                    elefield[1].append(elefieldy[j][i])
                    pointxy.append([xm[j][i], zm[j][i]])
                    xypotential[1].append(Dm[j][i])

            xypotential[0].append(pointxy)
            ele = [pointxy, elefield]
            path = "./output/devsim/2D_SICAR/" + str(bias_v) + "V_potential.pkl"
            f = open(path, "wb")
            pickle.dump(xypotential, f)
            f.close
            path = "./output/devsim/2D_SICAR/" + str(bias_v) + "V_elefield.pkl"
            f = open(path, "wb")
            pickle.dump(ele, f)
            f.close

        bias_v += 1

    diode_common.save_values(device=device,region=region)



    #存数据的代码
    file = ROOT.TFile("./output/2Dresult/Sicar1e5PINwithbufferTestCV{0}to{1}.root".format(bias_v,voltage), "RECREATE")
    tree = ROOT.TTree("SicarTestCV", "SicarTest with impactgen")


    x = array('d', [0])
    y = array('d', [0])

    tree.Branch("voltage", x, "x/D")
    tree.Branch("CAP", y, "y/D")

    for point in data:
        x[0], y[0] = point
        tree.Fill()

    file.Write()
    file.Close()

    file = ROOT.TFile("./output/2Dresult/Sicar1e5PINwithbufferTestCV{0}to{1}.root".format(bias_v,voltage), "READ")
    tree = file.Get("SicarTestCV")

    graph = ROOT.TGraph(tree.GetEntries())
    for i, entry in enumerate(tree):
        x = entry.x
        y = entry.y
        graph.SetPoint(i, x, y)

    canvas = ROOT.TCanvas("canvas", "Graph", 800, 600)
    graph.Draw("AL")

    graph.SetTitle("CAP vs Voltage")
    graph.GetXaxis().SetTitle("Voltage")
    graph.GetYaxis().SetTitle("CAP(pF)")

    canvas.Update()
    canvas.SaveAs("./output/2Dresult/Sicar1e5PINwithbufferTestCV_picture{0}to{1}.root".format(bias_v,voltage))

loop(bias_v,voltage)