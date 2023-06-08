#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from geant4_pybind import *

import math
import sys

class B2aDetectorMessenger(G4UImessenger):

    def __init__(self, detector):
        super().__init__()
        self.fDetectorConstruction = detector

        self.fB2Directory = G4UIdirectory("/B2/")
        self.fB2Directory.SetGuidance("UI commands specific to this example.")

        self.fDetDirectory = G4UIdirectory("/B2/det/")
        self.fDetDirectory.SetGuidance("Detector construction control")

        self.fChamMatCmd = G4UIcmdWithAString("/B2/det/setChamberMaterial", self)
        self.fChamMatCmd.SetGuidance("Select Material of the Chamber.")
        self.fChamMatCmd.SetParameterName("choice", False)
        self.fChamMatCmd.AvailableForStates(G4State_PreInit, G4State_Idle)

        self.fStepMaxCmd = G4UIcmdWithADoubleAndUnit("/B2/det/stepMax", self)
        self.fStepMaxCmd.SetGuidance("Define a step max")
        self.fStepMaxCmd.SetParameterName("stepMax", False)
        self.fStepMaxCmd.SetUnitCategory("Length")
        self.fStepMaxCmd.AvailableForStates(G4State_Idle)

    def SetNewValue(self, command, newValue):
        if command == self.fChamMatCmd:
            self.fDetectorConstruction.SetChamberMaterial(newValue)
        elif command == self.fStepMaxCmd:
            self.fDetectorConstruction.SetMaxStep(
                G4UIcmdWithADoubleAndUnit.GetNewDoubleValue(newValue))

class B2TrackerHit(G4VHit):

    def __init__(self, trackID, Name,chamberNb, edep, truthpos,hitpos):
        super().__init__()
        self.fTrackID = trackID
        self.fChamberNb = chamberNb
        self.fEdep = edep
        self.fTruthPos = truthpos
        self.fHitPos = hitpos
        self.fName = Name

    def Draw(self):
        vVisManager = G4VVisManager.GetConcreteInstance()
        if vVisManager != None:
            circle = G4Circle(self.fTruthPos)
            circle = G4Circle(self.fHitPos)
            circle.SetScreenSize(4)
            circle.SetFillStyle(G4Circle.filled)
            colour = G4Colour(1, 0, 0)
            attribs = G4VisAttributes(colour)
            circle.SetVisAttributes(attribs)
            vVisManager.Draw(circle)

    def Print(self):
        print("trackID:", self.fTrackID,"Name:",self.fName, self.fChamberNb, "Edep:", end=" ")
        print(G4BestUnit(self.fEdep, "Energy"), "TruthPosition:", G4BestUnit(self.fTruthPos, "Length"),
              "HitPosition:", G4BestUnit(self.fHitPos, "Length"))

class B2HitsCollection(G4VHitsCollection):

    def __init__(self, detName, colNam):
        super().__init__(detName, colNam)
        self.collection = []

    def __getitem__(self, i):
        return self.collection[i]

    def insert(self, item):
        self.collection.append(item)

    def GetHit(self, i):
        return self.collection[i]

    def GetSize(self):
        return len(self.collection)


class B2TrackerSD(G4VSensitiveDetector):

    def __init__(self, name, hitsCollectionName):
        
        super().__init__(name)
        self.collectionName.insert(hitsCollectionName)
        print("Jiaqi_B2TrackerSD_init()")

    def Initialize(self, hce):
        # Create hits collection
        #self.fHitsCollection = None
        print("Jiaqi_B2TrackerSD.Initialize()")
        self.fHitsCollection = B2HitsCollection(
            self.SensitiveDetectorName, self.collectionName[0])

        # Add this collection in hce
        hcID = G4SDManager.GetSDMpointer().GetCollectionID(self.collectionName[0])
        hce.AddHitsCollection(hcID, self.fHitsCollection)

    def ProcessHits(self, aStep, rOhist):
        # energy deposit
        edep = aStep.GetTotalEnergyDeposit()
        print("Jiaqi_B2TrackerSD.ProcessHits()1=",
              "TrackID:",aStep.GetTrack().GetTrackID(),
              "Name:",aStep.GetPreStepPoint().GetTouchable().GetVolume().GetLogicalVolume().GetName(),
               aStep.GetPreStepPoint().GetTouchable().GetCopyNumber(),
              "Edep:",edep,
              "TruthPosition",aStep.GetPreStepPoint().GetPosition(),
              "HitPosition:",aStep.GetPostStepPoint().GetPosition())
        
        if edep == 0:
            return False

        newHit = B2TrackerHit(aStep.GetTrack().GetTrackID(),
                              aStep.GetPreStepPoint().GetTouchable().GetVolume().GetLogicalVolume().GetName(),
                              aStep.GetPreStepPoint().GetTouchable().GetCopyNumber(),
                              edep,
                              aStep.GetPreStepPoint().GetPosition(),
                              aStep.GetPostStepPoint().GetPosition())
        

        self.fHitsCollection.insert(newHit)
        # newHit.Print()
        return True

    def EndOfEvent(self, hce):
        print("Jiaqi_B2TrackerSD.EndOfEvent")
        if self.verboseLevel > 1:
            nofHits = self.fHitsCollection.GetSize()
            print("-------->Hits Collection: in this event there are", nofHits,
                  "hits in the tracker chambers:")
            for i in range(nofHits):
                self.fHitsCollection[i].Print()


