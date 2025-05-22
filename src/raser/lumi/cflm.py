#!/usr/bin/env python3 
import os
import math

import geant4_pybind as g4b
import json

#G4AnalysisManager = g4b.G4RootAnalysisManager

X_position, Z_position,  Y_position, Particle = [], [], [], []

class cflmG4Interaction:

    def __init__(self, my_d):

        global s_eventIDs,s_edep_devices,s_p_steps,s_energy_steps
        s_eventIDs,s_edep_devices,s_p_steps,s_energy_steps = [],[],[],[]

        self.geant4_model = "cflm"

        geant4_json = os.getenv("RASER_SETTING_PATH")+"/g4experiment/cflm.json"
        with open(geant4_json) as f:
             g4_dic = json.load(f)

        runManager = g4b.G4RunManagerFactory.CreateRunManager(g4b.G4RunManagerType.Serial)
        UImanager = g4b.G4UImanager.GetUIpointer()

        physicsList = g4b.FTFP_BERT()
        physicsList.SetVerboseLevel(0)
        physicsList.RegisterPhysics(g4b.G4StepLimiterPhysics())
        runManager.SetUserInitialization(physicsList)

        detConstruction = cflmDetectorConstruction(g4_dic)
        runManager.SetUserInitialization(detConstruction)

        actionInitialization = cflmaActionInitialization(detConstruction,
                                                         g4_dic['par_in'],
                                                         g4_dic['par_direct'],
                                                         g4_dic['par_type'],
                                                         g4_dic['par_energy'],
                                                         g4_dic['NumofGun'],
                                                         g4_dic['EdepBaseName'],
                                                         g4_dic['PosBaseName']
                                                        )
        runManager.SetUserInitialization(actionInitialization)
        
        UImanager = g4b.G4UImanager.GetUIpointer()
        UImanager.ApplyCommand('/run/initialize')

        runManager.BeamOn(int(g4_dic['BeamOn']))

        self.p_steps=s_p_steps
        self.init_tz_device = -31
        self.p_steps_current=[[[-single_step[1] + my_d.l_x/2,                                                                                  ### *1000: mm---->um
                                single_step[2] - g4_dic['object']['binary_compounds']['detector']['position_z']*1000 + my_d.l_y/2,
                                self.init_tz_device*1000 - single_step[0]]\
            for single_step in p_step] for p_step in self.p_steps]

        self.energy_steps=s_energy_steps
        self.edep_devices=s_edep_devices
        self.HitFlag = 0
        print(f'The edep of detector: {self.edep_devices[0]}')

        with open("output/lumiTimeSignalEdep.txt", "a") as TimeSignalEdep:
             TimeSignalEdep.write(str(self.edep_devices[0])+'\n')
             

        if len(s_p_steps[0]) != 1:
            self.HitFlag = 1
        
        del s_eventIDs,s_edep_devices,s_p_steps,s_energy_steps

    def __del__(self):
        pass

