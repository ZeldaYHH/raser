# -*- encoding: utf-8 -*-
'''
Description:  Simulate e-h pairs drifting and calculate induced current
@Date       : 2021/09/02 14:01:46
@Author     : Yuhang Tan, Chenxi Fu
@version    : 2.0
'''
import random
import numpy as np
import ROOT
from raser.model import Mobility
from raser.model import Avalanche
from raser.model import Vector

class Carrier:
    """
    Description:
        Definition of carriers and the record of their movement
    Parameters:
        d_x_init, d_y_init, d_z_init, t_init : float
            initial space and time coordinates in um and s
        charge : float
            a set of drifting carriers, absolute value for number, sign for charge
    Attributes:
        d_x, d_y, d_z, t : float
            space and time coordinates in um and s
        path : float[]
            recording the carrier path in [d_x, d_y, d_z, t]
        charge : float
            a set of drifting carriers, absolute value for number, sign for charge
        signal : float[]
            the generated signal current on the reading electrode
        end_condition : 0/string
            tag of how the carrier ended drifting
    Modify:
        2022/10/28
    """
    def __init__(self, d_x_init, d_y_init, d_z_init, t_init, charge,tol_elenumber):
        self.d_x = d_x_init
        self.d_y = d_y_init
        self.d_z = d_z_init
        self.t = t_init
        self.path = [[d_x_init, d_y_init, d_z_init, t_init]]
        self.charge = charge
        self.signal = [[] for j in range(tol_elenumber)]
        
        if self.charge == 0:
            self.end_condition = "zero charge"
        else:
            self.end_condition = 0

    def not_in_sensor(self,my_d):
        if (self.d_x<=0) or (self.d_x>=my_d.l_x)\
            or (self.d_y<=0) or (self.d_y>=my_d.l_y)\
            or (self.d_z<=0) or (self.d_z>=my_d.l_z):
            self.end_condition = "out of bound"
        return self.end_condition

    def drift_single_step(self,step,my_d,my_f):
        e_field = my_f.get_e_field(self.d_x,self.d_y,self.d_z)
        intensity = Vector(e_field[0],e_field[1],e_field[2]).get_length()
        if(intensity!=0):
            #project steplength on the direction of electric field
            if(self.charge>0):
                delta_x=step*e_field[0]/intensity
                delta_y=step*e_field[1]/intensity
                delta_z=step*e_field[2]/intensity
            else:
                delta_x=-step*e_field[0]/intensity
                delta_y=-step*e_field[1]/intensity
                delta_z=-step*e_field[2]/intensity
        else:
            self.end_condition = "zero velocity"
            return

        # get velocity from electric field
        e_field_prime = my_f.get_e_field(self.d_x+delta_x,self.d_y+delta_y,self.d_z+delta_z)
        intensity_prime = Vector(e_field_prime[0],e_field_prime[1],e_field_prime[2]).get_length()
        if(intensity_prime==0):
            self.end_condition = "zero velocity"
            return
        
        average_intensity = (intensity+intensity_prime)/2.0*1e4 # V/cm
        mobility = Mobility(my_d.material)
        mu = mobility.cal_mobility(my_d, my_d.Neff(self.d_z+delta_z), self.charge, average_intensity)
        velocity = mu*average_intensity

        # get diffution from mobility and temperature
        delta_t = step*1e-4/velocity
        kboltz=8.617385e-5 #eV/K
        diffusion = (2.0*kboltz*mu*my_d.temperature*delta_t)**0.5
        #diffusion = 0.0
        dif_x=random.gauss(0.0,diffusion)*1e4
        dif_y=random.gauss(0.0,diffusion)*1e4
        dif_z=random.gauss(0.0,diffusion)*1e4

        # sum up
        # x axis   
        if((self.d_x+delta_x+dif_x)>=my_d.l_x): 
            self.d_x = my_d.l_x
        elif((self.d_x+delta_x+dif_x)<0):
            self.d_x = 0
        else:
            self.d_x = self.d_x+delta_x+dif_x
        # y axis
        if((self.d_y+delta_y+dif_y)>=my_d.l_y): 
            self.d_y = my_d.l_y
        elif((self.d_y+delta_y+dif_y)<0):
            self.d_y = 0
        else:
            self.d_y = self.d_y+delta_y+dif_y
        # z axis
        if((self.d_z+delta_z+dif_z)>=my_d.l_z): 
            self.d_z = my_d.l_z
        elif((self.d_z+delta_z+dif_z)<0):
            self.d_z = 0
        else:
            self.d_z = self.d_z+delta_z+dif_z
        #time
        self.t = self.t+delta_t

        #record
        self.path.append([self.d_x,self.d_y,self.d_z,self.t]) 

    def get_signal(self,my_f,my_d):
        """Calculate signal from carrier path"""
        # i = q*v*nabla(U_w) = q*dx*nabla(U_w)/dt = q*dU_w(x)/dt
        # signal = i*dt = q*dU_w(x)
        for j in range(my_f.tol_elenumber):
            for i in range(len(self.path)-1): # differentiate of weighting potential
                U_w_1 = my_f.get_w_p(self.path[i][0],self.path[i][1],self.path[i][2],j) # x,y,z
                U_w_2 = my_f.get_w_p(self.path[i+1][0],self.path[i+1][1],self.path[i+1][2],j)
                e0 = 1.60217733e-19
                if i>0:
                    d_t=self.path[i][3]-self.path[i-1][3]
                    self.trapping_time=my_d.trapping_time
                    self.charge=self.charge*np.exp(np.true_divide(-d_t,self.trapping_time))
                q = self.charge * e0
                dU_w = U_w_2 - U_w_1
                self.signal[j].append(q*dU_w)
 
        
    def drift_end(self,my_f):
        e_field = my_f.get_e_field(self.d_x,self.d_y,self.d_z)
        '''wpot = my_f.get_w_p(self.d_x,self.d_y,self.d_z) # after position check to avoid illegal input'''
        if (e_field[0]==0 and e_field[1]==0 and e_field[2]==0):
            self.end_condition = "zero velocity"
        '''elif wpot>(1-1e-5):
            self.end_condition = "reached cathode"
        elif wpot<1e-5:
            self.end_condition = "reached anode"
        elif(len(self.path)>10000):
            self.end_condition = "reciprocate"'''
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
        self.electrons = []
        self.holes = []
        for i in range(len(track_position)):
            electron = Carrier(track_position[i][0],\
                               track_position[i][1],\
                               track_position[i][2],\
                               track_position[i][3],\
                               -1*ionized_pairs[i],\
                                my_f.tol_elenumber)
            hole = Carrier(track_position[i][0],\
                           track_position[i][1],\
                           track_position[i][2],
                           track_position[i][3],\
                           ionized_pairs[i],\
                            my_f.tol_elenumber)
            if not electron.not_in_sensor(my_d):
                self.electrons.append(electron)
                self.holes.append(hole)
        
        self.drifting_loop(my_d, my_f)

        self.current_define(my_f.tol_elenumber)
        for i in range(my_f.tol_elenumber):
            self.sum_cu[i].Reset()
            self.positive_cu[i].Reset()
            self.negative_cu[i].Reset()
        self.get_current(my_f.tol_elenumber)
        if my_d.det_model == "lgad3D":
            self.gain_current = CalCurrentGain(my_d, my_f, self)
            self.gain_positive_cu.Reset()
            self.gain_negative_cu.Reset()
            self.get_current_gain()

    def drifting_loop(self, my_d, my_f):
        for electron in self.electrons:
            while not electron.not_in_sensor(my_d):
                electron.drift_single_step(my_d.steplength, my_d, my_f)
                electron.drift_end(my_f)
            electron.get_signal(my_f,my_d)
        for hole in self.holes:
            while not hole.not_in_sensor(my_d):
                hole.drift_single_step(my_d.steplength, my_d, my_f)
                hole.drift_end(my_f)
            hole.get_signal(my_f,my_d)

    def current_define(self,tol_elenumber):
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
        self.t_bin = 50e-12
        self.t_end = 5.0e-9
        self.t_start = 0
        self.n_bin = int((self.t_end-self.t_start)/self.t_bin)

        self.positive_cu=[]
        self.negative_cu=[]
        self.gain_positive_cu=[]
        self.gain_negative_cu=[]
        self.sum_cu=[]

        for i in range(tol_elenumber):
            self.positive_cu.append(ROOT.TH1F("charge+"+str(i), "Positive Current",
                                        self.n_bin, self.t_start, self.t_end))
            self.negative_cu.append(ROOT.TH1F("charge-"+str(i), "Negative Current",
                                        self.n_bin, self.t_start, self.t_end))
            self.gain_positive_cu.append(ROOT.TH1F("gain_charge+"+str(i),"Gain Positive Current",
                                        self.n_bin, self.t_start, self.t_end))
            self.gain_negative_cu.append(ROOT.TH1F("gain_charge-"+str(i),"Gain Negative Current",
                                        self.n_bin, self.t_start, self.t_end))
            self.sum_cu.append(ROOT.TH1F("charge"+str(i),"Total Current"+" No."+str(i+1)+"electron",
                                    self.n_bin, self.t_start, self.t_end))
            
        
    def get_current(self,tol_elenumber):
        test_p = ROOT.TH1F("test+","test+",self.n_bin,self.t_start,self.t_end)
        test_p.Reset()
        for j in range(tol_elenumber):
            sum_max_hole=0
            sum_min_hole=0
            for hole in self.holes:
                if (len(hole.signal[j])!=0):
                    sum_max_hole=sum_max_hole+max(hole.signal[j])/self.t_bin
                    sum_min_hole=sum_min_hole+min(hole.signal[j])/self.t_bin
            if(sum_max_hole>1e-11 or abs(sum_min_hole)>1e-11):
                for hole in self.holes:
                    for i in range(len(hole.path)-1):
                        test_p.Fill(hole.path[i][3],hole.signal[j][i]/self.t_bin)# time,current=int(i*dt)/Δt
                    self.positive_cu[j].Add(test_p)
                    test_p.Reset()


        test_n = ROOT.TH1F("test-","test-",self.n_bin,self.t_start,self.t_end)
        test_n.Reset()
        for j in range(tol_elenumber):
            sum_max_electron=0
            sum_min_electron=0
            for electron in self.electrons:
                if (len(electron.signal[j])!=0):
                    sum_max_electron=sum_max_electron+max(electron.signal[j])/self.t_bin
                    sum_min_electron=sum_min_electron+min(electron.signal[j])/self.t_bin
            if(sum_max_hole>1e-11 or abs(sum_min_hole)>1e-11):
                for electron in self.electrons:             
                    for i in range(len(electron.path)-1):
                        test_n.Fill(electron.path[i][3],electron.signal[j][i]/self.t_bin)# time,current=int(i*dt)/Δt
                    self.negative_cu[j].Add(test_n)
                    test_n.Reset()
    
        for i in range(tol_elenumber):
            self.sum_cu[i].Add(self.positive_cu[i])
            self.sum_cu[i].Add(self.negative_cu[i])

    def get_current_gain(self):
        self.gain_negative_cu = self.gain_current.negative_cu
        self.gain_positive_cu = self.gain_current.positive_cu
        self.sum_cu.Add(self.gain_positive_cu)
        self.sum_cu.Add(self.gain_negative_cu)
    
