# -*- encoding: utf-8 -*-

'''
Description:  
    Simulate e-h pairs drifting and calculate induced current
@Date       : 2021/09/02 14:01:46
@Author     : Yuhang Tan, Chenxi Fu
@version    : 2.0
'''

import random
import math
import os
from array import array

import numpy as np
import ROOT
ROOT.gROOT.SetBatch(True)

from .model import Material
from interaction.carrier_list import CarrierListFromG4P
from util.math import Vector, signal_convolution
from util.output import output
import csv

t_bin = 10e-12
# resolution of oscilloscope
t_end = 10e-9
t_start = 0
delta_t = 1e-12
min_intensity = 1 # V/cm

class Carrier:
    """
    Description:
        Definition of carriers and the record of their movement
    Parameters:
        x_init, y_init, z_init, t_init : float
            initial space and time coordinates in um and s
        charge : float
            a set of drifting carriers, absolute value for number, sign for charge
    Attributes:
        x, y, z, t : float
            space and time coordinates in um and s
        path : float[]
            recording the carrier path in [x, y, z, t]
        charge : float
            a set of drifting carriers, absolute value for number, sign for charge
        signal : float[]
            the generated signal current on the reading electrode
        end_condition : 0/string
            tag of how the carrier ended drifting
    Modify:
        2022/10/28
    """
    def __init__(self, x_init, y_init, z_init, t_init, charge, material, read_ele_num):
        self.x = x_init
        self.y = y_init
        self.z = z_init
        self.t = t_init
        self.t_end = t_end
        self.path = [[x_init, y_init, z_init, t_init]]
        self.signal = [[] for j in range(int(read_ele_num))]
        self.end_condition = 0

        self.cal_mobility = Material(material).cal_mobility
        self.charge = charge
        if self.charge == 0:
            self.end_condition = "zero charge"

    def not_in_sensor(self,my_d):
        if (self.x<=0) or (self.x>=my_d.l_x)\
            or (self.y<=0) or (self.y>=my_d.l_y)\
            or (self.z<=0) or (self.z>=my_d.l_z):
            self.end_condition = "out of bound"
        return self.end_condition

    def drift_single_step(self, my_d, my_f, delta_t=delta_t):
        e_field = my_f.get_e_field(self.x,self.y,self.z)
        intensity = Vector(e_field[0],e_field[1],e_field[2]).get_length()
        mobility = Material(my_d.material)
        mu = mobility.cal_mobility(my_d.temperature, my_f.get_doping(self.x, self.y, self.z), self.charge, intensity)
        velocity_vector = [e_field[0]*mu, e_field[1]*mu, e_field[2]*mu] # cm/s

        if(intensity > min_intensity):
            #project steplength on the direction of electric field
            if(self.charge>0):
                delta_x = velocity_vector[0]*delta_t*1e4 # um
                delta_y = velocity_vector[1]*delta_t*1e4
                delta_z = velocity_vector[2]*delta_t*1e4
            else:
                delta_x = -velocity_vector[0]*delta_t*1e4
                delta_y = -velocity_vector[1]*delta_t*1e4
                delta_z = -velocity_vector[2]*delta_t*1e4
        else:
            self.end_condition = "zero velocity"
            return

        # get diffution from mobility and temperature
        kboltz=8.617385e-5 #eV/K
        diffusion = (2.0*kboltz*mu*my_d.temperature*delta_t)**0.5
        #diffusion = 0.0
        dif_x=random.gauss(0.0,diffusion)*1e4
        dif_y=random.gauss(0.0,diffusion)*1e4
        dif_z=random.gauss(0.0,diffusion)*1e4

        # sum up
        # x axis   
        if((self.x+delta_x+dif_x)>=my_d.l_x): 
            self.x = my_d.l_x
        elif((self.x+delta_x+dif_x)<0):
            self.x = 0
        else:
            self.x = self.x+delta_x+dif_x
        # y axis
        if((self.y+delta_y+dif_y)>=my_d.l_y): 
            self.y = my_d.l_y
        elif((self.y+delta_y+dif_y)<0):
            self.y = 0
        else:
            self.y = self.y+delta_y+dif_y
        # z axis
        if((self.z+delta_z+dif_z)>=my_d.l_z): 
            self.z = my_d.l_z
        elif((self.z+delta_z+dif_z)<0):
            self.z = 0
        else:
            self.z = self.z+delta_z+dif_z
        #time
        self.t = self.t+delta_t
        #record
        self.path.append([self.x,self.y,self.z,self.t]) 

    def get_signal(self,my_f,my_d):
        """Calculate signal from carrier path"""
        # i = -q*v*nabla(U_w) = -q*dx*nabla(U_w)/dt = -q*dU_w(x)/dt
        # signal = i*dt = -q*dU_w(x)
        for j in range(my_f.read_ele_num):
            charge=self.charge
            for i in range(len(self.path)-1): # differentiate of weighting potential
                U_w_1 = my_f.get_w_p(self.path[i][0],self.path[i][1],self.path[i][2],j) # x,y,z
                U_w_2 = my_f.get_w_p(self.path[i+1][0],self.path[i+1][1],self.path[i+1][2],j)
                e0 = 1.60217733e-19
                if i>0 and my_d.irradiation_model != None:
                    d_t=self.path[i][3]-self.path[i-1][3]
                    if self.charge>=0:
                        self.trapping_rate=my_f.get_trap_h(self.path[i][0],self.path[i][1],self.path[i][2])
                    else:
                        self.trapping_rate=my_f.get_trap_e(self.path[i][0],self.path[i][1],self.path[i][2])
                    charge=charge*np.exp(-d_t*self.trapping_rate)
                q = charge * e0
                dU_w = U_w_2 - U_w_1
                self.signal[j].append(q*dU_w)
        

    def drift_end(self,my_f):
        e_field = my_f.get_e_field(self.x,self.y,self.z)
        if (e_field[0] == 0 and e_field[1] == 0 and e_field[2] == 0):
            self.end_condition = "out of bound"
        elif (self.t > t_end):
            self.end_condition = "time out"
        return self.end_condition
        

