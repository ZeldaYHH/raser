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


myFile=ROOT.TFile("edge_voltage_2019_10_09_12_26_57_HPK-EPI-W2-200-DS-SE5-04.txt.root")
myt = myFile.Get("edge")
n = myt.Draw("-volt:time","Vbias==-200&&z==11.974","goff")
graph = ROOT.TGraph(n,myt.GetV2(),myt.GetV1())
graph.Draw('apl')
c.SaveAs('g1.pdf')

#t = f_in_data.Get('edge')
#h_data = ROOT.TH2D('h_data', '', 192, 0, 10, 100, -0.005, 0.025)
#t.Draw('BlineRMS:time','Vbias==-200&&z==12.005','')
#h_data = ROOT.TH2D('h_data', '', 1920, 0, 10, 1920, 0.015, 0.02)
#t.Draw('-(volt-BlineMean):(time-10)>>h_data','Vbias==-200&&z==12.01','l')
#h_data.SetLineColor(1)
#h_data.Draw('l');
#h_data.SetMarkerSize(1)
#h_data.SetMarkerStyle(7)
#h_data.SetMarkerColor(1)



##Volt-time:VorZ
#f_in_data = TFile('edge_voltage_2019_10_24_15_12_57_HPK-EPI-W2-200-DS-SE5PINNM-01.txt.root')
#t = f_in_data.Get('edge')
#h_data = ROOT.TH2D('h_data', '', 100, 0, 20, 100, -0.005, 0.03)
#t.Draw('-(volt-BlineMean):(time-10)>>h_data','Vbias==-200&&z==12.005','l')
#h_data.SetLineColor(1)
#h_data.Draw('l');
#h_data.SetMarkerSize(1)
#h_data.SetMarkerStyle(3)
#h_data.SetMarkerColor(1)



#f_in_data2 = TFile('edge_voltage_2019_10_24_15_12_57_HPK-EPI-W2-200-DS-SE5PINNM-01.txt.root')
#t2 = f_in_data2.Get('edge')
#h_data2 = ROOT.TH2D('h_data2', '', 100, 0, 30, 100, -0.005, 0.03)
#h_data2.SetLineColor(2)
#t2.Draw('-(volt-BlineMean):(time-10)>>h_data2','Vbias==-140&&z==12.005','same')
#h_data2.Draw('same')
#h_data2.SetMarkerColor(2)
#h_data2.SetMarkerStyle(4)

#f_in_data3 = TFile('edge_voltage_2019_10_24_15_12_57_HPK-EPI-W2-200-DS-SE5PINNM-01.txt.root')
#t3 = f_in_data3.Get('edge')
#h_data3 = ROOT.TH2D('h_data3', '', 100, 0, 30, 100, -0.005, 0.03)
#h_data3.SetLineColor(6)
#t3.Draw('-(volt-BlineMean):(time-10)>>h_data3','Vbias==-80&&z==12.005','same')
#h_data3.Draw('same')
#h_data3.SetMarkerColor(6)
#h_data3.SetMarkerStyle(25)

#f_in_data4 = TFile('edge_voltage_2019_10_24_15_12_57_HPK-EPI-W2-200-DS-SE5PINNM-01.txt.root')
#t4 = f_in_data4.Get('edge')
#h_data4 = ROOT.TH2D('h_data4', '', 100, 0, 30, 100, -0.005, 0.03)
#h_data4.SetLineColor(7)
#t4.Draw('-(volt-BlineMean):(time-10)>>h_data3','Vbias==-20&&z==12.005','same')
#h_data4.Draw('same')
#h_data4.SetMarkerColor(7)
#h_data4.SetMarkerStyle(26)

#f_in_data5 = TFile('edge_voltage_2019_10_24_15_12_57_HPK-EPI-W2-200-DS-SE5PINNM-01.txt.root')
#t5 = f_in_data5.Get('edge')
#h_data5 = ROOT.TH2D('h_data5', '', 100, 0, 30, 100, -0.005, 0.03)
#h_data5.SetLineColor(4)
#t5.Draw('-(volt-BlineMean):(time-10)>>h_data3','Vbias==-20&&z==12.005','same')
#h_data5.Draw('same')
#h_data5.SetMarkerColor(4)

#legend.AddEntry(h_data, "z=11.985")
#legend.AddEntry(h_data1, "z=11.995")
#legend.AddEntry(h_data2, "z=12.005")
#legend.AddEntry(h_data3, "z=12.015")
#legend.AddEntry(h_data4, "z=12.025")
#legend.AddEntry(h_data5, "z=12.035")