class B2aDetectorConstruction(G4VUserDetectorConstruction):

    def __init__(self):
        super().__init__()
        self.fMessenger = B2aDetectorMessenger(self)
        self.fScoringVolume = None

        self.fNbOfChambers = 3
        self.fLogicChamber = []
        self.fCheckOverlaps = True

    def DefineMaterials(self):
        nistManager = G4NistManager.Instance()

        # Air defined using NIST Manager
        nistManager.FindOrBuildMaterial("G4_AIR")

        # Xenon gas defined using NIST Manager
        self.fChamberMaterial = nistManager.FindOrBuildMaterial("G4_Si")

        # Print materials
        print(G4Material.GetMaterialTable())

    def DefineVolumes(self):
        air = G4Material.GetMaterial("G4_AIR")

        # Sizes of the principal geometrical components (solids)

        chamberSpacing = 100*um  # from chamber center to center!

        chamberWidth = 100*um  # width of the chambers
        trackerLength = (self.fNbOfChambers+1)*chamberSpacing

        worldLength = 1.2*trackerLength
        trackerSize = 0.5*trackerLength   # Half length of the Tracker

        # Definitions of Solids, Logical Volumes, Physical Volumes  World
        G4GeometryManager.GetInstance().SetWorldMaximumExtent(worldLength)

        print("Computed tolerance =",
              G4GeometryTolerance.GetInstance().GetSurfaceTolerance()/um, "um")

        worldS = G4Box("world",                                      # its name
                       worldLength/2, worldLength/2, worldLength/2)  # its size

        worldLV = G4LogicalVolume(
            worldS,    # its solid
            air,       # its material
            "World")   # its name

        # Must place the World Physical volume unrotated at (0,0,0).
        worldPV = G4PVPlacement(
            None,                  # no rotation
            G4ThreeVector(),       # at (0,0,0)
            worldLV,               # its logical volume
            "World",               # its name
            None,                  # its mother  volume
            False,                 # no boolean operations
            0,                     # copy number
            self.fCheckOverlaps)   # checking overlaps
        
        # Tracker
        positionTracker = G4ThreeVector(0, 0, 0)
        trackerS = G4Box("tracker", trackerSize, trackerSize, trackerSize)

        trackerLV = G4LogicalVolume(trackerS, air, "Tracker", None, None, None)

        G4PVPlacement(None,                 # no rotation
                      positionTracker,      # at (x,y,z)
                      trackerLV,            # its logical volume
                      "Tracker",            # its name
                      worldLV,              # its mother  volume
                      False,                # no boolean operations
                      0,                    # copy number
                      self.fCheckOverlaps)  # checking overlaps
        
        # Visualization attributes
        boxVisAtt = G4VisAttributes(G4Colour(1, 1, 1))
        chamberVisAtt = G4VisAttributes(G4Colour(1, 1, 0))

        worldLV.SetVisAttributes(boxVisAtt)
        trackerLV.SetVisAttributes(boxVisAtt)
          
        self.fScoringVolume = trackerLV

          # Tracker segments
        print("There are", self.fNbOfChambers, "chambers in the tracker region.")
        print("The chambers are", chamberWidth/um, "um of", self.fChamberMaterial.GetName())
        print("The distance between chamber is", chamberSpacing/um,  "um")

        firstPosition = -trackerSize + chamberSpacing
        firstLength = trackerLength/10
        lastLength = trackerLength

        
        if self.fNbOfChambers > 0:
            
            if chamberSpacing < chamberWidth:
                G4Exception("B2aDetectorConstruction::DefineVolumes()",
                            "InvalidSetup", G4ExceptionSeverity.FatalException, "Width>Spacing")
                
        for copyNo in range(self.fNbOfChambers):
            Zposition = firstPosition + copyNo * chamberSpacing

            chamberS = G4Box("Chamber_solid", 60*um, 100*um, 5*um)

            self.fLogicChamber += [G4LogicalVolume(chamberS,
                                                   self.fChamberMaterial, "Chamber_LV", None, None, None)]

            self.fLogicChamber[copyNo].SetVisAttributes(chamberVisAtt)

            G4PVPlacement(None,                            # no rotation
                          G4ThreeVector(0, 0, Zposition),  # at (x,y,z)
                          self.fLogicChamber[copyNo],      # its logical volume
                          "Chamber_PV",                    # its name
                          trackerLV,                       # its mother  volume
                          False,                           # no boolean operations
                          copyNo,                          # copy number
                          self.fCheckOverlaps)             # checking overlaps

        # Example of User Limits
        # Below is an example of how to set tracking constraints in a given
        # logical volume
        # Sets a max step length in the tracker region, with G4StepLimiter

        maxStep = 0.5*chamberWidth
        self.fStepLimit = G4UserLimits(maxStep)
        trackerLV.SetUserLimits(self.fStepLimit)


        # always return the physical World
        return worldPV

    def Construct(self):
        self.DefineMaterials()
        return self.DefineVolumes()

    def ConstructSDandField(self):
        # Sensitive detectors
        trackerChamberSDname = "B2/TrackerChamberSD"
        self.aTrackerSD = B2TrackerSD(trackerChamberSDname, "TrackerHitsCollection")
        G4SDManager.GetSDMpointer().AddNewDetector(self.aTrackerSD)
        # Setting aTrackerSD to all logical volumes with the same name
        # of "Chamber_LV".
        self.SetSensitiveDetector("Chamber_LV", self.aTrackerSD, True)

    def GetChamber0(self):
       return self.fLogicChamber[0]
    
    def GetChamber1(self):
       return self.fLogicChamber[1]
    
    def GetChamber2(self):
       return self.fLogicChamber[2]


    def SetChamberMaterial(self, materialName):
        nistManager = G4NistManager.Instance()
        pttoMaterial = nistManager.FindOrBuildMaterial(materialName)
        if self.fChamberMaterial != pttoMaterial:
            if pttoMaterial != None:
                self.fChamberMaterial = pttoMaterial
                for copyNo in range(self.fNbOfChambers):
                    if self.fLogicChamber[copyNo] != None:
                        self.fLogicChamber[copyNo].SetMaterial(self.fChamberMaterial)
                print("\n----> The chambers are made of", materialName)
            else:
                print("\n-->  WARNING from SetChamberMaterial :", materialName, "not found")

    def SetMaxStep(self, maxStep):
        if self.fStepLimit != None and maxStep > 0:
            self.fStepLimit.SetMaxAllowedStep(maxStep)

    def SetCheckOverlaps(self, checkOverlaps):
        self.fCheckOverlaps = checkOverlaps


