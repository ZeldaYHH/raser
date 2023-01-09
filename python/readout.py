import ROOT
import numpy as np
from array import array
import csv
timevolt = np.loadtxt("TCT.csv",delimiter=",",skiprows=7,usecols=[0,1])
volt = array('d', [999.])
time = array('d', [999.])
number=0
myfile=ROOT.TFile("edgeTCT.root","RECREATE")
mytree=ROOT.TTree("tree","tct")
mytree.Branch("volt", volt, "volt/D")
mytree.Branch("time", time, "time/D")
mytree.Branch("number",number,"number/D")
for i in timevolt:
    time[0]= i[0]
    volt[0]= i[1]
    number=number+1
    mytree.Fill()
    
fields = []
rows = []
x=array('d', [999.])
y=array('d', [999.])
z=array('d', [999.])
with open("TCT.csv", 'r') as csvfile:
    csvreader=csv.reader(csvfile)
    fields = next(csvreader)
    for row in csvreader:
        rows.append(row)
x[0]=float(rows[1][2])
y[0]=float(rows[2][2])
z[0]=float(rows[3][2])
mytree.Branch("x",x,"x/D")
mytree.Branch("y",y,"y/D")
mytree.Branch("z",z,"z/D")
mytree.Fill()


tek=np.loadtxt("tek0000.csv",delimiter=",",skiprows=21,usecols=[0,1])
Volt = array('d')
Time = array('d')
for i in tek:
    if(i[0]>-0.0001 and i[0]<0.0001):
        Volt.append(i[1])
        Time.append(i[0])

m=len(Volt)
c1=ROOT.TCanvas("c1","canvas1",1000,1000)
c1.Divide(1,2)
c1.cd(1)
g1=ROOT.TGraph(m)
g1.SetName("g1")
g1.SetFillColor(6)
g1.SetFillStyle(3005)
g1.SetLineColor(4)
g1.SetLineWidth(2)
g1.GetXaxis().SetTitle("time[s]")
g1.GetYaxis().SetTitle("volt[V]")
for n in range(m):
    g1.SetPoint(n,Time[n],Volt[n])
g1.Draw()
c1.SaveAs("laser"+".pdf")

mytree.Write()
myfile.Close()