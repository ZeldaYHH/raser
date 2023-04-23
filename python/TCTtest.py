#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import raser
import time
import drawsave

args = sys.argv[1:]
start = time.time()
dset = raser.Setting(args)
if "parameter_alter=True" in args:
    # need to put the changed value at the end of the parameter list
    key,_,value=args[-1].rpartition('=')
    value=float(value)
    dset.laser_paras.update({key:value})
my_d = raser.R3dDetector(dset)
my_f = raser.FenicsCal(my_d, dset.fenics)
my_l = raser.TCTTracks(my_d, dset.laser)

my_current = raser.CalCurrentLaser(my_d, my_f, my_l)
ele_current = raser.Amplifier(my_current, dset.amplifier)
if "scan=True" in args: #assume parameter alter
    drawsave.save(dset,my_d,my_l,ele_current,my_f,key)
    if "planar3D" in my_d.det_model or "planarRing" in my_d.det_model:
        path = "output/" + "pintct/" + dset.det_name + "/"
    elif "lgad3D" in my_d.det_model:
        path = "output/" + "lgadtct/" + dset.det_name + "/"
    else:
        raise NameError
    drawsave.create_path(path) 
    drawsave.draw_plot(my_d,my_current,ele_current.BB_ele, "BB", path, "_"+args[-1])
else:
    drawsave.drawplot(my_d,ele_current,my_f,None,my_current,my_l)
if "ngspice" in args:
    drawsave.save_current(dset,my_d,my_l,my_current,my_f,"fz_abs")
    input_p=drawsave.set_input(dset,my_current,my_l,my_d,"fz_abs")
    print(input_p)
    input_c=','.join(input_p)
    with open('paras/T1.cir', 'r') as f:
        lines = f.readlines()
        lines[113] = 'I1 2 0 PWL('+str(input_c)+') \n'
        lines[140] = 'tran 0.1p ' + str((input_p[len(input_p) - 2])) + '\n'
        lines[141] = 'wrdata output/t1.raw v(out)\n'
        f.close()
    with open('output/T1_tmp.cir', 'w') as f:
        f.writelines(lines)
        f.close()
# now = time.strftime("%Y_%m%d_%H%M")
# path = "fig/" + now + "/"
# drawsave.create_path(path)
# drawsave.draw_nocarrier3D(path,my_l)
# drawsave.draw_nocarrier2D(path,my_l)

print("total time used:%s"%(time.time()-start))
