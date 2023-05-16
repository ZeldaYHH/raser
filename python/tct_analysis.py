#!/usr/bin/env python3

"""
author: wanghaobo
time: 2022.12.25
Use: 1.Read the data of Raser eTCT induced current
     2.Add experimental noise on induced current
     3.Get the risertime,charge collection and velocity profile
"""

from array import array
import contextlib
import os
import sys
import ROOT
import math
import numpy as np
import drawsave

def main():
    path=sys.argv[1]
    output_path=path+"result/"
    drawsave.create_path(output_path)
    if 'LGAD' in path:
        pulse_energy_scale = 1.58
    else:
        pulse_energy_scale = 1
    # the pulse energy difference in experiment

    if "experiment" in sys.argv:
        amplitude, charge, risetime, elefield, peaktime, basetime, Z ,volts, times= collect_data(path, "sim-TCT", pulse_energy_scale, 1e9)
        amplitude_exp, charge_exp, risetime_exp, elefield_exp, peaktime_exp, basetime_exp, Z_exp, volts_exp, times_exp= collect_data(path, "exp-TCT", 1, 1)
        draw_double_graphs(amplitude,amplitude_exp,Z,"Amplitude",output_path)
        draw_double_graphs(charge,charge_exp,Z,"Charge",output_path)
        draw_double_graphs(risetime,risetime_exp,Z,"RiseTime",output_path)
        draw_double_graphs(elefield,elefield_exp,Z,"Elefield",output_path)
        draw_double_graphs(peaktime,peaktime_exp,Z,"PeakTime",output_path)
        draw_double_graphs(basetime,basetime_exp,Z,"BaseTime",output_path)

        for volt,time,volt_exp,time_exp,z in zip(volts, times, volts_exp, times_exp, list(Z)):
            draw_double_signals(time,time_exp,volt,volt_exp,z,path)

    else:
        amplitude, charge, risetime, elefield, peaktime, basetime, Z ,volts, times= collect_data(path, "sim-TCT", pulse_energy_scale, 1e9)
        draw_graphs(amplitude,Z,"Amplitude",output_path)
        draw_graphs(charge,Z,"Charge",output_path)
        draw_graphs(risetime,Z,"RiseTime",output_path)
        draw_graphs(elefield,Z,"Elefield",output_path)
        draw_graphs(peaktime,Z,"PeakTime",output_path)
        draw_graphs(basetime,Z,"BaseTime",output_path)

def collect_data(path, model, volt_scale, time_scale):
    Z= array("d")
    amplitude= array("d")
    risetime= array("d")
    charge= array("d")
    elefield= array("d")
    peaktime= array("d")
    basetime= array("d")
    volts = []
    times = []
    baseline = 0

    sum_k=0
    sum_l=0

    for L in range(-10,61):

        rel_z = round(0.02*L,2)
        volt=array("d",[0.])
        time=array("d",[0.])
        rootfile=path+model+str(rel_z)+".root"
        print(str(rootfile))
        volt,time=read_rootfile(rootfile,volt_scale,time_scale)
        mean=0
        J=len(volt)
        k,l=get_average(volt,time,J,mean)
        if rel_z>=0 and rel_z<=1:
            sum_k+=k      
            sum_l+=l

    k=int(round(np.true_divide(sum_k,51)))
    l=int(round(np.true_divide(sum_l,51)))
    print("k=",k,"l=",l)

    for L in range(-10,61):
        rel_z = round(0.02*L,2)
        Z.append(L)

        volt=array("d",[0.])
        time=array("d",[0.])
        rootfile=path+model+str(rel_z)+".root"
        volt,time=read_rootfile(rootfile, volt_scale, time_scale)
        volts.append(volt)
        times.append(time)
        J=len(volt)

        amplitude.append(get_amplitude(volt,J))
        charge.append(get_charge(volt,J))
        elefield.append(get_elefield(volt,k,l,charge))
        risetime.append(get_risetime(volt,time,J))
        peaktime.append(get_peaktime(volt,time,J))
        basetime.append(get_basetime(volt,time,J))  
      
    return amplitude, charge, risetime, elefield, peaktime, basetime, Z, volts, times

def read_rootfile(rootfile,volt_scale,time_scale):
    J=0
    v1=array("d")
    t1=array("d")
    myFile = ROOT.TFile(str(rootfile))
    myt = myFile.tree
    for entry in myt:
       v1.append(volt_scale*entry.volt)
       t1.append(time_scale*entry.time)
       J=J+1
    return v1,t1

