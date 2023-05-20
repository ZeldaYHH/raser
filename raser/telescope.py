#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from geant4_pybind import *

import math
import sys


class B1DetectorConstruction(G4VUserDetectorConstruction):

    def __init__(self):
        super().__init__()
        self.fScoringVolume = None

    def Construct(self):
        nist = G4NistManager.Instance()
        env_sizeXY = 35*cm
        env_sizeZ = 35*cm
        env_mat = nist.FindOrBuildMaterial("G4_AIR")

        # Option to switch on/off checking of volumes overlaps
        checkOverlaps = True

        # World
        world_sizeXY = 1.2*env_sizeXY
        world_sizeZ = 1.2*env_sizeZ
        world_mat = nist.FindOrBuildMaterial("G4_AIR")

        solidWorld = G4Box("World", 0.5*world_sizeXY, 0.5 *
                           world_sizeXY, 0.5*world_sizeZ)

        logicWorld = G4LogicalVolume(solidWorld, world_mat, "World")

        physWorld = G4PVPlacement(None,              # no rotation
                                  G4ThreeVector(),   # at (0,0,0)
                                  logicWorld,        # its logical volume
                                  "World",           # its name
                                  None,              # its mother  volume
                                  False,             # no boolean operation
                                  0,                 # copy number
                                  checkOverlaps)     # overlaps checking

        # Envelope
        solidEnv = G4Box("Envelope", 0.5*env_sizeXY,
                         0.5*env_sizeXY, 0.5*env_sizeZ)

        logicEnv = G4LogicalVolume(solidEnv,    # its solid
                                   env_mat,     # its material
                                   "Envelope")  # its name

        G4PVPlacement(None,              # no rotation
                      G4ThreeVector(),   # at (0,0,0)
                      logicEnv,          # its logical volume
                      "Envelope",        # its name
                      logicWorld,        # its mother  volume
                      True,              # no boolean operation
                      0,                 # copy number
                      checkOverlaps)     # overlaps checking

        # Shape
        shape1_mat = nist.FindOrBuildMaterial("G4_Si")
        pos1 = G4ThreeVector(-2*cm, 2*cm, 2*cm)

        # Conical section shape
        shape1_dxa = 6*cm
        shape1_dxb = 6*cm
        shape1_dya = 10*cm
        shape1_dyb = 10*cm
        shape1_dz = 0.5*cm
        solidShape1 = G4Trd("Shape1",  # its name
                            0.5*shape1_dxa, 0.5*shape1_dxb,
                            0.5*shape1_dya, 0.5*shape1_dyb, 0.5*shape1_dz)  # its size

        logicShape1 = G4LogicalVolume(solidShape1,  # its solid
                                      shape1_mat,   # its material
                                      "Shape1")     # its name

        G4PVPlacement(None,           # no rotation
                      pos1,           # at position
                      logicShape1,    # its logical volume
                      "Shape1",       # its name
                      logicEnv,       # its mother  volume
                      False,          # no boolean operation
                      0,              # copy number
                      checkOverlaps)  # overlaps checking

        # Shape 2
        shape2_mat = nist.FindOrBuildMaterial("G4_Si")
        pos2 = G4ThreeVector(-2*cm, 2*cm, 4*cm)

        # Trapezoid shape
        shape2_dxa = 6*cm
        shape2_dxb = 6*cm
        shape2_dya = 10*cm
        shape2_dyb = 10*cm
        shape2_dz = 0.5*cm
        solidShape2 = G4Trd("Shape2",  # its name
                            0.5*shape2_dxa, 0.5*shape2_dxb,
                            0.5*shape2_dya, 0.5*shape2_dyb, 0.5*shape2_dz)  # its size

        logicShape2 = G4LogicalVolume(solidShape2,  # its solid
                                      shape2_mat,   # its material
                                      "Shape2")     # its name

        G4PVPlacement(None,            # no rotation
                      pos2,            # at position
                      logicShape2,     # its logical volume
                      "Shape2",        # its name
                      logicEnv,        # its mother  volume
                      False,           # no boolean operation
                      0,               # copy number
                      checkOverlaps)   # overlaps checking
        
         # Shape 3
        shape3_mat = nist.FindOrBuildMaterial("G4_Si")
        pos3 = G4ThreeVector(-2*cm, 2*cm, 6*cm)

        # Trapezoid shape
        shape3_dxa = 6*cm
        shape3_dxb = 6*cm
        shape3_dya = 10*cm
        shape3_dyb = 10*cm
        shape3_dz = 0.5*cm
        solidShape3 = G4Trd("Shape3",  # its name
                            0.5*shape3_dxa, 0.5*shape3_dxb,
                            0.5*shape3_dya, 0.5*shape3_dyb, 0.5*shape3_dz)  # its size

        logicShape3 = G4LogicalVolume(solidShape3,  # its solid
                                      shape3_mat,   # its material
                                      "Shape3")     # its name

        G4PVPlacement(None,            # no rotation
                      pos3,            # at position
                      logicShape3,     # its logical volume
                      "Shape3",        # its name
                      logicEnv,        # its mother  volume
                      False,           # no boolean operation
                      0,               # copy number
                      checkOverlaps)   # overlaps checking
        
          # Shape 4
        shape4_mat = nist.FindOrBuildMaterial("G4_Si")
        pos4 = G4ThreeVector(-2*cm, 2*cm, 8*cm)

        # Trapezoid shape
        shape4_dxa = 6*cm
        shape4_dxb = 6*cm
        shape4_dya = 10*cm
        shape4_dyb = 10*cm
        shape4_dz = 0.5*cm
        solidShape4 = G4Trd("Shape4",  # its name
                            0.5*shape4_dxa, 0.5*shape4_dxb,
                            0.5*shape4_dya, 0.5*shape4_dyb, 0.5*shape4_dz)  # its size

        logicShape4 = G4LogicalVolume(solidShape4,  # its solid
                                      shape4_mat,   # its material
                                      "Shape4")     # its name

        G4PVPlacement(None,            # no rotation
                      pos4,            # at position
                      logicShape4,     # its logical volume
                      "Shape4",        # its name
                      logicEnv,        # its mother  volume
                      False,           # no boolean operation
                      0,               # copy number
                      checkOverlaps)   # overlaps checking
        
        # Shape 5
        shape5_mat = nist.FindOrBuildMaterial("G4_Si")
        pos5 = G4ThreeVector(-2*cm, 2*cm, 10*cm)

        # Trapezoid shape
        shape5_dxa = 6*cm
        shape5_dxb = 6*cm
        shape5_dya = 10*cm
        shape5_dyb = 10*cm
        shape5_dz = 0.5*cm
        solidShape5 = G4Trd("Shape5",  # its name
                            0.5*shape5_dxa, 0.5*shape5_dxb,
                            0.5*shape5_dya, 0.5*shape5_dyb, 0.5*shape5_dz)  # its size

        logicShape5 = G4LogicalVolume(solidShape5,  # its solid
                                      shape5_mat,   # its material
                                      "Shape5")     # its name

        G4PVPlacement(None,            # no rotation
                      pos5,            # at position
                      logicShape5,     # its logical volume
                      "Shape5",        # its name
                      logicEnv,        # its mother  volume
                      False,           # no boolean operation
                      0,               # copy number
                      checkOverlaps)   # overlaps checking

        # Shape 6
        shape6_mat = nist.FindOrBuildMaterial("G4_Si")
        pos6 = G4ThreeVector(-2*cm, 2*cm, 12*cm)

        # Trapezoid shape
        shape6_dxa = 6*cm
        shape6_dxb = 6*cm
        shape6_dya = 10*cm
        shape6_dyb = 10*cm
        shape6_dz = 0.5*cm
        solidShape6 = G4Trd("Shape6",  # its name
                            0.5*shape6_dxa, 0.5*shape6_dxb,
                            0.5*shape6_dya, 0.5*shape6_dyb, 0.5*shape6_dz)  # its size

        logicShape6 = G4LogicalVolume(solidShape6,  # its solid
                                      shape6_mat,   # its material
                                      "Shape6")     # its name

        G4PVPlacement(None,            # no rotation
                      pos6,            # at position
                      logicShape6,     # its logical volume
                      "Shape6",        # its name
                      logicEnv,        # its mother  volume
                      False,           # no boolean operation
                      0,               # copy number
                      checkOverlaps)   # overlaps checking
        
        # Shape 7
        shape7_mat = nist.FindOrBuildMaterial("G4_Si")
        pos7 = G4ThreeVector(-2*cm, 2*cm, 14*cm)

        # Trapezoid shape
        shape7_dxa = 6*cm
        shape7_dxb = 6*cm
        shape7_dya = 10*cm
        shape7_dyb = 10*cm
        shape7_dz = 0.5*cm
        solidShape7 = G4Trd("Shape7",  # its name
                            0.5*shape7_dxa, 0.5*shape7_dxb,
                            0.5*shape7_dya, 0.5*shape7_dyb, 0.5*shape7_dz)  # its size

        logicShape7 = G4LogicalVolume(solidShape7,  # its solid
                                      shape7_mat,   # its material
                                      "Shape7")     # its name

        G4PVPlacement(None,            # no rotation
                      pos7,            # at position
                      logicShape7,     # its logical volume
                      "Shape7",        # its name
                      logicEnv,        # its mother  volume
                      False,           # no boolean operation
                      0,               # copy number
                      checkOverlaps)   # overlaps checking

        # Set Shape4 as scoring volume
        self.fScoringVolume = logicShape4


        # always return the physical World
        return physWorld