class CalCurrent:
    """
    Description:
        Calculate sum of the generated current by carriers drifting
    Parameters:
        my_d : R3dDetector
        my_f : FenicsCal 
        ionized_pairs : float[]
            the generated carrier amount from MIP or laser
        track_position : float[]
            position of the generated carriers
    Attributes:
        electrons, holes : Carrier[]
            the generated carriers, able to calculate their movement
    Modify:
        2022/10/28
    """
    def __init__(self, my_d, my_f, ionized_pairs, track_position):

        self.read_ele_num = my_f.read_ele_num
        self.electrons = []
        self.holes = []

        for i in range(len(track_position)):
            electron = Carrier(track_position[i][0],\
                               track_position[i][1],\
                               track_position[i][2],\
                               track_position[i][3],\
                               -1*ionized_pairs[i],\
                               my_d.material,\
                               self.read_ele_num)
            hole = Carrier(track_position[i][0],\
                           track_position[i][1],\
                           track_position[i][2],
                           track_position[i][3],\
                           ionized_pairs[i],\
                           my_d.material,\
                           self.read_ele_num)
            if not electron.not_in_sensor(my_d):
                self.electrons.append(electron)
                self.holes.append(hole)
        
        self.drifting_loop(my_d, my_f)

        self.t_bin = t_bin
        self.t_end = t_end
        self.t_start = t_start
        self.n_bin = int((self.t_end-self.t_start)/self.t_bin)

        self.current_define(self.read_ele_num)
        for i in range(self.read_ele_num):
            self.sum_cu[i].Reset()
            self.positive_cu[i].Reset()
            self.negative_cu[i].Reset()
        self.get_current(self.read_ele_num)
        for i in range(self.read_ele_num):
            self.sum_cu[i].Add(self.positive_cu[i])
            self.sum_cu[i].Add(self.negative_cu[i])

        if "lgad" in my_d.det_model:
            self.gain_current = CalCurrentGain(my_d, my_f, self)
            for i in range(self.read_ele_num):
                self.gain_positive_cu[i].Reset()
                self.gain_negative_cu[i].Reset()
                self.gain_negative_cu[i] = self.gain_current.negative_cu[i]
                self.gain_positive_cu[i] = self.gain_current.positive_cu[i]
                self.sum_cu[i].Add(self.gain_negative_cu[i])
                self.sum_cu[i].Add(self.gain_positive_cu[i])

    def drifting_loop(self, my_d, my_f):
        for electron in self.electrons:
            while not electron.not_in_sensor(my_d) and not electron.drift_end(my_f):
                electron.drift_single_step(my_d, my_f)
            electron.get_signal(my_f,my_d)
        for hole in self.holes:
            while not hole.not_in_sensor(my_d) and not hole.drift_end(my_f):
                hole.drift_single_step(my_d, my_f)
            hole.get_signal(my_f,my_d)

    def current_define(self, read_ele_num):
        """
        @description: 
            Parameter current setting     
        @param:
            positive_cu -- Current from holes move
            negative_cu -- Current from electrons move
            sum_cu -- Current from e-h move
        @Returns:
            None
        @Modify:
            2021/08/31
        """
        self.positive_cu=[]
        self.negative_cu=[]
        self.gain_positive_cu=[]
        self.gain_negative_cu=[]
        self.sum_cu=[]

        for i in range(read_ele_num):
            self.positive_cu.append(ROOT.TH1F("charge+"+str(i+1), " No."+str(i+1)+"Positive Current",
                                        self.n_bin, self.t_start, self.t_end))
            self.negative_cu.append(ROOT.TH1F("charge-"+str(i+1), " No."+str(i+1)+"Negative Current",
                                        self.n_bin, self.t_start, self.t_end))
            self.gain_positive_cu.append(ROOT.TH1F("gain_charge+"+str(i+1)," No."+str(i+1)+"Gain Positive Current",
                                        self.n_bin, self.t_start, self.t_end))
            self.gain_negative_cu.append(ROOT.TH1F("gain_charge-"+str(i+1)," No."+str(i+1)+"Gain Negative Current",
                                        self.n_bin, self.t_start, self.t_end))
            self.sum_cu.append(ROOT.TH1F("charge"+str(i+1),"Total Current"+" No."+str(i+1)+"electrode",
                                    self.n_bin, self.t_start, self.t_end))
            
        
    def get_current(self, read_ele_num):
        test_p = ROOT.TH1F("test+","test+",self.n_bin,self.t_start,self.t_end)
        test_p.Reset()
        for j in range(read_ele_num):
            for hole in self.holes:
                for i in range(len(hole.path)-1):
                    test_p.Fill(hole.path[i][3],hole.signal[j][i]/self.t_bin)# time,current=int(i*dt)/Δt
                self.positive_cu[j].Add(test_p)
                test_p.Reset()

        test_n = ROOT.TH1F("test-","test-",self.n_bin,self.t_start,self.t_end)
        test_n.Reset()
        for j in range(read_ele_num):
            for electron in self.electrons:             
                for i in range(len(electron.path)-1):
                    test_n.Fill(electron.path[i][3],electron.signal[j][i]/self.t_bin)# time,current=int(i*dt)/Δt
                self.negative_cu[j].Add(test_n)
                test_n.Reset()


    def draw_currents(self, path, tag=""):
        """
        @description:
            Save current in root file
        @param:
            None     
        @Returns:
            None
        @Modify:
            2021/08/31
        """
        for read_ele_num in range(self.read_ele_num):
            c=ROOT.TCanvas("c","canvas1",1600,1300)
            c.cd()
            c.Update()
            c.SetLeftMargin(0.25)
            # c.SetTopMargin(0.12)
            c.SetRightMargin(0.15)
            c.SetBottomMargin(0.17)
            ROOT.gStyle.SetOptStat(ROOT.kFALSE)
            ROOT.gStyle.SetOptStat(0)

            #self.sum_cu.GetXaxis().SetTitleOffset(1.2)
            #self.sum_cu.GetXaxis().SetTitleSize(0.05)
            #self.sum_cu.GetXaxis().SetLabelSize(0.04)
            self.sum_cu[read_ele_num].GetXaxis().SetNdivisions(510)
            #self.sum_cu.GetYaxis().SetTitleOffset(1.1)
            #self.sum_cu.GetYaxis().SetTitleSize(0.05)
            #self.sum_cu.GetYaxis().SetLabelSize(0.04)
            self.sum_cu[read_ele_num].GetYaxis().SetNdivisions(505)
            #self.sum_cu.GetXaxis().CenterTitle()
            #self.sum_cu.GetYaxis().CenterTitle() 
            self.sum_cu[read_ele_num].GetXaxis().SetTitle("Time [s]")
            self.sum_cu[read_ele_num].GetYaxis().SetTitle("Current [A]")
            self.sum_cu[read_ele_num].GetXaxis().SetLabelSize(0.08)
            self.sum_cu[read_ele_num].GetXaxis().SetTitleSize(0.08)
            self.sum_cu[read_ele_num].GetYaxis().SetLabelSize(0.08)
            self.sum_cu[read_ele_num].GetYaxis().SetTitleSize(0.08)
            self.sum_cu[read_ele_num].GetYaxis().SetTitleOffset(1.2)
            self.sum_cu[read_ele_num].SetTitle("")
            self.sum_cu[read_ele_num].SetNdivisions(5)
            self.sum_cu[read_ele_num].Draw("HIST")
            self.positive_cu[read_ele_num].Draw("SAME HIST")
            self.negative_cu[read_ele_num].Draw("SAME HIST")
            self.gain_positive_cu[read_ele_num].Draw("SAME HIST")
            self.gain_negative_cu[read_ele_num].Draw("SAME HIST")
            self.sum_cu[read_ele_num].Draw("SAME HIST")

            self.positive_cu[read_ele_num].SetLineColor(877)#kViolet-3
            self.negative_cu[read_ele_num].SetLineColor(600)#kBlue
            self.gain_positive_cu[read_ele_num].SetLineColor(617)#kMagneta+1
            self.gain_negative_cu[read_ele_num].SetLineColor(867)#kAzure+7
            self.sum_cu[read_ele_num].SetLineColor(418)#kGreen+2

            self.positive_cu[read_ele_num].SetLineWidth(2)
            self.negative_cu[read_ele_num].SetLineWidth(2)
            self.gain_positive_cu[read_ele_num].SetLineWidth(2)
            self.gain_negative_cu[read_ele_num].SetLineWidth(2)
            self.sum_cu[read_ele_num].SetLineWidth(2)
            c.Update()

            legend = ROOT.TLegend(0.5, 0.2, 0.8, 0.5)
            legend.AddEntry(self.negative_cu[read_ele_num], "electron", "l")
            legend.AddEntry(self.positive_cu[read_ele_num], "hole", "l")
            legend.AddEntry(self.gain_negative_cu[read_ele_num], "gain electron", "l")
            legend.AddEntry(self.gain_positive_cu[read_ele_num], "gain hole", "l")
            legend.AddEntry(self.sum_cu[read_ele_num], "e+h", "l")
            legend.SetBorderSize(0)
            #legend.SetTextFont(43)
            legend.SetTextSize(0.08)
            legend.Draw("same")
            c.Update()
            c.SaveAs(path+'/'+tag+"No_"+str(read_ele_num+1)+"electrode"+"_basic_infor.pdf")
            c.SaveAs(path+'/'+tag+"No_"+str(read_ele_num+1)+"electrode"+"_basic_infor.root")
            del c

    
