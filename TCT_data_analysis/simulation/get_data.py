#!/usr/bin/env python3
import sys
import os
import math
import ROOT
from array import array
from ROOT import gStyle, TCanvas, TString, TChain, TStyle
from ROOT import THStack, TH1D, TFile, TLegend

volt=array("d",[0.])
v1=array("d",[0.])
t1=array("d",[0.])
q1=array("d",[0.])
r1=array("d",[0.])
e1=array("d",[0.])



time=array("d",[0.])
Vmax=array("d",[0.])
t2=array("d",[0.])
noise=array("d")
L=1
RiseTime=array('d',[0.])
E=array('d',[0.])
Qtot=array('d',[0.])



fout = ROOT.TFile("end.root", "RECREATE")
t_out = ROOT.TTree("tree", "signal")
t_out.Branch("RiseTime", RiseTime, "RiseTime/D")
t_out.Branch("Vmax", Vmax, "Vmax/D")
t_out.Branch("Qtot", Qtot,"Qtot/D")
t_out.Branch("E", E,"E/D")


    
for L in range(51):
    t2.append(L)
    v1.append(L)
    r1.append(L)
    q1.append(L)
    e1.append(L)
#    print(v1)
    myFile = ROOT.TFile("TCT"+str(L)+".root")
    myFile.cd()
    myt = myFile.tree
    q=0
    e=0  
    for entry in myt:
        v1[L]=entry.Vmax
        r1[L]=entry.RiseTime
        q1[L]=entry.Qtot
        e1[L]=entry.E
    
    Vmax[0]=v1[L]
    RiseTime[0]=r1[L]
    E[0]=e1[L]
    Qtot[0]=q1[L]
    t_out.Fill()
t_out.Write()
fout.Close()
print(q1)
print(e1)









