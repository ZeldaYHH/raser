import geant4_pybind as g4b
import sys
import numpy as np
import math

class reactor:
    def __init__(self, my_d, my_f, dset):

        g4_dic = dset.pygeant4
        my_g4d = MyDetectorConstruction(my_d,my_f,g4_dic['det_model'],g4_dic['maxstep'])		
        if g4_dic['g4_vis']: 
            ui = None
            ui = g4b.G4UIExecutive(len(sys.argv), sys.argv)
        gRunManager = g4b.G4RunManagerFactory.CreateRunManager(g4b.G4RunManagerType.Default)
        rand_engine= g4b.RanecuEngine()
        g4b.HepRandom.setTheEngine(rand_engine)
        g4b.HepRandom.setTheSeed(dset.g4seed)
        gRunManager.SetUserInitialization(my_g4d)	
        # set physics list
        physics_list =  g4b.FTFP_BERT()
        physics_list.SetVerboseLevel(1)
        physics_list.RegisterPhysics(g4b.G4StepLimiterPhysics())
        gRunManager.SetUserInitialization(physics_list)
        # define global parameter
        global s_eventIDs,s_edep_devices,s_p_steps,s_energy_steps,s_events_angle
        s_eventIDs,s_edep_devices,s_p_steps,s_energy_steps,s_events_angle=[],[],[],[],[]

        #define action
        gRunManager.SetUserInitialization(MyActionInitialization(
                                          g4_dic['par_in'],
                                          g4_dic['par_out']))
        if g4_dic['g4_vis']:    
            visManager = g4b.G4VisExecutive()
            visManager.Initialize()
            UImanager = g4b.G4UImanager.GetUIpointer()
            UImanager.ApplyCommand('/control/execute init_vis.mac')
        else:
            UImanager = g4b.G4UImanager.GetUIpointer()
            UImanager.ApplyCommand('/run/initialize')
            
        gRunManager.BeamOn(int(dset.total_events))
        if g4_dic['g4_vis']:  
            ui.SessionStart()
        self.p_steps=s_p_steps
        self.init_tz_device = my_g4d.init_tz_device
        self.p_steps_current=[[[single_step[0],single_step[1],single_step[2]-self.init_tz_device]\
            for single_step in p_step] for p_step in self.p_steps]
        self.edep_devices=s_edep_devices
        self.events_angle=s_events_angle
        self.energy_steps=s_energy_steps
        

        del s_eventIDs,s_edep_devices,s_p_steps,s_energy_steps,s_events_angle
        
    def __del__(self):
        pass