class CalCurrentGain(CalCurrent):
    '''Calculation of gain carriers and gain current, simplified version'''
    def __init__(self, my_d, my_f, my_current):
        self.read_ele_num = my_current.read_ele_num
        self.electrons = [] # gain carriers
        self.holes = []
        cal_coefficient = Material(my_d.material).cal_coefficient
        gain_rate = self.gain_rate(my_d,my_f,cal_coefficient)
        print("gain_rate="+str(gain_rate))
        path = output(__file__, my_d.det_name)
        f_gain_rate = open(path+'/votage-gain_rate.csv', "a")
        writer_gain_rate = csv.writer(f_gain_rate)
        writer_gain_rate.writerow([str(my_f.voltage),str(gain_rate)])
        with open(path+'/Votage-gain_rate.txt', 'a') as file:
            file.write(str(my_f.voltage)+' -- '+str(gain_rate)+ '\n')
        # assuming gain layer at d>0
        if my_d.voltage<0 : # p layer at d=0, holes multiplicated into electrons
            for hole in my_current.holes:
                self.electrons.append(Carrier(hole.path[-1][0],\
                                              hole.path[-1][1],\
                                              my_d.avalanche_bond,\
                                              hole.path[-1][3],\
                                              -1*hole.charge*gain_rate,\
                                              my_d.material,\
                                              self.read_ele_num))
                
                self.holes.append(Carrier(hole.path[-1][0],\
                                          hole.path[-1][1],\
                                          my_d.avalanche_bond,\
                                          hole.path[-1][3],\
                                          hole.charge*gain_rate,\
                                          my_d.material,\
                                          self.read_ele_num))

        else : # n layer at d=0, electrons multiplicated into holes
            for electron in my_current.electrons:
                self.holes.append(Carrier(electron.path[-1][0],\
                                          electron.path[-1][1],\
                                          my_d.avalanche_bond,\
                                          electron.path[-1][3],\
                                          -1*electron.charge*gain_rate,\
                                          my_d.material,\
                                          self.read_ele_num))

                self.electrons.append(Carrier(electron.path[-1][0],\
                                                electron.path[-1][1],\
                                                my_d.avalanche_bond,\
                                                electron.path[-1][3],\
                                                electron.charge*gain_rate,\
                                                my_d.material,\
                                                self.read_ele_num))

        self.drifting_loop(my_d, my_f)

        self.t_bin = t_bin
        self.t_end = t_end
        self.t_start = t_start
        self.n_bin = int((self.t_end-self.t_start)/self.t_bin)

        self.current_define(self.read_ele_num)
        for i in range(self.read_ele_num):
            self.positive_cu[i].Reset()
            self.negative_cu[i].Reset()
        self.get_current(self.read_ele_num)

    def gain_rate(self, my_d, my_f, cal_coefficient):

        # gain = exp[K(d_gain)] / {1-int[alpha_minor * K(x) dx]}
        # K(x) = exp{int[(alpha_major - alpha_minor) dx]}

        n = 1001
        z_list = np.linspace(0, my_d.avalanche_bond * 1e-4, n) # in cm
        alpha_n_list = np.zeros(n)
        alpha_p_list = np.zeros(n)
        for i in range(n):
            Ex,Ey,Ez = my_f.get_e_field(0.5*my_d.l_x,0.5*my_d.l_y,z_list[i] * 1e4) # in V/cm
            E_field = Vector(Ex,Ey,Ez).get_length()
            alpha_n = cal_coefficient(E_field, -1, my_d.temperature)
            alpha_p = cal_coefficient(E_field, +1, my_d.temperature)
            alpha_n_list[i] = alpha_n
            alpha_p_list[i] = alpha_p

        if my_d.voltage>0:
            alpha_major_list = alpha_n_list # multiplication contributed mainly by electrons in Si
            alpha_minor_list = alpha_p_list
        elif my_d.voltage<0:
            alpha_major_list = alpha_p_list # multiplication contributed mainly by holes in SiC
            alpha_minor_list = alpha_n_list
        diff_list = alpha_major_list - alpha_minor_list
        int_alpha_list = np.zeros(n-1)

        for i in range(1,n):
            int_alpha = 0
            for j in range(i):
                int_alpha += (diff_list[j] + diff_list[j+1]) * (z_list[j+1] - z_list[j]) /2
            int_alpha_list[i-1] = int_alpha
        exp_list = np.exp(int_alpha_list)

        det = 0 # determinant of breakdown
        for i in range(0,n-1):
            average_alpha_minor = (alpha_minor_list[i] + alpha_minor_list[i+1])/2
            det_derivative = average_alpha_minor * exp_list[i]
            det += det_derivative*(z_list[i+1]-z_list[i])        
        if det>1:
            print("det="+str(det))
            print("The detector broke down")
            raise(ValueError)
        
        gain_rate = exp_list[n-2]/(1-det) -1
        return gain_rate

    def current_define(self,read_ele_num):
        """
        @description: 
            Parameter current setting     
        @param:
            positive_cu -- Current from holes move
            negative_cu -- Current from electrons move
            sum_cu -- Current from e-h move
        @Returns:
            None
        @Modify:
            2021/08/31
        """
        self.positive_cu=[]
        self.negative_cu=[]

        for i in range(read_ele_num):
            self.positive_cu.append(ROOT.TH1F("gain_charge_tmp+"+str(i+1)," No."+str(i+1)+"Gain Positive Current",
                                        self.n_bin, self.t_start, self.t_end))
            self.negative_cu.append(ROOT.TH1F("gain_charge_tmp-"+str(i+1)," No."+str(i+1)+"Gain Negative Current",
                                        self.n_bin, self.t_start, self.t_end))

