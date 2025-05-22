import geant4_pybind as g4b

class GeneralPrimaryGeneratorAction(g4b.G4VUserPrimaryGeneratorAction):
    "My Primary Generator Action"
    def __init__(self,par_in,par_out,par_type,par_energy,geant4_model):
        g4b.G4VUserPrimaryGeneratorAction.__init__(self)
        self.geant4_model=geant4_model
        self.par_direction = [ par_out[i] - par_in[i] for i in range(3) ]  
        particle_table = g4b.G4ParticleTable.GetParticleTable()
        particle = particle_table.FindParticle(par_type) # define particle
        beam = g4b.G4ParticleGun(1)
        beam.SetParticleEnergy(par_energy*g4b.MeV)
        beam.SetParticleMomentumDirection(g4b.G4ThreeVector(self.par_direction[0],
                                                            self.par_direction[1],
                                                            self.par_direction[2]))
        beam.SetParticleDefinition(particle)
        beam.SetParticlePosition(g4b.G4ThreeVector(par_in[0]*g4b.um,
                                                   par_in[1]*g4b.um,
                                                   par_in[2]*g4b.um))  
        self.particleGun = beam
        self.position = par_in

    def GeneratePrimaries(self, event):
        self.particleGun.GeneratePrimaryVertex(event)
