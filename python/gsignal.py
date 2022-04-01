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
import raser
import drawsave
import math

def main():
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
        drawplot -- Draw electric field ,drift path and energy deposition        
    Modify:
    ---------
        2021/09/02
    """
    args = sys.argv[1:]
    dset = raser.Setting(args)
    set_electrodes(dset)
    my_d = raser.R3dDetector(dset)
    my_f = raser.FenicsCal(my_d,dset.fenics,dset.detector)
    my_g4p = raser.Particles(my_d, my_f, dset)
    if "3Dscan" not in dset.det_model:
        my_current = raser.CalCurrent(my_d, my_f, my_g4p, dset)
        ele_current = raser.Amplifier(my_d, dset.amplifer)
        drawsave.drawplot(my_d,ele_current,my_f,my_g4p,my_current)
    else:
        batch_loop(dset,my_d, my_f, my_g4p)
    del my_f

def set_electrodes(dset):
    det_dic = dset.detector
    if det_dic['custom_electron'] == "False":
        pass
    elif det_dic['custom_electron'] == "True":
        l_x = det_dic['lx'] 
        l_y = det_dic['ly']  
        l_z = det_dic['lz'] 
        e_int = det_dic['e_gap']
        e_ir = det_dic['e_ir']
        e_t_xy = e_int/math.sqrt(2)
        e_tr=[]
        e_t_1 = [l_x*0.5           , l_y*0.5         , e_ir,0, l_z,"p"]
        e_t_2 = [l_x*0.5-e_t_xy    , l_y*0.5-e_t_xy  , e_ir,0, l_z,"n"]
        e_t_3 = [l_x*0.5-e_t_xy    , l_y*0.5+e_t_xy  , e_ir,0, l_z,"n"]
        e_t_4 = [l_x*0.5+e_t_xy    , l_y*0.5-e_t_xy  , e_ir,0, l_z,"n"]
        e_t_5 = [l_x*0.5+e_t_xy    , l_y*0.5+e_t_xy  , e_ir,0, l_z,"n"]
        for i in range(5):
           n_e = eval('e_t_' + str(i+1))
           e_tr.append(n_e)
        dset.electron_custom(e_tr)
    else:
        print("The electrode model is wrong.")

def batch_loop(dset,my_d, my_f, my_g4p):
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
    start_n = dset.intance_number * dset.total_events
    end_n = (dset.intance_number + 1) * dset.total_events
    effective_number = 0
    for event in range(start_n,end_n):
        print("run events number:%s"%(event))
        if len(my_g4p.p_steps[event-start_n]) > 5:
            effective_number += 1
            my_current = raser.CalCurrent(my_d, my_f, my_g4p, dset, event-start_n)
            ele_current = raser.Amplifier(my_d, dset.amplifer)
            drawsave.savedata(my_d,dset.output,event,ele_current,my_g4p,start_n,my_f)
            del ele_current
    detection_efficiency =  effective_number/(end_n-start_n) 
    print("detection_efficiency=%s"%detection_efficiency)


if __name__ == '__main__':
    start = time.time()
    main()
    print("drift_total1:%s"%(time.time()-start))
    print("RUN END")
    os._exit(0) 