##Ve+Vh
#f_in_data = TFile('edge_voltage_2019_10_24_15_12_57_HPK-EPI-W2-200-DS-SE5PINNM-01.txt.root')
#t = f_in_data.Get('edge')
#h_data = ROOT.TH2D('h_data', '', 100, -0.01, 0.07, 100, -0.015, 0.017)
#h_data = ROOT.TH2D('h_data', '', 100, -10, 60, 100, -0.01, 0.1)
#t.Draw('-Sum$((volt-aBlineMean)*((time>atleft+0.4)&&(time<(atleft+0.6)))):((z-11.985)*1000)>>h_data','Vbias==-200','')
#h_data = ROOT.TH2D('h_data', '', 100, -200, 0, 100, -0.01, 0.1)
#t.Draw('-Sum$((volt-aBlineMean)*((time>atleft+0.4)&&(time<(atleft+0.6)))):Vbias>>h_data','z==12.005','')
#t.Draw('-(volt-BlineMean)*RiseTime:(z-11.985)>>h_data','Vbias==-200','')
#h_data.Draw()
#h_data.SetMarkerSize(1)
#h_data.SetMarkerStyle(3)
#h_data.SetMarkerColor(4)
#h_data.GetYaxis().SetTitle('v_{e}+v_{h}[a.u.]')
#h_data.GetXaxis().SetTitle('Depth[um]')
#h_data.GetXaxis().SetTitle('Vbias[V]')

##charge
#f_in_data = TFile('edge_voltage_2019_10_24_15_12_57_HPK-EPI-W2-200-DS-SE5PINNM-01.txt.root')
#t = f_in_data.Get('edge')
#h_data = ROOT.TH2D('h_data', '', 100, -200, 0, 100, -60000, 120000)
#t.Draw('(-Sum$((volt-aBlineMean)*((time>atleft)&&(time<(atleft+20)))))/LPower:Vbias>>h_data','z==12.005','l')

#h_data = ROOT.TH2D('h_data', '', 100, -0.01, 0.06, 100, -0.5, 1)
#t.Draw('(-Sum$((volt-BlineMean)*((time>atleft)&&(time<(atleft+20)))))/LPower:Vbias>>h_data','z=12.005','l')
#h_data.Draw()
#h_data.SetMarkerSize(1)
#h_data.SetMarkerStyle(3)
#h_data.SetMarkerColor(4)
#h_data.GetYaxis().SetTitle('Charge[V/50\Omega]')
#h_data.GetXaxis().SetTitle('Vbias[V]')
#h_data.GetXaxis().SetTitle('Depth[um]')


##Vmin-BlineMean
#f_in_data = TFile('edge_voltage_2019_10_24_15_12_57_HPK-EPI-W2-200-DS-SE5PINNM-01.txt.root')
#t = f_in_data.Get('edge')
#h_data = ROOT.TH2D('h_data', '', 100, -10, 60, 100, 0, 0.03)
#t.Draw('-(Vmin-BlineMean):((z-11.985)*1000)>>h_data','Vbias==-200','l')
#h_data.Draw;()
#h_data.SetMarkerSize(1)
#h_data.SetMarkerStyle(3)
#h_data.SetMarkerColor(4)
#h_data.GetXaxis().SetTitle('Vbias[V]')
#h_data.GetYaxis().SetTitle('Signal[V]')
#h_data.GetXaxis().SetTitle('Depth[um]')

#t.Draw('RiseTime:Vbias','z==11.985')
#t1 = f_in_data.Get('edge')
#t1.Draw('(-Sum$((volt-aBlineMean)*((time>atleft)&&(time<(atleft+20)))))/LPower:(z-11.985)>>h_data','Vbias==-100','lsame')

#h_data = ROOT.TH2D('h_data', '', 100, -0.05, 0.1, 100, 0, 0.003)
#t.Draw('-(volt-BlineMean):time>>h_data','Vbias==-200&&z==12.005','l')
#t.Draw('(Vmax-BlineMean):(z-11.985)','Vbias==-200','l')
#t1.Draw('-(volt-BlineMean):time','Vbias==-100&&z==12.005','lsame')
#t.Draw('-(volt-BlineMean):time','Vbias==-200&&z==11.985','l')

##   RISETIME0.0
#f_in_data = TFile('edge_voltage_2019_10_24_15_12_57_HPK-EPI-W2-200-DS-SE5PINNM-01.txt.root')
#t = f_in_data.Get('edge')
#h_data = ROOT.TH2D('h_data', '', 100, -10, 60, 100, 0, 1.5)
#t.Draw('RiseTime:((z-11.985)*1000)>>h_data','Vbias==-200','l')
#h_data.Draw;('l')
#h_data.SetMarkerSize(1)
#h_data.SetMarkerColor(4)
#h_data.GetXaxis().SetTitle('Depth[um]')
#h_data.GetYaxis().SetTitle('RiseTime[ns]')
#h_data.GetXaxis().SetTitle('Vbias[V]')