class B1RunAction(G4UserRunAction):

    def __init__(self):
        super().__init__()
        milligray = 1.e-3*gray
        microgray = 1.e-6*gray
        nanogray = 1.e-9*gray
        picogray = 1.e-12*gray

        G4UnitDefinition("milligray", "milliGy", "Dose", milligray)
        G4UnitDefinition("microgray", "microGy", "Dose", microgray)
        G4UnitDefinition("nanogray", "nanoGy", "Dose", nanogray)
        G4UnitDefinition("picogray", "picoGy", "Dose", picogray)

        self.edep = G4Accumulable(0)
        self.edep2 = G4Accumulable(0)

        accumulableManager = G4AccumulableManager.Instance()
        accumulableManager.RegisterAccumulable(self.edep)
        accumulableManager.RegisterAccumulable(self.edep2)

    def BeginOfRunAction(self, aRun):
        G4RunManager.GetRunManager().SetRandomNumberStore(False)

        accumulableManager = G4AccumulableManager.Instance()
        accumulableManager.Reset()

    def EndOfRunAction(self, aRun):
        nofEvents = aRun.GetNumberOfEvent()
        if nofEvents == 0:
            return

        # Merge accumulables
        accumulableManager = G4AccumulableManager.Instance()
        accumulableManager.Merge()

        edep = self.edep.GetValue()
        edep2 = self.edep2.GetValue()

        # Compute dose = total energy deposit in a run and its variance
        rms = edep2 - edep*edep/nofEvents
        if rms > 0:
            rms = math.sqrt(rms)
        else:
            rms = 0

        detectorConstruction = G4RunManager.GetRunManager().GetUserDetectorConstruction()
        mass = detectorConstruction.fScoringVolume.GetMass()
        dose = edep/mass
        rmsDose = rms/mass

        generatorAction = G4RunManager.GetRunManager().GetUserPrimaryGeneratorAction()
        runCondition = ""
        if generatorAction != None and isinstance(generatorAction, B1PrimaryGeneratorAction):
            particleGun = generatorAction.fParticleGun
            runCondition += particleGun.GetParticleDefinition().GetParticleName() + "(s)"
            runCondition += " of "
            particleEnergy = particleGun.GetParticleEnergy()
            runCondition += "{:.5g}".format(G4BestUnit(particleEnergy, "Energy"))

        if self.IsMaster():
            print("--------------------End of Global Run-----------------------")
        else:
            print("--------------------End of Local Run------------------------")

        print(" The run consists of", nofEvents, runCondition)
        print(" Cumulated dose per run, in scoring volume: ", end="")
        print("{:.5f} rms = {:.5f}".format(G4BestUnit(dose, "Dose"), G4BestUnit(rmsDose, "Dose")))
        print("------------------------------------------------------------")
        print("")

    def AddEdep(self, edep):
        self.edep += edep
        self.edep2 += edep*edep