def add_noise(rootfile,J,v1,t1):
    v2=array("d",[0.])
    t2=array("d",[0.])
    noise=np.array([0])
    fout = ROOT.TFile("noise_"+str(rootfile), "RECREATE")
    t_out = ROOT.TTree("tree", "signal")
    t_out.Branch("volt", v2, "volt/D")
    t_out.Branch("time", t2, "time/D")
    for i in range(J):
          t2[0]=t1[i]
          v2[0]=v1[i]+noise[i]
          t_out.Fill()
    t_out.Write()
    fout.Close()
    
def get_average(volt,time,J,baseline):
    Vmax=max(volt)
    for k in range(1,J):
        if (volt[k-1] - baseline)<0.2*(Vmax - baseline)<(volt[k] - baseline):
            break
    for l in range(J-1):
        if (volt[l] - baseline)<0.4*(Vmax - baseline)<(volt[l+1] - baseline):
            break
    return k,l

def get_elefield(volt,k,l,charge):
    sum_volt=0
    for j in range(k,l+1):
        sum_volt+=volt[j]
    if charge[-1] > 0:
        return sum_volt/(l+1-k)
    else:
        return 0

def get_amplitude(volt,J):
    Vmax = max(volt)
    for Max in range(J):
        if volt[Max] - Vmax > -1e-5*Vmax:
            break
    for min in range(Max,0,-1):
        if volt[min-1] > volt[min]:
            #Vmin = volt[min]
            Vmin = 0
            break
        else:
            #Vmin = volt[0]
            Vmin = 0
    return(Vmax-Vmin)

def get_charge(volt,J):
    sum_charge=0
    for j in range(J):
        sum_charge+=volt[j]
    return sum_charge

def get_peaktime(volt,time,J):
    Vmax=max(volt)
    for k in range(J):
        if volt[k] - Vmax > -1e-5*Vmax:
            break
    return time[k]

def get_basetime(volt,time,J):
    Vmax=max(volt)
    for Max in range(J):
        if volt[Max] - Vmax > -1e-5*Vmax:
            break
    for min in range(Max,0,-1):
        if volt[min-1] > volt[min] and volt[min]<0.1*Vmax:
            break
    return time[min]

def get_risetime(volt,time,J):
    x=array("d")
    y=array("d")
    Vmax=max(volt)
    for Max in range(J):
        if volt[Max] - Vmax > -1e-5*Vmax:
            break
    for min in range(Max,0,-1):
        if volt[min-1] > volt[min]and volt[min]<0.1*Vmax:
            Vmin = volt[min]
            break
        else:
            Vmin = volt[0]
    for k in range(J):
        if (volt[k] - Vmin)<0.2*(Vmax - Vmin)<(volt[k+1] - Vmin):
            break
    for l in range(J):
        if (volt[l-1] - Vmin)<0.8*(Vmax - Vmin)<(volt[l] - Vmin):
            break
    n=l-k
    for j in range(k,l+1):
        x.append(time[j])
        y.append(volt[j])

    graph1 = ROOT.TGraph(n,x,y)
    f=ROOT.TF1("f","[0]+[1]*x",0,2)
    graph1.Fit(f,"Q")
    b=f.GetParameter(1)
    c=f.GetParameter(0)
    e1=np.true_divide((0.2*(Vmax-Vmin)-c),b)
    e2=np.true_divide((0.8*(Vmax-Vmin)-c),b)
    risetime=np.true_divide((e2-e1),0.6)
    return risetime

def draw_graphs(array1,Z,name,path):
    n=len(array1)
    g = ROOT.TCanvas('g', '', 800, 600)
    g.SetFillColor(0)
    g.SetFrameFillColor(0)
    ROOT.gStyle.SetPadColor(0)
    ROOT.gStyle.SetCanvasColor(0)
    ROOT.gStyle.SetOptStat(0)
    g.SetLeftMargin(0.15)
    g.SetRightMargin(0.15)
    g.SetTopMargin(0.1)
    g.SetBottomMargin(0.15)

    graph=ROOT.TGraph(n,Z,array1)
    graph.SetMarkerStyle(3)
    graph.Draw('ap')

    legend = ROOT.TLegend(0.6,0.7, 0.83, 0.89)
    legend.AddEntry(graph,"RASER Simulation", "p")
    legend.SetTextSize(18)
    legend.SetTextFont(43)
    legend.SetBorderSize(0)
    legend.SetFillColor(0)
    legend.Draw()

    g.SaveAs(path+name+".pdf")
  
    return