class cflmDetectorConstruction(g4b.G4VUserDetectorConstruction):

    def __init__(self,g4_dic):
        g4b.G4VUserDetectorConstruction.__init__(self)
        self.solid = {}
        self.logical = {}
        self.physical = {}
        self.checkOverlaps = True
        self.create_world(g4_dic['world'])

        self.maxStep = g4_dic['maxStep']*g4b.um

        self.rotation = g4b.G4RotationMatrix()
        self.rotation.rotateZ(3*math.pi/2)

        for object_type in g4_dic['object']:
            if(object_type=="elemental"):
                for every_object in g4_dic['object'][object_type]:
                    self.create_elemental(g4_dic['object'][object_type][every_object])
            if(object_type=="binary_compounds"):
                for every_object in g4_dic['object'][object_type]:
                    self.create_binary_compounds(g4_dic['object'][object_type][every_object])

        self.fStepLimit = g4b.G4UserLimits(self.maxStep)
        self.logical["detector"].SetUserLimits(self.fStepLimit)

    def create_world(self,world_type):

        self.nist = g4b.G4NistManager.Instance()
        material = self.nist.FindOrBuildMaterial(world_type)
        self.solid['world'] = g4b.G4Box("world",
                                        800*g4b.mm,
                                        800*g4b.mm,
                                        800*g4b.mm)
        self.logical['world'] = g4b.G4LogicalVolume(self.solid['world'],
                                                    material,
                                                    "world")
        self.physical['world'] = g4b.G4PVPlacement(None,
                                                   g4b.G4ThreeVector(0,0,0),
                                                   self.logical['world'],
                                                   "world", 
                                                   None, 
                                                   False,
                                                   0,
                                                   self.checkOverlaps)

        self.logical['world'].SetVisAttributes(g4b.G4VisAttributes.GetInvisible())


    def create_elemental(self,object):
        
            material_type = self.nist.FindOrBuildMaterial(object['material'],
                                                        False)

            translation = g4b.G4ThreeVector(object['position_x']*g4b.mm, object['position_y']*g4b.mm, object['position_z']*g4b.mm)
            visual = g4b.G4VisAttributes(g4b.G4Color(object['colour'][0],object['colour'][1],object['colour'][2]))
            mother = self.physical['world']

            Rmin = object['Rmin']*g4b.mm
            Rmax = object['Rmax']*g4b.mm
            Pipe_Z = object['Pipe_Z']*g4b.mm
            PipeSphi = object['PipeSphi']*g4b.deg
            PipeDphi = object['PipeDphi']*g4b.deg

            self.solid['pipe'] = g4b.G4Tubs("Pipe",
                                            Rmin, Rmax, Pipe_Z/2,PipeSphi,PipeDphi)

            self.logical['pipe'] = g4b.G4LogicalVolume(self.solid['pipe'],
                                                       material_type,
                                                       'pipe')
            self.physical['pipe'] = g4b.G4PVPlacement(self.rotation,
                                                      translation,
                                                      'pipe',
                                                      self.logical['pipe'],
                                                      mother, 
                                                      False,
                                                      0,
                                                      self.checkOverlaps)
            self.logical['pipe'].SetVisAttributes(visual)

    def create_binary_compounds(self,object):
        name = object['name']
        material_1 = self.nist.FindOrBuildElement(object['material_1'],False)
        material_2 = self.nist.FindOrBuildElement(object['material_2'],False)
        material_density = object['density']*g4b.g/g4b.cm3
        compound=g4b.G4Material(object['compound_name'],material_density,2)
        compound.AddElement(material_1,object['natoms_1']*g4b.perCent)
        compound.AddElement(material_2,object['natoms_2']*g4b.perCent)
        translation = g4b.G4ThreeVector(object['position_x']*g4b.mm, object['position_y']*g4b.mm, object['position_z']*g4b.mm)
        visual = g4b.G4VisAttributes(g4b.G4Color(object['colour'][0],object['colour'][1],object['colour'][2]))
        mother = self.physical['world']
        sidex = object['side_x']*g4b.mm
        sidey = object['side_y']*g4b.mm
        sidez = object['side_z']*g4b.mm
        
        self.solid[name] = g4b.G4Box(name, sidex/2., sidey/2., sidez/2.)

        self.logical[name] = g4b.G4LogicalVolume(self.solid[name],
                                                 compound,
                                                 name)
        self.physical[name] = g4b.G4PVPlacement(self.rotation,
                                                translation,
                                                name,
                                                self.logical[name],
                                                mother, 
                                                False,
                                                0,
                                                self.checkOverlaps)
        
        self.logical[name].SetVisAttributes(visual)

    def Construct(self): 
        self.fStepLimit.SetMaxAllowedStep(self.maxStep)       
        return self.physical['world']

class cflmPrimaryGeneratorAction(g4b.G4VUserPrimaryGeneratorAction):

    def __init__(self, par_in, par_direct, par_type, par_energy, numofgun):
        super().__init__()
        self.nofParticles = numofgun
        self.fParticleGun = g4b.G4ParticleGun(1)
        particleDefinition = g4b.G4ParticleTable.GetParticleTable().FindParticle(par_type)
        self.fParticleGun.SetParticleDefinition(particleDefinition)
        self.directions = []
        self.par_in = []
        self.energy = []    

        self.directions = [g4b.G4ThreeVector(direction[0], direction[1], direction[2]) for direction in par_direct]
        self.par_in = [g4b.G4ThreeVector(position[0], position[1], position[2]) for position in par_in]
        self.energy = par_energy

    def GeneratePrimaries(self, anEvent):
        
        for i in range(self.nofParticles):
       
            self.fParticleGun.SetParticlePosition(self.par_in[i])
            self.fParticleGun.SetParticleMomentumDirection(self.directions[i])

            self.fParticleGun.SetParticleEnergy(self.energy[i]*g4b.GeV) 
            
            self.fParticleGun.GeneratePrimaryVertex(anEvent)