class B1EventAction(G4UserEventAction):

    def __init__(self, runAction):
        super().__init__()
        self.fRunAction = runAction

    def BeginOfEventAction(self, anEvent):
        self.fEdep = 0

    def EndOfEventAction(self, anEvent):
        self.fRunAction.AddEdep(self.fEdep)

    def AddEdep(self, edep):
        self.fEdep += edep


class B1SteppingAction(G4UserSteppingAction):

    def __init__(self, eventAction):
        super().__init__()
        self.fEventAction = eventAction
        self.fScoringVolume = None

    def UserSteppingAction(self, aStep):
        if self.fScoringVolume == None:
            detectorConstruction = G4RunManager.GetRunManager().GetUserDetectorConstruction()
            self.fScoringVolume = detectorConstruction.fScoringVolume

        volume = aStep.GetPreStepPoint().GetTouchable().GetVolume().GetLogicalVolume()

        # check if we are in scoring volume
        if volume != self.fScoringVolume:
            return

        # collect energy deposited in this step
        edepStep = aStep.GetTotalEnergyDeposit()
        self.fEventAction.AddEdep(edepStep)


class B1PrimaryGeneratorAction(G4VUserPrimaryGeneratorAction):

    def __init__(self):
        super().__init__()
        self.fEnvelopeBox = None
        self.fParticleGun = G4ParticleGun(1)

        # default particle kinematic
        particleTable = G4ParticleTable.GetParticleTable()
        particle = particleTable.FindParticle("pi+")
        self.fParticleGun.SetParticleDefinition(particle)
        self.fParticleGun.SetParticleMomentumDirection(G4ThreeVector(0, 0, 1))
        self.fParticleGun.SetParticleEnergy(120*GeV)

    def GeneratePrimaries(self, anEvent):
        # this function is called at the begining of each event

        # In order to avoid dependence of PrimaryGeneratorAction
        # on DetectorConstruction class we get Envelope volume
        # from G4LogicalVolumeStore.
        envSizeXY = 0
        envSizeZ = 0
        if self.fEnvelopeBox == None:
            envLV = G4LogicalVolumeStore.GetInstance().GetVolume("Envelope")
            if envLV != None:
                self.fEnvelopeBox = envLV.GetSolid()

        if self.fEnvelopeBox != None:
            envSizeXY = self.fEnvelopeBox.GetXHalfLength()*2
            envSizeZ = self.fEnvelopeBox.GetZHalfLength()*2
        else:
            msg = "Envelope volume of box shape not found.\n"
            msg += "Perhaps you have changed geometry.\n"
            msg += "The gun will be place at the center."
            G4Exception("B1PrimaryGeneratorAction::GeneratePrimaries()",
                        "MyCode0002", G4ExceptionSeverity.JustWarning, msg)

        x0=-2*cm
        y0=2*cm
        z0=0*cm

        self.fParticleGun.SetParticlePosition(G4ThreeVector(x0, y0, z0))
        self.fParticleGun.GeneratePrimaryVertex(anEvent)


