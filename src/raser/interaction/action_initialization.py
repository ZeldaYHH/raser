import numpy as np
import geant4_pybind as g4b

from .run_action import GeneralRunAction
from .event_action import GeneralEventAction
from .stepping_action import GeneralSteppingAction
from .primary_generator_action import GeneralPrimaryGeneratorAction

class GeneralActionInitialization(g4b.G4VUserActionInitialization):
    def __init__(self, par_in, par_out, par_type, par_energy,
                 eventIDs, edep_devices, p_steps, energy_steps, events_angles, geant4_model):
        g4b.G4VUserActionInitialization.__init__(self)
        self.par_in = par_in
        self.par_out = par_out
        self.par_type=par_type
        self.par_energy=par_energy

        self.eventIDs = eventIDs
        self.edep_devices = edep_devices
        self.p_steps = p_steps
        self.energy_steps = energy_steps
        self.events_angles = events_angles

        self.geant4_model=geant4_model

    def Build(self):
        self.SetUserAction(GeneralPrimaryGeneratorAction(self.par_in,
                                                    self.par_out,
                                                    self.par_type,
                                                    self.par_energy,
                                                    self.geant4_model))
        # global myRA_action
        myRA_action = GeneralRunAction()
        self.SetUserAction(myRA_action)
        myEA = GeneralEventAction(myRA_action, self.par_in, self.par_out,
                                  self.eventIDs, self.edep_devices, self.p_steps, self.energy_steps, self.events_angles)
        self.SetUserAction(myEA)
        self.SetUserAction(GeneralSteppingAction(myEA))