class MyDetectorConstruction(g4b.G4VUserDetectorConstruction):                
    "My Detector Construction"
    def __init__(self,my_d,my_f,sensor_model,maxStep=0.5):
        g4b.G4VUserDetectorConstruction.__init__(self)
        self.solid = {}
        self.logical = {}
        self.physical = {}
        self.checkOverlaps = True
        self.create_world(my_d)
        #3D source order: beta->sic->si
        #2D source order: beta->Si->SiC
        tx_all = my_d.l_x/2.0*g4b.um
        ty_all = my_d.l_y/2.0*g4b.um
        if "planar3D" or "lgad3D" in sensor_model:
            tz_device = my_d.l_z/2.0*g4b.um
            self.init_tz_device = 0
            device_x = my_d.l_x*g4b.um 
            device_y = my_d.l_y*g4b.um
            device_z = my_d.l_z*g4b.um

        self.create_Ni_box(
                                name = "Ni",
                                sidex = device_x,
                                sidey = device_y,
                                sidez = 0.1*g4b.um,
                                translation = [tx_all,ty_all,30.05*g4b.um],
                                material_type = "G4_Ni",
                                colour = [1,0.1,0.8],
                                mother = 'world')
        
        self.create_sic_box(
                            name = "Device",
                            sidex = device_x,
                            sidey = device_y,
                            sidez = device_z,
                            translation = [tx_all,ty_all,tz_device],
                            material_Si = "Si",
                            material_c = "C",
                            colour = [1,0,0],
                            mother = 'world')
        self.maxStep = maxStep*g4b.um
        self.fStepLimit = g4b.G4UserLimits(self.maxStep)
        self.logical["Device"].SetUserLimits(self.fStepLimit)

    def create_Ni_box(self, **kwargs):
        name = kwargs['name']
        material_type = self.nist.FindOrBuildMaterial(kwargs['material_type'],
                                                      False)

        translation = g4b.G4ThreeVector(*kwargs['translation'])
        visual = g4b.G4VisAttributes(g4b.G4Color(*kwargs['colour']))
        mother = self.physical[kwargs['mother']]
        sidex = kwargs['sidex']
        sidey = kwargs['sidey']
        sidez = kwargs['sidez']

        self.solid[name] = g4b.G4Box(name, sidex/2., sidey/2., sidez/2.)
        
        self.logical[name] = g4b.G4LogicalVolume(self.solid[name], 
                                                 material_type, 
                                                 name)
        self.physical[name] = g4b.G4PVPlacement(None,translation,                                                
                                                name,self.logical[name],
                                                mother, False, 
                                                0,self.checkOverlaps)
        self.logical[name].SetVisAttributes(visual)     


    def create_world(self,my_d):

        self.nist = g4b.G4NistManager.Instance()
        material = self.nist.FindOrBuildMaterial("G4_AIR")  
        self.solid['world'] = g4b.G4Box("world",
                                        25000*g4b.um,
                                        25000*g4b.um,
                                        25000*g4b.um)
        self.logical['world'] = g4b.G4LogicalVolume(self.solid['world'], 
                                                    material, 
                                                    "world")
        self.physical['world'] = g4b.G4PVPlacement(None, 
                                                   g4b.G4ThreeVector(0,0,0), 
                                                   self.logical['world'], 
                                                   "world", None, False, 
                                                   0,self.checkOverlaps)
        visual = g4b.G4VisAttributes()
        visual.SetVisibility(False)
        self.logical['world'].SetVisAttributes(visual)

    def create_sic_box(self, **kwargs):
        name = kwargs['name']
        material_si = self.nist.FindOrBuildElement(kwargs['material_Si'],False)
        material_c = self.nist.FindOrBuildElement(kwargs['material_c'],False)
        sic_density = 3.2*g4b.g/g4b.cm3
        SiC = g4b.G4Material("SiC",sic_density,2) 
        SiC.AddElement(material_si,50*g4b.perCent)
        SiC.AddElement(material_c,50*g4b.perCent)
        translation = g4b.G4ThreeVector(*kwargs['translation'])
        visual = g4b.G4VisAttributes(g4b.G4Color(*kwargs['colour']))
        mother = self.physical[kwargs['mother']]
        sidex = kwargs['sidex']
        sidey = kwargs['sidey']
        sidez = kwargs['sidez']

        self.solid[name] = g4b.G4Box(name, sidex/2., sidey/2., sidez/2.)
        
        self.logical[name] = g4b.G4LogicalVolume(self.solid[name], 
                                                 SiC, 
                                                 name)
        self.physical[name] = g4b.G4PVPlacement(None,translation,                                                
                                                name,self.logical[name],
                                                mother, False, 
                                                0,self.checkOverlaps)
        self.logical[name].SetVisAttributes(visual)
    def Construct(self): # return the world volume
        self.fStepLimit.SetMaxAllowedStep(self.maxStep)
        return self.physical['world']

    def __del__(self):
        print("using __del__ to delete the MyDetectorConstruction class ")


class MyPrimaryGeneratorAction(g4b.G4VUserPrimaryGeneratorAction):
    "My Primary Generator Action"
    def __init__(self,par_in,par_out):
        g4b.G4VUserPrimaryGeneratorAction.__init__(self)
        par_direction = [ par_out[i] - par_in[i] for i in range(3) ]  
        particle_table = g4b.G4ParticleTable.GetParticleTable()
        particle = particle_table.FindParticle("gamma") # define the proton
        beam = g4b.G4ParticleGun(1)
        beam.SetParticleEnergy(1.33*g4b.MeV)
        beam.SetParticleMomentumDirection(g4b.G4ThreeVector(par_direction[0],
                                                            par_direction[1],
                                                            par_direction[2]))
        beam.SetParticleDefinition(particle)
        beam.SetParticlePosition(g4b.G4ThreeVector(par_in[0]*g4b.um,
                                                   par_in[1]*g4b.um,
                                                   par_in[2]*g4b.um))  
        self.particleGun = beam
    
    def GeneratePrimaries(self, event):
        self.particleGun.GeneratePrimaryVertex(event)


class MyRunAction(g4b.G4UserRunAction):
    def __init__(self):
        g4b.G4UserRunAction.__init__(self)
        milligray = 1.e-3*g4b.gray
        microgray = 1.e-6*g4b.gray
        nanogray = 1.e-9*g4b.gray
        picogray = 1.e-12*g4b.gray

        g4b.G4UnitDefinition("milligray", "milliGy", "Dose", milligray)
        g4b.G4UnitDefinition("microgray", "microGy", "Dose", microgray)
        g4b.G4UnitDefinition("nanogray", "nanoGy", "Dose", nanogray)
        g4b.G4UnitDefinition("picogray", "picoGy", "Dose", picogray)
      
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
    def __init__(self,par_in,par_out):
        g4b.G4VUserActionInitialization.__init__(self)
        self.par_in = par_in
        self.par_out = par_out

    def Build(self):
        self.SetUserAction(MyPrimaryGeneratorAction(self.par_in,
                                                    self.par_out))
        # global myRA_action
        myRA_action = MyRunAction()
        self.SetUserAction(myRA_action)
        myEA = MyEventAction(myRA_action,self.par_in,self.par_out)
        self.SetUserAction(myEA)
        self.SetUserAction(MySteppingAction(myEA))

