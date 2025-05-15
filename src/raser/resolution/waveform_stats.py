import os
import re
import json
from array import array

import ROOT

from util.output import output
from util.math import is_number, fit_data_normal, fit_data_landau

CFD = 0.5 # partition
#TODO: get threshold and CFD from electronics setting

class InputWaveform():
    """
    ToA : time of arrival
    ToT : time over threshold
    amplitude : peak amplitude for charge sensitive preamp
    charge : total charge for current sensitive preamp
    ToR : time of ratio (CFD)
    """
    def __init__(self, input_entry, threshold, amplitude_threshold, read_ele_num=1, CFD=CFD):
        self.waveforms = [None for _ in range(read_ele_num)]
        self.read_ele_num = read_ele_num
        self.CFD = CFD
        self.peak_time = [0 for i in range(read_ele_num)]
        self.ToA = [0 for i in range(read_ele_num)]
        self.ToT = [0 for i in range(read_ele_num)]
        self.amplitude = [0 for i in range(read_ele_num)] # for charge sensitive pre amp
        self.charge = [0 for i in range(read_ele_num)] # for current sensitive pre amp
        self.ToR = [0 for i in range(read_ele_num)]
        self.threshold = threshold
        self.amplitude_threshold = amplitude_threshold

        for i in range(read_ele_num):
            self.waveforms[i] = eval(f"input_entry.amplified_waveform_{i}")
            self.amplitude[i], self.peak_time[i] = get_amplitude(self.waveforms[i])
            if self.amplitude[i] < self.threshold:
                self.amplitude[i] = 0
                self.ToA[i] = None
                self.ToT[i] = 0
                self.charge[i] = 0
                self.ToR[i] = None
            else:
                self.ToA[i] = get_ToA(self.waveforms[i], self.threshold, self.peak_time[i])
                self.ToT[i] = get_ToT(self.waveforms[i], self.threshold, self.peak_time[i])
                self.charge[i] = get_charge(self.waveforms[i])
                self.ToR[i] = get_ToR(self.waveforms[i], CFD, self.peak_time[i])

        self.get_total_data()

    def get_total_data(self):
        self.data = {}
        if max(self.amplitude) < self.amplitude_threshold:
            self.data["gravity_center_ToT"] = None
            self.data["gravity_center_amplitude"] = None
            self.data["gravity_center_charge"] = None
            self.data["ToA"] = None
            self.data["ToT"] = None
            self.data["amplitude"] = None
            self.data["charge"] = None
            self.data["ToR"] = None
        elif self.read_ele_num == 1:
            self.data["gravity_center_ToT"] = 0 # No spacial resolution
            self.data["gravity_center_amplitude"] = 0
            self.data["gravity_center_charge"] = 0
            self.data["ToA"] = self.ToA[0]
            self.data["ToT"] = self.ToT[0]
            self.data["amplitude"] = self.amplitude[0]
            self.data["charge"] = self.charge[0]
            self.data["ToR"] = self.ToR[0]
        else:
            # assume strip, one dimensional spacial resolution
            self.data["gravity_center_ToT"] = get_gravity_center(self.ToT, 10e-9) # TODO: assign a proper value for all DAQ systems
            self.data["gravity_center_amplitude"] = get_gravity_center(self.amplitude, self.amplitude_threshold)
            self.data["gravity_center_charge"] = get_gravity_center(self.charge, 1e5) # TODO: assign a proper value for all DAQ systems
            self.data["ToA"] = get_conjoined_time(self.ToA) # TODO: conjoint measurement
            self.data["ToT"] = get_total_amp(self.ToT, 10e-9)
            self.data["amplitude"] = get_total_amp(self.amplitude, self.amplitude_threshold)
            self.data["charge"] = get_total_amp(self.charge, 1e5)
            self.data["ToR"] = get_conjoined_time(self.ToR) # TODO: conjoint measurement

def get_ToA(hist, threshold, peak_time_bin):
    for i in range(peak_time_bin, 0, -1):
        content = hist.GetBinContent(i)
        if abs(content) < threshold:
            return hist.GetBinCenter(i)
    return None

def get_ToT(hist, threshold, peak_time_bin):
    start = None
    for i in range(peak_time_bin, 0, -1):
        content = abs(hist.GetBinContent(i))
        if content < threshold:
            start = hist.GetBinCenter(i)
            break
    if start is None:
        return 0.0
    end = None
    for i in range(peak_time_bin, hist.GetNbinsX() + 1):
        content = abs(hist.GetBinContent(i))
        if content < threshold:
            end = hist.GetBinCenter(i)
            break
    if end is None:
        return 0.0
    return end - start

