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

from particle import geometry as geo
from particle import g4simulation as g4s
#from field import pyfenics as pyf
from field import devsim_field as devfield
from field import solve_field as stripfield
from current import cal_current as ccrt
from elec import ele_readout as rdout

from read_json import Setting
from draw import draw_save
import math

def main(args):
    """
    Description:
        The main program of Raser induced current simulation      
    Parameters:
    ---------
    dset : class
        Parameters of simulation
    Function or class:
        R3dDetector -- Define the structure of the detector
        FenicsCal -- Get the electric field and weighting potential 
        Particles -- Electron and hole paris distibution
        CalCurrent -- Drift of e-h pais and induced current
        Amplifier -- Readout electronics simulation
        draw_plots -- Draw electric field, drift path and energy deposition        
    Modify:
    ---------
        2021/09/02
    """
    dset = Setting()
    if "scan" in args:
        dset.scan_variation()
    if "parameter_alter" in args:
        # need to put the changed value at the end of the parameter list
        key,_,value=args[-1].rpartition('=')
        value=float(value)
        dset.paras.update({key:value})
    det_dic = dset.detector
    if "plugin3D" in det_dic['det_model']:
        if det_dic['custom_electrode'] == "False":
            pass
        elif det_dic['custom_electrode'] == "True":
            set_electrodes(det_dic,dset)
        else:
            print("The electrode model is wrong.")
    my_d = geo.R3dDetector(dset)
    
    if "pixeldetector" in args:
        my_f = pyf.FenicsCal(my_d,dset.fenics)
        #my_f = 0
        my_g4p = g4s.Particles(my_d, my_f, dset)
        my_charge = ccrt.CalCurrentPixel(my_d,my_f,my_g4p, dset.total_events,6)
        #drawsave.draw_charge(my_charge)
        return  
    
    if "beammonitor" in args:
        my_f = pyf.FenicsCal(my_d,dset.fenics)
        my_g4p = g4s.Particles(my_d, my_f, dset)
        my_current = ccrt.CalCurrentG4P(my_d, my_f, my_g4p, 0)
        ele_current = rdout.Amplifier(my_current, dset.amplifier)
        drawsave.get_beam_number(my_g4p,ele_current)
        return  

    if "proton-irrad" in args:
        my_f = pyf.FenicsCal2D(my_d,dset.fenics)
        my_g4p = g4s.SiITk(my_d, my_f, dset)
        #my_current = raser.CalCurrentG4P(my_d, my_f, my_g4p, 0)
        #ele_current = raser.Amplifier(my_current, dset.amplifier)
        draw_save.get1_beam_number(my_g4p)
        #drawsave.cce(my_d,my_f,my_current)
        return

    if "Carrier" in args:
        my_f = pyf.FenicsCal1D(my_d,dset.fenics)
        my_g4p = g4s.Particles(my_d, my_f, dset)
        my_current = ccrt.CalCurrentG4P(my_d, my_f, my_g4p, 0)
        ele_current = rdout.Amplifier(my_current, dset.amplifier)
        draw_save.get_beam_number(my_g4p,ele_current)
        return  

    if "reactor" in args:
        my_f = pyf.FenicsCal(my_d,dset.fenics)
        my_g4p = g4s.Particles(my_d, my_f, dset)
        my_current = ccrt.CalCurrentG4P(my_d, my_f, my_g4p, 0)
        ele_current = rdout.Amplifier(my_current, dset.amplifier)
        draw_save.draw_plots(my_d,ele_current,my_f,my_g4p,my_current)
        return
    
    if "Si_Strip"==dset.detector_name:
        my_f = stripfield.FieldCal(my_d, dset.detector_name, dset.detector, dset.fenics)
        my_g4p = g4s.Particles(my_d, my_f, dset)
        my_current = ccrt.CalCurrentStrip(my_d, my_f, my_g4p, 0)
        ele_current = rdout.Amplifier(my_current, dset.amplifier)
        draw_save.draw_plots(my_d,ele_current,my_f,my_g4p,my_current)
        draw_save.cce(my_d,my_f,my_current)
        return
   
    if('devsim' in args):
        print("using devsim to build the field")
        try:
            my_f = devfield.DevsimCal(my_d, dset.det_name, dset.detector, dset.fenics)
        except:
            print("Please run 1.3.3 first to get efield(make sure run 1.3.1 once before you run 1.3.3)")
            exit(0)
    else:
        print("using fenics to build the field")
        my_f = pyf.FenicsCal(my_d,dset.fenics)
        
    my_g4p = g4s.Particles(my_d, my_f, dset)
    if "scan=True" not in args:
        my_current = ccrt.CalCurrentG4P(my_d, my_f, my_g4p, 0)
        #if "lgad" in dset.det_model:
        #   print("gain_efficiency="+str(my_current.gain_efficiency))
        ele_current = rdout.Amplifier(my_current, dset.amplifier)
        draw_save.draw_plots(my_d,ele_current,my_f,my_g4p,my_current)
    else:
        batch_loop(dset,my_d, my_f, my_g4p)
    del my_f

def set_electrodes(det_dic,dset):
    
    l_x = det_dic['lx'] 
    l_y = det_dic['ly']  
    l_z = det_dic['lz'] 
    e_int = det_dic['e_gap']
    e_r = det_dic['e_r']
    e_t_xy = e_int/math.sqrt(2)
    e_tr=[]
    e_t_1 = [l_x*0.5           , l_y*0.5         , e_r,0, l_z,"p"]
    e_t_2 = [l_x*0.5-e_t_xy    , l_y*0.5-e_t_xy  , e_r,0, l_z,"n"]
    e_t_3 = [l_x*0.5-e_t_xy    , l_y*0.5+e_t_xy  , e_r,0, l_z,"n"]
    e_t_4 = [l_x*0.5+e_t_xy    , l_y*0.5-e_t_xy  , e_r,0, l_z,"n"]
    e_t_5 = [l_x*0.5+e_t_xy    , l_y*0.5+e_t_xy  , e_r,0, l_z,"n"]
    for i in range(5):
        n_e = eval('e_t_' + str(i+1))
        e_tr.append(n_e)
    dset.electron_custom(e_tr)


def batch_loop(dset, my_d, my_f, my_g4p):
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
    if "plugin" in dset.det_model:
        drawsave.draw_ele_field(my_d,my_f,"xy",my_d.det_model,my_d.l_z*0.5,dset.output)
    else:
        drawsave.draw_ele_field_1D(my_d,my_f,dset.output)
        drawsave.draw_ele_field(my_d,my_f,"xz",my_d.det_model,my_d.l_y*0.5,dset.output)
    start_n = dset.instance_number * dset.total_events
    end_n = (dset.instance_number + 1) * dset.total_events
    effective_number = 0
    for event in range(start_n,end_n):
        print("run events number:%s"%(event))
        if len(my_g4p.p_steps[event-start_n]) > 5:
            effective_number += 1
            my_current = ccrt.CalCurrentG4P(my_d, my_f, my_g4p, event-start_n)
            ele_current = rdout.Amplifier(my_current, dset.amplifier)
            drawsave.save_signal_time_resolution(my_d,dset.output,event,ele_current,my_g4p,start_n,my_f)
            del ele_current
    detection_efficiency =  effective_number/(end_n-start_n) 
    print("detection_efficiency=%s"%detection_efficiency)


if __name__ == '__main__':
    start = time.time()
    main(sys.argv[1:])
    print("drift_total1:%s"%(time.time()-start))
    print("RUN END")
    os._exit(0) 