class CalCurrentGain(CalCurrent):
    '''Calculation of gain carriers and gain current, simplified version'''
    def __init__(self, my_d, my_f, my_current):
        self.electrons = [] # gain carriers
        self.holes = []
        my_ava = Avalanche(my_d.avalanche_model)
        gain_rate = self.gain_rate(my_d,my_f,my_ava)
        print("gain_rate="+str(gain_rate))
        # assuming gain layer at d>0
        if my_d.voltage<0 : # p layer at d=0, holes multiplicated into electrons
            for hole in my_current.holes:
                self.electrons.append(Carrier(hole.path[-1][0],\
                                              hole.path[-1][1],\
                                              my_d.avalanche_bond,\
                                              hole.path[-1][3],\
                                              -1*hole.charge*gain_rate))
                if gain_rate>5:
                    self.holes.append(Carrier(hole.path[-1][0],\
                                              hole.path[-1][1],\
                                              my_d.avalanche_bond,\
                                              hole.path[-1][3],\
                                              hole.charge*gain_rate/np.log(gain_rate)))

        else : # n layer at d=0, electrons multiplicated into holes
            for electron in my_current.electrons:
                self.holes.append(Carrier(electron.path[-1][0],\
                                          electron.path[-1][1],\
                                          my_d.avalanche_bond,\
                                          electron.path[-1][3],\
                                          -1*electron.charge*gain_rate))
                if gain_rate>5:
                    self.electrons.append(Carrier(electron.path[-1][0],\
                                                  electron.path[-1][1],\
                                                  my_d.avalanche_bond,\
                                                  electron.path[-1][3],\
                                                  electron.charge*gain_rate/np.log(gain_rate)))

        self.drifting_loop(my_d, my_f)

        self.current_define()
        self.positive_cu.Reset()
        self.negative_cu.Reset()
        self.get_current()

    def gain_rate(self, my_d, my_f, my_ava):

        # gain = exp[K(d_gain)] / {1-int[alpha_minor * K(x) dx]}
        # K(x) = exp{int[(alpha_major - alpha_minor) dx]}

        n = 1001
        z_list = np.linspace(0, my_d.avalanche_bond * 1e-4, n) # in cm
        alpha_n_list = np.zeros(n)
        alpha_p_list = np.zeros(n)
        for i in range(n):
            Ex,Ey,Ez = my_f.get_e_field(0.5*my_d.l_x,0.5*my_d.l_y,z_list[i] * 1e4) # in um
            E_field = Vector(Ex,Ey,Ez).get_length() * 1e4 # in V/cm
            alpha_n = my_ava.cal_coefficient(E_field, -1, my_d.temperature)
            alpha_p = my_ava.cal_coefficient(E_field, +1, my_d.temperature)
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

    def current_define(self):
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
        self.t_bin = 50e-12
        self.t_end = 5.0e-9
        self.t_start = 0
        self.n_bin = int((self.t_end-self.t_start)/self.t_bin)

        self.positive_cu = ROOT.TH1F("gain_charge+","Gain Positive Current",
                                     self.n_bin, self.t_start, self.t_end)
        self.negative_cu = ROOT.TH1F("gain_charge-","Gain Negative Current",
                                     self.n_bin, self.t_start, self.t_end)
        
    def get_current(self):
        test_p = ROOT.TH1F("test+","test+",self.n_bin,self.t_start,self.t_end)
        test_p.Reset()
        for hole in self.holes:
            for i in range(len(hole.path)-1):
                test_p.Fill(hole.path[i][3],hole.signal[i]/self.t_bin)# time,current=int(i*dt)/Δt
            self.positive_cu.Add(test_p)
            test_p.Reset()

        test_n = ROOT.TH1F("test-","test-",self.n_bin,self.t_start,self.t_end)
        test_n.Reset()
        for electron in self.electrons:             
            for i in range(len(electron.path)-1):
                test_n.Fill(electron.path[i][3],electron.signal[i]/self.t_bin)# time,current=int(i*dt)/Δt
            self.negative_cu.Add(test_n)
            test_n.Reset()