class cflmaSteppingAction(g4b.G4UserSteppingAction):

    def __init__(self, detectorConstruction, eventAction, X_position, Z_position, Y_position, Particle):
        super().__init__()
        self.fDetConstruction = detectorConstruction
        self.fEventAction = eventAction
        self.X_position = X_position
        self.Z_position = Z_position
        self.Y_position = Y_position
        self.Particle = Particle

    def UserSteppingAction(self, step):
        volume_pre = step.GetPreStepPoint().GetTouchable().GetVolume()
        volume_post = step.GetPostStepPoint().GetTouchable().GetVolume()
        edep = step.GetTotalEnergyDeposit()
        point_in = step.GetPreStepPoint().GetPosition()

        if volume_pre != self.fDetConstruction.physical['detector']  and volume_post == self.fDetConstruction.physical['detector']:
            self.X_position.append(step.GetPostStepPoint().GetPosition().getX())
            self.Z_position.append(step.GetPostStepPoint().GetPosition().getZ())
            self.Y_position.append(step.GetPostStepPoint().GetPosition().getY())
            self.Particle.append(step.GetTrack().GetDefinition().GetParticleName())
        
        if volume_pre == self.fDetConstruction.physical['pipe']:
            self.fEventAction.AddPipe(edep)
        
        if volume_pre == self.fDetConstruction.physical['detector']:

            self.fEventAction.AddDetector(edep)
            self.fEventAction.RecordDetector(edep, point_in)    

class cflmaEventAction(g4b.G4UserEventAction):

    def BeginOfEventAction(self, event):

        self.fEnergyPipe = 0
        self.fEnergyDetector = 0
     
        self.edep_device=0
        self.p_step = []
        self.energy_step = []


    def EndOfEventAction(self, event):

        analysisManager = g4b.G4AnalysisManager.Instance()

        analysisManager.FillNtupleDColumn(0, self.fEnergyPipe)
        analysisManager.FillNtupleDColumn(1, self.fEnergyDetector)
        analysisManager.AddNtupleRow()

        eventID = event.GetEventID()  
        save_geant4_events(eventID,self.edep_device,self.p_step,self.energy_step)
        printModulo = g4b.G4RunManager.GetRunManager().GetPrintProgress()
        if printModulo > 0 and eventID % printModulo == 0:
            print("---> End of event:", eventID)
            print("Pipe: total energy:", g4b.G4BestUnit(self.fEnergyPipe, "Energy"), end="")
            print("Detector: total energy:", g4b.G4BestUnit(self.fEnergyDetector, "Energy"), end="")
            print("Detector: total energy:", g4b.G4BestUnit(self.edep_device, "Energy"), end="")


    def AddPipe(self, de):
        self.fEnergyPipe += de

    def AddDetector(self, de):
        self.fEnergyDetector += de

    def RecordDetector(self, edep,point_in):
        self.edep_device += edep
        self.p_step.append([point_in.getX()*1000,
                            point_in.getY()*1000,
                            point_in.getZ()*1000])
        self.energy_step.append(edep)

class cflmRunAction(g4b.G4UserRunAction):

    def __init__(self, EdepBaseName, PosBaseName):
        super().__init__()

        self.EdepBaseName = EdepBaseName
        self.PosBaseName = PosBaseName

        g4b.G4RunManager.GetRunManager().SetPrintProgress(1)

        analysisManager = g4b.G4AnalysisManager.Instance()
        print("Using", analysisManager.GetType())

        analysisManager.SetVerboseLevel(1)
        analysisManager.SetNtupleMerging(True)

        analysisManager.CreateNtuple("cflm", "Edep")
        analysisManager.CreateNtupleDColumn("Epipe")
        analysisManager.CreateNtupleDColumn("Edetector")
        analysisManager.FinishNtuple()

    def BeginOfRunAction(self, run):

        analysisManager = g4b.G4AnalysisManager.Instance()
        EdepName = f"output/lumi{self.EdepBaseName}"
        analysisManager.OpenFile(EdepName)
        
    def EndOfRunAction(self, run):

        analysisManager = g4b.G4AnalysisManager.Instance()

        if self.IsMaster():
            print("for the entire run \n")
        
        else:
            print("for the local thread \n")

            print(" EPipe : mean =", g4b.G4BestUnit(analysisManager.GetH1(0).mean(), "Energy"), end="")
            print(" rms =", g4b.G4BestUnit(analysisManager.GetH1(0).rms(),  "Energy"))

            print(" EDetector : mean =", g4b.G4BestUnit(analysisManager.GetH1(1).mean(), "Energy"), end="")
            print(" rms =", g4b.G4BestUnit(analysisManager.GetH1(1).rms(),  "Energy"))
        # save histograms & ntuple
        analysisManager.Write()
        
        PosName = f"output/lumi{self.PosBaseName}"
        with open(PosName, 'w') as file:  
             for i in range(len(Particle)):
                file.write(f"{Particle[i]} {X_position[i]} {Z_position[i]} {Y_position[i]}\n")
    
