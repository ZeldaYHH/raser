#!/usr/bin/env python3 
import geant4_pybind as g4b
import sys
import os

# Choose specific analysis manager
G4AnalysisManager = g4b.G4RootAnalysisManager


class B4DetectorConstruction(g4b.G4VUserDetectorConstruction):

    def __init__(self):
        super().__init__()
        self.fCheckOverlaps = True

    def DefineMaterials(self):
        # Lead material defined using NIST Manager
        nistManager = g4b.G4NistManager.Instance()
        nistManager.FindOrBuildMaterial("G4_Cu")

        g4b.G4Material("silicon", z=14, a=28.08*g4b.g/g4b.mole, density=2.330*g4b.g/g4b.cm3)

        # Vacuum
        g4b.G4Material("Galactic", z=1, a=1.01*g4b.g/g4b.mole, density=g4b.universe_mean_density,
                   state=g4b.kStateGas, temp=2.73*g4b.kelvin, pressure=3e-18*g4b.pascal)

        # Print materials
        print(g4b.G4Material.GetMaterialTable())

    def DefineVolumes(self):
        # Geometry parameters
        nofLayers = 1
        pipeThickness = 2*g4b.mm
        detectorThickness = 0.5*g4b.mm
        calorSizeXY = 1000*g4b.mm

        layerThickness = pipeThickness + detectorThickness
        calorThickness = nofLayers * layerThickness
        worldSizeXY = 1.2 * calorSizeXY
        worldSizeZ = 1.2 * calorThickness

        # Get materials
        defaultMaterial = g4b.G4Material.GetMaterial("Galactic")
        pipeMaterial = g4b.G4Material.GetMaterial("G4_Cu")
        detectorMaterial = g4b.G4Material.GetMaterial("silicon")

        if defaultMaterial == None or pipeMaterial == None or detectorMaterial == None:
            msg = "Cannot retrieve materials already defined."
            g4b.G4Exception("B4DetectorConstruction::DefineVolumes()",
                        "MyCode0001", FatalException, msg)

        # World
        worldS = g4b.G4Box("World",                                     # its name
                       worldSizeXY/2, worldSizeXY/2, worldSizeZ/2)  # its size

        worldLV = g4b.G4LogicalVolume(worldS,           # its solid
                                  defaultMaterial,  # its material
                                  "World")          # its name

        worldPV = g4b.G4PVPlacement(None,                 # no rotation
                                g4b.G4ThreeVector(),      # at (0,0,0)
                                worldLV,              # its logical volume
                                "World",              # its name
                                None,                 # its mother  volume
                                False,                # no boolean operation
                                0,                    # copy number
                                self.fCheckOverlaps)  # checking overlaps

        # Calorimeter
        calorimeterS = g4b.G4Box("Calorimeter",                                   # its name
                             calorSizeXY/2, calorSizeXY/2, calorThickness/2)  # its size

        calorLV = g4b.G4LogicalVolume(calorimeterS,     # its solid
                                  defaultMaterial,  # its material
                                  "Calorimeter")    # its name

        g4b.G4PVPlacement(None,                 # no rotation
                      g4b.G4ThreeVector(),      # at (0,0,0)
                      calorLV,              # its logical volume
                      "Calorimeter",        # its name
                      worldLV,              # its mother  volume
                      False,                # no boolean operation
                      0,                    # copy number
                      self.fCheckOverlaps)  # checking overlaps

        # Layer
        layerS = g4b.G4Box("Layer",                                         # its name
                       calorSizeXY/2, calorSizeXY/2, layerThickness/2)  # its size

        layerLV = g4b.G4LogicalVolume(layerS,           # its solid
                                  defaultMaterial,  # its material
                                  "Layer")          # its name

        g4b.G4PVReplica("Layer",         # its name
                    layerLV,         # its logical volume
                    calorLV,         # its mother
                    g4b.kZAxis,          # axis of replication
                    nofLayers,       # number of replica
                    layerThickness)  # width of replica

        # Pipe
        pipeS = g4b.G4Box("Pipe",                                         # its name
                          calorSizeXY/2, calorSizeXY/2, pipeThickness/2)  # its size

        pipeLV = g4b.G4LogicalVolume(pipeS,         # its solid
                                     pipeMaterial,  # its material
                                     "Pipe")            # its name

        self.fpipePV = g4b.G4PVPlacement(None,                                  # no rotation
                                         g4b.G4ThreeVector(0, 0, -detectorThickness/2),  # its position
                                         pipeLV,                            # its logical volume
                                         "Pipe",                                # its name
                                         layerLV,                               # its mother  volume
                                         False,                                 # no boolean operation
                                         0,                                     # copy number
                                         self.fCheckOverlaps)                   # checking overlaps

        # detector
        detectorS = g4b.G4Box("Detector",                                         # its name
                     10*g4b.cm, 2.5*g4b.cm, detectorThickness/2)  # its size

        detectorLV = g4b.G4LogicalVolume(detectorS,         # its solid
                                detectorMaterial,  # its material
                                "Detector")        # its name

        self.fdetectorPV = g4b.G4PVPlacement(None,                                  # no rotation
                                    g4b.G4ThreeVector(0, 0, pipeThickness/2),  # its position
                                    detectorLV,                                 # its logical volume
                                    "Detector",                                 # its name
                                    layerLV,                               # its mother volume
                                    False,                                 # no boolean operation
                                    0,                                     # copy number
                                    self.fCheckOverlaps)                   # checking overlaps

        # print parameters
        print("")
        print("------------------------------------------------------------")
        print("---> The calorimeter is", nofLayers, "layers of: [", end="")
        print(pipeThickness/g4b.mm, "mm of",  pipeMaterial.GetName(), "+", end="")
        print(detectorThickness/g4b.mm, "mm of", detectorMaterial.GetName(), "]")
        print("------------------------------------------------------------")

        # Visualization attributes
        worldLV.SetVisAttributes(g4b.G4VisAttributes.GetInvisible())

        simpleBoxVisAtt = g4b.G4VisAttributes(g4b.G4Colour(1, 1, 1))
        simpleBoxVisAtt.SetVisibility(True)
        calorLV.SetVisAttributes(simpleBoxVisAtt)

        # Always return the physical World
        return worldPV

    def Construct(self):
        self.DefineMaterials()
        return self.DefineVolumes()

    def ConstructSDandField(self):
        # Create global magnetic field messenger.
        # Uniform magnetic field is then created automatically if
        # the field value is not zero.
        fieldValue = g4b.G4ThreeVector()
        self.fMagFieldMessenger = g4b.G4GlobalMagFieldMessenger(fieldValue)
        self.fMagFieldMessenger.SetVerboseLevel(1)


