#!/usr/bin/env python3 
import os
import math
import array
import ROOT
import geant4_pybind as g4b
import json

pixelZIndex = []
for i in range(30):
    pixelZIndex.append(i)
pixelYIndex = [-3, -2, -1, 0, 1, 2]

class cflmPixelG4Interaction:

    def __init__(self, my_d, i, j):

        global s_eventIDs,s_edep_devices,s_p_steps,s_energy_steps
        s_eventIDs,s_edep_devices,s_p_steps,s_energy_steps = {}, {}, {}, {}

        global detectorID, singleAreaEdep
        detectorID, singleAreaEdep = [], []

        self.geant4_model = "cflm"

        for m in pixelYIndex:
            for n in pixelZIndex:
                s_eventIDs[f'{m}_{n}'] = []
                s_edep_devices[f'{m}_{n}'] = []
                s_p_steps[f'{m}_{n}'] = []
                s_energy_steps[f'{m}_{n}'] = []
        
        json_s_p_steps_path = 'output/lumip3/s_p_steps.json'
        json_s_energy_steps_path = 'output/lumip3/s_energy_steps.json'
        json_s_edep_devices_path = 'output/lumip3/s_edep_devices.json'
                                        
        if os.path.exists(json_s_p_steps_path) and os.path.exists(json_s_energy_steps_path) and os.path.exists(json_s_edep_devices_path):

           with open(json_s_p_steps_path, 'r') as step_file:
                step = json.load(step_file)
                self.p_steps = step[f'{i}_{j}']
           with open(json_s_energy_steps_path, 'r') as step_energy_file:
                step_energy = json.load(step_energy_file)
                self.energy_steps = step_energy[f'{i}_{j}']
           with open(json_s_edep_devices_path, 'r') as edep_device_file:
                edep_device = json.load(edep_device_file)
                self.edep_devices = edep_device[f'{i}_{j}']
           
           self.init_tz_device = -31
           if i>=0:
               y_position = (i * 5 + 2.5)
           elif i<0:
               y_position = ((i + 1) * 5 - 2.5)
            
           z_position = (j * 5 + 2.5)
            
           self.p_steps_current=[[[my_d.l_x/2 - single_step[1] + y_position*1000,   ### *1000: mm---->um
                                   my_d.l_y/2 + single_step[2] - z_position*1000,
                                   self.init_tz_device*1000 - single_step[0]]\
                for single_step in p_step] for p_step in self.p_steps]

           self.HitFlag = 0
        
           if len(self.p_steps[0]) != 1:
              self.HitFlag = 1
        else:
           geant4_json = os.getenv("RASER_SETTING_PATH")+"/g4experiment/cflm_p3.json"
           with open(geant4_json) as f:
                g4_dic = json.load(f)

           runManager = g4b.G4RunManagerFactory.CreateRunManager(g4b.G4RunManagerType.Serial)
           rand_engine= g4b.RanecuEngine()
           g4b.HepRandom.setTheEngine(rand_engine)
           g4b.HepRandom.setTheSeed(3020122)
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
                                                            g4_dic['NumofGun']
                                                            )
           runManager.SetUserInitialization(actionInitialization)
            
           UImanager = g4b.G4UImanager.GetUIpointer()
           UImanager.ApplyCommand('/run/initialize')
           UImanager.ApplyCommand('/tracking/verbose 0')

           runManager.BeamOn(int(g4_dic['BeamOn']))

           SaveJson(s_p_steps, json_s_p_steps_path)
           SaveJson(s_energy_steps, json_s_energy_steps_path)
           SaveJson(s_edep_devices, json_s_edep_devices_path)
           print('*******************************************************************************')
           print(f'{json_s_p_steps_path} has been created successfully!')
           print(f'{json_s_energy_steps_path} has been created successfully!')
           print(f'{json_s_edep_devices_path} has been created successfully!')
           print('Secondary particle distribution has been created successfully!')
           print('Energy deposition of whole detector has been created successfully!')
           print('*******************************************************************************')
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
                    self.detMaterial(g4_dic['object'][object_type][every_object])
                    self.SiCdetector(g4_dic['object'][object_type][every_object])

        self.fStepLimit = g4b.G4UserLimits(self.maxStep)
        
        for i in pixelYIndex:  
            for j in pixelZIndex:
                self.logical[f'detector_{i}_{j}'].SetUserLimits(self.fStepLimit)

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
    
    def SiCdetector(self, object):
        for i in pixelYIndex: 
            for j in pixelZIndex:
                name = f"detector_{i}_{j}"
                if i>=0:
                    y_position = (i * 5 + 2.5) * g4b.mm
                    z_position = (j * 5 + 2.5) * g4b.mm
                    translation = g4b.G4ThreeVector(-31.05 * g4b.mm, y_position, z_position)
                    visual = g4b.G4VisAttributes(g4b.G4Color(object['colour'][0], object['colour'][1], object['colour'][2]))
                    mother = self.physical['world']
                    sidex = 5 * g4b.mm
                    sidey = 0.1 * g4b.mm
                    sidez = 5 * g4b.mm

                    self.solid[name] = g4b.G4Box(name, sidex / 2., sidey / 2., sidez / 2.)

                    self.logical[name] = g4b.G4LogicalVolume(self.solid[name], self.compound, name)
                    self.physical[name] = g4b.G4PVPlacement(self.rotation, translation, name, self.logical[name], mother, False, 0, self.checkOverlaps)
                    self.logical[name].SetVisAttributes(visual)
                if i<0:
                    y_position = ((i + 1) * 5 - 2.5) * g4b.mm
                    z_position = (j * 5 + 2.5) * g4b.mm
                    translation = g4b.G4ThreeVector(-31.05 * g4b.mm, y_position, z_position)
                    visual = g4b.G4VisAttributes(g4b.G4Color(object['colour'][0], object['colour'][1], object['colour'][2]))
                    mother = self.physical['world']
                    sidex = 5 * g4b.mm
                    sidey = 0.1 * g4b.mm
                    sidez = 5 * g4b.mm

                    self.solid[name] = g4b.G4Box(name, sidex / 2., sidey / 2., sidez / 2.)

                    self.logical[name] = g4b.G4LogicalVolume(self.solid[name], self.compound, name)
                    self.physical[name] = g4b.G4PVPlacement(self.rotation, translation, name, self.logical[name], mother, False, 0, self.checkOverlaps)
                    self.logical[name].SetVisAttributes(visual)

    def detMaterial(self, object):
        material_1 = self.nist.FindOrBuildElement(object['material_1'], False)
        material_2 = self.nist.FindOrBuildElement(object['material_2'], False)
        material_density = object['density']*g4b.g/g4b.cm3
        self.compound = g4b.G4Material(object['compound_name'], material_density, 2)
        self.compound.AddElement(material_1, object['natoms_1']*g4b.perCent)
        self.compound.AddElement(material_2, object['natoms_2']*g4b.perCent)

        return self.compound
    
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

    def __init__(self, detectorConstruction, eventAction):
        super().__init__()
        self.fDetConstruction = detectorConstruction
        self.fEventAction = eventAction

    def UserSteppingAction(self, step):
        volume_pre = step.GetPreStepPoint().GetTouchable().GetVolume()
        edep = step.GetTotalEnergyDeposit()
        point_in = step.GetPreStepPoint().GetPosition()

        if volume_pre == self.fDetConstruction.physical['pipe']:
            self.fEventAction.AddPipe(edep)
        
        for i in pixelYIndex:
            for j in pixelZIndex:
                if volume_pre == self.fDetConstruction.physical[f'detector_{i}_{j}']:
                    self.fEventAction.RecordDetector(edep, point_in, i, j) 

