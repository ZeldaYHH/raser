#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@Description: The main program of Raser induced current simulation      
@Date       : 2021/09/7 12:14:31
@Author     : tanyuhang
@version    : 1.0
'''
import sys
import os
import time

from field import build_device as bdv
from particle import g4simulation as g4s
from field import devsim_field as devfield
from current import cal_current as ccrt
from elec import ele_readout as rdout

from draw import draw_save

import json

import random

def main(kwargs):
    """
    Description:
        The main program of Raser induced current simulation      
    Parameters:
    ---------
    dset : class
        Parameters of simulation
    Function or class:
        Detector -- Define the basic parameters and mesh structure of the detector
        DevsimCal -- Get the electric field and weighting potential 
        Particles -- Electron and hole paris distibution
        CalCurrent -- Drift of e-h pais and induced current
        Amplifier -- Readout electronics simulation
        draw_plots -- Draw electric field, drift path and energy deposition        
    Modify:
    ---------
        2021/09/02
    """
    detector_name = kwargs['detector_name']
    voltage = float(kwargs['voltage'])
    absorber = kwargs['absorber_name']
    amplifier = kwargs['absorber_name']

    my_d = bdv.Detector(detector_name)
    if "strip" in detector_name:
        my_f = devfield.DevsimField(my_d.device, my_d.dimension, voltage, 2)
    else: 
        my_f = devfield.DevsimField(my_d.device, my_d.dimension, voltage)

    if kwargs['scan'] != None:
        from util.output import output
        geant4_json = "./setting/absorber/" + absorber + ".json"
        with open(geant4_json) as f:
            g4_dic = json.load(f)

        total_events = int(g4_dic['total_events'])
        instance_number = kwargs['scan'][0]
        g4_seed = instance_number * total_events
        path = output(__file__, my_d.det_name)

        my_g4p = g4s.Particles(my_d, absorber, g4_seed)
        batch_loop(my_d, my_f, my_g4p, amplifier, g4_seed, total_events, instance_number, path)
        return
    
    else:  
        g4_seed = random.randint(0,1e7)
        my_g4p = g4s.Particles(my_d, absorber, g4_seed)

    if "strip" in detector_name:
        my_current = ccrt.CalCurrentStrip(my_d, my_f, my_g4p, 0)
    else: 
        my_current = ccrt.CalCurrentG4P(my_d, my_f, my_g4p, 0)

    if 'ngspice' in amplifier:
        draw_save.save_current(my_d, my_current, my_f, "fz_abs")
        input_p=draw_save.set_input(my_current, my_d, "fz_abs")
        input_c=','.join(input_p)
        ngspice(input_c, input_p)
    else:
        ele_current = rdout.Amplifier(my_current, amplifier)
        draw_save.draw_plots(my_d,ele_current,my_f,my_g4p,my_current)
        
    if "strip" in my_d.detector_name:
        draw_save.cce(my_d,my_f,my_current)

    del my_f

def ngspice(input_c, input_p):
    with open('./paras/T1.cir', 'r') as f:
        lines = f.readlines()
        lines[113] = 'I1 2 0 PWL('+str(input_c)+') \n'
        lines[140] = 'tran 0.1p ' + str((input_p[len(input_p) - 2])) + '\n'
        lines[141] = 'wrdata output/t1.raw v(out)\n'
        f.close()
    with open('./output/T1_tmp.cir', 'w') as f:
        f.writelines(lines)
        f.close()


def batch_loop(my_d, my_f, my_g4p, amplifier, g4_seed, total_events, instance_number, path):
    """
    Description:
        Batch run some events to get time resolution
    Parameters:
    ---------
    start_n : int
        Start number of the event
    end_n : int
        end number of the event 
    detection_efficiency: float
        The ration of hit particles/total_particles           
    @Returns:
    ---------
        None
    @Modify:
    ---------
        2021/09/07
    """
    if "plugin" in my_d.det_model:
        draw_save.draw_ele_field(my_d,my_f,"xy",my_d.det_model,my_d.l_z*0.5,path)
    else:
        draw_save.draw_ele_field_1D(my_d,my_f,path)
        draw_save.draw_ele_field(my_d,my_f,"xz",my_d.det_model,my_d.l_y*0.5,path)

    start_n = instance_number * total_events
    end_n = (instance_number + 1) * total_events

    effective_number = 0
    for event in range(start_n,end_n):
        print("run events number:%s"%(event))
        if len(my_g4p.p_steps[event-start_n]) > 5:
            effective_number += 1
            my_current = ccrt.CalCurrentG4P(my_d, my_f, my_g4p, event-start_n)
            ele_current = rdout.Amplifier(my_current, amplifier)
            draw_save.save_signal_time_resolution(my_d,path,event,ele_current,my_g4p,start_n,my_f)
            del ele_current
    detection_efficiency =  effective_number/(end_n-start_n) 
    print("detection_efficiency=%s"%detection_efficiency)


if __name__ == '__main__':
    start = time.time()
    main(sys.argv[1], sys.argv[2])
    print("drift_total1:%s"%(time.time()-start))
    print("RUN END")
    os._exit(0) 
