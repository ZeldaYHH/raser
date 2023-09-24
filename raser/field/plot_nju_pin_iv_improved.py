#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import ROOT
import math
from array import array

g_sim = ROOT.TGraph("./output/devsim/nju_pin_reverse_iv.csv","-%lf,%lf")
g_data = ROOT.TGraph("/afs/ihep.ac.cn/users/l/lizaiyi/data/NJU-4H-SiC-PIN-8-IV-R.csv","%lf,%*lf,%lf")

g_data.SetNameTitle("")
g_data.SetLineWidth(0)
g_data.SetMarkerColor(ROOT.kBlue)
g_data.SetMarkerStyle(4)
g_data.SetMarkerSize(1)

g_sim.SetLineWidth(4)
g_sim.SetLineStyle(ROOT.kSolid)

g_data.GetXaxis().SetLimits(0,800)
g_data.GetXaxis().SetTitle("Reverse Bias Voltage [V]")
g_data.GetXaxis().CenterTitle()
g_data.GetXaxis().SetTitleOffset(1.4)
g_data.GetXaxis().SetTitleSize(0.05)
g_data.GetXaxis().SetLabelSize(0.05)
g_data.GetXaxis().SetNdivisions(505)
g_data.GetYaxis().SetRangeUser(1e-13,1e-5)
g_data.GetYaxis().SetTitle("Current [A]")
g_data.GetYaxis().CenterTitle()
g_data.GetYaxis().SetTitleOffset(1.8)
g_data.GetYaxis().SetTitleSize(0.05)
g_data.GetYaxis().SetLabelSize(0.05)
#first plot 0-800V logy
c = ROOT.TCanvas("c","c",500,500)
c.SetLeftMargin(0.22)
c.SetBottomMargin(0.16)

legend = ROOT.TLegend(0.27,0.72,0.70,0.85)
legend.SetTextSize(0.04)
legend.AddEntry(g_data,"measurement")
legend.AddEntry(g_sim,"simulation")

c.cd()
c.SetLogy()
g_data.Draw("AP")
g_sim.Draw("C")
legend.Draw("SAME")
c.SaveAs("./output/nju_pin_iv_improved.pdf")

#plot linear axis 450-800V
c1 = ROOT.TCanvas("c1","c1",500,500)
c1.SetLeftMargin(0.22)
c1.SetBottomMargin(0.16)
c1.cd()
#c1.SetLogy()
g_data.GetXaxis().SetLimits(450,800)
g_data.GetYaxis().SetRangeUser(1e-8,1e-7)
g_data.Draw("AP")
g_sim.Draw("C")
legend.Draw("SAME")
c1.SaveAs("./output/nju_pin_iv_improved_linear.pdf")
