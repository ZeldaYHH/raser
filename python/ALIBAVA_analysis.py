#!/usr/bin/env python3

import ROOT
import os
import sys
import numpy as np
from array import array
import h5py

def import_h5(path):
    try:
        if not os.path.exists(os.path.normpath(path)):
            raise Exception('The path {!s} does not exist.'.format(path))
        return h5py.File(os.path.normpath(path), 'r')
    except OSError as err:
        return False

def dir_maker(path, file_name):
    try:
        os.mkdir(os.path.join(path, file_name))
    except:
        pass

def get_data_list(data_path):
    RSrun_list = []
    calibration_list = []
    ped_list = []
    for file in os.listdir(data_path):
        if 'ped' in file:
            ped_list.append(file)
        elif 'calibration' in file:
            calibration_list.append(file)
        else:
            RSrun_list.append(file)

    return ped_list, calibration_list ,RSrun_list

def Analysis_ped(data_path, ped_list):
    ped_path = os.path.join(data_path, ped_list[0])
    ped_data = import_h5(ped_path)

    numchan = len(ped_data["events"]["signal"][0])
    signal = np.array(ped_data["events"]["signal"][:], dtype=np.float32)
    pedestal = np.mean(ped_data["events"]["signal"][0:], axis=0)

    cm = np.subtract(signal, pedestal, dtype=np.float32)
    keep = np.array(list(range(0,len(signal))))
    for i in range(3): 
        CMsig = np.std(cm[keep], axis=1)
        CMnoise = np.mean(cm[keep], axis=1)
        keep = np.where(np.logical_and(CMnoise<(CMnoise+2.5*CMsig), CMnoise>(CMnoise-2.5*CMsig)))[0]
    score = np.subtract(cm[keep], CMnoise[keep][:,None], dtype=np.float32)
    noise = np.std(score, axis=0)
    noiseNC = np.std(cm[keep], axis=0)

    return noise, noiseNC, CMnoise, CMsig, numchan, pedestal

def Analysis_RSrun(pedestal, data_path, RSrun, Channel = False, Channel_used = 1):
    RSrun_path = os.path.join(data_path, RSrun)
    RSrun_data = import_h5(RSrun_path)

    signal = RSrun_data["events"]["signal"][0:] - pedestal
    numevents = np.arange(signal.shape[0])
    hit_channal = np.argmax(np.abs(signal), axis=1)
    if Channel:
        signal_hit = signal[:, Channel_used]
    else:
        signal_hit = signal[numevents, hit_channal]

    return numevents, hit_channal, signal_hit

def plot_noise(noise, numchan, ouput_path, filename):
    canvas = ROOT.TCanvas('noise', 'noise', 700, 600)
    graph = ROOT.TGraph()
    graph.SetTitle(filename)
    graph.GetXaxis().SetTitle('Channel')
    graph.GetXaxis().SetTitleSize(0.05)
    graph.GetXaxis().SetTitleOffset(0.9)
    graph.GetYaxis().SetTitle('Charge [ADC]')
    graph.GetYaxis().SetTitleSize(0.05)
    graph.GetYaxis().SetTitleOffset(0.9)
    for channal in range(0, numchan):
        graph.SetPoint(channal, channal, noise[channal])
    graph.Draw("AB")
    canvas.SaveAs(os.path.join(ouput_path,sys.argv[1], filename + '.root'))

def plot_signal(signal_hit, ouput_path, filename):
    canvas = ROOT.TCanvas('signal', 'signal', 700, 600)
    num_bins = 100
    graph = ROOT.TH1F('', '',num_bins, min(signal_hit) ,max(signal_hit))
    graph.SetTitle("Signal")
    graph.SetLineColor(1)
    graph.GetXaxis().SetTitle('Charge [ADC]')
    graph.GetXaxis().SetTitleSize(0.05)
    graph.GetXaxis().SetTitleOffset(0.9)
    graph.GetYaxis().SetTitle('events')
    graph.GetYaxis().SetTitleSize(0.05)
    graph.GetYaxis().SetTitleOffset(0.9)
    for sign in signal_hit:
        graph.Fill(sign)
    graph.Draw()

    signal_1 = ROOT.TH1F('', '', num_bins, min(signal_hit) ,max(signal_hit))
    signal_2 = ROOT.TH1F('', '', num_bins, min(signal_hit) ,max(signal_hit))
    graph_1 = ROOT.TGraph()
    graph_2 = ROOT.TGraph()
    graph_1.SetLineColor(2)
    graph_2.SetLineColor(3)

    i = 0
    for sign in signal_hit:
        i = i + 1
        if i % 2 ==1:
            sign_1 = sign
        if i % 2 == 0:
            sign_2 = sign
            signal_1.Fill(min(sign_1, sign_2))
            signal_2.Fill(max(sign_1, sign_2))

    bin_width = graph.GetBinWidth(1)
    for i in range(0, num_bins):
        graph_1.SetPoint(i, min(signal_hit) + bin_width * (i - 0.5), signal_1.GetBinContent(i))
        graph_2.SetPoint(i, min(signal_hit) + bin_width * (i - 0.5), signal_2.GetBinContent(i))

    graph_1.Draw("same")
    graph_2.Draw("same")
    canvas.Update()
    canvas.SaveAs(os.path.join(ouput_path,sys.argv[1], filename +'_signal.root'))

def plot_hitmap(numchan, hit_channal, ouput_path, filename):
    canvas = ROOT.TCanvas('signal', 'signal', 700, 600)
    graph = ROOT.TH1F('','',numchan, 0 ,numchan)
    graph.SetTitle("Hit map")
    graph.GetXaxis().SetTitle('Channel')
    graph.GetXaxis().SetTitleSize(0.05)
    graph.GetXaxis().SetTitleOffset(0.9)
    graph.GetYaxis().SetTitle('events')
    graph.GetYaxis().SetTitleSize(0.05)
    graph.GetYaxis().SetTitleOffset(0.9)

    for hit in hit_channal:
        graph.Fill(hit)

    graph.Draw()
    canvas.SaveAs(os.path.join(ouput_path,sys.argv[1], filename + '_hitmap.root'))

def main():
    data_path = os.path.join('data', sys.argv[1])
    ouput_path = 'output'
    Channel = True
    Channel_used = 114
    dir_maker(ouput_path, sys.argv[1])

    ped_list, calibration_list ,RSrun_list  = get_data_list(data_path)

    if len(ped_list) != 1 or len(calibration_list) != 1:
        print("Please use only one ped and calibration")
        exit(0)

    print("Analysising ped file")
    noise, noiseNC, CMnoise, CMsig, numchan, pedestal = Analysis_ped(data_path, ped_list)
    plot_noise(noise, numchan, ouput_path, 'noise')
    plot_noise(noiseNC, numchan, ouput_path, 'noiseNC')

    print("Analysising RSrun file")
    if Channel:
        for RSrun in RSrun_list:
            numevents, hit_channal, signal_hit = Analysis_RSrun(pedestal, data_path, RSrun, True, Channel_used)
            plot_signal(signal_hit, ouput_path, RSrun)
    else:
        for RSrun in RSrun_list:
            numevents, hit_channal, signal_hit = Analysis_RSrun(pedestal, data_path, RSrun)
            plot_hitmap(numchan, hit_channal, ouput_path, RSrun)
            plot_signal(signal_hit, ouput_path, RSrun)
 
if __name__ == '__main__':
    main()