class cflmaActionInitialization(g4b.G4VUserActionInitialization):

    def __init__(self, detConstruction, par_in, par_direct, par_type, par_energy, numofgun, EdepBaseName, PosBaseName):
        super().__init__()
        self.fDetConstruction = detConstruction
        self.par_in = par_in
        self.par_direct = par_direct
        self.par_type=par_type
        self.par_energy=par_energy
        self.numofgun = numofgun
        self.EdepBaseName = EdepBaseName
        self.PosBaseName = PosBaseName

    def BuildForMaster(self):
        self.SetUserAction(cflmRunAction(self.EdepBaseName, self.PosBaseName))

    def Build(self):
        self.SetUserAction(cflmPrimaryGeneratorAction(self.par_in,
                                                      self.par_direct,
                                                      self.par_type,
                                                      self.par_energy,
                                                      self.numofgun))
        self.SetUserAction(cflmRunAction(self.EdepBaseName, self.PosBaseName))
        eventAction = cflmaEventAction()
        self.SetUserAction(eventAction)
        self.SetUserAction(cflmaSteppingAction(self.fDetConstruction, eventAction, X_position, Z_position, Y_position, Particle))

def save_geant4_events(eventID,edep_device,p_step,energy_step):
    if(len(p_step)>0):
        s_eventIDs.append(eventID)
        s_edep_devices.append(edep_device)
        s_p_steps.append(p_step)
        s_energy_steps.append(energy_step)
    else:
        s_eventIDs.append(eventID)
        s_edep_devices.append(edep_device)
        s_p_steps.append([[0,0,0]])
        s_energy_steps.append([0])


def main():

    global s_eventIDs,s_edep_devices,s_p_steps,s_energy_steps
    s_eventIDs,s_edep_devices,s_p_steps,s_energy_steps = [],[],[],[]

    geant4_json = os.getenv("RASER_SETTING_PATH")+"/g4experiment/cflm.json"
    with open(geant4_json) as f:
        g4_dic = json.load(f)

    runManager = g4b.G4RunManagerFactory.CreateRunManager(g4b.G4RunManagerType.Serial)
    
    physicsList = g4b.FTFP_BERT()
    physicsList.RegisterPhysics(g4b.G4StepLimiterPhysics())
    runManager.SetUserInitialization(physicsList)

    detConstruction = cflmDetectorConstruction(g4_dic)
    runManager.SetUserInitialization(detConstruction)

    actionInitialization = cflmaActionInitialization(detConstruction,
                                                     g4_dic['par_in'],
                                                     g4_dic['par_direct'],
                                                     g4_dic['par_type'],
                                                     g4_dic['par_energy'],
                                                     g4_dic['NumofGun'],
                                                     g4_dic['EdepBaseName'],
                                                     g4_dic['PosBaseName']
                                                    )
    runManager.SetUserInitialization(actionInitialization)

    visManager = g4b.G4VisExecutive()
    visManager.Initialize()
    UImanager = g4b.G4UImanager.GetUIpointer()
   
    if g4_dic['vis']:

         UImanager.ApplyCommand("/control/execute param_file/g4macro/init_vis.mac")
    
    UImanager.ApplyCommand('/run/initialize')
    UImanager.ApplyCommand('/tracking/verbose 0')
    
    UImanager.ApplyCommand(f"/run/beamOn {g4_dic['BeamOn']}")
    
    if g4_dic['vis']:
      
         UImanager.ApplyCommand('/vis/ogl/set/printMode vectored')
         UImanager.ApplyCommand("/vis/viewer/set/background 0 0 0")
         UImanager.ApplyCommand('/vis/ogl/set/printSize 2000 600')#可视化打印尺寸为2000*2000
         UImanager.ApplyCommand('/vis/ogl/set/printFilename output/cflm/image.pdf')
         UImanager.ApplyCommand('/vis/ogl/export')
         
         for i in range(1000):
             UImanager.ApplyCommand("/vis/viewer/refresh")
             
if __name__ == '__main__':
    main()