##BlineRMS
#f_in_data = TFile('edge_voltage_2019_10_24_15_12_57_HPK-EPI-W2-200-DS-SE5PINNM-01.txt.root')
#t = f_in_data.Get('edge')
#h_data = ROOT.TH2D('h_data', '', 100, -200, 0, 100, 0, 0.0015)
#t.Draw('BlineRMS:Vbias>>h_data','z==12.005','l')
#h_data = ROOT.TH2D('h_data', '', 100, -10, 60, 100, 0, 0.0015)
#t.Draw('BlineRMS:((z-11.985)*1000)>>h_data','Vbias==-200','l')


#h_data.Draw()
#h_data.SetMarkerSize(1)
#h_data.SetMarkerStyle(3)
#h_data.SetMarkerColor(4)
#h_data.GetXaxis().SetTitle('Depth[um]')
#h_data.GetYaxis().SetTitle('BlineRMS')
#h_data.GetXaxis().SetTitle('Vbias[V]')

##XYaxis
#h_data.Draw;('l')
#h_data.SetMarkerSize(1)
#h_data.SetMarkerStyle(3)
#h_data.SetMarkerColor(4)
#h_data.GetXaxis().SetTitle('z-11.985')
#h_data.GetYaxis().SetTitle('Charge[a.u.]')
#h_data.GetYaxis().SetTitleOffset(1.5)
#h_data.GetYaxis().SetTitle('v_{e}+v_{h}[a.u.]')
#h_data.GetXaxis().SetTitle('Depth[um]')
#h_data.GetYaxis().SetTitle('RiseTime[ns]')
#h_data.GetYaxis().SetTitle('Signal[V]')
#h_data.GetXaxis().SetTitle('Vbias[V]')
#h_data.GetYaxis().SetTitle('Signal[V]')
#h_data.GetXaxis().SetTitle('time[ns]')

##others

# f_in_data = TFile('data/hpk_w2/red_top_voltage_2019_10_24_16_11_03_HPK-EPI-W2-200-DS-SE5PINNM-01.txt.root')
# t = f_in_data.Get('edge')
# h_data = ROOT.TH2D('h_data', '', 100, 9e-9, 15e-9, 100, -0.5e-3, 40e-4)
# t.Draw('(-volt*0.65e-1):(time*10e-10 - 35*1e-10)>>h_data','Vbias==-200&&x==82.51')
#h_data = ROOT.TH2D('h_data', '', 100, 0, 0.05, 100, -60000, 120000)
#t.Draw('(-Sum$((volt-aBlineMean)*((time>atleft)&&(time<(atleft+20)))))/LPower:(z-11.985)>>h_data','Vbias==-200','l')
#h_data = ROOT.TH2D('h_data', '', 100, -0.01, 0.06, 100, -0.005, 0.02)
#t.Draw('-(volt-aBlineMean)*RiseTime:(z-11.985)>>h_data','Vbias==-200','')
#t.Draw('-(volt-BlineMean)*RiseTime:(z-11.985)','Vbias==-200','c')
#t.Draw('-(volt-BlineMean)*(z-11.985)','Vbias==-200','l')
#t.Draw('-(volt-BlineMean):Vbias','z==11.985','l')
#t.Draw('-(volt-BlineMean):time','Vbias==-200&&z==12.005','l')
#t.Draw('BlineRMS:time','Vbias==-200&&z=12.005')


#h_data.Draw;('l')
#h_data.SetMarkerSize(1)
#h_data.SetMarkerStyle(3)
#h_data.SetMarkerColor(4)
#h_data.GetXaxis().SetTitle('z-11.985')
#h_data.GetYaxis().SetTitle('Charge[a.u.]')
#h_data.GetYaxis().SetTitleOffset(1.5)
#h_data.GetYaxis().SetTitle('v_{e}+v_{h}[a.u.]')
#h_data.GetXaxis().SetTitle('Depth[um]')
#h_data.GetYaxis().SetTitle('RiseTime[ns]')
#h_data.GetYaxis().SetTitle('Signal[V]')
#h_data.GetXaxis().SetTitle('Vbias[V]')
#h_data.GetYaxis().SetTitle('Signal[V]')
#h_data.GetXaxis().SetTitle('time[ns]')