class CalCurrentG4P(CalCurrent):
    def __init__(self, my_d, my_f, my_g4p, batch):
        G4P_carrier_list = CarrierListFromG4P(my_d.material, my_g4p, batch)
        self.tol_elenumber = my_f.tol_elenumber
        super().__init__(my_d, my_f, G4P_carrier_list.ionized_pairs, G4P_carrier_list.track_position)

class CalCurrentLaser(CalCurrent):
    def __init__(self, my_d, my_f, my_l):
        super().__init__(my_d, my_f, my_l.ionized_pairs, my_l.track_position)
        self.tol_elenumber = my_f.tol_elenumber
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

        self.signalConvolution(self.positive_cu,my_l.timePulse,convolved_positive_cu)
        self.signalConvolution(self.negative_cu,my_l.timePulse,convolved_negative_cu)
        self.signalConvolution(self.gain_positive_cu,my_l.timePulse,convolved_gain_positive_cu)
        self.signalConvolution(self.gain_negative_cu,my_l.timePulse,convolved_gain_negative_cu)
        self.signalConvolution(self.sum_cu,my_l.timePulse,convolved_sum_cu)

        self.positive_cu = []
        self.negative_cu = []
        self.gain_positive_cu = []
        self.gain_negative_cu = []
        self.sum_cu = []
        for i in range(self.tol_elenumber):
            self.positive_cu[i] = convolved_positive_cu
            self.negative_cu[i] = convolved_negative_cu
            self.gain_positive_cu[i] = convolved_gain_positive_cu
            self.gain_negative_cu[i] = convolved_gain_negative_cu
            self.sum_cu[i] = convolved_sum_cu

    def signalConvolution(self,cu,timePulse,convolved_cu):
        for i in range(self.n_bin):
            pulse_responce = cu.GetBinContent(i)
            for j in range(-i,self.n_bin-i): 
                time_pulse = timePulse(j*self.t_bin)
                convolved_cu.Fill((i+j)*self.t_bin - 1e-14, pulse_responce*time_pulse)
                #resolve float error