class cflmaEventAction(g4b.G4UserEventAction):

    def BeginOfEventAction(self, event):
        self.edepSingleArea = {}
        self.p_stepSingleArea = {}
        self.edepStepSingleArea = {}
        for m in pixelYIndex:
            for n in pixelZIndex:
                self.edepSingleArea[f'{m}_{n}'] = 0
                self.p_stepSingleArea[f'{m}_{n}'] = []
                self.edepStepSingleArea[f'{m}_{n}'] = []
        self.totalSingleEdep = 0
        self.fEnergyPipe = 0       
        self.pixelIndex = []

    def EndOfEventAction(self, event):
        
        eventID = event.GetEventID()  
        for i in pixelYIndex:
            for j in pixelZIndex:
                save_geant4_events(eventID, self.edepSingleArea[f'{i}_{j}'], self.p_stepSingleArea[f'{i}_{j}'], self.edepStepSingleArea[f'{i}_{j}'], i, j)
        printModulo = g4b.G4RunManager.GetRunManager().GetPrintProgress()
        if printModulo > 0 and eventID % printModulo == 0:
            print("---> End of event:", eventID)
            print("Pipe: total energy:", g4b.G4BestUnit(self.fEnergyPipe, "Energy"))
            for i in pixelYIndex:
                for j in pixelZIndex:
                    detectorID.append([i, j])
                    singleAreaEdep.append(self.edepSingleArea[f'{i}_{j}'])
                    self.totalSingleEdep += self.edepSingleArea[f'{i}_{j}']
                    print(f"Detector_{i}_{j}: total energy:", g4b.G4BestUnit(self.edepSingleArea[f'{i}_{j}'], "Energy"))
            print('total energy deposition of detect area:', g4b.G4BestUnit(self.totalSingleEdep, "Energy"))

    def AddPipe(self, de):
        self.fEnergyPipe += de

    def RecordDetector(self, edep, point_in, i, j):
        self.edepSingleArea[f'{i}_{j}'] += edep 
        self.p_stepSingleArea[f'{i}_{j}'].append([point_in.getX()*1000,
                                              point_in.getY()*1000,
                                              point_in.getZ()*1000])
        self.edepStepSingleArea[f'{i}_{j}'].append(edep)
        
