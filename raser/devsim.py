#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   devsim.py
@Time    :   2023/06/04
@Author  :   Henry Stone 
@Version :   1.0
'''

import os
import csv
from scipy.interpolate import interp1d
import math

class DevsimCal:
    def __init__(self, my_d,det_name,det_dic,dev_dic):
        self.voltage = my_d.voltage
        self.protential = []
        self.l_z = my_d.l_z
        self.read_ele_num = dev_dic['read_ele_num']        
        self.lz = []
        self.elefield = []
        self.gradu = []
        if(det_name=="NJU-PIN"):
            e_field_filepath = './output/devsim/1D_NJU_PIN/'+ str(-int(det_dic['voltage'])) + '.0V_x_E.csv'
        self.readfile(e_field_filepath)

    def readfile(self, e_field_filepath):
        i = 0
        with open(e_field_filepath, 'r') as f:
            for line in f.readlines():
                try:
                    fargs = list(map(float, 
                                     line.strip('\n').strip().split(',')))
                    self.lz.append(fargs[0]*1e4) #cm->um
                    self.elefield.append(fargs[1]/1e4) #V/cm -> V/um         
                except Exception as e:
                    pass
        self.gradu.append(0)
        grad = self.voltage
        for i in range(len(self.elefield)-1):
            grad = grad - (self.elefield[i]+self.elefield[i+1]) * \
                            (self.lz[i+1]-self.lz[i]) / 2
            self.gradu.append(grad)

    def get_e_field(self, x, y, depth):
        f_ef = interp1d(self.lz, self.elefield, 
                        kind='linear', fill_value="extrapolate")
        return 0, 0, f_ef(depth) #x, y方向为0
    
    def get_w_p(self, x, y, depth, i):
        if depth >= 1:
            f_p = (1/(self.l_z-1)) * (depth-1)
        else:
            f_p = 0
        return f_p
    
    def get_potential(self, x, y, depth):
        f_u = interp1d(self.lz, self.gradu, 
                       kind = 'linear', fill_value="extrapolate")
        return f_u(depth)