class CarrierListFromG4P:
    def __init__(self, material, my_g4p, batch):
        """
        Description:
            Events position and energy depositon
        Parameters:
            material : string
                deciding the energy loss of MIP
            my_g4p : Particles
            batch : int
                batch = 0: Single event, select particle with long enough track
                batch != 0: Multi event, assign particle with batch number
        Modify:
            2022/10/25
        """
        if (material == "SiC"):
            self.energy_loss = 8.4 #ev
        elif (material == "Si"):
            self.energy_loss = 3.6 #ev

        if batch == 0:
            total_step=0
            particle_number=0
            for p_step in my_g4p.p_steps_current:   # selecting particle with long enough track
                if len(p_step)>1:
                    particle_number=1+particle_number
                    total_step=len(p_step)+total_step
            
            for j in range(len(my_g4p.p_steps_current)):
                if(len(my_g4p.p_steps_current[j])>((total_step/particle_number)*0.5)):
                    self.batch_def(my_g4p,j)
                    break

            if particle_number > 0:
                batch=1
                         
            if batch == 0:
                print("the sensor didn't have particles hitted")
                raise ValueError
        else:
            self.batch_def(my_g4p,batch)

    def batch_def(self,my_g4p,j):
        self.beam_number = j
        self.track_position = [[single_step[0],single_step[1],single_step[2],1e-9] for single_step in my_g4p.p_steps_current[j]]
        self.tracks_step = my_g4p.energy_steps[j]
        self.tracks_t_energy_deposition = my_g4p.edep_devices[j] #为什么不使用？
        self.ionized_pairs = [step*1e6/self.energy_loss for step in self.tracks_step]
