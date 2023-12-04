#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import devsim
from . import physics_2d
from .build_device import Detector
import math
import sys
from array import array
import ROOT
import numpy as np
import pickle
import json
import os
simname=sys.argv[1]
device=simname
region=simname

#This requires a circuit element to integrated current
devsim.circuit_element(name="V1", n1=physics_2d.GetContactBiasName("top"), n2=0, value=0.0, acreal=1.0, acimag=0.0)
areafactor=10000

with open('./output/parainprogram/config_loop.json', 'r') as f:
    params = json.load(f)
bias_v=float(params["bias_v"])
voltage= float(params["voltage"])


devsim.set_parameter(name = "extended_solver", value=True)
devsim.set_parameter(name = "extended_model", value=True)
devsim.set_parameter(name = "extended_equation", value=True)

MyDetector = Detector(simname)

physics_2d.SetSiliconParameters(device, region, 300)
    
physics_2d.InitialSolution(device, region, circuit_contacts="top")
#diode_common.InitialSolution(device, region, circuit_contacts="bot")

# Initial DC solution
devsim.solve(type="dc", absolute_error=1e30, relative_error=1e-3, maximum_iterations=1500)

#physics_2d.DriftDiffusionInitialSolution(device, region, circuit_contacts="top")
physics_2d.SiDriftDiffusionInitialSolution(device, region, circuit_contacts="top")
#diode_common.DriftDiffusionInitialSolution(device, region, circuit_contacts=["bot"])
devsim.delete_node_model(device=device, region=region, name="IntrinsicElectrons")
devsim.delete_node_model(device=device, region=region, name="IntrinsicHoles")

devsim.solve(type="dc", absolute_error=1e30, relative_error=1e-3, maximum_iterations=1500)
data = []
def loop(bias_v,voltage):
    
    while bias_v < voltage:
        
        devsim.circuit_alter(name="V1", value=0-bias_v)
        devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-3, maximum_iterations=1500)

        # TODO: 获取电路信息

        devsim.solve(type="ac", frequency=1e6)
        cap = devsim.get_circuit_node_value(node="V1.I", solution="ssac_imag") / (-2 * math.pi)
        print("capacitance {0} {1}".format(bias_v, cap))
        data.append((bias_v, cap * 1e12 /areafactor ))
        bias_v += 1
      

    
    # 指定文件夹路径
    folder_path = "./output/2Dresult/sim{0}".format(simname)

    # 检查文件夹是否存在，如果不存在则创建
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)





    #存数据的代码
    file = ROOT.TFile("./output/2Dresult/sim{0}/simCV{1}to{2}.root".format(simname,bias_v,voltage), "RECREATE")
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

    file = ROOT.TFile("./output/2Dresult/sim{0}/simCV{1}to{2}.root".format(simname,bias_v,voltage), "READ")
    tree = file.Get("SicarTestCV")

    graph = ROOT.TGraph(tree.GetEntries())
    for i, entry in enumerate(tree):
        x = entry.x
        y = entry.y
        graph.SetPoint(i, x, y)

    canvas = ROOT.TCanvas("canvas", "Graph", 800, 600)
    graph.SetMarkerStyle(ROOT.kFullCircle)
    graph.SetMarkerSize(0.5)
    graph.SetMarkerColor(ROOT.kBlue)
    graph.SetLineColor(ROOT.kWhite)
    graph.Draw("AP")

    graph.SetTitle("CAP vs Voltage")
    graph.GetXaxis().SetTitle("Voltage")
    graph.GetYaxis().SetTitle("CAP(pF)")

    canvas.Update()
    canvas.SaveAs("./output/2Dresult/sim{0}/simCV{1}to{2}_picture.root".format(simname,bias_v,voltage) )
    canvas.SaveAs("./output/2Dresult/sim{0}/simCV{1}to{2}_picture.pdf".format(simname,bias_v,voltage))
   

loop(bias_v,voltage)