def get_amplitude(hist):
    max_val = 0.0
    peak_bin = 0
    for i in range(1, hist.GetNbinsX() + 1):
        content = abs(hist.GetBinContent(i))
        if content > max_val:
            max_val = content
            peak_bin = i
    return max_val, peak_bin

def get_charge(hist):
    charge = 0.0
    for i in range(1, hist.GetNbinsX() + 1):
        charge += abs(hist.GetBinContent(i))
    return charge

def get_ToR(hist, CFD, peak_time_bin):
    amplitude = abs(hist.GetBinContent(peak_time_bin))
    target = amplitude * CFD
    for i in range(peak_time_bin, 0, -1):
        content = abs(hist.GetBinContent(i))
        if content > target:
            return hist.GetBinCenter(i)
    return None

def get_conjoined_time(time_list):
    # TODO: conjoint measurement
    new_list = remove_none(time_list)
    if len(new_list) == 0:
        return None
    return min(new_list)

def get_total_amp(amp_list, amp_thres):
    max_amp = max(amp_list)
    i_max = amp_list.index(max_amp)
    if max_amp == 0:
        return None
    seeds = set()
    for i in range(len(amp_list)):
        if amp_list[i] > amp_thres:
            seeds.add(i)
    if len(seeds) == 0:
        return None
    new_seeds = set()
    for i in seeds:
        new_seeds.add(i)
        if i > 0:
            new_seeds.add(i-1)
        if i < len(amp_list) - 1:
            new_seeds.add(i+1)
    return sum([amp_list[i] for i in new_seeds])

def get_gravity_center(amp_list, amp_thres):
    max_amp = max(amp_list)
    i_max = amp_list.index(max_amp)
    if max_amp == 0:
        return None
    seeds = set()
    for i in range(len(amp_list)):
        if amp_list[i] > amp_thres:
            seeds.add(i)
    if len(seeds) == 0:
        return None
    new_seeds = set()
    for i in seeds:
        new_seeds.add(i)
        if i > 0:
            new_seeds.add(i-1)
        if i < len(amp_list) - 1:
            new_seeds.add(i+1)
    return sum([i * amp_list[i] for i in new_seeds]) / sum(amp_list[i] for i in new_seeds)

def remove_none(list):
    new_list = []
    for i in list:
        if i == None:
            continue
        new_list.append(i)
    return new_list

