#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import json
import os

class Detector:
    """
    Description:
    ---------
        Different types detectors parameters assignment.
    Parameters:
    ---------
    device_name : string
        name the device and define the device by device.json 
    dimension : int
        the dimension of devsim mesh
    Modify:
    ---------
        2023/12/03
    """ 
    def __init__(self, device_name):
        self.det_name = device_name
        self.device = device_name
        self.region = device_name
        device_json = os.getenv("RASER_SETTING_PATH")+"/detector/" + device_name + ".json"
        with open(device_json) as f:
            self.device_dict = json.load(f)
        self.dimension = self.device_dict['default_dimension']

        self.l_x = self.device_dict['lx'] 
        self.l_y = self.device_dict['ly']  
        self.l_z = self.device_dict['lz'] 
        
        self.voltage = float(self.device_dict['bias']['voltage'])
        self.temperature = self.device_dict['temperature']
        self.material = self.device_dict['material']

        self.det_model = self.device_dict['det_model']
        self.doping = self.device_dict['doping']
        self.read_out_contact = self.device_dict["read_out_contact"]
        if "irradiation" in self.device_dict:
            self.irradiation_model = self.device_dict['irradiation']['irradiation_model']
            self.irradiation_flux = self.device_dict['irradiation']['irradiation_flux']
        else:
            self.irradiation_model = None
            self.irradiation_flux = 0

        self.g4experiment = self.device_dict['g4experiment']
        self.amplifier = self.device_dict['amplifier']


        if "lgad" in self.det_model:
            self.avalanche_bond = self.device_dict['avalanche_bond']
            self.avalanche_model = self.device_dict['avalanche_model']
            
        if "3Dpixel" in self.det_model: 
            self.e_r = self.device_dict['e_r']
            self.e_gap = self.device_dict['e_gap']
            self.e_t = self.device_dict['e_t']

        if "strip" in self.det_model: 
            self.read_ele_num = self.device_dict['read_ele_num']
        else:
            self.read_ele_num = 1
            
        if "pixel" in self.det_model:
            self.p_x = self.device_dict['px']
            self.p_y = self.device_dict['py']
            self.p_z = self.device_dict['pz']

if __name__ == "__main__":
    import sys
    Detector(sys.argv[1])