# f_in_sim = TFile('sim/HPK-W2-LGAD/edge/current200V_scan0.root')
# f_in_sim = TFile('sim/HPK-W2-LGAD/redtop/current200V_scan0.root')
# f_in_sim = TFile('sim/HPK-W2-PIN/edge/current200V_scan0.root')
# f_in_sim = TFile('sim/HPK-W2-PIN/redtop/current200V_scan0.root')

#h_sim = f_in_sim.Get('i_total')
#h_data.Get#legend.AddEntry(h_data1, "Vbias=-100")Xaxis().SetTitle('Depth[um]')# h_sim.Draw('same')
#h_sim.SetLineColor(2)
#h_sim.SetLineWidth(2)
#c.Update()

#######LGAD#######

##Volt-time:VorZ
#f_in_data = TFile('edge_voltage_2019_10_09_12_26_57_HPK-EPI-W2-200-DS-SE5-04.txt.root')
#t = f_in_data.Get('edge')
#h_data = ROOT.TH2D('h_data', '', 100, 0, 20, 100, -0.005, 0.9)
#t.SetLineColor(5)
#t.Draw('-(volt-BlineMean):time>>h_data','Vbias==-20&&z==11.979','l')
#h_data.SetLineColor(5)
#h_data.Draw('l')
#h_data.SetMarkerSize(1)
#h_data.SetMarkerStyle(1)
#h_data.SetMarkerColor(5)

#t1 = f_in_data.Get('edge')
#h_data1 = ROOT.TH2D('h_data1', '', 100, 0, 20, 100, -0.005, 0.12)
#t1.SetLineColor(3)
#t1.Draw('-(volt-BlineMean):time>>h_data1','Vbias==-140&&z==11.979','lsame')
#h_data1.SetLineColor(3)
#h_data1.Draw('same')
#h_data1.SetMarkerSize(1)
#h_data1.SetMarkerStyle(1)
#h_data1.SetMarkerColor(3)

#t2 = f_in_data.Get('edge')
#h_data2 = ROOT.TH2D('h_data2', '', 100, 0, 20, 100, -0.005, 0.12)
#t2.SetLineColor(4)
#t2.Draw('-(volt-BlineMean):time>>h_data2','Vbias==-80&&z==11.979','lsame')
#h_data2.SetLineColor(4)
#h_data2.Draw('same')
#h_data2.SetMarkerSize(1)
#h_data2.SetMarkerStyle(1)
#h_data2.SetMarkerColor(4)

#t4 = f_in_data.Get('edge')
#h_data4 = ROOT.TH2D('h_data4', '', 100, 0, 20, 100, -0.005, 0.12)
#t4.SetLineColor(1)
#t4.Draw('-(volt-BlineMean):time>>h_data4','Vbias==-200&&z==11.979','lsame')
#h_data4.SetLineColor(1)
#h_data4.Draw('same')
#h_data4.SetMarkerSize(1)
#h_data4.SetMarkerStyle(1)
#h_data4.SetMarkerColor(1)

#t3 = f_in_data.Get('edge')
#h_data3 = ROOT.TH2D('h_data3', '', 100, 0, 20, 100, -0.005, 0.12)
#t3.SetLineColor(5)
#t3.Draw('-(volt-BlineMean):time>>h_data3','Vbias==-20&&z==11.979','lsame')
#h_data3.SetLineColor(5)
#h_data3.Draw('same')




#h_data.SetLineColor(1)
#h_data.Draw('l')
#h_data.SetMarkerSize(1)
#h_data.SetMarkerStyle(3)
#h_data.SetMarkerColor(1)
#h_data.GetYaxis().SetTitle('Signal[V]')
#h_data.GetXaxis().SetTitle('Vbias[V]')
#h_data.GetYaxis().SetTitle('Signal[V]')
#h_data.GetXaxis().SetTitle('time[ns]')
#t.SetLineColor(1)








###Legend
legend = ROOT.TLegend(0.5, 0.78, 0.83, 0.88)
#legend.AddEntry(h_data, "TCT measurement")
# legend.AddEntry(h_sim,  "TRACS simulation")
legend.SetBorderSize(0)
legend.SetFillColor(0)
#legend.AddEntry(h_data, "z=11.985")
#legend.AddEntry(h_data1, "z=11.995")
#legend.AddEntry(h_data2, "z=12.005")
#legend.AddEntry(h_data3, "z=12.015")
#legend.AddEntry(h_data4, "z=12.025")
#legend.AddEntry(h_data5, "z=12.035")
# legend.SetFillsStyle(303)
#legend.AddEntry(h_data, "Vbias=-200")
#legend.AddEntry(h_data1, "Vbias=-140")
#legend.AddEntry(h_data2, "Vbias=-80")
#legend.AddEntry(h_data3, "z=12.015")

legend.Draw()
c.SaveAs('c.pdf')







