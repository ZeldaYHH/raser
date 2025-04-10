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
from array import array
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
from current.cross_talk import cross_talk
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

    length = 1000 # time length of the signal
    time = array('d', [0. for _ in range(length)])

    tree_cu = ROOT.TTree("tree", "Waveform Data")
    tree_cu.Branch("time", time, "time[{length}]/D".format(length=length))
    data_cu = []
    for i in range(my_d.read_ele_num):
        data_cu.append(array('d', [0. for _ in range(length)]))
        tree_cu.Branch("data_cu_{i}".format(i=i), data_cu[i], "data_cu_{i}[{length}]/D".format(i=i,length=length))
    
    event_cu = array('i', [0])
    tree_cu.Branch("event", event_cu, "event/I")

    other_data_cu = {}
    for i in ['e_dep']:
        other_data_cu[i] = array('d', [0.])
        tree_cu.Branch(i, other_data_cu[i], f"{i}/D")

    # Note: TTree.Branch() needs the binded variable (namely the address) to be valid and the same while Fill(), 
    # so don't put the Branch() into other methods/functions!

    if "strip" in my_d.det_model:
        tree_ct = ROOT.TTree("tree", "Waveform Data")
        tree_ct.Branch("time", time, "time[{length}]/D".format(length=length))
        data_ct = []
        for i in range(my_d.read_ele_num):
            data_ct.append(array('d', [0. for _ in range(length)]))
            tree_ct.Branch("data_ct_{i}".format(i=i), data_ct[i], "data_ct_{i}[{length}]/D".format(i=i,length=length))
        
        event_ct = array('i', [0])
        tree_ct.Branch("event", event_ct, "event/I")

        other_data_ct = {}
        for i in ['e_dep']:
            other_data_ct[i] = array('d', [0.])
            tree_ct.Branch(i, other_data_ct[i], f"{i}/D")
    
    tree_amp = ROOT.TTree("tree", "Waveform Data")
    tree_amp.Branch("time", time, "time[{length}]/D".format(length=length))
    data_amp = []
    for i in range(my_d.read_ele_num):
        data_amp.append(array('d', [0. for _ in range(length)]))
        tree_amp.Branch("data_amp_{i}".format(i=i), data_amp[i], "data_amp_{i}[{length}]/D".format(i=i,length=length))
    
    event_amp = array('i', [0])
    tree_amp.Branch("event", event_amp, "event/I")

    other_data_amp = {}
    for i in ['e_dep']:
        other_data_amp[i] = array('d', [0.])
        tree_amp.Branch(i, other_data_amp[i], f"{i}/D")

    for event in range(start_n,end_n):
        print("run events number:%s"%(event))
        if len(my_g4p.p_steps[event-start_n]) > 5:
            effective_number += 1
            my_current = ccrt.CalCurrentG4P(my_d, my_f, my_g4p, event-start_n)
            if "strip" in my_d.det_model:
                my_current.cross_talk_cu = cross_talk(my_current.sum_cu)
                ele_current = rdo.Amplifier(my_current.cross_talk_cu, amplifier, seed=event, is_cut=True)
            else:
                ele_current = rdo.Amplifier(my_current.sum_cu, amplifier, seed=event, is_cut=True)

            e_dep = my_g4p.edep_devices[event-start_n] #mv
            # need to add ngspice branch

            # Note: TTree.Fill() needs the binded variable (namely the address) to be valid and the same with Branch(), 
            # so don't put Fill() into other methods/functions!
            for j in range(my_current.sum_cu[0].GetNbinsX()):
                time[j] = j*my_current.sum_cu[0].GetBinWidth(j)
            for i in range(len(my_current.sum_cu)):
                for j in range(my_current.sum_cu[i].GetNbinsX()):
                    data_cu[i][j] = my_current.sum_cu[i].GetBinContent(j)
            kwargs = {"e_dep":e_dep}
            for key in kwargs:
                other_data_cu[key][0] = kwargs[key]

            event_cu[0] = event
                
            tree_cu.Fill()

            if "strip" in my_d.det_model:
                for j in range(my_current.cross_talk_cu[0].GetNbinsX()):
                    time[j] = j*my_current.cross_talk_cu[0].GetBinWidth(j)
                for i in range(len(my_current.cross_talk_cu)):
                    for j in range(my_current.cross_talk_cu[i].GetNbinsX()):
                        data_ct[i][j] = my_current.cross_talk_cu[i].GetBinContent(j)
                kwargs = {"e_dep":e_dep}
                for key in kwargs:
                    other_data_ct[key][0] = kwargs[key]

                event_ct[0] = event
                    
                tree_ct.Fill()

            for j in range(ele_current.amplified_currents[0].GetNbinsX()):
                time[j] = j*ele_current.amplified_currents[0].GetBinWidth(j)
            for i in range(len(ele_current.amplified_currents)):
                for j in range(ele_current.amplified_currents[i].GetNbinsX()):
                    data_amp[i][j] = ele_current.amplified_currents[i].GetBinContent(j)
            kwargs = {"e_dep":e_dep}
            for key in kwargs:
                other_data_amp[key][0] = kwargs[key]

            event_amp[0] = event

            tree_amp.Fill()

    detection_efficiency =  effective_number/(end_n-start_n) 
    print("detection_efficiency=%s"%detection_efficiency)

    output_file_cu = os.path.join(output(__file__, my_d.det_name, 'batch'),"signal_cu"+str(instance_number)+".root")
    file_cu = ROOT.TFile(output_file_cu, "RECREATE")
    tree_cu.Write()
    file_cu.Close()

    if "strip" in my_d.det_model:
        output_file_ct = os.path.join(output(__file__, my_d.det_name, 'batch'),"signal_ct"+str(instance_number)+".root")
        file_ct = ROOT.TFile(output_file_ct, "RECREATE")
        tree_ct.Write()
        file_ct.Close()

    output_file_amp = os.path.join(output(__file__, my_d.det_name, 'batch'),"signal_amp"+str(instance_number)+".root")
    file_amp = ROOT.TFile(output_file_amp, "RECREATE")
    tree_amp.Write()
    file_amp.Close()

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