class CalCurrentG4P(CalCurrent):
    def __init__(self, my_d, my_f, my_g4p, batch):
        G4P_carrier_list = CarrierListFromG4P(my_d.material, my_g4p, batch)
        super().__init__(my_d, my_f, G4P_carrier_list.ionized_pairs, G4P_carrier_list.track_position)
        if self.read_ele_num > 1:
            #self.cross_talk()
            pass
            
    def cross_talk(self):
        temp_cu = []
        for i in range(self.read_ele_num):
            temp_cu.append(self.sum_cu[i].Clone())
            self.sum_cu[i].Reset()
        for i in range(self.read_ele_num):
            if i == 0:
                pass
            else:
                self.sum_cu[i-1].Add(temp_cu[i], 0.1)
            self.sum_cu[i].Add(temp_cu[i], 0.8)
            if i == self.read_ele_num-1:
                pass
            else:
                self.sum_cu[i+1].Add(temp_cu[i], 0.1)


class CalCurrentLaser(CalCurrent):
    def __init__(self, my_d, my_f, my_l):
        super().__init__(my_d, my_f, my_l.ionized_pairs, my_l.track_position)
        
        for i in range(self.read_ele_num):
            
            # convolute the signal with the laser pulse shape in time
            convolved_positive_cu = ROOT.TH1F("convolved_charge+", "Positive Current",
                                        self.n_bin, self.t_start, self.t_end)
            convolved_negative_cu = ROOT.TH1F("convolved_charge-", "Negative Current",
                                        self.n_bin, self.t_start, self.t_end)
            convolved_gain_positive_cu = ROOT.TH1F("convolved_gain_charge+","Gain Positive Current",
                                        self.n_bin, self.t_start, self.t_end)
            convolved_gain_negative_cu = ROOT.TH1F("convolved_gain_charge-","Gain Negative Current",
                                        self.n_bin, self.t_start, self.t_end)
            convolved_sum_cu = ROOT.TH1F("convolved_charge","Total Current",
                                    self.n_bin, self.t_start, self.t_end)
            
            convolved_positive_cu.Reset()
            convolved_negative_cu.Reset()
            convolved_gain_positive_cu.Reset()
            convolved_gain_negative_cu.Reset()
            convolved_sum_cu.Reset()

            signal_convolution(self.positive_cu[i],convolved_positive_cu,[my_l.timePulse])
            signal_convolution(self.negative_cu[i],convolved_negative_cu,[my_l.timePulse])
            signal_convolution(self.gain_positive_cu[i],convolved_gain_positive_cu,[my_l.timePulse])
            signal_convolution(self.gain_negative_cu[i],convolved_gain_negative_cu,[my_l.timePulse])
            signal_convolution(self.sum_cu[i],convolved_sum_cu,[my_l.timePulse])

            self.positive_cu[i] = convolved_positive_cu
            self.negative_cu[i] = convolved_negative_cu
            self.gain_positive_cu[i] = convolved_gain_positive_cu
            self.gain_negative_cu[i] = convolved_gain_negative_cu
            self.sum_cu[i] = convolved_sum_cu
