#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import raser

# TODO: Need to be rewritten!

import time
from draw import draw_save

args = sys.argv[1:]
start = time.time()
dset = raser.Setting(args)
if "parameter_alter=True" in args:
    # need to put the changed value at the end of the parameter list
    key,_,value=args[-1].rpartition('=')
    value=float(value)
    if key in dset.laser_paras:
        dset.laser_paras.update({key:value})
        key_string = str(dset.laser_paras[key])+key
    elif key in dset.paras:
        dset.paras.update({key:value})
        key_string = str(dset.paras[key])+key
else:
    key_string = ""
my_d = raser.R3dDetector(dset)

if('devsim' in args):
    print("using devsim to build the field")
    my_f = raser.DevsimCal(my_d, dset.det_name, dset.detector, dset.fenics)
else:
    print("using fenics to build the field")
    my_f = raser.FenicsCal(my_d,dset.fenics)

my_l = raser.TCTTracks(my_d, dset.laser)
my_current = raser.CalCurrentLaser(my_d, my_f, my_l)
ele_current = raser.Amplifier(my_current, dset.amplifier)
if "ngspice" in args:
    draw_save.save_current(dset,my_d,my_l,my_current,my_f,"fx_rel")
    input_p=draw_save.set_input(dset,my_current,my_l,my_d,"fx_rel")
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
if "scan=True" in args: #assume parameter alter
    draw_save.save_signal_TTree(dset,my_d,key_string,ele_current,my_f)
    if "planar3D" in my_d.det_model or "planarRing" in my_d.det_model:
        path = "output/" + "pintct/" + dset.det_name + "/"
    elif "lgad3D" in my_d.det_model:
        path = "output/" + "lgadtct/" + dset.det_name + "/"
    else:
        raise NameError
else:
    draw_save.draw_plots(my_d,ele_current,my_f,None,my_current,my_l)

if "draw_carrier" in label:
    now = time.strftime("%Y_%m%d_%H%M")
    path = "output/fig/" + now + "/"
    draw_save.create_path(path)
    draw_save.draw_nocarrier3D(path,my_l)
    draw_save.draw_nocarrier2D(path,my_l)

print("total time used:%s"%(time.time()-start))
