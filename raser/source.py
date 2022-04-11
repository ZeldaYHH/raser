import math
import ROOT
import numpy as np
from raser.geometry import R3dDetector

class TCTTracks():
    """
    Description:
        Transfer Carrier Distribution from Laser Coordinate System 
        to 2d Detector Coordinate System
    Parameters:
    ---------
    my_d : R2dDetector or R3dDetector
        the Detector
    laser : dict
        the Parameter List of Your Laser
    x_rel,y_rel,z_rel:
        the Normalized Coordinate for Laser Focus 
        in Detector Coordinate System
    @Modify:
    ---------
        2021/09/13
    """
    def __init__(self,my_d,laser,min_carrier=0):
        #technique used
        self.tech=laser["tech"]
        self.direction=laser["direction"]
        #material parameters to certain wavelength of the beam
        self.refractionIndex=laser["refractionIndex"]
        if self.tech == "SPA":
            self.alpha=laser["alpha"]
        if self.tech == "TPA":
            self.beta_2=laser["beta_2"]
        #laser parameters
        self.wavelength=laser["wavelength"]*1e-3 #um
        self.tau=laser["tau"]
        self.power=laser["power"]
        self.widthBeamWaist=laser["widthBeamWaist"]#um
        if "l_Reyleigh" not in laser:
            self.l_Rayleigh = np.pi*self.widthBeamWaist**2*self.refractionIndex/self.wavelength
        else:
            self.l_Rayleigh = laser["l_Rayleigh"]#um
        #the size of the detector
        self.lx=my_d.l_x#um
        self.ly=my_d.l_y
        self.lz=my_d.l_z
        #relative and absolute position of the focus
        self.fx_rel=laser["fx_rel"]
        self.fy_rel=laser["fy_rel"]
        self.fz_rel=laser["fz_rel"]
        self.fx_abs=self.fx_rel*self.lx
        self.fy_abs=self.fy_rel*self.ly
        self.fz_abs=self.fz_rel*self.lz
        #accuracy parameters
        self.r_step=laser["r_step"]#um
        self.h_step=laser["h_step"]#um
        self.min_carrier=min_carrier
        
        self.mesh_definition()

    def mesh_definition(self):
        self.r_char=self.widthBeamWaist
        if self.tech == "SPA":
            self.h_char=float('inf')

        elif self.tech == "TPA":
            self.h_char=self.l_Rayleigh

        self.change_coordinate()
        self.x_min,self.x_max=max(0,self.fx_abs-5*self.x_char),min(self.lx,self.fx_abs+5*self.x_char)
        self.y_min,self.y_max=max(0,self.fy_abs-5*self.y_char),min(self.ly,self.fy_abs+5*self.y_char)
        self.z_min,self.z_max=max(0,self.fz_abs-5*self.z_char),min(self.lz,self.fz_abs+5*self.z_char)
        xArray = np.linspace(self.x_min,self.x_max,int((self.x_max-self.x_min)/self.x_step))
        yArray = np.linspace(self.y_min,self.y_max,int((self.y_max-self.y_min)/self.y_step))
        zArray = np.linspace(self.z_min,self.z_max,int((self.z_max-self.z_min)/self.z_step))

        Y,X,Z=np.meshgrid(yArray,xArray,zArray) #Feature of numpy.meshgrid
        self.projGrid=self._getCarrierDensity(X,Y,Z)\
            *self.x_step*self.y_step*self.z_step*1e-18
        self.track_position = list(np.transpose(np.array([
            list(np.ravel(X)),\
            list(np.ravel(Y)),\
            list(np.ravel(Z))])))
        self.ionized_pairs = list(np.ravel(self.projGrid))
        self.ionized_total_pairs = 0
        for i in range(len(self.ionized_pairs)-1,-1,-1):
            if self.ionized_pairs[i]<=self.min_carrier:
                del self.ionized_pairs[i]
                del self.track_position[i]
            else:
                self.ionized_total_pairs+=self.ionized_pairs[i]

    def change_coordinate(self):
        #from cylindral coordinate (axis parallel with the beam, origin at focus)
        #to rectilinear coordinate inside the detector
        if self.direction in ("top","bottom"):
            self.z_step=self.h_step
            self.z_char=self.h_char
            self.x_step=self.y_step=self.r_step
            self.x_char=self.y_char=self.r_char
            if self.direction == "top":
                absorb_depth=self.lz*self.fz_rel
                def _getCarrierDensity(x,y,z):
                    return self.getCarrierDensity(z-self.fz_abs,absorb_depth,(x-self.fx_abs)**2+(y-self.fy_abs)**2)
                self._getCarrierDensity=_getCarrierDensity
            if self.direction == "bottom":
                absorb_depth=self.lz*(1-self.fz_rel)
                def _getCarrierDensity(x,y,z):
                    return self.getCarrierDensity(self.lz-z+self.fz_abs,absorb_depth,(x-self.fx_abs)**2+(y-self.fy_abs)**2)
                self._getCarrierDensity=_getCarrierDensity

        elif self.direction == "edge":
            self.x_step=self.h_step
            self.x_char=self.h_char
            self.y_step=self.z_step=self.r_step
            self.y_char=self.z_char=self.r_char

            absorb_depth=self.lx*self.fx_rel
            def _getCarrierDensity(x,y,z):
                return self.getCarrierDensity(x-self.fx_abs,absorb_depth,(y-self.fy_abs)**2+(z-self.fz_abs)**2)
            self._getCarrierDensity=_getCarrierDensity
        else:
            raise NameError(self.direction)

    def getCarrierDensity(self,h,depth,r2):
        #return the carrier density of a given point
        #referring to the vertical and horizontal distance from the focus 
        widthSquared=(self.widthBeamWaist**2)*(1+(h/self.l_Rayleigh)**2)

        if self.tech=="SPA":
            intensity = ((2*self.power)/(np.pi*widthSquared*1e-12))*np.exp((-2*r2/(widthSquared)))*np.exp(-self.alpha*(h+depth)*1e-6)
            e0 = 1.60217733e-19
            return self.alpha*intensity/(3.6*e0)
            
        elif self.tech=="TPA":
            k=(self.power**2)*8*np.log(2)/(self.tau*(np.pi**2.5)*(np.log(4))**0.5)
            intensity_squared = k*np.exp(-4*r2/widthSquared)/((widthSquared**2)*1e-24)
            h_Planck = 6.626*1e-34
            speedofLight = 2.998*1e8
            return self.beta_2*self.wavelength*1e-6*intensity_squared/(2*h_Planck*speedofLight)
