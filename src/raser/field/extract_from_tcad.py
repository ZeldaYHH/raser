#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@File    :   extract_from_tcad.py
@Time    :   2025/04/01
@Author  :   Chenxi Fu
@Version :   1.0
'''

import os
import sys
import subprocess

import devsim

from .save_milestone import save_milestone
from device.build_device import Detector
from util.math import is_number

def main(tdr_file):
    # make sure the file is in output/[det_name]/
    # and named as [bias voltage]V.tdr
    dir_name = os.path.dirname(tdr_file)
    file_base_name = os.path.basename(tdr_file)
    if not file_base_name.endswith('V.tdr'):
        raise ValueError("The input file should end with 'V.tdr'")
    else:
        bias_voltage_str = file_base_name[:-5] # remove the V.tdr suffix
    
    if not is_number(bias_voltage_str):
        raise ValueError("The bias voltage should be a number")
    
    bias_voltage_float = float(bias_voltage_str)
    
    devsim_file = os.path.join(dir_name, bias_voltage_str+'.devsim')
    det_name = os.path.basename(dir_name)
    my_detector = Detector(det_name)

    subprocess.run(['tdr_convert', 
                    '--tdr', tdr_file, 
                    '--devsim', devsim_file,
                    '--load_datasets'])

    devsim.load_devices(file=devsim_file) # no positional arguments
    print(devsim.get_device_list()[0])
    device = devsim.get_device_list()[0]

    # TODO: ensure the region name is consistent with the intrinsic area we want
    save_milestone(device, "Silicon_1", bias_voltage_float, dir_name, my_detector.dimension, None, False, is_tcad=True)

if __name__ == '__main__':
    main(sys.argv[1])