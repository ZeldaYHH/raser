#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import raser
import sys
import time
import drawsave
from array import array
import math
import ROOT
import os
import json

#for L in range(51):
model=egde_TCT_Si       
L=10    
with open('laser_setting.json','rb') as f:   
      paras=json.load(f)
      for para in paras:
          if "egde_TCT_Si" in model:
             para.update({'fz_rel':str(0+L*0.02)})                   
      json_str = json.dumps([para], indent=4)
      with open('laser_setting.json','w') as r:
                  r.write(json_str)
                  r.close
#L=40
#args = sys.argv[1:]
#start = time.time()
#dset = raser.Setting(args)
#my_d = raser.R3dDetector(dset)
#my_f = raser.FenicsCal(my_d, dset.fenics)
#my_l = raser.TCTTracks(my_d, dset.laser, 1000)
#my_current = raser.CalCurrentLaser(my_d, my_f, my_l, dset)
#ele_current = raser.Amplifier(my_d, dset.amplifier)
#drawsave.drawplot(my_d,ele_current,my_f,None,my_current,my_l)
#drawsave.save(L,ele_current)
#drawsave.resave(L)
#print("total time used:%s"%(time.time()-start))


#    args = sys.argv[1:]
#    start = time.time()
#    dset = raser.Setting(args)
#    my_d = raser.R3dDetector(dset)
#    my_f = raser.FenicsCal(my_d, dset.fenics)
#    my_l = raser.TCTTracks(my_d, dset.laser, 1000)
#    my_current = raser.CalCurrentLaser(my_d, my_f, my_l, dset)
#    ele_current = raser.Amplifier(my_d, dset.amplifier)
#    drawsave.drawplot(my_d,ele_current,my_f,None,my_current,my_l)
#    drawsave.save(L,ele_current)
#    drawsave.resave(L)
#    print("total time used:%s"%(time.time()-start))