class WaveformStatistics():
    def __init__(self, input_path, read_ele_num, threshold, amplitude_threshold, output_path, vis=False):
        self.ToA_data = []
        self.ToT_data = []
        self.amplitude_data = []
        self.charge_data = []
        self.ToR_data = []
        self.gravity_center_ToT_data = []
        self.gravity_center_amplitude_data = []
        self.gravity_center_charge_data = []
        self.waveforms = [[] for i in range(read_ele_num)]

        self.output_path = output_path

        files = os.listdir(input_path)
        files.sort()
        for file in files:
            if '.root' not in file:
                continue
            
            path = os.path.join(input_path, file)
            file_pointer = ROOT.TFile(path, "READ")
            tree = file_pointer.Get("tree")
            n = tree.GetEntries()
            for i in range(n):
                tree.GetEntry(i) 
                iw = InputWaveform(tree, threshold, amplitude_threshold, read_ele_num)
                self.fill_data(iw.data)
                if vis == True:
                    for j in range(read_ele_num):
                        self.waveforms[j].append(iw.waveforms[j])

            print("read {n} events from {file}".format(n=n, file=file))
            file_pointer.Close()

        if vis == True:
            for j in range(read_ele_num):
                canvas = ROOT.TCanvas("canvas", "Canvas", 800, 600)
                multigraph = ROOT.TMultiGraph("mg","")
                count = 0
                for waveform in (self.waveforms[j]):
                    if count > 100:
                        break
                    x = [float(i[0]) for i in waveform]
                    y = [float(i[1]) for i in waveform]
                    graph = ROOT.TGraph(len(x), array('f', x), array('f', y))
                    multigraph.Add(graph)
                    count += 1
                multigraph.Draw("APL")
                canvas.SaveAs(os.path.join(output_path, "waveform_electrode_{}.pdf".format(j)))
                canvas.SaveAs(os.path.join(output_path, "waveform_electrode_{}.png".format(j)))

        self.time_resolution_fit(self.ToA_data, "ToA")
        self.time_resolution_fit(self.ToR_data, "ToR")
        self.amplitude_fit(self.amplitude_data, "amplitude")
        self.amplitude_fit(self.charge_data, "charge")
        self.amplitude_fit(self.ToT_data, "ToT")
        self.gravity_center_fit(self.gravity_center_ToT_data, "gravity_center_ToT")
        self.gravity_center_fit(self.gravity_center_amplitude_data, "gravity_center_amplitude")
        self.gravity_center_fit(self.gravity_center_charge_data, "gravity_center_charge")
    
    def fill_data(self, data):
        self.ToA_data.append(data["ToA"])
        self.ToT_data.append(data["ToT"])
        self.amplitude_data.append(data["amplitude"])
        self.charge_data.append(data["charge"])
        self.ToR_data.append(data["ToR"])
        self.gravity_center_amplitude_data.append(data["gravity_center_amplitude"])
        self.gravity_center_charge_data.append(data["gravity_center_charge"])
        self.gravity_center_ToT_data.append(data["gravity_center_ToT"])

    def time_resolution_fit(self, data, model):
        data = remove_none(data)
        try:
            x2_min = min(data)
            x2_max = sorted(data)[int(len(data))-1]
        except ValueError:
            print("No valid data for "+model)
            x2_min = 0
            x2_max = 0
        n2_bin = 100
        histo=ROOT.TH1F("","",n2_bin,x2_min,x2_max)
        for i in range(0,len(data)):
            histo.Fill(data[i])
        fit_func_1,_,_,sigma,sigma_error=fit_data_normal(histo,x2_min,x2_max)# in nanosecond
        sigma=sigma*1e12 # in picosecond
        sigma_error=sigma_error*1e12

        c1 = ROOT.TCanvas("c1","c1",200,10,800,600)
        ROOT.gStyle.SetOptStat(0)
        c1.SetGrid()
        c1.SetLeftMargin(0.2)
        c1.SetTopMargin(0.12)
        c1.SetBottomMargin(0.2)

        histo.GetXaxis().SetTitle(model+" [s]")
        histo.GetYaxis().SetTitle("Events")
        histo.GetXaxis().SetTitleOffset(1.2)
        histo.GetXaxis().SetTitleSize(0.07)
        histo.GetXaxis().SetLabelSize(0.05)
        histo.GetXaxis().SetNdivisions(510)
        histo.GetYaxis().SetTitleOffset(1.1)
        histo.GetYaxis().SetTitleSize(0.07)
        histo.GetYaxis().SetLabelSize(0.05)
        histo.GetYaxis().SetNdivisions(505)
        histo.GetXaxis().CenterTitle()
        histo.GetYaxis().CenterTitle()
        histo.SetLineWidth(2)

        # Legend setting
        leg = ROOT.TLegend(0.75, 0.6, 0.85, 0.8)
        leg.AddEntry(fit_func_1,"Fit","L")
        leg.AddEntry(histo,"Sim","L")
        # Draw
        histo.Draw()
        fit_func_1.Draw("same")
        leg.Draw("same")
        # Text set
        tex = ROOT.TLatex()
        tex.SetNDC(1)
        tex.SetTextFont(43)
        tex.SetTextSize(25)
        #tex.DrawLatexNDC(0.65, 0.7, "CFD=0.5")
        tex.DrawLatexNDC(0.65, 0.6, "#sigma = %.3f #pm %.3f ps"%(sigma,sigma_error))
        # Save
        c1.SaveAs(self.output_path+'/'+model+".pdf")
        c1.SaveAs(self.output_path+'/'+model+".C")

    def amplitude_fit(self, data, model):
        data = remove_none(data)
        try:
            x2_min = min(data)
            x2_max = sorted(data)[int(len(data))-1]
        except ValueError:
            print("No valid data for "+model)
            x2_min = 0
            x2_max = 0
        n2_bin = 100
        histo=ROOT.TH1F("","",n2_bin,x2_min,x2_max)
        for i in range(0,len(data)):
            histo.Fill(data[i])
        fit_func_1,mean,mean_error,sigma,sigma_error=fit_data_landau(histo,x2_min,x2_max)

        c1 = ROOT.TCanvas("c1","c1",200,10,800,600)
        ROOT.gStyle.SetOptStat(0)
        c1.SetGrid()
        c1.SetLeftMargin(0.2)
        c1.SetTopMargin(0.12)
        c1.SetBottomMargin(0.2)

        histo.GetXaxis().SetTitle(model+" [a.u.]")
        histo.GetYaxis().SetTitle("Events")
        histo.GetXaxis().SetTitleOffset(1.2)
        histo.GetXaxis().SetTitleSize(0.07)
        histo.GetXaxis().SetLabelSize(0.05)
        histo.GetXaxis().SetNdivisions(510)
        histo.GetYaxis().SetTitleOffset(1.1)
        histo.GetYaxis().SetTitleSize(0.07)
        histo.GetYaxis().SetLabelSize(0.05)
        histo.GetYaxis().SetNdivisions(505)
        histo.GetXaxis().CenterTitle()
        histo.GetYaxis().CenterTitle()
        histo.SetLineWidth(2)
        histo.SetLineWidth(2)

        # Legend setting
        leg = ROOT.TLegend(0.75, 0.6, 0.85, 0.8)
        leg.AddEntry(fit_func_1,"Fit","L")
        leg.AddEntry(histo,"Sim","L")
        # Draw
        histo.Draw()
        fit_func_1.Draw("same")
        leg.Draw("same")
        # Text set
        tex = ROOT.TLatex()
        tex.SetNDC(1)
        tex.SetTextFont(43)
        tex.SetTextSize(25)
        tex.DrawLatexNDC(0.65, 0.6, "%.3g #pm %.3g a.u."%(mean,sigma))
        # Save
        c1.SaveAs(self.output_path+'/'+model+".pdf")
        c1.SaveAs(self.output_path+'/'+model+".C")

    def gravity_center_fit(self, data, model):
        data = remove_none(data)
        
        try:
            mid = sorted(data)[int(len(data)/2)]
        except IndexError:
            print("No valid data for "+model)
            return
        x2_min = mid-2
        x2_max = mid+2
        n2_bin = 100
        histo=ROOT.TH1F("","",n2_bin,x2_min,x2_max)
        for i in range(0,len(data)):
            histo.Fill(data[i])
        fit_func_1,_,_,sigma,sigma_error=fit_data_normal(histo,x2_min,x2_max)
        sigma=sigma
        sigma_error=sigma_error

        c1 = ROOT.TCanvas("c1","c1",200,10,800,600)
        ROOT.gStyle.SetOptStat(0)
        c1.SetGrid()
        c1.SetLeftMargin(0.2)
        c1.SetTopMargin(0.12)
        c1.SetBottomMargin(0.2)

        histo.GetXaxis().SetTitle(model)
        histo.GetYaxis().SetTitle("Events")
        histo.GetXaxis().SetTitleOffset(1.2)
        histo.GetXaxis().SetTitleSize(0.07)
        histo.GetXaxis().SetLabelSize(0.05)
        histo.GetXaxis().SetNdivisions(510)
        histo.GetYaxis().SetTitleOffset(1.1)
        histo.GetYaxis().SetTitleSize(0.07)
        histo.GetYaxis().SetLabelSize(0.05)
        histo.GetYaxis().SetNdivisions(505)
        histo.GetXaxis().CenterTitle()
        histo.GetYaxis().CenterTitle()
        histo.SetLineWidth(2)

        # Legend setting
        leg = ROOT.TLegend(0.75, 0.6, 0.85, 0.8)
        leg.AddEntry(fit_func_1,"Fit","L")
        leg.AddEntry(histo,"Sim","L")
        # Draw
        histo.Draw()
        fit_func_1.Draw("same")
        leg.Draw("same")
        # Text set
        tex = ROOT.TLatex()
        tex.SetNDC(1)
        tex.SetTextFont(43)
        tex.SetTextSize(25)
        #tex.DrawLatexNDC(0.65, 0.7, "CFD=0.5")
        tex.DrawLatexNDC(0.65, 0.6, "#sigma = %.3f #pm %.3f"%(sigma,sigma_error))
        # Save
        c1.SaveAs(self.output_path+'/'+model+".pdf")
        c1.SaveAs(self.output_path+'/'+model+".C")


def main(kwargs):
    det_name = kwargs['det_name']
    device_json = os.getenv("RASER_SETTING_PATH")+"/detector/" + det_name + ".json"
    with open(device_json) as f:
        device_dict = json.load(f)
        if device_dict['det_model'] == 'planar' or device_dict['det_model'] == 'lgad':
            read_ele_num = 1
        else:
            read_ele_num = device_dict['read_ele_num']
        daq_name = device_dict['daq']

    if kwargs['daq'] != None:
        daq_name = kwargs['daq']

    daq_json = os.getenv("RASER_SETTING_PATH")+"/daq/" + daq_name + ".json"
    with open(daq_json) as f:
        daq_dict = json.load(f)
        threshold = daq_dict['threshold']
        amplitude_threshold = daq_dict['amplitude_threshold']

    tct = kwargs['tct']
    if tct != None:
        input_path = "output/tct/" + det_name + "/" + tct
    else:
        input_path = "output/signal/" + det_name + "/batch"

    output_path = output(__file__, det_name)
    WaveformStatistics(input_path, read_ele_num, threshold, amplitude_threshold, output_path)