class cflmRunAction(g4b.G4UserRunAction):

    def __init__(self):
        super().__init__()

        g4b.G4RunManager.GetRunManager().SetPrintProgress(1)

        analysisManager = g4b.G4AnalysisManager.Instance()
        print("Using", analysisManager.GetType())

        analysisManager.SetVerboseLevel(1)
        
    def BeginOfRunAction(self, run):
        if self.IsMaster():
            print("Begin of run for the entire run \n")
        else:
            print("Begin of run for the local thread \n")

    def EndOfRunAction(self, run):
        if self.IsMaster():
            print("End of run for the entire run \n")
        else:
            print("End of run for the local thread \n")

        pixelAreaEdep(detectorID, singleAreaEdep)

class cflmaActionInitialization(g4b.G4VUserActionInitialization):

    def __init__(self, detConstruction, par_in, par_direct, par_type, par_energy, numofgun):
        super().__init__()
        self.fDetConstruction = detConstruction
        self.par_in = par_in
        self.par_direct = par_direct
        self.par_type=par_type
        self.par_energy=par_energy
        self.numofgun = numofgun

    def BuildForMaster(self):
        self.SetUserAction(cflmRunAction(self.PosBaseName))
    def Build(self):
        self.SetUserAction(cflmPrimaryGeneratorAction(self.par_in,
                                                      self.par_direct,
                                                      self.par_type,
                                                      self.par_energy,
                                                      self.numofgun))
        self.SetUserAction(cflmRunAction())
        eventAction = cflmaEventAction()
        self.SetUserAction(eventAction)
        self.SetUserAction(cflmaSteppingAction(self.fDetConstruction, eventAction))

def save_geant4_events(eventID,edep_device,p_step,energy_step, i, j):
    key = f'{i}_{j}'
    if(len(p_step)>0):
        s_eventIDs[key].append(eventID)
        s_edep_devices[key].append(edep_device)
        s_p_steps[key].append(p_step)
        s_energy_steps[key].append(energy_step)
    else:
        s_eventIDs[key].append(eventID)
        s_edep_devices[key].append(edep_device)
        s_p_steps[key].append([[0,0,0]])
        s_energy_steps[key].append([0]) 

def pixelAreaEdep(detectorID, singleAreaEdep): 
   
    i_value, j_value, valueEdep = array.array('d',[999.]), array.array('d',[999.]), array.array('d',[999.])
    
    file = ROOT.TFile("output/lumip3/pixelAreaEdep.root", "RECREATE")
    tree = ROOT.TTree("DetectorID", "DetectorID")

    tree.Branch("i", i_value, 'i/D')
    tree.Branch("j", j_value, 'j/D')
    tree.Branch("Edep", valueEdep, 'valueEdep/D')

    for m in range(len(detectorID)):
        
        i_value[0] = float(detectorID[m][0])
        j_value[0] = float(detectorID[m][1])
        valueEdep[0] = float(singleAreaEdep[m])
        tree.Fill()

    file.Write()
    file.Close()

def SaveJson(dic, dicFile):
    with open(dicFile, 'w') as dic_file:
        json.dump(dic, dic_file)
    print(f'{dicFile} has been created successfully!')

def main():
   
   from device import build_device as bdv
   
   geant4_json = os.getenv("RASER_SETTING_PATH")+"/g4experiment/cflm_p3.json"
   with open(geant4_json) as f:
         g4_dic = json.load(f)

   detector_json = os.getenv("RASER_SETTING_PATH")+"/detector/"
   with open(os.path.join(detector_json , g4_dic['DetModule'])) as q:
        det_dic = json.load(q)

   det_name = det_dic['det_name']
   my_d = bdv.Detector(det_name)
   
   my_g4 = cflmPixelG4Interaction(my_d, i=0, j=0)    

if __name__ == '__main__':
    main()


