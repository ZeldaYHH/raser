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

#myFile=ROOT.TFile("edge_voltage_2019_10_09_12_26_57_HPK-EPI-W2-200-DS-SE5-04.txt.root")
#myt = myFile.Get("edge")
#n = myt.Draw("-volt:time","Vbias==-200&&z==11.974","goff")
#graph = ROOT.TGraph(n,myt.GetV2(),myt.GetV1())
#graph.Draw('apl')
#graph.GetYaxis().SetTitle('Amplitude/V')
#graph.GetXaxis().SetTitle('Time/ns')

##Ve+Vh
#f_in_data = TFile('edge_voltage_2019_10_09_12_26_57_HPK-EPI-W2-200-DS-SE5-04.txt.root')
#t = f_in_data.Get('edge')
#h_data = ROOT.TH2D('h_data', '', 120, -220, 0, 120, -0.05, 2.0)
#h_data = ROOT.TH2D('h_data', '', 100, -10, 60, 100, 0, 2)
#t.Draw('-Sum$((volt-aBlineMean)*((time>atleft+0.4)&&(time<(atleft+0.6)))):((z-11.954)*1000)>>h_data','Vbias==-200','')
#h_data = ROOT.TH2D('h_data', '', 100, -200, 0, 100, -0.01, 0.1)
#t.Draw('-Sum$((volt-aBlineMean)*((time>atleft+0.4)&&(time<(atleft+0.6)))):Vbias>>h_data','z==11.974','')
#t.Draw('-(volt-BlineMean)*RiseTime:(z-11.985)>>h_data','Vbias==-200','')
#h_data.Draw()
#h_data.SetMarkerSize(1)
#h_data.SetMarkerStyle(3)
#h_data.SetMarkerColor(4)
#h_data.GetYaxis().SetTitle('v_{e}+v_{h}[a.u.]')
#h_data.GetXaxis().SetTitle('Depth[um]')
#h_data.GetXaxis().SetTitle('Vbias[V]')

##Vmin-BlineMean
#f_in_data = TFile('edge_voltage_2019_10_09_12_26_57_HPK-EPI-W2-200-DS-SE5-04.txt.root')
#t = f_in_data.Get('edge')
#h_data = ROOT.TH2D('h_data', '', 200, -220, 0, 200, 0, 0.9)
#t.Draw('-(Vmin-BlineMean):Vbias>>h_data','z==11.974','l')
#h_data = ROOT.TH2D('h_data', '', 200, -10, 60, 200, 0, 0.9)
#t.Draw('-(Vmin-BlineMean):((z-11.954)*1000)>>h_data','Vbias==-200','l')
#h_data.Draw()
#h_data.SetMarkerSize(1)
#h_data.SetMarkerStyle(3)
#h_data.SetMarkerColor(4)
#h_data.GetXaxis().SetTitle('Vbias[V]')
#h_data.GetYaxis().SetTitle('Signal[V]')
#h_data.GetXaxis().SetTitle('Depth[um]')

###RiseTime
#f_in_data = TFile('edge_voltage_2019_10_09_12_26_57_HPK-EPI-W2-200-DS-SE5-04.txt.root')
#t = f_in_data.Get('edge')
#h_data = ROOT.TH2D('h_data', '', 100, -10, 60, 100, 0, 1.0)
#t.Draw('RiseTime:((z-11.954)*1000)>>h_data','Vbias==-200','l')
#h_data = ROOT.TH2D('h_data', '', 200, -220, 0, 200, 0, 1.5)
#t.Draw('RiseTime:Vbias>>h_data','z==11.974','l')
#h_data.Draw()
#h_data.SetMarkerSize(1)
#h_data.SetMarkerStyle(3)
#h_data.SetMarkerColor(4)
#h_data.GetXaxis().SetTitle('Depth[um]')
#h_data.GetYaxis().SetTitle('RiseTime[ns]')
#h_data.GetXaxis().SetTitle('Vbias[V]')

##BlineRMS
#f_in_data = TFile('edge_voltage_2019_10_09_12_26_57_HPK-EPI-W2-200-DS-SE5-04.txt.root')
#t = f_in_data.Get('edge')
#h_data = ROOT.TH2D('h_data', '', 200, -220, 0, 200, 0, 0.0020)
#t.Draw('BlineRMS:Vbias>>h_data','z==11.974','l')
#h_data = ROOT.TH2D('h_data', '', 200, -10, 60, 200, 0, 0.0020)
#t.Draw('BlineRMS:((z-11.954)*1000)>>h_data','Vbias==-200','l')
#h_data.Draw()
#h_data.SetMarkerSize(1)
#h_data.SetMarkerStyle(3)
#h_data.SetMarkerColor(4)
#h_data.GetXaxis().SetTitle('Depth[um]')
#h_data.GetYaxis().SetTitle('BlineRMS')
#h_data.GetXaxis().SetTitle('Vbias[V]')

##Qtot
f_in_data = TFile('edge_voltage_2019_10_09_12_26_57_HPK-EPI-W2-200-DS-SE5-04.txt.root')
t = f_in_data.Get('edge')
#h_data = ROOT.TH2D('h_data', '', 200, -220, 0, 200, -100000, 1900000)
#t.Draw('(-Sum$((volt-aBlineMean)*((time>atleft)&&(time<(atleft+20)))))/LPower:Vbias>>h_data','z==11.974','l')
h_data = ROOT.TH2D('h_data', '', 200, -10, 60, 200, -100000, 3000000)
t.Draw('(-Sum$((volt-aBlineMean)*((time>atleft)&&(time<(atleft+20)))))/LPower:((z-11.954)*1000)>>h_data','Vbias==-200','l')
h_data.Draw()
h_data.SetMarkerSize(1)
h_data.SetMarkerStyle(3)
h_data.SetMarkerColor(4)
h_data.GetYaxis().SetTitle('Charge[V/50\Omega]')
#h_data.GetXaxis().SetTitle('Vbias[V]')
h_data.GetXaxis().SetTitle('Depth[um]')


###Legend
legend = ROOT.TLegend(0.5, 0.78, 0.83, 0.88)
legend.AddEntry(h_data, "TCT measurement")
# legend.AddEntry(h_sim,  "TRACS simulation")
legend.SetBorderSize(0)
legend.SetFillColor(0)
legend.Draw()


c.SaveAs('g5.pdf')


