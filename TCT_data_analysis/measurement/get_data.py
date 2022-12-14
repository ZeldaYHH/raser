#!/usr/bin/env python
import sys
import os
import math
import ROOT
from array import array
from ROOT import gStyle, TCanvas, TString, TChain, TStyle
from ROOT import THStack, TH1D, TFile, TLegend
import numpy

c = ROOT.TCanvas('c', '', 800, 600)
c.SetFillColor(0)
c.SetFrameFillColor(0)
ROOT.gStyle.SetPadColor(0)
ROOT.gStyle.SetCanvasColor(0)
ROOT.gStyle.SetOptStat(0)
c.SetLeftMargin(0.15)
c.SetRightMargin(0.15)
c.SetTopMargin(0.1)
c.SetBottomMargin(0.15)

myFile = ROOT.TFile("edge_voltage_2019_10_24_15_12_57_HPK-EPI-W2-200-DS-SE5PINNM-01.txt.root")
myt = myFile.Get("edge")
n = myt.Draw("BlineMean:z","Vbias==-200&&z>11.984&&z<12.036","goff")
graph = ROOT.TGraph(n,myt.GetV2(),myt.GetV1())
graph.Draw('apl')
c.SaveAs('g1.pdf')

v1=array("d")
t1=array("d") 
for i in range(51):
    t1.append(graph.GetPointY(i))

print(t1)   






































































