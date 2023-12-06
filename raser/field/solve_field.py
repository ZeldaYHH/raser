#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pickle
import numpy as np
import ROOT
import os

class FieldCal:
    def __init__(self, my_d,det_name,det_dic,dev_dic):
        self.voltage = my_d.voltage
        self.l_z = my_d.l_z
        self.read_ele_num = int(dev_dic['read_ele_num'])     
        if not os.access("./output/strip", os.F_OK):  
            print("please run field first")
            return
        with open("./output/strip/x.pkl",'rb') as file:
            x=pickle.load(file)
        with open("./output/strip/y.pkl",'rb') as file:
            y=pickle.load(file)
        with open("./output/strip/potential_{}_1.6e15_.pkl".format(self.voltage),'rb') as file:
            potential=pickle.load(file)
        self.x_efield,self.y_efield,self.potential=get_field(x,y,potential)

        with open("./output/strip/TrappingRate_p_1.6e15_{}.pkl".format(self.voltage),'rb') as file:
            TrappingRate_p=pickle.load(file)
        with open("./output/strip/TrappingRate_n_1.6e15_{}.pkl".format(self.voltage),'rb') as file:
            TrappingRate_n=pickle.load(file)
        self.TrappingRate_p=get_trapping_rate(x,y,TrappingRate_p)
        self.TrappingRate_n=get_trapping_rate(x,y,TrappingRate_n)
        if not os.access("./output/strip/weighting_field/", os.F_OK):
            os.makedirs("./output/strip/weighting_field/", exist_ok=True) 
            total_w_p=[]
            for i in range(self.read_ele_num):
                total_x,total_z,t_w_p=new_w_p(i)
                total_w_p.append(t_w_p)
            with open("./output/strip/weighting_field/weighting_potential.pkl",'wb') as file:
                pickle.dump(total_w_p, file)
            with open("./output/strip/weighting_field/weighting_potential_x.pkl",'wb') as file:
                pickle.dump(total_x, file)
            with open("./output/strip/weighting_field/weighting_potential_z.pkl",'wb') as file:
                pickle.dump(total_z, file)

        with open("./output/strip/weighting_field/weighting_potential.pkl",'rb') as file:
            weighting_potential=pickle.load(file)
        with open("./output/strip/weighting_field/weighting_potential_x.pkl",'rb') as file:
            weighting_potential_x=pickle.load(file)
        with open("./output/strip/weighting_field/weighting_potential_z.pkl",'rb') as file:
            weighting_potential_z=pickle.load(file)
        self.w_p=[]  
        for i in range(self.read_ele_num):
            self.w_p.append(w_p(weighting_potential_x,weighting_potential_z,weighting_potential[i]))
        

    def get_trap_e(self,x,y,depth):
        t_e=self.TrappingRate_n.Interpolate(depth,x)
        return t_e
    
    def get_trap_h(self,x,y,depth):
        t_h=self.TrappingRate_p.Interpolate(depth,x)
        return t_h
    
    def get_e_field(self, x, y, depth):    
        f_efx = self.x_efield.Interpolate(depth,x)
        f_efz = self.y_efield.Interpolate(depth,x)
        return f_efz, 0, f_efx
    
    def get_w_p(self, x, y, depth, i):
        f_p = self.w_p[i].Interpolate(x,depth)
        if(f_p<1e-2):
            f_p=1e-2
        return f_p
    
    def get_potential(self, x, y, depth):
        f_u = self.potential.Interpolate(depth,x)
        return f_u
    
def get_field(x,y,potential):
    x_efield=[]
    y_efield=[]
    x_u=np.unique(x)
    y_u=np.unique(y)
    reorganization_potential=[]
    for i in range(len(x_u)):
        temporary_potential=[]
        for j in range(len(x)):
            if x_u[i]==x[j]:
                temporary_potential.append(potential[j])
        reorganization_potential.append(temporary_potential)
    for i in range(len(reorganization_potential)-1):
        grad=np.gradient(np.array([reorganization_potential[i], reorganization_potential[i+1]], dtype=np.float))
        x_efield.append(grad[0][1])
        y_efield.append(grad[1][0])
        if i == (len(reorganization_potential)-2):
            y_efield.append(grad[1][1])
            x_efield.append(np.gradient(reorganization_potential[i+1]))
    re_potential=ROOT.TGraph2D()
    x_field=ROOT.TGraph2D()
    y_field=ROOT.TGraph2D()
    for i in range(len(x_u)):
        for j in range(len(y_u)):
            x_field.SetPoint(int(i*len(y_u)+j), x_u[i]*1e4, y_u[j]*1e4, x_efield[i][j]/3)
            y_field.SetPoint(int(i*len(y_u)+j), x_u[i]*1e4, y_u[j]*1e4, y_efield[i][j]/3)
            re_potential.SetPoint(int(i*len(y_u)+j), x_u[i]*1e4, y_u[j]*1e4, reorganization_potential[i][j])
    return x_field,y_field,re_potential


def w_p(x,z,w_p):
    weighting_potential=ROOT.TGraph2D()
    for i in range(len(z)):
        for j in range(len(x)):
            weighting_potential.SetPoint(int(i*len(x)+j),z[i],x[j]*6,w_p[i][j])
    return weighting_potential
    

def get_trapping_rate(x,y,trapping_rate):
    trap_time=ROOT.TGraph2D()
    for i in range(len(y)):
        trap_time.SetPoint(i,x[i]*1e4,y[i]*1e4,trapping_rate[i])
    return trap_time


def new_w_p(ele_number):
    nx = 51  
    ny = 301  
    xmin, xmax = 0.0, 50.0  
    ymin, ymax = 0.0, 300.0 
    dx = (xmax - xmin) / (nx - 1)  
    dy = (ymax - ymin) / (ny - 1) 


    u = np.zeros((ny, nx))
    u[ele_number*75:(ele_number*75+20), 0] = 1.0  
    u[:, -1] = 0.0  

    max_iter = 100000  
    tolerance = 1e-6  
    for iteration in range(max_iter):
        u_old = u.copy()
        for i in range(1, ny - 1):
            for j in range(1, nx - 1):
                u[i, j] = (u[i+1, j] + u[i-1, j] + u[i, j+1] + u[i, j-1]) / 4
        diff = np.abs(u - u_old).max()
        if diff < tolerance:
            break
    
    x = np.linspace(xmin, xmax, nx)
    y = np.linspace(ymin, ymax, ny)
    
    w_potential=ROOT.TGraph2D()
    for i in range(len(y)):
        for j in range(len(x)):
            w_potential.SetPoint(int(i*len(x)+j),x[j]*6,y[i],u[i][j])
    return x ,y ,u