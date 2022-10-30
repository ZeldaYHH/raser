# -*- encoding: utf-8 -*-
'''
Description:  Simulate e-h pairs drifting and calculate induced current
@Date       : 2021/09/02 14:01:46
@Author     : Yuhang Tan, Chenxi Fu
@version    : 2.0
'''
import random
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
    def __init__(self, d_x_init, d_y_init, d_z_init, t_init, charge):
        self.d_x = d_x_init
        self.d_y = d_y_init
        self.d_z = d_z_init
        self.t = t_init
        self.path = [[d_x_init, d_y_init, d_z_init, t_init]]
        self.charge = charge
        self.signal = []
        
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
            delta_x=0.0
            delta_y=0.0
            delta_z=0.0

        # get velocity from electric field
        e_field_prime = my_f.get_e_field(self.d_x+delta_x,self.d_y+delta_y,self.d_z+delta_z)
        intensity_prime = Vector(e_field_prime[0],e_field_prime[1],e_field_prime[2]).get_length()
        average_intensity = (intensity+intensity_prime)/2.0*1e4 # V/cm
        mobility = Mobility(my_d.material)
        mu = mobility.cal_mobility(my_d, my_d.Neff(self.d_z+delta_z), self.charge, average_intensity)
        velocity = mu*average_intensity

        # get diffution from mobility and temperature
        if(velocity==0):
            self.end_condition = "zero velocity"
            return

        else:
            delta_t = step*1e-4/velocity
            kboltz=8.617385e-5 #eV/K
            diffusion = (2.0*kboltz*mu*my_d.temperature*delta_t)**0.5
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

    def get_signal(self,my_f):
        """Calculate signal from carrier path"""
        # i = q*v*nabla(U_w) = q*dx*nabla(U_w)/dt = q*dU_w(x)/dt
        # signal = i*dt = q*dU_w(x)
        for i in range(len(self.path)-1): # differentiate of weighting potential
            U_w_1 = my_f.get_w_p(self.path[i][0],self.path[i][1],self.path[i][2]) # x,y,z
            U_w_2 = my_f.get_w_p(self.path[i+1][0],self.path[i+1][1],self.path[i+1][2])
            e0 = 1.60217733e-19
            q = self.charge * e0
            dU_w = U_w_2 - U_w_1
            self.signal.append(q*dU_w)

    def drift_end(self,my_f):
        e_field = my_f.get_e_field(self.d_x,self.d_y,self.d_z)
        wpot = my_f.get_w_p(self.d_x,self.d_y,self.d_z) # after position check to avoid illegal input
        if (e_field[0]==0 and e_field[1]==0 and e_field[2]==0):
            self.end_condition = "zero velocity"
        elif wpot>(1-1e-5):
            self.end_condition = "reached cathode"
        elif wpot<1e-5:
            self.end_condition = "reached anode"
        elif(len(self.path)>10000):
            self.end_condition = "reciprocate"
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
            self.electrons.append(Carrier(track_position[i][0],\
                                          track_position[i][1],\
                                          track_position[i][2],\
                                          1e-9,\
                                          -1*ionized_pairs[i]))
            self.holes.append(Carrier(track_position[i][0],\
                                      track_position[i][1],\
                                      track_position[i][2],\
                                      1e-9,\
                                      ionized_pairs[i]))
        
        self.drifting_loop(my_d, my_f)
        self.get_current(my_d, my_d.positive_cu, my_d.negative_cu)
        if my_d.det_model == "lgad3D":
            gain_current = CalCurrentGain(my_d, my_f, self)

    def drifting_loop(self, my_d, my_f):
        for electron in self.electrons:
            while not electron.not_in_sensor(my_d):
                electron.drift_single_step(my_d.steplength, my_d, my_f)
                electron.drift_end(my_f)
            electron.get_signal(my_f)
        for hole in self.holes:
            while not hole.not_in_sensor(my_d):
                hole.drift_single_step(my_d.steplength, my_d, my_f)
                hole.drift_end(my_f)
            hole.get_signal(my_f)
        
    def get_current(self, my_d, positive_cu, negative_cu):
        test_p = ROOT.TH1F("test+","test+",my_d.n_bin,my_d.t_start,my_d.t_end)
        for hole in self.holes:
            for i in range(len(hole.path)-1):
                test_p.Fill(hole.path[i][3],hole.signal[i]/my_d.t_bin)# time,current=int(i*dt)/Δt
            positive_cu.Add(test_p)
            test_p.Reset()

        test_n = ROOT.TH1F("test-","test-",my_d.n_bin,my_d.t_start,my_d.t_end)
        for electron in self.electrons:             
            for i in range(len(electron.path)-1):
                test_n.Fill(electron.path[i][3],electron.signal[i]/my_d.t_bin)# time,current=int(i*dt)/Δt
            negative_cu.Add(test_n)
            test_n.Reset()

        my_d.sum_cu.Add(positive_cu)
        my_d.sum_cu.Add(negative_cu)

class CalCurrentGain(CalCurrent):
    '''Calculation of gain carriers and gain current, simplified version'''
    def __init__(self, my_d, my_f, my_current):
        self.electrons = [] # gain carriers
        self.holes = []
        my_ava = Avalanche(my_d.material)
        # assuming gain layer at d>0
        if my_d.voltage<0 : # p layer at d=0, holes multiplicated into electrons
            for hole in my_current.holes:
                self.electrons.append(Carrier(hole.path[-1][0],\
                                              hole.path[-1][1],\
                                              my_d.avalanche_bond,\
                                              hole.path[-1][3],\
                                              #-1*hole.charge*my_ava.gain_rate(my_d,my_f)))
                                              -1*hole.charge*10))

        else : # n layer at d=0, electrons multiplicated into holes
            for electron in my_current.electrons:
                self.holes.append(Carrier(electron.path[-1][0],\
                                          electron.path[-1][1],\
                                          my_d.avalanche_bond,\
                                          electron.path[-1][3],\
                                          #-1*electron.charge*my_ava.gain_rate(my_d,my_f)))
                                          -1*electron.charge*10))

        self.drifting_loop(my_d, my_f)
        self.get_current(my_d, my_d.gain_positive_cu, my_d.gain_negative_cu)

class CalCurrentG4P(CalCurrent):
    def __init__(self, my_d, my_f, my_g4p, batch):
        G4P_carrier_list = CarrierListFromG4P(my_d.material, my_g4p, batch)
        super().__init__(my_d, my_f, G4P_carrier_list.ionized_pairs, G4P_carrier_list.track_position)

class CalCurrentLaser(CalCurrent):
    def __init__(self, my_d, my_f, my_l):
        super().__init__(my_d, my_f, my_l.ionized_pairs, my_l.track_position)

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
            for j in range(len(my_g4p.p_steps_current)):
                if len(my_g4p.p_steps_current[j])>10 and batch == 0: # selecting particle with long enough track
                    self.batch_def(my_g4p,j)
                    batch=1
                    break
            if batch == 0:
                print("the sensor didn't have particles hitted")
                raise ValueError
        else:
            self.batch_def(my_g4p,batch)

    def batch_def(self,my_g4p,j):
        self.beam_number = j
        self.track_position = my_g4p.p_steps_current[j]
        self.tracks_step = my_g4p.energy_steps[j]
        self.tracks_t_energy_deposition = my_g4p.edep_devices[j] #为什么不使用？
        self.ionized_pairs = [step*1e6/self.energy_loss for step in self.tracks_step]
