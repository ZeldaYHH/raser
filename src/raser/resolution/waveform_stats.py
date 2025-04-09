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
    def __init__(self, input_entry, threshold, read_ele_num=1, CFD=CFD):
        self.waveforms = [None for _ in range(read_ele_num)]
        self.read_ele_num = read_ele_num
        self.CFD = CFD
        self.ToA = [0 for i in range(read_ele_num)]
        self.ToT = [0 for i in range(read_ele_num)]
        self.amplitude = [0 for i in range(read_ele_num)] # for charge sensitive pre amp
        self.charge = [0 for i in range(read_ele_num)] # for current sensitive pre amp
        self.ToR = [0 for i in range(read_ele_num)]
        self.threshold = threshold

        time = input_entry.time
        for i in range(read_ele_num):
            amp = eval(f"input_entry.data_amp_{i}")
            self.waveforms[i] = list(zip(time, amp))
            self.amplitude[i] = get_amplitude(self.waveforms[i])
            if self.amplitude[i] < self.threshold:
                self.amplitude[i] = None
                self.ToA[i] = None
                self.ToT[i] = None
                self.charge[i] = None
                self.ToR[i] = None
            else:
                self.ToA[i] = get_ToA(self.waveforms[i], self.threshold)
                self.ToT[i] = get_ToT(self.waveforms[i], self.threshold)
                self.charge[i] = get_charge(self.waveforms[i])
                self.ToR[i] = get_ToR(self.waveforms[i], self.amplitude[i], CFD)

        self.get_total_data()

    def get_total_data(self):
        self.data = {}
        if self.read_ele_num == 1:
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
            self.data["gravity_center_ToT"] = get_gravity_center(self.ToT)
            self.data["gravity_center_amplitude"] = get_gravity_center(self.amplitude)
            self.data["gravity_center_charge"] = get_gravity_center(self.charge)
            self.data["ToA"] = get_conjoined_time(self.ToA) # TODO: conjoint measurement
            self.data["ToT"] = get_total_amp(self.ToT)
            self.data["amplitude"] = get_total_amp(self.amplitude)
            self.data["charge"] = get_total_amp(self.charge)
            self.data["ToR"] = get_conjoined_time(self.ToR) # TODO: conjoint measurement

def get_ToA(waveform, threshold):
    for i in waveform:
        if abs(float(i[1])) > threshold:
            return float(i[0])

def get_ToT(waveform, threshold):
    for i in waveform:
        if abs(float(i[1])) > threshold:
            start = float(i[0])
            break
    else:
        return None
    for i in waveform[::-1]:
        if abs(float(i[1])) > threshold:
            end = float(i[0])
            break
    else:
        return None
    return end - start

def get_amplitude(waveform):
    return max(abs(float(i[1])) for i in waveform)

def get_charge(waveform):
    return abs(sum(float(i[1]) for i in waveform))

def get_ToR(waveform, amplitude, CFD):
    # CFD = Constant Fraction Discriminator
    for i in waveform:
        if abs(float(i[1])) > amplitude * CFD:
            return float(i[0])
        
def get_conjoined_time(time_list):
    # TODO: conjoint measurement
    new_list = remove_none(time_list)
    if len(new_list) == 0:
        return None
    return min(new_list)

def get_total_amp(amp_list):
    # TODO: conjoint measurement
    new_list = remove_none(amp_list)
    if len(new_list) == 0:
        return None
    return sum(new_list)

def get_gravity_center(amp_list):
    zip_list = zip(amp_list,range(len(amp_list)))
    new_zip = []
    for (amp,i) in zip_list:
        if amp == None:
            continue
        else:
            new_zip.append((amp,i))
    if len(new_zip) == 0:
        return None
    return sum([amp * i for (amp,i) in new_zip]) / sum([amp for (amp,i) in new_zip])

def remove_none(list):
    new_list = []
    for i in list:
        if i == None:
            continue
        new_list.append(i)
    return new_list

class WaveformStatistics():
    def __init__(self, input_path, read_ele_num, threshold, output_path):
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
            if '.root' not in file or "amp" not in file:
                continue
            
            path = os.path.join(input_path, file)
            file_pointer = ROOT.TFile(path, "READ")
            tree = file_pointer.Get("tree")
            for i in range(tree.GetEntries()):
                tree.GetEntry(i) 
                iw = InputWaveform(tree, threshold)
                self.fill_data(iw.data)
                for j in range(read_ele_num):
                    self.waveforms[j].append(iw.waveforms[j])

        for j in range(read_ele_num):
            canvas = ROOT.TCanvas("canvas", "Canvas", 800, 600)
            multigraph = ROOT.TMultiGraph("mg","")
            for waveform in (self.waveforms[j]):
                x = [float(i[0]) for i in waveform]
                y = [float(i[1]) for i in waveform]
                graph = ROOT.TGraph(len(x), array('f', x), array('f', y))
                multigraph.Add(graph)
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

    tct = kwargs['tct']
    if tct != None:
        input_path = "output/tct/" + det_name + "/" + tct
    else:
        input_path = "output/signal/" + det_name + "/batch"

    output_path = output(__file__, det_name)
    WaveformStatistics(input_path, read_ele_num, threshold, output_path)