class B2RunAction(G4UserRunAction):

    def __init__(self):
        super().__init__()
        G4RunManager.GetRunManager().SetPrintProgress(1000)

    def BeginOfRunAction(self, aRun):
        # inform the runManager to save random number seed
        G4RunManager.GetRunManager().SetRandomNumberStore(False)


class B2PrimaryGeneratorAction(G4VUserPrimaryGeneratorAction):

    def __init__(self):
        super().__init__()
        nofParticles = 1
        self.fParticleGun = G4ParticleGun(nofParticles)

        # default particle kinematic
        particleDefinition = G4ParticleTable.GetParticleTable().FindParticle("pi+")
        self.fParticleGun.SetParticleDefinition(particleDefinition)
        self.fParticleGun.SetParticleMomentumDirection(G4ThreeVector(0, 0, 1))
        self.fParticleGun.SetParticleEnergy(120*GeV)

    def GeneratePrimaries(self, anEvent):
        # This function is called at the begining of event

        # In order to avoid dependence of PrimaryGeneratorAction
        # on DetectorConstruction class we get world volume
        # from G4LogicalVolumeStore.
        worldZHalfLength = 0
        worldLV = G4LogicalVolumeStore.GetInstance().GetVolume("World")
        worldBox = None
        if worldLV != None:
            worldBox = worldLV.GetSolid()

        if worldBox != None:
            worldZHalfLength = worldBox.GetZHalfLength()
        else:
            print("World volume of box not found.", file=sys.stderr)
            print("Perhaps you have changed geometry.", file=sys.stderr)
            print("The gun will be place in the center.", file=sys.stderr)

        # Note that this particular case of starting a primary particle on the world boundary
        # requires shooting in a direction towards inside the world.
        self.fParticleGun.SetParticlePosition(G4ThreeVector(0, 0, -worldZHalfLength))
        self.fParticleGun.GeneratePrimaryVertex(anEvent)


