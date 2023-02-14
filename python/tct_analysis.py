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
   drawsave.create_path(path)
   Z= array("d")
   amplitude= array("d")
   risetime= array("d")
   charge= array("d")
   elefield= array("d")
   sum_k=0
   sum_l=0

   for L in range(51):
      volt=array("d",[0.])
      time=array("d",[0.])
      Z.append(L)     
      rootfile=path + "sim-TCT"+str(L)+".root"
      print(str(rootfile))
      volt,time=read_rootfile(rootfile)
      mean=0
      J=len(volt)
      amplitude.append(max(volt))
      k,l=get_average(volt,time,J,mean)
      sum_k+=k      
      sum_l+=l
   k=int(round(np.true_divide(sum_k,51)))
   l=int(round(np.true_divide(sum_l,51)))

   for L in range(51):
      volt=array("d",[0.])
      time=array("d",[0.])
      sum_v=0
      rootfile=path + "sim-TCT"+str(L)+".root"
      volt,time=read_rootfile(rootfile)
      J=len(volt)
      field=get_elefield(volt,k,l)
      elefield.append(field)
      cha=get_charge(volt,J)
      charge.append(cha)
      rt=get_risetime(volt,time,J,mean)
      risetime.append(rt)  
      
   draw_graphs(amplitude,Z,"Amplitude",path)
   draw_graphs(charge,Z,"Charge",path)
   draw_graphs(risetime,Z,"RiseTime",path)
   draw_graphs(elefield,Z,"Elefield",path)
   return

def read_rootfile(rootfile):
    J=0
    v1=array("d")
    v2=array("d",[0.])
    t1=array("d")
    t2=array("d",[0.])
    noise=np.array([0])
    myFile = ROOT.TFile(str(rootfile))
    myt = myFile.tree
    mean=0
    for entry in myt:
       v1.append(entry.volt)
       t1.append(1000000000*entry.time)
       J=J+1
    return v1,t1    

def add_noise(v1,t1):
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

def get_average(volt,time,J,mean):
    Vmax=max(volt)
    for k in range(1,J):
      if (volt[k-1] - mean)<0.4*(Vmax-mean)<(volt[k] - mean) and time[k]>0.5:
         break
    for l in range(J-1):
      if (volt[l] - mean)<0.6*(Vmax - mean)<(volt[l+1] - mean):
         break
    return k,l 

def get_elefield(volt,k,l):
    sum_volt=0
    for j in range(k,l+1):
         sum_volt+=volt[j]    
    return sum_volt

def get_charge(volt,J):
    sum_charge=0
    for j in range(J):
        sum_charge+=volt[j]
    return sum_charge

def get_risetime(volt,time,J,mean):
    x=array("d")
    y=array("d")
    Vmax=max(volt)
    for k in range(1,J):
      if (volt[k-1] - mean)<0.2*(Vmax-mean)<(volt[k] - mean) and time[k]>0.5:
         break
    for l in range(J-1):
      if (volt[l] - mean)<0.8*(Vmax - mean)<(volt[l+1] - mean):
         break
    n=l-k+1
    for j in range(k,l+1):
         x.append(time[j])
         y.append(volt[j])
    graph1 = ROOT.TGraph(n,x,y)
    f=ROOT.TF1("f","[0]+[1]*x",0,2)
    graph1.Fit(f)
    b=f.GetParameter(1)
    c=f.GetParameter(0)
    e1=np.true_divide((0.2*(Vmax-mean)-c),b)
    e2=np.true_divide((0.8*(Vmax-mean)-c),b)
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
if __name__ == "__main__":
    main()
