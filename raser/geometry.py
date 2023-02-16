# -*- encoding: utf-8 -*-
'''
@Description: Detector structure definition      
@Date       : 2021/08/31 11:09:40
@Author     : tanyuhang
@version    : 1.0
''' 

import ROOT
import math
import sys

#Detector structure
class R3dDetector:
    def __init__(self,dset):
        """
        Description:
            Different types detectors parameters assignment.
        Parameters:
        ---------
        det_dic : dictionary
            Contain all detector parameters 
        material : string
            name of the material
        Modify:
        ---------
            2021/09/02
        """ 
        det_dic = dset.detector
        self.l_x = det_dic['lx'] 
        self.l_y = det_dic['ly']  
        self.l_z = det_dic['lz'] 
        
        self.voltage = det_dic['voltage'] 
        self.temperature = det_dic['temp']
        self.steplength = det_dic['steplength']
        self.material = det_dic['material']
        self.det_model = det_dic['det_model']

        if self.det_model == "lgad3D":
            self.avalanche_model = det_dic['avalanche_model']

            self.part = det_dic['part']
            if self.part == 2:
                self.avalanche_bond = det_dic['avalanche_bond']
                self.doping1 = det_dic['doping1']
                self.doping2 = det_dic['doping2']
            elif self.part == 3:
                self.control_bond = det_dic['control_bond']
                self.avalanche_bond = det_dic['avalanche_bond']
                self.doping1 = det_dic['doping1']
                self.doping2 = det_dic['doping2']
                self.doping3 = det_dic['doping3']
            else:
                raise ValueError
        else:
            self.d_neff = det_dic['doping'] 
            
        if 'plugin3D' in self.det_model: 
            self.e_r = det_dic['e_r']
            self.e_gap = det_dic['e_gap']
            if det_dic['custom_electrode'] == "False":
                self.set_3D_electrode(det_dic['e_r'],det_dic['e_gap'])
            elif det_dic['custom_electrode'] == "True":
                self.e_tr = dset.electron_customs

    def set_3D_electrode(self,e_r,e_gap=0):
        """
        @description: 
            3D plug-in detector electrodes setting     
        @param:
            e_r -- The radius of electrode
            e_gap -- The spacing between the electrodes  
        @Returns:
            None
        @Modify:
            2021/08/31
        """
        self.e_gap = e_gap
        e_int = e_gap 
        e_t_y = self.infor_ele(e_r,e_int)
        self.e_tr=[]
        self.e_t_1 = [self.l_x*0.5          ,self.l_y*0.5      ,e_r,0,self.l_z,"p"]
        self.e_t_2 = [self.l_x*0.5-e_int    ,self.l_y*0.5      ,e_r,0,self.l_z,"n"]
        self.e_t_3 = [self.l_x*0.5+e_int    ,self.l_y*0.5      ,e_r,0,self.l_z,"n"]
        self.e_t_4 = [self.l_x*0.5-e_int*0.5,self.l_y*0.5+e_t_y,e_r,0,self.l_z,"n"]
        self.e_t_5 = [self.l_x*0.5+e_int*0.5,self.l_y*0.5+e_t_y,e_r,0,self.l_z,"n"]
        self.e_t_6 = [self.l_x*0.5-e_int*0.5,self.l_y*0.5-e_t_y,e_r,0,self.l_z,"n"]
        self.e_t_7 = [self.l_x*0.5+e_int*0.5,self.l_y*0.5-e_t_y,e_r,0,self.l_z,"n"]
        for i in range(7):
           n_e = eval('self.e_t_' + str(i+1))
           self.e_tr.append(n_e)

    def infor_ele(self,e_r,e_int):
        """
        @description: 
            3D plug-in detector electrodes spacing    
        @param:
            e_x_gap -- Judge whether the electrode is outer the detector
            e_t_y -- Distance between electrodes at y bottom or to and center
        @Returns:
            None
        @Modify:
            2021/08/31
        """
        e_x_gap = self.l_x - 2*e_r - 2*e_int
        if e_x_gap < 0:
            print("the electrode at x position is larger than sensor length")
            sys.exit(0)
        e_t_y = math.sqrt(e_int*e_int*0.75)
        if 2*e_t_y > self.l_y:
            print("the electrode at y position is larger than sensor length")
            sys.exit(0)            
        return e_t_y

    def Neff(self,z):
        if self.det_model == "lgad3D":
            if self.part == 2:
                if (z < self.avalanche_bond):
                    Neff = self.doping1
                else:
                    Neff = self.doping2
            elif self.part == 3:
                if (z < self.control_bond):
                    Neff = self.doping1
                elif (z > self.avalanche_bond):
                    Neff = self.doping3
                else:
                    Neff = self.doping2
        else:
            Neff = self.d_neff
        return Neff