def draw_double_graphs(array1,array2,Z,name,path):
    c = ROOT.TCanvas('c', '', 800, 600)
    c.SetFillColor(0)
    c.SetFrameFillColor(0)
    ROOT.gStyle.SetPadColor(0)
    ROOT.gStyle.SetCanvasColor(0)
    ROOT.gStyle.SetOptStat(0)
    c.SetLeftMargin(0.15)
    c.SetBottomMargin(0.15)

    mg=ROOT.TMultiGraph("mg","")
    n1=len(array1)
    graph1 = ROOT.TGraph(n1,Z,array1)
    n2=len(array2)
    graph2 = ROOT.TGraph(n2,Z,array2)

    graph1.SetLineColor(2)
    graph2.SetLineColor(1)
    graph1.SetMarkerColor(2)
    graph2.SetMarkerColor(1)
    graph1.SetMarkerStyle(26)
    graph2.SetMarkerStyle(4)

    mg.Add(graph1)
    mg.Add(graph2)
    mg.Draw('ap')

    if name == 'Amplitude':
        Y_title = 'Amplitude [V]'
        if 'LGAD' in path:
            mg.GetYaxis().SetRangeUser(0,1.13)
        else:
            mg.GetYaxis().SetRangeUser(0,0.04)

    if name == 'Charge':
        Y_title = 'Charge [a.u.]'
        if 'LGAD' in path:
            mg.GetYaxis().SetRangeUser(0,28)
        else:
            mg.GetYaxis().SetRangeUser(0,1.0)

    if name == 'Elefield':
        Y_title = 'Ve+Vh [a.u.]'
        if 'LGAD' in path:
            mg.GetYaxis().SetRangeUser(0,0.6)
        else:
            mg.GetYaxis().SetRangeUser(0,0.012)

    if name == 'RiseTime':
        Y_title = 'RiseTime [ns]'
        if 'LGAD' in path:
            mg.GetYaxis().SetRangeUser(0,1.5)
        else:
            mg.GetYaxis().SetRangeUser(0,1.5)

    if name == 'PeakTime':
        Y_title = 'PeakTime [ns]'
        if 'LGAD' in path:
            mg.GetYaxis().SetRangeUser(1.0,3.0)
        else:
            mg.GetYaxis().SetRangeUser(1.0,3.0)

    if name == 'BaseTime':
        Y_title = 'BaseTime [ns]'
        if 'LGAD' in path:
            mg.GetYaxis().SetRangeUser(0,1.5)
        else:
            mg.GetYaxis().SetRangeUser(0,1.5)
    
    
    mg.GetYaxis().SetTitle(Y_title)
    mg.GetXaxis().SetTitle('z [um]')
    mg.GetYaxis().SetLabelSize(0.05)
    mg.GetYaxis().SetTitleSize(0.05)
    mg.GetXaxis().SetLabelSize(0.05)
    mg.GetXaxis().SetTitleSize(0.05)

    legend = ROOT.TLegend(0.45,0.65, 0.81, 0.86)
    legend.AddEntry(graph1, "RASER simulation", "p")
    legend.AddEntry(graph2, "TCT measurement", "p")
    legend.SetTextSize(27)
    legend.SetTextFont(43)

    legend.SetBorderSize(0)
    legend.SetFillColor(0)
    legend.Draw()

    c.SaveAs(path+name+"_comparison.pdf")

def draw_double_signals(time_1,time_2,signal_1,signal_2,z,path):
    c = ROOT.TCanvas('c', '', 800, 600)
    c.SetFillColor(0)
    c.SetFrameFillColor(0)
    ROOT.gStyle.SetPadColor(0)
    ROOT.gStyle.SetCanvasColor(0)
    ROOT.gStyle.SetOptStat(0)
    c.SetLeftMargin(0.15)
    c.SetBottomMargin(0.15)

    mg=ROOT.TMultiGraph("mg","")
    n1=len(time_1)
    graph1 = ROOT.TGraph(n1,time_1,signal_1)
    n2=len(time_2)
    graph2 = ROOT.TGraph(n2,time_2,signal_2)

    graph1.SetLineColor(2)
    graph2.SetLineColor(1)
    graph1.SetMarkerColor(2)
    graph2.SetMarkerColor(1)
    graph1.SetMarkerStyle(26)
    graph2.SetMarkerStyle(4)

    mg.Add(graph1)
    mg.Add(graph2)
    mg.Draw('ap')
    
    mg.GetYaxis().SetTitle('signal [V]')
    mg.GetXaxis().SetTitle('time [ns]')
    mg.GetYaxis().SetLabelSize(0.05)
    mg.GetYaxis().SetTitleSize(0.05)
    mg.GetXaxis().SetLabelSize(0.05)
    mg.GetXaxis().SetTitleSize(0.05)

    mg.GetXaxis().SetLimits(0,10)

    legend = ROOT.TLegend(0.45,0.65, 0.81, 0.86)
    legend.AddEntry(graph1, "RASER simulation", "p")
    legend.AddEntry(graph2, "TCT measurement", "p")
    legend.SetTextSize(27)
    legend.SetTextFont(43)

    legend.SetBorderSize(0)
    legend.SetFillColor(0)
    legend.Draw()

    c.SaveAs(path+str(z)+"_comparison.pdf")


if __name__ == "__main__":
    main()
