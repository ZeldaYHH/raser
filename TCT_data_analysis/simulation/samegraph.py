#!/usr/bin/env python
import sys
import os
import math
import ROOT
from array import array
from ROOT import gStyle, TCanvas, TString, TChain, TStyle
from ROOT import THStack, TH1D, TFile, TLegend


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

mg=ROOT.TMultiGraph("mg","")

myFile = ROOT.TFile("edge_voltage_2019_10_24_15_12_57_HPK-EPI-W2-200-DS-SE5PINNM-01.txt.root")
myt = myFile.Get("edge")
n = myt.Draw("-volt:(time-10.9)","Vbias==-200&&z==12.005&&((time-10.6)>0)&&((time-10.6)<10)","goff")
graph2 = ROOT.TGraph(n,myt.GetV2(),myt.GetV1())
v2=array("d")
t2=array("d")

for i in range(199):
    t2.append(graph2.GetPointX(i))
    v2.append(graph2.GetPointY(i))

myFile1 = ROOT.TFile("sim-TCT4.root")
myt1 = myFile1.Get("tree")
n1 = myt1.Draw("-volt:time*1000000000","","goff")
#graph1 = ROOT.TGraph(n1,myt1.GetV2(),myt1.GetV1())
#graph1.Draw('apl')
v1=array("d")
t1=array("d")
#for entry in myt1:
#    v1.append(-entry.volt)
#    t1.append(1000000000*entry.time)
graph1 = ROOT.TGraph(192,myt1.GetV2(),myt1.GetV1())



graph2.SetLineColor(1)
graph1.SetLineColor(2)
graph2.SetMarkerColor(1)
graph1.SetMarkerColor(2)
graph2.SetMarkerStyle(1)
graph1.SetMarkerStyle(1)


mg.Add(graph1)
mg.Add(graph2)
mg.Draw('alp')
mg.GetYaxis().SetTitle('Amplitude/V')
mg.GetXaxis().SetTitle('Time/s')

legend = ROOT.TLegend(0.5, 0.7, 0.78, 0.89)
legend.AddEntry(graph1, "sim-TCT", "lp")
legend.AddEntry(graph2, "TCT", "lp")
#legend = ROOT.TLegend(0.5, 0.7, 0.78, 0.89)
legend.SetBorderSize(0)
legend.SetFillColor(0)
# legend.SetFillsStyle(303)
legend.Draw()



c.SaveAs('g1.pdf')

