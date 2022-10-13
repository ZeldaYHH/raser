#!/usr/bin/env python


import ROOT
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

myFile=ROOT.TFile("edge_voltage_2019_10_09_12_26_57_HPK-EPI-W2-200-DS-SE5-04.txt.root")
myt = myFile.Get("edge")
n = myt.Draw("-volt:time","Vbias==-200&&z==11.974","goff")
graph = ROOT.TGraph(n,myt.GetV2(),myt.GetV1())

myFile1=ROOT.TFile("edge_voltage_2019_10_09_12_26_57_HPK-EPI-W2-200-DS-SE5-04.txt.root")
myt1 = myFile.Get("edge")
n1 = myt.Draw("-volt:time","Vbias==-40&&z==11.974","goff")
graph1 = ROOT.TGraph(n1,myt1.GetV2(),myt1.GetV1())

myFile2=ROOT.TFile("edge_voltage_2019_10_09_12_26_57_HPK-EPI-W2-200-DS-SE5-04.txt.root")
myt2 = myFile.Get("edge")
n2 = myt.Draw("-volt:time","Vbias==-80&&z==11.974","goff")
graph2 = ROOT.TGraph(n2,myt2.GetV2(),myt2.GetV1())

myFile3=ROOT.TFile("edge_voltage_2019_10_09_12_26_57_HPK-EPI-W2-200-DS-SE5-04.txt.root")
myt3 = myFile.Get("edge")
n3 = myt.Draw("-volt:time","Vbias==-140&&z==11.974","goff")
graph3 = ROOT.TGraph(n3,myt3.GetV2(),myt3.GetV1())

myFile4=ROOT.TFile("edge_voltage_2019_10_09_12_26_57_HPK-EPI-W2-200-DS-SE5-04.txt.root")
myt4 = myFile.Get("edge")
n4 = myt.Draw("-volt:time","Vbias==-60&&z==11.974","goff")
graph4 = ROOT.TGraph(n4,myt4.GetV2(),myt4.GetV1())


graph.SetLineColor(1)
graph1.SetLineColor(2)
graph2.SetLineColor(3)
graph3.SetLineColor(4)
graph4.SetLineColor(6)

graph.SetMarkerStyle(1)
graph1.SetMarkerStyle(1)
graph2.SetMarkerStyle(1)
graph3.SetMarkerStyle(1)
graph4.SetMarkerStyle(1)

graph.SetMarkerColor(1)
graph1.SetMarkerColor(2)
graph2.SetMarkerColor(3)
graph3.SetMarkerColor(4)
graph4.SetMarkerColor(6)


mg.Add(graph)
mg.Add(graph1)
mg.Add(graph2)
mg.Add(graph3)
mg.Add(graph4)
mg.Draw('alp')
mg.GetYaxis().SetTitle('Amplitude/V')
mg.GetXaxis().SetTitle('Time/ns')

legend = ROOT.TLegend(0.5, 0.7, 0.78, 0.89)
legend.AddEntry(graph, "Vbias=200V", "lp")
legend.AddEntry(graph1, "Vbias=40V", "lp")
legend.AddEntry(graph2, "Vbias=80V", "lp")
legend.AddEntry(graph3, "Vbias=140V", "lp")
legend.AddEntry(graph4, "Vbias=60V", "lp")

#legend = ROOT.TLegend(0.5, 0.7, 0.78, 0.89)
legend.SetBorderSize(0)
legend.SetFillColor(0)
# legend.SetFillsStyle(303)
legend.Draw()

c.SaveAs('g1.pdf')