class B4PrimaryGeneratorAction(g4b.G4VUserPrimaryGeneratorAction):

    def __init__(self):
        super().__init__()
        nofParticles = 1
        self.fParticleGun = g4b.G4ParticleGun(nofParticles)

        # default particle kinematic
        particleDefinition = g4b.G4ParticleTable.GetParticleTable().FindParticle("e-")
        self.fParticleGun.SetParticleDefinition(particleDefinition)
        self.fParticleGun.SetParticleMomentumDirection(g4b.G4ThreeVector(0, 10, 1))
        self.fParticleGun.SetParticleEnergy(24*g4b.GeV)

    def GeneratePrimaries(self, anEvent):
        # This function is called at the begining of an event

        # In order to avoid dependence of PrimaryGeneratorAction
        # on DetectorConstruction class we get world volume
        # from G4LogicalVolumeStore
        worldZHalfLength = 0
        worldLV = g4b.G4LogicalVolumeStore.GetInstance().GetVolume("World")

        # Check that the world volume has box shape
        worldBox = None
        if worldLV != None:
            worldBox = worldLV.GetSolid()

        if worldBox != None:
            worldZHalfLength = worldBox.GetZHalfLength()
        else:
            msg = "World volume of box shape not found."
            msg += "Perhaps you have changed geometry."
            msg += "The gun will be place in the center."
            g4b.G4Exception("B4PrimaryGeneratorAction::GeneratePrimaries()",
                        "MyCode0002", JustWarning, msg)

        # Set gun position
        self.fParticleGun.SetParticlePosition(g4b.G4ThreeVector(0, 0, -worldZHalfLength))
        self.fParticleGun.GeneratePrimaryVertex(anEvent)


class B4aEventAction(g4b.G4UserEventAction):

    def BeginOfEventAction(self, event):
        # initialisation per event
        self.fEnergyPipe = 0
        self.fEnergyDetector = 0
        self.fTrackLPipe = 0
        self.fTrackLDetector = 0

    def EndOfEventAction(self, event):
        # Accumulate statistics

        # get analysis manager
        analysisManager = g4b.G4AnalysisManager.Instance()

        # fill histograms
        analysisManager.FillH1(0, self.fEnergyPipe)
        analysisManager.FillH1(1, self.fEnergyDetector)
        analysisManager.FillH1(2, self.fTrackLPipe)
        analysisManager.FillH1(3, self.fTrackLDetector)

        # fill ntuple
        analysisManager.FillNtupleDColumn(0, self.fEnergyPipe)
        analysisManager.FillNtupleDColumn(1, self.fEnergyDetector)
        analysisManager.FillNtupleDColumn(2, self.fTrackLPipe)
        analysisManager.FillNtupleDColumn(3, self.fTrackLDetector)
        analysisManager.AddNtupleRow()

        # Print per event (modulo n)
        eventID = event.GetEventID()
        printModulo = g4b.G4RunManager.GetRunManager().GetPrintProgress()
        if printModulo > 0 and eventID % printModulo == 0:
            print("---> End of event:", eventID)
            print("Pipe: total energy:", g4b.G4BestUnit(self.fEnergyPipe, "Energy"), end="")
            print("total track length:", g4b.G4BestUnit(self.fTrackLPipe, "Length"))
            print("Detector: total energy:", g4b.G4BestUnit(self.fEnergyDetector, "Energy"), end="")
            print("total track length:", g4b.G4BestUnit(self.fTrackLDetector, "Length"))

    def AddPipe(self, de,  dl):
        self.fEnergyPipe += de
        self.fTrackLPipe += dl

    def AddDetector(self, de, dl):
        self.fEnergyDetector += de
        self.fTrackLDetector += dl


