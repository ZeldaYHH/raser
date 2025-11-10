#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

'''
Description: 
    Math Objects
@Date       : 2024/09/19 20:57:33
@Author     : Chenxi Fu
@version    : 1.0
'''

import math
from typing import Callable

import numpy as np
from scipy.interpolate import interp1d as p1d
from scipy.interpolate import interp2d as p2d
from scipy.interpolate import interpn as pn
from scipy.interpolate import griddata
import ROOT
ROOT.gROOT.SetBatch(True)

x_bin_2d = 200
y_bin_2d = 200

x_bin_3d = 50
y_bin_3d = 50
z_bin_3d = 50

class Vector:
    def __init__(self,a1,a2,a3):
        self.components = [a1,a2,a3]
        
    def cross(self,Vector_b):
        """ Get vector cross product of self and another Vector"""
        o1 = self.components[1]*Vector_b.components[2]-self.components[2]*Vector_b.components[1]
        o2 = self.components[2]*Vector_b.components[0]-self.components[0]*Vector_b.components[2]
        o3 = self.components[0]*Vector_b.components[1]-self.components[1]*Vector_b.components[0]
        return Vector(o1,o2,o3)

    def get_length(self):
        " Return length of self"
        return math.sqrt(self.components[0]*self.components[0]+self.components[1]*self.components[1]+self.components[2]*self.components[2])

    def add(self,Vector_b):
        " Return the sum of two Vectors. eg: [1,2,3]+[1,2,3] = [2,4,6]"
        o1 = self.components[0]+Vector_b.components[0]
        o2 = self.components[1]+Vector_b.components[1]
        o3 = self.components[2]+Vector_b.components[2]
        return Vector(o1,o2,o3)

    def sub(self,Vector_b):
        " Return the subtraction of two Vectors. eg: [1,2,3]-[1,2,3] = [0,0,0]"
        o1 = self.components[0]-Vector_b.components[0]
        o2 = self.components[1]-Vector_b.components[1]
        o3 = self.components[2]-Vector_b.components[2]
        return Vector(o1,o2,o3)
    
    def mul(self,k):
        " Return Vector multiplied by number. eg: 2 * [1,2,3] = [2,4,6]"
        return Vector(self.components[0]*k,self.components[1]*k,self.components[2]*k)


def get_common_interpolate_1d(data):
    values = data['values']
    points = data['points']

    def f(x):
        return p1d(points, values)(x)
    return f

def get_common_interpolate_2d(data):
    values = data['values']
    points_x = []
    points_y = []
    for point in data['points']:
        points_x.append(point[0])
        points_y.append(point[1])
    new_x = np.linspace(min(points_x), max(points_x), x_bin_2d)
    new_y = np.linspace(min(points_y), max(points_y), y_bin_2d)
    new_points = np.array(np.meshgrid(new_x, new_y)).T.reshape(-1, 2)
    new_values = griddata((points_x, points_y), values, new_points, method='linear')

    def f(x, y):
        return p2d(new_x, new_y, new_values)(x,y)[0]
    return f


def get_common_interpolate_3d(data):
    values = data['values']
    points_x = []
    points_y = []
    points_z = []
    for point in data['points']:
        points_x.append(point[0])
        points_y.append(point[1])
        points_z.append(point[2])

    new_x = np.linspace(min(points_x), max(points_x), x_bin_3d)
    new_y = np.linspace(min(points_y), max(points_y), y_bin_3d)
    new_z = np.linspace(min(points_z), max(points_z), z_bin_3d)
    new_points = np.array(np.meshgrid(new_x, new_y, new_z)).T.reshape(-1, 3)
    new_points_pn = (new_x, new_y, new_z)
    new_values = griddata((points_x, points_y, points_z), values, new_points, method='linear')
    new_values_pn = new_values.reshape(x_bin_3d, y_bin_3d, z_bin_3d)

    def f(x, y, z):
        point = np.array([x, y, z]).reshape(1, -1)
        return pn(new_points_pn, new_values_pn, point)[0]
    return f

