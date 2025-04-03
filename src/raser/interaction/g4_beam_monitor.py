#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
Description: 
    geat4_pybind simulation   
@Date       : 2021/09/02 12:46:27
@Author     : tanyuhang
@version    : 1.0
   
@Date       : 2023/04/18
@Author     : xingchenli
@version    : 2.0
'''

import sys
import random
import math
import json
import os

import numpy as np
import geant4_pybind as g4b

verbose = 0
world_size = 25000

# Geant4 main process
class Particles:
    def __init__(self, my_d, g4experiment, g4_seed = random.randint(0, 1e7)):
        """
        Description:
            Geant4 main process
            Simulate s_num particles through device
            Record the energy depositon in the device
        Parameters:
        ---------
        energy_steps : list
            Energy deposition of each step in simulation
        edep_devices : list
            Total energy deposition in device          
        @Modify:
        ---------
            2023/04/18
        """	
        geant4_json = os.getenv("RASER_SETTING_PATH")+"/g4experiment/" + g4experiment + ".json"
        with open(geant4_json) as f:
            g4_dic = json.load(f)

        self.geant4_model = g4_dic['geant4_model']
        detector_material=my_d.device_dict['material']
        my_g4d = MyDetectorConstruction(my_d,g4_dic,detector_material,g4_dic['maxstep'])

        if g4_dic['g4_vis']: 
            ui = None
            ui = g4b.G4UIExecutive(len(sys.argv), sys.argv)
        g4RunManager = g4b.G4RunManagerFactory.CreateRunManager(g4b.G4RunManagerType.Default)
        rand_engine= g4b.RanecuEngine()
        g4b.HepRandom.setTheEngine(rand_engine)
        g4b.HepRandom.setTheSeed(g4_seed)
        g4RunManager.SetUserInitialization(my_g4d)
        # set physics list
        physics_list =  g4b.FTFP_BERT()
        physics_list.RegisterPhysics(g4b.G4StepLimiterPhysics())
        g4RunManager.SetUserInitialization(physics_list)
        # define global parameter
        global s_eventIDs,s_edep_devices,s_p_steps,s_energy_steps,s_events_angle
        s_eventIDs,s_edep_devices,s_p_steps,s_energy_steps,s_events_angle=[],[],[],[],[]

        #define action
        g4RunManager.SetUserInitialization(MyActionInitialization(
                                          g4_dic['par_in'],
                                          g4_dic['par_out'],
                                          g4_dic['par_type'],
                                          g4_dic['par_energy'],
                                          self.geant4_model))
        if g4_dic['g4_vis']:    
            visManager = g4b.G4VisExecutive()
            visManager.Initialize()
            UImanager = g4b.G4UImanager.GetUIpointer()
            UImanager.ApplyCommand('/control/execute setting/g4macro/init_vis.mac')
        else:
            UImanager = g4b.G4UImanager.GetUIpointer()
            # reduce verbose from physics list
            UImanager.ApplyCommand('/process/em/verbose %d'%(verbose))
            UImanager.ApplyCommand('/process/had/verbose %d'%(verbose))
            UImanager.ApplyCommand('/run/initialize')
            
        g4RunManager.BeamOn(int(g4_dic['total_events']))
        if g4_dic['g4_vis']:  
            ui.SessionStart()
        self.p_steps=s_p_steps
        self.init_tz_device = 0    
        self.p_steps_current=[[[single_step[0]+my_d.l_x/2,
                                single_step[1]+my_d.l_y/2,
                                single_step[2]-self.init_tz_device]\
            for single_step in p_step] for p_step in self.p_steps]

        self.energy_steps=s_energy_steps
        self.edep_devices=s_edep_devices
        self.events_angle=s_events_angle
            
        hittotal=0
        for particleenergy in s_edep_devices:
            if(particleenergy>0):
                hittotal=hittotal+1
        self.hittotal=hittotal      #count the numver of hit particles

        number=0
        total_steps=0
        for step in s_p_steps:
            total_steps=len(step)+total_steps
        average_steps=total_steps/len(s_p_steps)
        for step in s_p_steps:
            if(len(step)>=average_steps*0.9):
                break
            number=number+1
        newtype_step=s_p_steps[number]      #new particle's step
        self.p_steps_current=[[[single_step[0]+my_d.l_x/2,
                                single_step[1]+my_d.l_y/2,
                                single_step[2]-self.init_tz_device]\
            for single_step in newtype_step]]
    
        newtype_energy=[0 for i in range(len(newtype_step))]
        for energy in s_energy_steps:
            for i in range(len(newtype_step)):
                if(len(energy)>i):
                    newtype_energy[i]+=energy[i]
        self.energy_steps=[newtype_energy]      #new particle's every step energy

        del s_eventIDs,s_edep_devices,s_p_steps,s_energy_steps,s_events_angle
        
    def __del__(self):
        pass
#Geant4 for object
class MyDetectorConstruction(g4b.G4VUserDetectorConstruction):                
    "My Detector Construction"
    def __init__(self,my_d,g4_dic,detector_material,maxStep=0.5):
        g4b.G4VUserDetectorConstruction.__init__(self)
        self.solid = {}
        self.logical = {}
        self.physical = {}
        self.checkOverlaps = True
        self.create_world(g4_dic['world'])
        self.geant4_model = g4_dic['geant4_model']
        
        if(detector_material=='Si'):
            detector={
                        "name" : "Device",
                        "material" : "G4_Si",
                        "side_x" : my_d.l_x,
                        "side_y" : my_d.l_y,
                        "side_z" : my_d.l_z,
                        "colour" : [1,0,0],
                        "position_x" : 0,
                        "position_y" : 0,
                        "position_z" : my_d.l_z/2.0
                        }
            self.create_elemental(detector)

        if(detector_material=='SiC' and self.geant4_model != 'cflm'):
            detector={
                        "name" : "Device",
                        "material_1" : "Si",
                        "material_2" : "C",
                        "compound_name" :"SiC",
                        "density" : 3.2,
                        "natoms_1" : 50,
                        "natoms_2" : 50,
                        "side_x" : my_d.l_x,
                        "side_y" : my_d.l_y,
                        "side_z" : my_d.l_z,
                        "colour" : [1,0,0],
                        "position_x" : 0,
                        "position_y" : 0,
                        "position_z" : my_d.l_z/2.0,
                        "tub" : {}
                        }
            self.create_binary_compounds(detector)
            
        if(g4_dic['object']):
            for object_type in g4_dic['object']:
                if(object_type=="elemental"):
                    for every_object in g4_dic['object'][object_type]:
                        self.create_elemental(g4_dic['object'][object_type][every_object])
                if(object_type=="binary_compounds"):
                    for every_object in g4_dic['object'][object_type]:
                        self.create_binary_compounds(g4_dic['object'][object_type][every_object])
       
        self.maxStep = maxStep*g4b.um
        self.fStepLimit = g4b.G4UserLimits(self.maxStep)
        
        self.logical["Device"].SetUserLimits(self.fStepLimit)

    def create_world(self,world_type):

        self.nist = g4b.G4NistManager.Instance()
        material = self.nist.FindOrBuildMaterial(world_type)  
        self.solid['world'] = g4b.G4Box("world",
                                        world_size*g4b.um,
                                        world_size*g4b.um,
                                        world_size*g4b.um)
        self.logical['world'] = g4b.G4LogicalVolume(self.solid['world'], 
                                                    material, 
                                                    "world")
        self.physical['world'] = g4b.G4PVPlacement(None, 
                                                   g4b.G4ThreeVector(0,0,0), 
                                                   self.logical['world'], 
                                                   "world", None, False, 
                                                   0,self.checkOverlaps)
        
        self.logical['world'].SetVisAttributes(g4b.G4VisAttributes.GetInvisible())

    
    def create_elemental(self,object): 
        name = object['name']
        material_type = self.nist.FindOrBuildMaterial(object['material'],
                                                    False)
        translation = g4b.G4ThreeVector(object['position_x']*g4b.um, object['position_y']*g4b.um, object['position_z']*g4b.um)
        visual = g4b.G4VisAttributes(g4b.G4Color(object['colour'][0],object['colour'][1],object['colour'][2]))
        mother = self.physical['world']
        sidex = object['side_x']*g4b.um
        sidey = object['side_y']*g4b.um
        sidez = object['side_z']*g4b.um
        self.solid[name] = g4b.G4Box(name, sidex/2., sidey/2., sidez/2.)
        
        self.logical[name] = g4b.G4LogicalVolume(self.solid[name], 
                                                material_type, 
                                                name)
        self.physical[name] = g4b.G4PVPlacement(None,translation,                                                
                                                name,self.logical[name],
                                                mother, False, 
                                                0,self.checkOverlaps)
        self.logical[name].SetVisAttributes(visual)     

    def create_binary_compounds(self,object):
        name = object['name']
        material_1 = self.nist.FindOrBuildElement(object['material_1'],False)
        material_2 = self.nist.FindOrBuildElement(object['material_2'],False)
        material_density = object['density']*g4b.g/g4b.cm3
        compound=g4b.G4Material(object['compound_name'],material_density,2) 
        compound.AddElement(material_1,object['natoms_1']*g4b.perCent)
        compound.AddElement(material_2,object['natoms_2']*g4b.perCent)
        translation = g4b.G4ThreeVector(object['position_x']*g4b.um, object['position_y']*g4b.um, object['position_z']*g4b.um)
        visual = g4b.G4VisAttributes(g4b.G4Color(object['colour'][0],object['colour'][1],object['colour'][2]))
        mother = self.physical['world']
        sidex = object['side_x']*g4b.um
        sidey = object['side_y']*g4b.um
        sidez = object['side_z']*g4b.um
        if not(object['tub']):
            self.solid[name] = g4b.G4Box(name, sidex/2., sidey/2., sidez/2.)
        else:
            self.solid[name+"box"] = g4b.G4Box(name+"box", 
                                           sidex/2., sidey/2., sidez/2.)
            self.solid[name+"tub"] = g4b.G4Tubs(name+"tub", 0,object['tub']['tub_radius']*g4b.um,
                                                object['tub']['tub_depth']*g4b.um, 0,360*g4b.deg)
            self.solid[name] = g4b.G4SubtractionSolid(name,
                                                    self.solid[name+"box"],
                                                    self.solid[name+"tub"])
            
        self.logical[name] = g4b.G4LogicalVolume(self.solid[name], 
                                                 compound, 
                                                 name)
        self.physical[name] = g4b.G4PVPlacement(None,translation,                                                
                                                name,self.logical[name],
                                                mother, False, 
                                                0,self.checkOverlaps)
        self.logical[name].SetVisAttributes(visual)


    

    def Construct(self): # return the world volume
        self.fStepLimit.SetMaxAllowedStep(self.maxStep)
        return self.physical['world']


class MyPrimaryGeneratorAction(g4b.G4VUserPrimaryGeneratorAction):
    "My Primary Generator Action"
    def __init__(self,par_in,par_out,par_type,par_energy,geant4_model):
        g4b.G4VUserPrimaryGeneratorAction.__init__(self)
        self.geant4_model=geant4_model
        par_direction = [ par_out[i] - par_in[i] for i in range(3) ]  
        particle_table = g4b.G4ParticleTable.GetParticleTable()
        particle = particle_table.FindParticle(par_type) # define particle
        beam = g4b.G4ParticleGun(1)
        beam.SetParticleEnergy(par_energy*g4b.MeV)
        beam.SetParticleMomentumDirection(g4b.G4ThreeVector(par_direction[0],
                                                            par_direction[1],
                                                            par_direction[2]))
        beam.SetParticleDefinition(particle)
        beam.SetParticlePosition(g4b.G4ThreeVector(par_in[0]*g4b.um,
                                                   par_in[1]*g4b.um,
                                                   par_in[2]*g4b.um))  
        self.particleGun = beam
        self.position = par_in


    def GeneratePrimaries(self, event):
        self.particleGun.GeneratePrimaryVertex(event)


class MyRunAction(g4b.G4UserRunAction):
    def __init__(self):
        g4b.G4UserRunAction.__init__(self)
      
    def BeginOfRunAction(self, run):
        g4b.G4RunManager.GetRunManager().SetRandomNumberStore(False)
   
    def EndOfRunAction(self, run):
        nofEvents = run.GetNumberOfEvent()
        if nofEvents == 0:
            print("nofEvents=0")
            return

class MyEventAction(g4b.G4UserEventAction):
    "My Event Action"
    def __init__(self, runAction, point_in, point_out):
        g4b.G4UserEventAction.__init__(self)
        self.fRunAction = runAction
        self.point_in = point_in
        self.point_out = point_out

    def BeginOfEventAction(self, event):
        self.edep_device=0.
        self.event_angle = 0.
        self.p_step = []
        self.energy_step = []

    def EndOfEventAction(self, event):
        eventID = event.GetEventID()
        #print("eventID:%s"%eventID)
        if len(self.p_step):
            point_a = [ b-a for a,b in zip(self.point_in,self.point_out)]
            point_b = [ c-a for a,c in zip(self.point_in,self.p_step[-1])]
            self.event_angle = cal_angle(point_a,point_b)
        else:
            self.event_angle = None
        save_geant4_events(eventID,self.edep_device,
                           self.p_step,self.energy_step,self.event_angle)

        #print("Detector: total energy:", g4b.G4BestUnit(self.edep_device, "Energy"), end="")

    def RecordDevice(self, edep,point_in,point_out):
        self.edep_device += edep
        self.p_step.append([point_in.getX()*1000,
                           point_in.getY()*1000,point_in.getZ()*1000])
        self.energy_step.append(edep)

def save_geant4_events(eventID,edep_device,p_step,energy_step,event_angle):
    if(len(p_step)>0):
        s_eventIDs.append(eventID)
        s_edep_devices.append(edep_device)
        s_p_steps.append(p_step)
        s_energy_steps.append(energy_step)
        s_events_angle.append(event_angle)
    else:
        s_eventIDs.append(eventID)
        s_edep_devices.append(edep_device)
        s_p_steps.append([[0,0,0]])
        s_energy_steps.append([0])
        s_events_angle.append(event_angle)
        
        
def cal_angle(point_a,point_b):
    "Calculate the angle between point a and b"
    x=np.array(point_a)
    y=np.array(point_b)
    l_x=np.sqrt(x.dot(x))
    l_y=np.sqrt(y.dot(y))
    dot_product=x.dot(y)
    if l_x*l_y > 0:
        cos_angle_d=dot_product/(l_x*l_y)
        angle_d=np.arccos(cos_angle_d)*180/np.pi
    else:
        angle_d=9999
    return angle_d


class MySteppingAction(g4b.G4UserSteppingAction):
    "My Stepping Action"
    def __init__(self, eventAction):
        g4b.G4UserSteppingAction.__init__(self)
        self.fEventAction = eventAction

    def UserSteppingAction(self, step):
        edep = step.GetTotalEnergyDeposit()
        point_pre  = step.GetPreStepPoint()
        point_post = step.GetPostStepPoint() 
        point_in   = point_pre.GetPosition()
        point_out  = point_post.GetPosition()
        volume = step.GetPreStepPoint().GetTouchable().GetVolume().GetLogicalVolume()
        volume_name = volume.GetName()

        if(volume_name == "Device"):
            self.fEventAction.RecordDevice(edep,point_in,point_out)

class MyActionInitialization(g4b.G4VUserActionInitialization):
    def __init__(self,par_in,par_out,par_type,par_energy,geant4_model):
        g4b.G4VUserActionInitialization.__init__(self)
        self.par_in = par_in
        self.par_out = par_out
        self.par_type=par_type
        self.par_energy=par_energy
        self.geant4_model=geant4_model

    def Build(self):
        self.SetUserAction(MyPrimaryGeneratorAction(self.par_in,
                                                    self.par_out,
                                                    self.par_type,
                                                    self.par_energy,
                                                    self.geant4_model))
        # global myRA_action
        myRA_action = MyRunAction()
        self.SetUserAction(myRA_action)
        myEA = MyEventAction(myRA_action,self.par_in,self.par_out)
        self.SetUserAction(myEA)
        self.SetUserAction(MySteppingAction(myEA))

