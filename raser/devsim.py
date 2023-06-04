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
    def __init__(self, filepath, my_d, dev_dic):
        self.elefield = []
        self.protential = []
        self.gradu = []
        self.lz = []
        self.l_z = my_d.l_z
        self.det_model = dev_dic['det_model']
        self.fl_x=my_d.l_x/dev_dic['xyscale']  
        self.fl_y=my_d.l_y/dev_dic['xyscale']
        self.readfile(filepath)
        self.tol_elenumber=dev_dic["tol_elenumber"]

    def readfile(self, filepath):
        i = 0
        with open(filepath, 'r') as f:
            for line in f.readlines():
                try:
                    fargs = list(map(float, 
                                     line.strip('\n').strip().split(',')))
                    self.lz.append(fargs[0]*1e4) #cm->um
                    self.elefield.append(fargs[1]/1e4) #V/cm -> V/um         
                except Exception as e:
                    pass
        self.gradu.append(0)
        grad = 0
        for i in range(len(self.elefield)-1):
            grad = grad + (self.elefield[i]+self.elefield[i+1]) * \
                            (self.lz[i+1]-self.lz[i]) / 2
            self.gradu.append(grad)

    def get_e_field(self, x, y, depth):
        f_ef = interp1d(self.lz, self.elefield, 
                        kind='linear', fill_value="extrapolate")
        #print(depth)        
        #print(f_ef(depth))
        return 0, 0, f_ef(depth) #x, y方向为0
    
    def get_w_p(self, x, y, depth, i):
        f_p = 1 - (1/self.l_z) * depth
        return f_p
    
    def get_potential(self, x, y, depth):
        f_u = interp1d(self.lz, self.gradu, 
                       kind = 'linear', fill_value="extrapolate")
        return f_u(depth)
