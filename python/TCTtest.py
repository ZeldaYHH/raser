#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import raser
import sys
import time
import drawsave

args = sys.argv[1:]
start = time.time()
dset = raser.Setting(args)
my_d = raser.R3dDetector(dset)
my_f = raser.FenicsCal(my_d, dset.fenics)
my_l = raser.TCTTracks(my_d, dset.laser, 1000)
my_current = raser.CalCurrentLaser(my_d, my_f, my_l, dset)
ele_current = raser.Amplifier(my_d, dset.amplifier)
drawsave.drawplot(my_d,ele_current,my_f,None,my_current,my_l)
print("total time used:%s"%(time.time()-start))