#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import ROOT
import math
from array import array

g_1 = ROOT.TGraph("./output/devsim/nju_pin_reverse_iv.csv","%lf,%lf")
g_2 = ROOT.TGraph("./output/devsim/nju_pin_reverse_iv0.csv","%lf,%lf")
g_3 = ROOT.TGraph("./output/devsim/nju_pin_reverse_iv1.csv","%lf,%lf")
g_4 = ROOT.TGraph("./output/devsim/nju_pin_reverse_iv2.csv","%lf,%lf")
g_5 = ROOT.TGraph("./output/devsim/nju_pin_reverse_iv3.csv","%lf,%lf")
mg = ROOT.TMultiGraph()

g_1.SetNameTitle("")
g_1.SetLineWidth(2)
g_1.SetLineColor(ROOT.kGray+3)
g_1.SetMarkerColor(ROOT.kGray+3)
g_1.SetMarkerStyle(21)
g_1.SetMarkerSize(1)

g_2.SetLineWidth(2)
g_2.SetLineColor(ROOT.kOrange+7)
g_2.SetMarkerColor(ROOT.kOrange+7)
g_2.SetMarkerStyle(21)
g_2.SetMarkerSize(1)

g_3.SetLineWidth(2)
g_3.SetLineColor(ROOT.kOrange)
g_3.SetMarkerColor(ROOT.kOrange)
g_3.SetMarkerStyle(21)
g_3.SetMarkerSize(1)

g_4.SetLineWidth(2)
g_4.SetLineColor(ROOT.kSpring+3)
g_4.SetMarkerColor(ROOT.kSpring+3)
g_4.SetMarkerStyle(21)
g_4.SetMarkerSize(1)

g_5.SetLineWidth(2)
g_5.SetLineColor(ROOT.kAzure+2)
g_5.SetMarkerColor(ROOT.kAzure+2)
g_5.SetMarkerStyle(21)
g_5.SetMarkerSize(1)

mg.Add(g_1)
mg.Add(g_2)
mg.Add(g_3)
mg.Add(g_4)
mg.Add(g_5)

mg.GetXaxis().SetRangeUser(-805,5)
mg.GetXaxis().SetTitle("Reverse Voltage [V]")
mg.GetXaxis().CenterTitle()
mg.GetXaxis().SetTitleOffset(1.4)
mg.GetXaxis().SetTitleSize(0.05)
mg.GetXaxis().SetLabelSize(0.05)
mg.GetXaxis().SetNdivisions(505)
mg.GetYaxis().SetRangeUser(5e-27,2e-24)
mg.GetYaxis().SetTitle("Current [A]")
mg.GetYaxis().CenterTitle()
mg.GetYaxis().SetTitleOffset(1.8)
mg.GetYaxis().SetTitleSize(0.05)
mg.GetYaxis().SetLabelSize(0.05)

c = ROOT.TCanvas("c","c",500,500)
c.SetLeftMargin(0.22)
c.SetBottomMargin(0.16)
c.SetGrid()
c.SetFrameLineWidth(5)
legend = ROOT.TLegend(0.25+0.32,0.2,0.6+0.27,0.55)
legend.SetTextSize(0.03)
legend.AddEntry(g_1,"N_{ t (Z_{ 1/2})} = 0 cm^{-3}")
legend.AddEntry(g_2,"N_{ t (Z_{ 1/2})} =10^{12}cm^{-3}")
legend.AddEntry(g_3,"N_{ t (Z_{ 1/2})} =10^{13}cm^{-3}")
legend.AddEntry(g_4,"N_{ t (Z_{ 1/2})} =10^{14}cm^{-3}")
legend.AddEntry(g_5,"N_{ t (Z_{ 1/2})} =10^{15}cm^{-3}")

c.cd()
c.SetLogy()

mg.Draw("ALP")
legend.Draw("SAME")

c.SaveAs("./output/devsim/Z12-Nt.pdf")