def signal_convolution(signal_original: ROOT.TH1F, signal_convolved: ROOT.TH1F, pulse_responce_function_list: list[Callable[[float],float]]):
    # assume so and sc share same bin width
    so = signal_original
    sc = signal_convolved
    st = ROOT.TH1F("signal_temp","signal_temp",so.GetNbinsX(),so.GetXaxis().GetXmin(),so.GetXaxis().GetXmax())
    st.Reset()
    st.Add(so)

    t_bin = so.GetBinWidth(0) # for uniform bin
    n_bin = so.GetNbinsX()
    for pr in pulse_responce_function_list:
        for i in range(n_bin):
            st_i = st.GetBinContent(i)
            for j in range(-i,n_bin-i): 
                pr_j = pr(j*t_bin)
                sc.Fill((i+j)*t_bin + 1e-14, st_i*pr_j*t_bin) # 1e-14 resolves float error
        st.Reset()
        st.Add(sc)
        sc.Reset()

    sc.Add(st)


def calculate_gradient(function: Callable, component: list, coordinate: list):
    diff_res = 1e-5 # difference resolution in cm
    diff_steps = [(diff_res / 2, diff_res / 2), (diff_res, 0), (0, diff_res)]

    gradient = []
    for i in range(len(coordinate)):
        for diff1, diff2 in diff_steps:
            try:
                args_plus = [c + diff1 if i == j else c for j, c in enumerate(coordinate)]
                args_minus = [c - diff2 if i == j else c for j, c in enumerate(coordinate)] 
                gradient_trial = (function(*args_plus) - function(*args_minus)) / diff_res
                gradient.append(gradient_trial)
                break
            except ValueError as e:
                if "out of bound" in str(e) or "interpolation range" in str(e):
                    continue
                else:
                    raise e
        else:
            raise ValueError(f"Point {coordinate} might be out of bound")
    
    return gradient

def inversed_fast_fourier_transform():
    pass

def is_number(s):
    """ 
    Define the input s is number or not.
    if Yes, return True, else return False.
    """ 
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False

def fit_data_normal(histo,x_min,x_max):
    """ Fit data distribution """
    fit_func_1 = ROOT.TF1('fit_func_1','gaus',x_min,x_max)
    histo.Fit("fit_func_1","ROQ+","",x_min,x_max)

    print("constant:%s"%fit_func_1.GetParameter(0))
    print("constant_error:%s"%fit_func_1.GetParError(0))
    print("mean:%s"%fit_func_1.GetParameter(1))
    print("mean_error:%s"%fit_func_1.GetParError(1))
    print("sigma:%s"%fit_func_1.GetParameter(2))
    print("sigma_error:%s"%fit_func_1.GetParError(2))
    mean=fit_func_1.GetParameter(1)
    mean_error=fit_func_1.GetParError(1)
    sigma=fit_func_1.GetParameter(2)
    sigma_error=fit_func_1.GetParError(2)
    fit_func_1.SetLineWidth(2)
    return fit_func_1,mean,mean_error,sigma,sigma_error

def fit_data_landau(histo,x_min,x_max):
    """ Fit data distribution """
    fit_func_1 = ROOT.TF1('fit_func_1','landau',x_min,x_max)
    histo.Fit("fit_func_1","ROQ+","",x_min,x_max)

    print("constant:%s"%fit_func_1.GetParameter(0))
    print("constant_error:%s"%fit_func_1.GetParError(0))
    print("mpv:%s"%fit_func_1.GetParameter(1))
    print("mpv_error:%s"%fit_func_1.GetParError(1))
    print("sigma:%s"%fit_func_1.GetParameter(2))
    print("sigma_error:%s"%fit_func_1.GetParError(2))
    mean=fit_func_1.GetParameter(1)
    mean_error=fit_func_1.GetParError(1)
    sigma=fit_func_1.GetParameter(2)
    sigma_error=fit_func_1.GetParError(2)
    fit_func_1.SetLineWidth(2)
    return fit_func_1,mean,mean_error,sigma,sigma_error