#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import ROOT
import math
from array import array

g_sim = ROOT.TGraph("./output/devsim/nju_pin_reverse_iv.csv","%lf,%lf")
g_data = ROOT.TGraph("/afs/ihep.ac.cn/users/l/lizaiyi/data/nju_pin_iv_r.csv","%lf,%lf")
mg=ROOT.TMultiGraph()

g_data.SetNameTitle("")
g_data.SetLineWidth(0)
g_data.SetMarkerColor(ROOT.kBlue)
g_data.SetMarkerStyle(4)
g_data.SetMarkerSize(4)

g_sim.SetLineWidth(4)
g_sim.SetLineStyle(ROOT.kDashed)

mg.add(g_data)
mg.add(g_sim)

mg.GetXaxis().SetLimits(450,800)
mg.GetXaxis().SetTitle("Reverse Bias Voltage [V]")
mg.GetXaxis().CenterTitle()
mg.GetXaxis().SetTitleOffset(1.4)
mg.GetXaxis().SetTitleSize(0.05)
mg.GetXaxis().SetLabelSize(0.05)
mg.GetXaxis().SetNdivisions(505)
mg.GetYaxis().SetRangeUser(1e-11,1e-6)
#g_sim.GetYaxis().SetRangeUser(20,300)
mg.GetYaxis().SetTitle("Current [A]")
mg.GetYaxis().CenterTitle()
mg.GetYaxis().SetTitleOffset(1.8)
mg.GetYaxis().SetTitleSize(0.05)
mg.GetYaxis().SetLabelSize(0.05)

c = ROOT.TCanvas("c","c",500,500)
c.SetLeftMargin(0.22)
c.SetBottomMargin(0.16)
legend = ROOT.TLegend(0.27,0.62,0.60,0.75)


legend.SetTextSize(0.04)
legend.AddEntry(g_data,"measurement")
legend.AddEntry(g_sim,"simulation")

c.cd()
#c.SetLogy()
#g_data.Draw()
mg.Draw()
legend.Draw("SAME")

c.SaveAs("./output/nju_pin_iv_improved.pdf")
