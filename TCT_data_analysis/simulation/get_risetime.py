#!/usr/bin/env python3

from array import array
import math
import ROOT
import sys
import os
import time
import numpy as np

v1=array("d")
t1=array("d")
r1=array("d")
time=array("d",[0.])
volt=array("d",[0.])
v2=array("d")
t2=array("d")
z=array("d",[0.])
Vmax=array("d",[0.])
RiseTime=array('d',[0.])
BlineMean=array('d',[0.])
BlineRMS=array('d',[0.])
E=array('d',[0.])
Qtot=array('d',[0.])
J=0
for L in range(51):
   v1=array("d")
   t1=array("d")
   myFile = ROOT.TFile("TCT"+str(L)+".root")
   myt = myFile.tree
#   fout = ROOT.TFile("PTCT"+str(L)+".root", "RECREATE")
#   t_out = ROOT.TTree("tree", "signal")
#   t_out.Branch("volt", volt, "volt/D")
#   t_out.Branch("time", time, "time/D")
#   t_out.Branch("z", z, "z/D")
#   t_out.Branch("RiseTime", RiseTime, "RiseTime/D")
#t_out.Branch("Vmax", Vmax, "Vmax/D")
# t_out.Branch("BlineMean",BlineMean , "BlineMean/D")
# t_out.Branch("BlineRMS", BlineRMS, "BlineRMS/D")
#t_out.Branch("Qtot", Qtot,"Qtot/D")
#t_out.Branch("E", E,"E/D")
   Mean=np.array([0.00033243082142857136, 8.824742857142855e-05, 0.0004053836517857144, 0.0010010143348214288, 0.00017645273214285715, 0.00012015875000000006, 5.40438883928572e-05, -0.00021439406249999988, 0.0007968599374999997, 4.5325915178571344e-05, 0.0004891657142857144, 0.0004727932410714284, 0.0004435015803571429, 0.0006440360892857141, 0.00014541913392857145, -2.0991955357142835e-05, -0.00040066849107142866, 0.0005230586250000001, 0.0002712754598214285, 0.0005945093660714286, 0.0004167786964285714, 0.0006453769776785721, 0.0007039226250000003, -0.0005224082098214285, 0.0007585116205357144, 0.0011352242767857141, 0.0002745170267857142, -1.247159821428572e-05, 0.00014448292857142855, -0.00021798845982142832, 0.000944485, -0.00024661204017857136, 0.00014989804910714287, 0.00041829358482142867, 0.0004447483392857146, 0.0002821998169642858, 0.00016303843303571436, -0.00013298333482142868, -7.17371785714286e-05, 6.961174553571425e-05, -0.00013699179464285715, 0.00013765162053571428, 0.00042861579910714284, 0.0010761092410714285, 0.0006653626339285715, 0.00023811177678571415, 8.3904799107143e-05, -0.00027197524553571436, -3.97554017857143e-05, 0.0005225992633928572, 0.0008994781875000003])

   for entry in myt:
      v1.append(-entry.volt)
      t1.append(entry.time)
      J=J+1
   Vmax=max(v1)
   for j in range(J):
      if v1[j]>(0.2*(Vmax+Mean[L])-Mean[L])>v1[j-1]:
#         print(j)
         break
   for l in range(J):
      if v1[l]<(0.8*(Vmax+Mean[L])-Mean[L])<v1[l+1]:
#         print(l)
         break
   d=np.true_divide(v1[j],Vmax)
   e=np.true_divide(v1[l],Vmax)
   r=np.true_divide((t1[l]-t1[j]),(e-d))
   r1.append(r)
print(r1)
#print(d,e)
#print(r)
#RiseTime[0]=
#E[0]=
#Vmax[0]=
#z[0]=L
#Qtot[0]=
#t_out.Fill()
#for i in range(J):
#    t_out.Fill()
#t_out.Write()
#fout.Close()













