#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@Description: The main program of Raser induced current simulation      
@Date       : 2024/09/26 15:11:20
@Author     : tanyuhang, Chenxi Fu
@version    : 2.0
'''
import sys
import os
import array
import time
import subprocess
import json
import random

import ROOT
ROOT.gROOT.SetBatch(True)

from device import build_device as bdv
from interaction import g4_general as g4g
from field import devsim_field as devfield
from current import cal_current as ccrt
from afe import readout as rdo
from util.output import output
from util.math import inversed_fast_fourier_transform as ifft


def batch_loop(my_d, my_f, my_g4p, amplifier, g4_seed, total_events, instance_number):
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
    start_n = instance_number * total_events
    end_n = (instance_number + 1) * total_events

    effective_number = 0

    ele_json = os.getenv("RASER_SETTING_PATH")+"/electronics/" + amplifier + ".json"
    ele_cir = os.getenv("RASER_SETTING_PATH")+"/electronics/" + amplifier + ".cir"
    if os.path.exists(ele_json):
        ROOT.gRandom.SetSeed(instance_number) # to ensure time resolution result reproducible
    elif os.path.exists(ele_cir):
        subprocess.run(['ngspice -b '+ele_cir], shell=True)
        noise_raw = "./output/elec/" + amplifier + "/noise.raw" # need to be fixed in the .cir
        try:
            with open(noise_raw, 'r') as f_in:
                lines = f_in.readlines()
                freq, noise = [],[]
                for line in lines:
                    freq.append(float(line.split()[0]))
                noise.append(float(line.split()[1]))
        except FileNotFoundError:
            print("Warning: ngspice .noise experiment is not set.")
            print("Please check the .cir file or make sure you have set an TRNOISE source.")
        # TODO: fix noise seed, add noise from ngspice .noise spectrum

    for event in range(start_n,end_n):
        print("run events number:%s"%(event))
        if len(my_g4p.p_steps[event-start_n]) > 5:
            effective_number += 1
            my_current = ccrt.CalCurrentG4P(my_d, my_f, my_g4p, event-start_n)
            ele_current = rdo.Amplifier(my_current.sum_cu, amplifier, is_cut=True)

            e_dep = "%.5f"%(my_g4p.edep_devices[event-start_n]) #mv
            tag = "event" + str(event) + "_" + "Edep" + str(e_dep)
            # need to add ngspice branch 
            ele_current.save_signal_TTree(output(__file__, my_d.det_name, 'batch'), tag)
            del ele_current

    detection_efficiency =  effective_number/(end_n-start_n) 
    print("detection_efficiency=%s"%detection_efficiency)

def main(kwargs):
    det_name = kwargs['det_name']
    my_d = bdv.Detector(det_name)
    
    if kwargs['voltage'] != None:
        voltage = kwargs['voltage']
    else:
        voltage = my_d.voltage

    if kwargs['g4experiment'] != None:
        g4experiment = kwargs['g4experiment']
    else:
        g4experiment = my_d.g4experiment

    if kwargs['amplifier'] != None:
        amplifier = kwargs['amplifier']
    else:
        amplifier = my_d.amplifier

    my_f = devfield.DevsimField(my_d.device, my_d.dimension, voltage, my_d.read_out_contact, my_d.irradiation_flux)

    geant4_json = os.getenv("RASER_SETTING_PATH")+"/g4experiment/" + g4experiment + ".json"
    with open(geant4_json) as f:
        g4_dic = json.load(f)
    total_events = int(g4_dic['total_events'])

    job_number = kwargs['job']
    instance_number = job_number

    g4_seed = instance_number * total_events
    my_g4p = g4g.Particles(my_d, g4experiment, g4_seed)
    batch_loop(my_d, my_f, my_g4p, amplifier, g4_seed, total_events, instance_number)
    del my_g4p

