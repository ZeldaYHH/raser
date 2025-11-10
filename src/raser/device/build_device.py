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

        self.l_x = self.device_dict['l_x'] 
        self.l_y = self.device_dict["l_y"]  
        self.l_z = self.device_dict["l_z"] 
        
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

        if "cross_talk" in self.device_dict:
            self.cross_talk = self.device_dict['cross_talk']
        else:
            self.cross_talk = None

        self.g4experiment = self.device_dict['g4experiment']
        self.amplifier = self.device_dict['amplifier']
        self.daq = self.device_dict['daq']

        if "vector_delta_t" in self.device_dict:
            try:
                self.vector_delta_t = float(self.device_dict["vector_delta_t"])
            except (TypeError, ValueError):
                pass
        if "vector_boundary_tolerance" in self.device_dict:
            try:
                self.vector_boundary_tolerance = float(self.device_dict["vector_boundary_tolerance"])
            except (TypeError, ValueError):
                pass
        if "vector_field_resolution" in self.device_dict:
            try:
                self.vector_field_resolution = float(self.device_dict["vector_field_resolution"])
            except (TypeError, ValueError):
                pass
        if "vector_field_fallback" in self.device_dict:
            self.vector_field_fallback = self.device_dict["vector_field_fallback"]
        if "vector_max_steps" in self.device_dict:
            try:
                self.vector_max_steps = int(self.device_dict["vector_max_steps"])
            except (TypeError, ValueError):
                pass
        if "vector_min_field_strength" in self.device_dict:
            try:
                self.vector_min_field_strength = float(self.device_dict["vector_min_field_strength"])
            except (TypeError, ValueError):
                pass
        if "current_smoothing_window" in self.device_dict:
            try:
                self.current_smoothing_window = int(self.device_dict["current_smoothing_window"])
            except (TypeError, ValueError):
                pass
        if "current_savgol_window" in self.device_dict:
            try:
                self.current_savgol_window = int(self.device_dict["current_savgol_window"])
            except (TypeError, ValueError):
                pass
        if "current_savgol_poly" in self.device_dict:
            try:
                self.current_savgol_poly = int(self.device_dict["current_savgol_poly"])
            except (TypeError, ValueError):
                pass

        if "strip" in self.det_model:
            self.x_ele_num = self.device_dict['read_ele_num']
            self.y_ele_num = 1
            self.read_ele_num = self.device_dict['read_ele_num']
            self.field_shift_x = self.device_dict['field_shift_x']
        elif "pixel" in self.det_model:
            self.x_ele_num = self.device_dict['x_ele_num']
            self.y_ele_num = self.device_dict['y_ele_num']
            self.read_ele_num = self.device_dict['x_ele_num']*self.device_dict['y_ele_num']
            self.field_shift_x = self.device_dict['field_shift_x']
            self.field_shift_y = self.device_dict['field_shift_y']
        elif "hexagonal" in self.det_model:
            pass
        else:
            self.x_ele_num = 1
            self.y_ele_num = 1
            self.read_ele_num = 1

        if "lgad" in self.det_model:
            self.avalanche_bond = self.device_dict['avalanche_bond']
            self.avalanche_model = self.device_dict['avalanche_model']
            
        if "3D" in self.det_model: 
            self.e_r = self.device_dict['e_r']
            self.e_gap = self.device_dict['e_gap']
            self.e_t = self.device_dict['e_t']

        if "planar" in self.det_model or "lgad" == self.det_model:
            self.p_x = self.device_dict['l_x']
            self.p_y = self.device_dict['l_y']

        if "strip" in self.det_model: 
            self.p_x = self.device_dict['p_x']
            self.p_y = self.device_dict['l_y']
            
        if "pixel" in self.det_model:
            self.p_x = self.device_dict["p_x"]
            self.p_y = self.device_dict["p_y"]

        if "hexagonal" in self.det_model:
            self.p_r = self.device_dict["p_r"]

if __name__ == "__main__":
    import sys
    Detector(sys.argv[1])
