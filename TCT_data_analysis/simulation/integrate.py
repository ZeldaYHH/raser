#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from array import array
import math
import ROOT
import sys
import os
import time
import numpy as np

Z=array("d")
Max=array("d")
Amp=array("d")
Ele=array("d")
Rt=array("d")
Ch=array("d")
n=51

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

def risetime(J,v,t,Vmax,mean):
  for k in range(1,J):
      if (v[k-1] - mean)<0.2*(Vmax-mean)<(v[k] - mean) and t[k]>0.5:
         break
  for l in range(J-1):
      if (v[l] - mean)<0.8*(Vmax - mean)<(v[l+1] - mean):
         break
  m=l-k+1
  for j in range(k,l+1):
    x.append(t[j])
    y.append(v[j])
  gfit = ROOT.TGraph(m,x,y)
  f=ROOT.TF1("f","[0]+[1]*x",0,2)
  gfit.Fit(f)
  a=f.GetParameter(1)
  b=f.GetParameter(0)
  t1=np.true_divide((0.2*(Vmax-mean)-b),a)
  t2=np.true_divide((0.8*(Vmax-mean)-b),a)
  rt=np.true_divide((t2-t1),0.6)
  return(rt)

def draw(Amp,Ele,Rt,Ch):
  graph1=ROOT.TGraph(51,Z,Amp)
  graph1.SetMarkerStyle(3)
  graph1.Draw('ap')
  g.SaveAs('Amplitude.pdf')

  graph2=ROOT.TGraph(51,Z,Ele)
  graph2.SetMarkerStyle(3)
  graph2.Draw('ap')
  g.SaveAs('Elefield.pdf')

  graph3=ROOT.TGraph(51,Z,Rt)
  graph3.SetMarkerStyle(3)
  graph3.Draw('ap')
  g.SaveAs('Risetime.pdf')

  graph1=ROOT.TGraph(51,Z,Ch)
  graph1.SetMarkerStyle(3)
  graph1.Draw('ap')
  g.SaveAs('Charge.pdf')

for L in range(51):
  Z.append(L)
  v=array("d")
  t=array("d")
  x=array("d")
  y=array("d")
  J=0
  c=0
  mean=0
  
  myFile = ROOT.TFile("sim-TCT"+str(L)+".root")
  myt = myFile.tree
  for entry in myt:
        v.append(entry.volt)
        t.append(1000000000*entry.time)
        J=J+1

  Vmax=max(v)
  Amp.append(Vmax)
 
  e=v[31]+v[32]
  Ele.append(e)

  c=0
  for i in range(J):
    c+=v[i]
  Ch.append(c)

  rt= risetime(J,v,t,Vmax,mean)
  Rt.append(rt)

draw(Amp,Ele,Rt,Ch)


