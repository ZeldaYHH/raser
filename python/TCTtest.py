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
my_l = raser.TCTTracks(my_d, dset.laser)

my_current = raser.CalCurrentLaser(my_d, my_f, my_l)
ele_current = raser.Amplifier(my_d, dset.amplifier)
drawsave.drawplot(my_d,ele_current,my_f,None,my_current,my_l)
drawsave.save(my_l,ele_current)

# now = time.strftime("%Y_%m%d_%H%M")
# path = "fig/" + now + "/"
# drawsave.create_path(path)
# drawsave.draw_nocarrier3D(path,my_l)
print("total time used:%s"%(time.time()-start))
