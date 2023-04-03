import math
import ROOT
import numpy as np
from raser.geometry import R3dDetector

class TCTTracks():
    """
    Description:
        Transfer Carrier Distribution from Laser Coordinate System 
        to Detector Coordinate System
    Parameters:
    ---------
    my_d : R3dDetector
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
    def __init__(self, my_d, laser, pulse_time=1e-9, t_step=50e-12):
        #technique used
        self.tech = laser["tech"]
        self.direction = laser["direction"]
        #material parameters to certain wavelength of the beam
        self.refractionIndex = laser["refractionIndex"]
        if self.tech == "SPA":
            self.alpha = laser["alpha"]
        if self.tech == "TPA":
            self.beta_2 = laser["beta_2"]
        #laser parameters
        self.wavelength = laser["wavelength"]*1e-3 #um
        self.tau = laser["tau"]
        self.power = laser["power"]
        self.widthBeamWaist = laser["widthBeamWaist"]#um
        if "l_Reyleigh" not in laser:
            self.l_Rayleigh = np.pi*self.widthBeamWaist**2*self.refractionIndex/self.wavelength
        else:
            self.l_Rayleigh = laser["l_Rayleigh"]#um
        #the size of the detector
        self.lx = my_d.l_x#um
        self.ly = my_d.l_y
        self.lz = my_d.l_z
        #relative and absolute position of the focus
        self.fx_rel = laser["fx_rel"]
        self.fy_rel = laser["fy_rel"]
        self.fz_rel = laser["fz_rel"]
        self.fx_abs = self.fx_rel * self.lx
        self.fy_abs = self.fy_rel * self.ly
        self.fz_abs = self.fz_rel * self.lz
        #accuracy parameters
        self.r_step = laser["r_step"]#um
        self.h_step = laser["h_step"]#um
        self.t_step = t_step#s

        self.pulse_time = pulse_time        
        self.mesh_definition(my_d)

    def mesh_definition(self,my_d):
        self.r_char = self.widthBeamWaist / 2
        if self.tech == "SPA":
            self.h_char = max(my_d.l_x, my_d.l_y, my_d.l_z)
        elif self.tech == "TPA":
            self.h_char = self.l_Rayleigh
        else:
            raise NameError(self.tech)

        self.change_coordinate()
        x_min = max(0,self.fx_abs - 3 * self.x_char)
        x_max = min(my_d.l_x,self.fx_abs + 3 * self.x_char)
        y_min = max(0,self.fy_abs - 3 * self.y_char)
        y_max = min(my_d.l_y,self.fy_abs + 3 * self.y_char)
        z_min = max(0,self.fz_abs - 3 * self.z_char)
        z_max = min(my_d.l_z,self.fz_abs + 3 * self.z_char)

        self.x_left_most, self.x_right_most = self.window(x_min, x_max, 0, my_d.l_x)
        self.y_left_most, self.y_right_most = self.window(y_min, y_max, 0, my_d.l_y)
        self.z_left_most, self.z_right_most = self.window(z_min, z_max, 0, my_d.l_z)
        
        xArray = np.linspace(x_min, x_max, int((x_max - x_min) / self.x_step) + 1)
        yArray = np.linspace(y_min, y_max, int((y_max - y_min) / self.y_step) + 1)
        zArray = np.linspace(z_min, z_max, int((z_max - z_min) / self.z_step) + 1)

        xCenter = (xArray[:-1] + xArray[1:]) / 2
        yCenter = (yArray[:-1] + yArray[1:]) / 2
        zCenter = (zArray[:-1] + zArray[1:]) / 2

        xDiff = (xArray[1:] - xArray[:-1])
        yDiff = (yArray[1:] - yArray[:-1])
        zDiff = (zArray[1:] - zArray[:-1])

        YC, XC, ZC = np.meshgrid(yCenter, xCenter, zCenter) #Feature of numpy.meshgrid
        YD, XD, ZD = np.meshgrid(yDiff, xDiff, zDiff)
        self.projGrid = self._getCarrierDensity(XC, YC, ZC)\
            * XD * YD * ZD * 1e-18
        self.track_position = list(np.transpose(np.array([
            list(np.ravel(XC)),\
            list(np.ravel(YC)),\
            list(np.ravel(ZC)),\
            [self.pulse_time for x in np.ravel(XC)]])))
        self.ionized_pairs = list(np.ravel(self.projGrid))
        print(len(self.ionized_pairs))

    def change_coordinate(self):
        #from cylindral coordinate (axis parallel with the beam, origin at focus)
        #to rectilinear coordinate inside the detector
        if self.direction in ("top","bottom"):
            self.z_step = self.h_step
            self.z_char = self.h_char
            self.x_step = self.y_step = self.r_step
            self.x_char = self.y_char = self.r_char
            if self.direction == "top":
                absorb_depth = self.lz * self.fz_rel
                def _getCarrierDensity(x, y, z):
                    return self.getCarrierDensity(z - self.fz_abs, absorb_depth, (x - self.fx_abs) ** 2 + (y - self.fy_abs) ** 2)
                self._getCarrierDensity = _getCarrierDensity
            if self.direction == "bottom":
                absorb_depth = self.lz * (1 - self.fz_rel)
                def _getCarrierDensity(x, y, z):
                    return self.getCarrierDensity(self.lz - z + self.fz_abs, absorb_depth, (x - self.fx_abs) ** 2 + (y - self.fy_abs) ** 2)
                self._getCarrierDensity = _getCarrierDensity

        elif self.direction == "edge":
            self.x_step = self.h_step
            self.x_char = self.h_char
            self.y_step = self.z_step = self.r_step
            self.y_char = self.z_char = self.r_char

            absorb_depth = self.lx * self.fx_rel
            def _getCarrierDensity(x, y, z):
                return self.getCarrierDensity(x - self.fx_abs, absorb_depth, (y - self.fy_abs) ** 2 + (z -self.fz_abs) ** 2)
            self._getCarrierDensity = _getCarrierDensity
        else:
            raise NameError(self.direction)

    def window(self,inner_min,inner_max,outer_min,outer_max):
        inner_length = inner_max - inner_min
        if outer_max - outer_min <= inner_length:
            return outer_min, outer_max # range shrunk
        else:
            if inner_min >= outer_min and inner_max <= outer_max:
                return inner_min, inner_max
            elif inner_min <= outer_min:
                return outer_min, outer_min + inner_length
            elif inner_max >= outer_max:
                return outer_max - inner_length, outer_max

    def getCarrierDensity(self, h, depth, r2):
        #return the carrier density of a given point in a given time period
        #referring to the vertical and horizontal distance from the focus 
        w_0 = self.widthBeamWaist / 2
        wSquared = (w_0 ** 2) * (1 + (h / self.l_Rayleigh) ** 2)
        intensity = ((self.power) / self.tau)\
                    * (4 * np.log(2) ** 0.5 / (np.pi ** 1.5 * wSquared * 1e-12))\
                    * np.exp((-2 * r2 / wSquared))\
                    * self.t_step

        if self.tech == "SPA":
            # I = I_0 * exp(-αz)
            # dE_deposit = (αdz)dE_flux = (αdz)I*dSdt = (αI)*dVdt
            # dN_ehpair = dE_deposit / Energy_for_each_ionized_ehpair
            e0 = 1.60217733e-19
            return self.alpha * intensity * np.exp(-self.alpha * (h + depth) * 1e-6) / (3.6 * e0)
        elif self.tech == "TPA":
            h_Planck = 6.626*1e-34
            speedofLight = 2.998*1e8
            return self.beta_2 * self.wavelength * 1e-6 * intensity ** 2 / (2 * h_Planck * speedofLight)
        
    def timePulse(self, t):
        # to reduce run time, convolute the time pulse function with the signal after the signal is calculated
        return np.exp(-4 * np.log(2) * t ** 2 / self.tau ** 2)