class B4aSteppingAction(g4b.G4UserSteppingAction):

    def __init__(self, detectorConstruction, eventAction):
        super().__init__()
        self.fDetConstruction = detectorConstruction
        self.fEventAction = eventAction

    def UserSteppingAction(self, step):
        # Collect energy and track length step by step

        # get volume of the current step
        volume = step.GetPreStepPoint().GetTouchable().GetVolume()

        # energy deposit
        edep = step.GetTotalEnergyDeposit()

        # step length
        stepLength = 0
        if step.GetTrack().GetDefinition().GetPDGCharge() != 0:
            stepLength = step.GetStepLength()

        if volume == self.fDetConstruction.fpipePV:
            self.fEventAction.AddPipe(edep, stepLength)

        if volume == self.fDetConstruction.fdetectorPV:
            self.fEventAction.AddDetector(edep, stepLength)


class B4RunAction(g4b.G4UserRunAction):

    def __init__(self):
        super().__init__()

        # set printing event number per each event
        g4b.G4RunManager.GetRunManager().SetPrintProgress(1)

        # Create analysis manager
        analysisManager = g4b.G4AnalysisManager.Instance()
        print("Using", analysisManager.GetType())

        # Create directories
        # analysisManager.SetHistoDirectoryName("histograms")
        # analysisManager.SetNtupleDirectoryName("ntuple")
        analysisManager.SetVerboseLevel(1)
        analysisManager.SetNtupleMerging(True)
        # Note: merging ntuples is available only with Root output

        # Book histograms, ntuple
        # Creating histograms
        analysisManager.CreateH1("Epipe", "Edep in pipe", 100, 0, 1000*g4b.MeV)
        analysisManager.CreateH1("Edetector", "Edep in detector", 100, 0, 100*g4b.MeV)

        # Creating ntuple
        analysisManager.CreateNtuple("FLM", "Edep")
        analysisManager.CreateNtupleDColumn("Epipe")
        analysisManager.CreateNtupleDColumn("Edetector")
        analysisManager.FinishNtuple()

    def BeginOfRunAction(self, run):
        # inform the runManager to save random number seed
        # G4RunManager.GetRunManager().SetRandomNumberStore(True)

        # Get analysis manager
        analysisManager = g4b.G4AnalysisManager.Instance()

        # Open an output file
        try:
            os.mkdir('output/FLM')
        except:
            print('path already exist')

        fileName = "output/FLM/energy_deposition.root"
        analysisManager.OpenFile(fileName)

    def EndOfRunAction(self, run):

        # print histogram statistics
        analysisManager = g4b.G4AnalysisManager.Instance()
        if analysisManager.GetH1(1) != None:
            print("\n ----> print histograms statistic ", end="")

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


class B4aActionInitialization(g4b.G4VUserActionInitialization):

    def __init__(self, detConstruction):
        super().__init__()
        self.fDetConstruction = detConstruction

    def BuildForMaster(self):
        self.SetUserAction(B4RunAction())

    def Build(self):
        self.SetUserAction(B4PrimaryGeneratorAction())
        self.SetUserAction(B4RunAction())
        eventAction = B4aEventAction()
        self.SetUserAction(eventAction)
        self.SetUserAction(B4aSteppingAction(self.fDetConstruction, eventAction))


def PrintUsage():
    print(" Usage: ", file=sys.stderr)
    print(" python exampleB4a.py [-m macro ] [-u UIsession] [-t nThreads]", file=sys.stderr)
    print("   note: -t option is available only for multi-threaded mode.", file=sys.stderr)

def main():

    # Construct the default run manager
    runManager = g4b.G4RunManagerFactory.CreateRunManager(g4b.G4RunManagerType.Serial)

    # Set mandatory initialization classes
    detConstruction = B4DetectorConstruction()
    runManager.SetUserInitialization(detConstruction)

    physicsList = g4b.FTFP_BERT()
    runManager.SetUserInitialization(physicsList)

    actionInitialization = B4aActionInitialization(detConstruction)
    runManager.SetUserInitialization(actionInitialization)

    # Initialize visualization
    visManager = g4b.G4VisExecutive()
    # G4VisExecutive can take a verbosity argument - see /vis/verbose guidance.
    # visManager = G4VisExecutive("Quiet")
    visManager.Initialize()

    # Get the User Interface manager
    UImanager = g4b.G4UImanager.GetUIpointer()

    UImanager.ApplyCommand("/control/execute cfg/init_vis.mac")

    UImanager.ApplyCommand('/run/initialize')
    UImanager.ApplyCommand('/tracking/verbose 2')
    UImanager.ApplyCommand('/run/beamOn 1')
    UImanager.ApplyCommand('/vis/ogl/set/printSize 2000 2000')

    UImanager.ApplyCommand('/vis/ogl/export output/FLM/image.pdf')

if __name__ == '__main__':
    main()
