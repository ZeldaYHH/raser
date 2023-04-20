#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import time
import os
from array import array
import ROOT

def T1():
    current_SiC = array("d")
    T_SiC = array("d")

    myFile = ROOT.TFile("output/pintct/NJU-PIN/sim-TCT-current-50.root")
    myt = myFile.tree
    for entry in myt:
        current_SiC.append(entry.current0 * 1e3)
        T_SiC.append(entry.time * 1e9)

    volt_ele = array("d")
    T_ele = array("d")

    myFile = ROOT.TFile("output/pintct/NJU-PIN/sim-TCT-50.root")
    myt = myFile.tree
    for entry in myt:
        volt_ele.append(entry.volt)
        T_ele.append(entry.time * 1e9)

    c_max = min(current_SiC)
    for i in range(0, len(current_SiC)):
        if current_SiC[i] < c_max * 0.05:
            t1 = T_SiC[i]
            for j in range(i, len(current_SiC)):
                if current_SiC[j] == c_max:
                    t2 = T_SiC[j]
                if current_SiC[j] > c_max * 0.05:
                    t3 = T_SiC[j]
                    break
            break

    t_start = t1
    t_rise = t2 - t1
    t_fall = t3 - t2

    now = time.strftime("%Y_%m%d_%H%M")

    path = os.path.join("fig", str(now))
    os.makedirs(path)
    
    volt_out = array("d")
    T_out = array("d")
    with open('output/t1.raw') as f:
        lines = f.readlines()
        for line in lines:
            volt_out.append(float(line.split()[1]) * 1e3)
            T_out.append(float(line.split()[0]) * 1e9)

    current_in = array("d")
    T_in = array("d")
    t_in = 0
    c_in = 0
    while t_in < T_ele[len(T_ele) - 1]:
        if t_in >= t_start and t_in < t_start + t_rise:
            current_in.append(c_in)
            T_in.append(t_in)
            c_in = c_in + c_max * 0.05/t_rise
            t_in = t_in + 0.05
        elif t_in >= t_start + t_rise and t_in < t_start + t_rise + t_fall:
            current_in.append(c_in)
            T_in.append(t_in)
            c_in = c_in - c_max * 0.05/t_fall
            t_in = t_in + 0.05
        else:
            current_in.append(0)
            T_in.append(t_in)
            t_in = t_in + 0.05
    
    length_SiC = len(T_SiC)
    length_ele = len(T_ele)
    length_in = len(T_in)
    length_out = len(T_out)
    print(len(T_out))
    print(len(volt_out))
    print(T_ele[length_ele - 1])

    with open(os.path.join(path, 'volt_out.csv'), 'w') as f:
        lines = []
        lines.append('v(V),t(ns)\n')
        for i in range(0,length_out):
            lines.append(str(volt_out[i]) + ',' + str(T_out[i]) + '\n')
        f.writelines(lines)
        f.close()

    ROOT.gROOT.SetBatch()    
    c = ROOT.TCanvas('c','c',700,600)

    f1 = ROOT.TGraph(length_ele, T_ele, volt_ele)
    f2 = ROOT.TGraph(length_SiC, T_SiC, current_SiC)
    f3 = ROOT.TGraph(length_in, T_in, current_in)
    f4 = ROOT.TGraph(length_out, T_out, volt_out)

    f1.SetLineColor(2)
    f1.SetLineWidth(2)

    f1.GetXaxis().SetTitle('Time [ns]')
    f1.GetXaxis().SetLimits(0, T_ele[length_ele - 1])
    f1.GetXaxis().CenterTitle()
    f1.GetXaxis().SetTitleSize(0.05)
    f1.GetXaxis().SetTitleOffset(0.8)

    f1.GetYaxis().SetTitle('Current [uA]')
    f1.GetYaxis().SetLimits(0,min(volt_ele))
    f1.GetYaxis().CenterTitle()
    f1.GetYaxis().SetTitleSize(0.05)
    f1.GetYaxis().SetTitleOffset(0.7)

    f2.SetLineColor(8)
    f2.SetLineWidth(2)

    f3.SetLineColor(4)
    f3.SetLineWidth(2)

    f4.SetLineColor(6)
    f4.SetLineWidth(2)
    
    legend = ROOT.TLegend(0.5, 0.3, 0.8, 0.6)
    legend.AddEntry(f1, "voltage:simulation", "l")
    legend.AddEntry(f2, "current:e+h", "l")
    legend.AddEntry(f3, "current:T1-input", "l")
    legend.AddEntry(f4, "voltage:T1-output", "l")
    legend.SetBorderSize(0)

    c.Update()
    c.cd()

    f1.Draw('AL')
    f2.Draw('L')
    f3.Draw('L')
    f4.Draw('L')
    legend.Draw("same")

    c.SaveAs(os.path.join('fig', str(now), 't1.pdf'))
    

if __name__ == '__main__':
    T1()