class B1ActionInitialization(G4VUserActionInitialization):

    def BuildForMaster(self):
        self.SetUserAction(B1RunAction())

    def Build(self):
        self.SetUserAction(B1PrimaryGeneratorAction())

        runAction = B1RunAction()
        self.SetUserAction(runAction)

        eventAction = B1EventAction(runAction)
        self.SetUserAction(eventAction)

        self.SetUserAction(B1SteppingAction(eventAction))


ui = None
if len(sys.argv) == 1:
    ui = G4UIExecutive(len(sys.argv), sys.argv)

# Optionally: choose a different Random engine...
# G4Random.setTheEngine(MTwistEngine())

runManager = G4RunManagerFactory.CreateRunManager(G4RunManagerType.Serial)

runManager.SetUserInitialization(B1DetectorConstruction())

# Physics list
physicsList = FTFP_BERT()
physicsList.SetVerboseLevel(1)

runManager.SetUserInitialization(physicsList)

# User action initialization
runManager.SetUserInitialization(B1ActionInitialization())

visManager = G4VisExecutive()
# G4VisExecutive can take a verbosity argument - see /vis/verbose guidance.
# visManager = G4VisExecutive("Quiet")
visManager.Initialize()

# Get the User Interface manager
UImanager = G4UImanager.GetUIpointer()

# # Process macro or start UI session
if ui == None:
    # batch mode
    command = "/control/execute ./cfg/"
    fileName = sys.argv[1]
    UImanager.ApplyCommand(command+fileName)
else:
    # interactive mode
    UImanager.ApplyCommand("/control/execute ./cfg/init_vistelescope.mac")
    ui.SessionStart()
    #123