class B2EventAction(G4UserEventAction):
    def EndOfEventAction(self, event):
        # get number of stored trajectories
        trajectoryContainer = event.GetTrajectoryContainer()
        n_trajectories = 0
        if trajectoryContainer != None:
            n_trajectories = trajectoryContainer.entries()

        # periodic printing
        eventID = event.GetEventID()
        if eventID < 100 or eventID % 100 == 0:
            print(">>> Event:", eventID)
            if trajectoryContainer != None:
                print("   ", n_trajectories, "trajectories stored in this event.")

            hc = event.GetHCofThisEvent().GetHC(0)
            print("   ", hc.GetSize(), "hits stored in this event")
            
class B2SteppingAction(G4UserSteppingAction):
    
    def __init__(self):
        super().__init__()
        self.fScoringVolume = None
        self.hitpos0 = None
        self.hitpos1 = None
        self.hitpos2 = None
    def UserSteppingAction(self, aStep):
        #print("Jiaqi_UserSteppingAction() =",aStep.GetPreStepPoint().GetTouchable().GetVolume().GetLogicalVolume().GetName())
        detectorConstruction = G4RunManager.GetRunManager().GetUserDetectorConstruction()
        if self.fScoringVolume == None:
            self.fScoringVolume = detectorConstruction.fScoringVolume
            chamber0 = 0
            chamber1 = 0
            chamber2 = 0

        if detectorConstruction:
             chamber0 = detectorConstruction.GetChamber0()
             chamber1 = detectorConstruction.GetChamber1()
             chamber2 = detectorConstruction.GetChamber2()
        if aStep.GetTrack().GetTrackID() == 1:
           PreStepVolume = aStep.GetPreStepPoint().GetTouchable().GetVolume().GetLogicalVolume()

           if PreStepVolume == self.fScoringVolume:
               PostStepVolume = aStep.GetPostStepPoint().GetTouchable().GetVolume().GetLogicalVolume()
               if PostStepVolume == chamber0:
                 self.hitpos0 = aStep.GetPostStepPoint().GetPosition()
                 return self.hitpos0
               
               if PostStepVolume == chamber1:
                 self.hitpos1 = aStep.GetPostStepPoint().GetPosition()
                 return self.hitpos1

               if PostStepVolume == chamber2:
                self.hitpos2 = aStep.GetPostStepPoint().GetPosition()
                return self.hitpos2
        if  self.hitpos0 != None and self.hitpos1 != None and self.hitpos2 != None:
             print("hitpos0:",G4BestUnit(self.hitpos0,"Length"),
                   "hitpos1:",G4BestUnit(self.hitpos1,"Length"),
                   "hitpos2:",G4BestUnit(self.hitpos2,"Length"),
                   "位置分辨:",G4BestUnit((self.hitpos0 + self.hitpos2)/2 - self.hitpos1,"Length"))
             return
        edepStep = aStep.GetTotalEnergyDeposit()

       

        


class B2ActionInitialization(G4VUserActionInitialization):

    def BuildForMaster(self):
        self.SetUserAction(B2RunAction())

    def Build(self):
        self.SetUserAction(B2PrimaryGeneratorAction())
        self.SetUserAction(B2RunAction())
        self.SetUserAction(B2EventAction())
        self.SetUserAction(B2SteppingAction())

# Detect interactive mode (if no arguments) and define UI session
ui = None
if len(sys.argv) == 1:
    ui = G4UIExecutive(len(sys.argv), sys.argv)

# Optionally: choose a different Random engine...
# G4Random.setTheEngine(MTwistEngine())

# Construct the default run manager
runManager = G4RunManagerFactory.CreateRunManager(G4RunManagerType.Serial)

# Set mandatory initialization classes
runManager.SetUserInitialization(B2aDetectorConstruction())

physicsList = FTFP_BERT()
physicsList.RegisterPhysics(G4StepLimiterPhysics())
runManager.SetUserInitialization(physicsList)

# Set user action classes
runManager.SetUserInitialization(B2ActionInitialization())

# Initialize visualization
visManager = G4VisExecutive()
# G4VisExecutive can take a verbosity argument - see /vis/verbose guidance.
# visManager = G4VisExecutive("Quiet");
visManager.Initialize()

# Get the pointer to the User Interface manager
UImanager = G4UImanager.GetUIpointer()

# Process macro or start UI session
if ui == None:
    # batch mode
    command = "/control/execute ./cfg/ "
    fileName = sys.argv[1]
    UImanager.ApplyCommand(command+fileName)
else:
    # interactive mode
    UImanager.ApplyCommand("/control/execute ./cfg/init_vistelescope.mac")
    if ui.IsGUI():
        UImanager.ApplyCommand("/control/execute ./cfg/gui.mac")
    ui.SessionStart()
