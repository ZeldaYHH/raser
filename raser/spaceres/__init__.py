from . import telescope

import ROOT
import sys
import time
import os
sys.path.append("..")
from g4simulation import Particles
from setting import Setting
from geometry import R3dDetector
from calcurrent import CalCurrentPixel

def main(args):
    label = vars(args)['label']
    
   
        
    if label == "-h":
        print("taichu_v1:   ","first version of telescope simulation")
        print("taichu_v2:   ","second version of telescope simulation")
    elif label.startswith("taichu_v1"):
        paths = ['det_name=Taichu3', 'parfile=setting/detector.json', 'geant4_model=pixeldetector', 'geant4_parfile=setting/absorber.json', 'pixeldetector']
        dset = Setting(paths)
        my_d = R3dDetector(dset)
        #my_f = 0
        #my_g4p = Particles(my_d, my_f, dset)
        #my_charge = CalCurrentPixel(my_d,my_f,my_g4p, dset.total_events,6)
        #drawsave.draw_charge(my_charge)
        #my_telescope = telescope(my_d,my_charge) 
        telescope.main(my_d)  
    elif label.startswith("taichu_v2"):
        #virtual object
        class MyObject:
            pass
        #output 
        res = []
        psize = []
        N = 25
        MaxSize = 25.
        for i in range(N):
            t_my_d = MyObject()
            t_my_d.p_x = MaxSize*(i+1)/N
            t_my_d.p_y = MaxSize*(i+1)/N
            t_my_d.p_z = 200.
            t_my_d.lt_z = [20000.,60000.,100000.,140000.,180000.,220000.]
            psize.append(t_my_d.p_x)
            res.append(telescope.main(t_my_d))
        
        graph = ROOT.TGraph()
        for i in range(len(psize)):
            graph.SetPoint(i,psize[i],res[i])
        
        canvas = ROOT.TCanvas("canvas", "TGraph", 800, 600)
        graph.SetMarkerStyle(ROOT.kFullCircle)
        graph.GetYaxis().SetTitle("Resolution [um]")
        graph.GetYaxis().CenterTitle()  
        graph.GetXaxis().SetTitle("Pixel Size [um]")
        graph.GetXaxis().CenterTitle()  
        
        legend = ROOT.TLegend(0.27,0.67,0.62,0.80)
        legend.SetTextSize(0.04)
        legend.AddEntry(graph,label)
        
        canvas.SetGrid() 
        
        graph.Draw("APL")
        legend.Draw()

        canvas.Draw()
        Name = "Res vs size"
        now = time.strftime("%Y_%m%d_%H%M")
        path = os.path.join("fig", str(now),'' )
        """ If the path does not exit, create the path"""
        if not os.access(path, os.F_OK):
            os.makedirs(path) 
        canvas.SaveAs(path+Name+".png")
        
    else:
        raise NameError(label)
    