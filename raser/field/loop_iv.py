#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import devsim
import physics_2d
import build_2d_device
import math
import sys
from array import array
import ROOT
import numpy as np
import pickle
import json
import os



areafactor=250

simname=sys.argv[1]


device="MyDevice"
region="MyRegion"
with open('./output/parainprogram/config_loopiv.json', 'r') as f:
    params = json.load(f)
bias_v=float(params["bias_v"])
voltage= float(params["voltage"])

devsim.set_parameter(name = "extended_solver", value=True)
devsim.set_parameter(name = "extended_model", value=True)
devsim.set_parameter(name = "extended_equation", value=True)

build_2d_device.Create2DMesh(device, region,simname)

build_2d_device.SetParameters(device=device, region=region)

build_2d_device.SetNetDoping(device=device, region=region,simname=simname)


physics_2d.InitialSolution(device, region, circuit_contacts=False)
#diode_common.InitialSolution(device, region, circuit_contacts="bot")

# Initial DC solution
devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=1500)


physics_2d.DriftDiffusionInitialSolution(device, region, circuit_contacts=False)
#diode_common.DriftDiffusionInitialSolution(device, region, circuit_contacts=["bot"])
devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=1500)



data = []
def loop(bias_v,voltage):   
    while bias_v < voltage:
        devsim.set_parameter(device=device, name=physics_2d.GetContactBiasName("top"), value=0-bias_v)
        devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-6, maximum_iterations=1500)
        physics_2d.PrintCurrents(device, "top")
        physics_2d.PrintCurrents(device, "bot")
        reverse_top_electron_current= devsim.get_contact_current(device=device, contact="top", equation="ElectronContinuityEquation")
        reverse_top_hole_current    = devsim.get_contact_current(device=device, contact="top", equation="HoleContinuityEquation")
        #reverse_bot_electron_current= devsim.get_contact_current(device=device, contact="bot", equation="ElectronContinuityEquation")
        #reverse_bot_hole_current    = devsim.get_contact_current(device=device, contact="bot", equation="HoleContinuityEquation")
        reverse_top_total_current   = reverse_top_electron_current + reverse_top_hole_current   
        #reverse_bot_total_current   = reverse_bot_electron_current + reverse_bot_hole_current
        reverse_total_current =   reverse_top_total_current 
        # TODO: 获取电路信息
        
        data.append((bias_v,  abs(reverse_total_current)*25))
        bias_v += 1

    # 指定文件夹路径
    folder_path = "./output/2Dresult/sim{0}".format(simname)

    # 检查文件夹是否存在，如果不存在则创建
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)





    #存数据的代码
    file = ROOT.TFile("./output/2Dresult/sim{0}/simIV{1}to{2}.root".format(simname,bias_v,voltage), "RECREATE")
    tree = ROOT.TTree("SicarTestIV", "SicarTest with impactgen")


    x = array('d', [0])
    y = array('d', [0])

    tree.Branch("voltage", x, "x/D")
    tree.Branch("Current", y, "y/D")

    for point in data:
        x[0], y[0] = point
        tree.Fill()

    file.Write()
    file.Close()

    file = ROOT.TFile("./output/2Dresult/sim{0}/simIV{1}to{2}.root".format(simname,bias_v,voltage), "READ")
    tree = file.Get("SicarTestIV")

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

    graph.SetTitle("Current vs Voltage")
    graph.GetXaxis().SetTitle("Voltage(V)")
    graph.GetYaxis().SetTitle("Current(A)")

    canvas.Update()
    canvas.SaveAs("./output/2Dresult/sim{0}/simIV{1}to{2}_picture.root".format(simname,bias_v,voltage))
   
loop(bias_v,voltage)