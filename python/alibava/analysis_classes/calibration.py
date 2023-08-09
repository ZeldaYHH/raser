"""This file contains the class for the ALiBaVa calibration"""
#pylint: disable=C0103,C0301,R0913,R0902
import logging
import numpy as np
from scipy.interpolate import CubicSpline
from .utilities import import_h5

class Calibration:# used
    """This class handles everything concerning the calibration.

    Charge Scan Details:
        - Each channel of the beetle chip is connected to a calibration
          capacitor which can inject a certain amount of charge (test pulse)
          into the channel. Each pulse generates a signal which is given in
          ADCs.
        - The charge scan is a sequence of injected test pulses with different
          pulse hights (charge values) for each channel.
        - The generated signal must be adjusted by subtracting the
          pedestal. Since alibava uses alternating pulses (pos/neg) in the
          course of the sequence (channel 1 -->pos, channel 2 -->neg, ...), one
          needs to calculate the absolute difference between pedestal and
          raw signal for each channel to obtain the 'real signal'.
        - The gain is the conversion factor between ADCs and electrons. It is
          defined as the gradient of the signal in ADCs vs. pulse height
          characteristic for each channel.
    """
    def __init__(self, file_path="", Noise_calc=None,
                 configs=None, logger=None):
        """
        :param delay_path: Path to calibration file
        :param charge_path: Path to calibration file
        """
        self.log = logger or logging.getLogger(__class__.__name__)

        # self.charge_cal = None
        self.delay_cal = None
        self.delay_data = None
        self.charge_data = None
        self.pedestal = Noise_calc.pedestal
        self.noisy_channels = Noise_calc.noisy_strips
        # self.CMN = np.std(Noise_calc.CMnoise)
        self.coeff_per_ch = []
        self.mean_sig_all_ch = [] # mean signal per pulse over all channels
        self.gains_per_pulse = []
        self.pulses = [] # list of injected test pulses
        self.meancoeff = None  # Mean coefficient out of all calibrations curves
        self.meansig_charge = []  # mean signal per channel per pulse
        self.sig_std = []  # std signal per channel per pulse
        self.charge_sig = None  # Standard deviation of all charge calibartions
        self.delay_cal = []
        self.meansig_delay = []  # mean per pulse per channel
        self.isBinary = configs.get("isBinary", "False")
        self.use_gain_per_channel = configs.get("use_gain_per_channel", True)
        self.numChan = configs.get("numChan", 256)
        self.degpoly = configs.get("charge_cal_polynom", 5)
        self.range = configs.get("range_ADC_fit", [])
        self.offset = 0 # offset of adc to e conversion
        self.ADC_sig = None
        self.configs = configs
        self.mean_sig_all_ch = []
        self.mean_std_all_ch = []
        if self.configs["calibrate_gain_to"] == "negative":
            self.polarity = -1
        elif self.configs["calibrate_gain_to"] == "positive":
            self.polarity = 1
        else:
            self.log.info("No polarity for gain pulse calibration selected, using both instead."
                          "Warning: This can cause serious miscalculations when converting ADC to electrons!")
            self.polarity = 0

        if not self.configs["use_charge_cal"]:
            self.use_predefined_cal_params()
            #self.delay_calibration_calc(file_path)
        elif file_path == "":
            self.use_predefined_cal_params()
        else:
            self.charge_calibration_calc(file_path)

    def use_predefined_cal_params(self):# used
        """Uses the predefined calibration parameters from the calibration file"""
        self.log.info("Using predefined gain parameters: %s", self.configs["Gain_params"])
        self.meancoeff = self.configs["Gain_params"]
        self.ADC_sig = 1.
        self.charge_sig = 1.
        self.chargecoeff = [np.array(self.configs["Gain_params"]) for i in range(256)]
        #self.gain_calc()
        # So every strip has the same gain

    def charge_calibration_calc(self, charge_path):# used
        """Analyze the calibration scan and calculate conversion parameters
        for converting ADC Signals to e Signals"""

        # Loading the file------------------------------------------------------
        # Charge scan
        self.log.info("Loading charge calibration file: %s", charge_path)
        self.charge_data = import_h5(charge_path)

        # Look if data is valid------------------------------------------------------
        if not self.charge_data:
            raise ValueError("Unable to read the calibration file...")
        else:
            # Process data ----------------------------------------------------------
            # list of injected test pulse values aka x-data
            self.pulses = np.array(self.charge_data["scan"]["value"][:])

            # Sometime it happens, that h5py does not read correctly
            if not len(self.pulses):
                self.log.error("A HDF5 read error! Loaded empty array. "
                               "Restart python")

            # signals per pulse subtracted by pedestals and excluding noisy channels
            signals = np.array(self.charge_data["events"]["signal"][:]) - self.pedestal
            # signals = np.delete(signals, self.noisy_channels, axis=1)
            # Calculate size of pulse group to obtain number of injected signals per pulse step
            sigppulse = int(len(signals) / len(self.pulses))

            start = 0

            # summarize signals of each pulse group by calculating the mean
            # signals of each pulse group per channel
            for i in range(sigppulse, len(signals) + sigppulse, sigppulse):

                raw_half = np.mean(signals[start:i][0::2], axis=0)
                raw_half_std = np.std(signals[start:i][0::2], axis=0)
                raw_half2 = np.mean(signals[start:i][1::2], axis=0)
                raw_half2_std = np.std(signals[start:i][1::2], axis=0)

                # Take only the correct polarity of pulses
                if self.polarity == -1:
                    meansig_neg_pulses = np.hstack(list(zip(raw_half[0:104:2], raw_half2[1:103:2])))
                    std_neg_pulses = np.hstack(list(zip(raw_half_std[0:104:2], raw_half2_std[1:103:2])))
                    #meansig_neg_pulses = np.hstack(list(zip(raw_half[0::2], raw_half2[1::2])))
                    #std_neg_pulses = np.hstack(list(zip(raw_half_std[0::2], raw_half2_std[1::2])))
                    self.meansig_charge.append(np.abs(meansig_neg_pulses))
                    self.sig_std.append(std_neg_pulses)
                elif self.polarity == 1:
                    meansig_pos_pulses = np.hstack(list(zip(raw_half[1::2], raw_half2[0::2])))
                    std_pos_pulses = np.hstack(list(zip(raw_half_std[1::2], raw_half2_std[0::2])))
                    self.meansig_charge.append(np.abs(meansig_pos_pulses))
                    self.sig_std.append(std_pos_pulses)
                else:
                    self.meansig_charge.append(np.mean(np.abs(signals[start:i]), axis=0))
                    self.sig_std.append(np.std(np.abs(signals[start:i]), axis=0))
                start = i
            self.meansig_charge = np.array(self.meansig_charge)
            self.sig_std = np.array(self.sig_std)

            # For a pulse height of 0 one often finds non-zero values in meansig_charge
            # Use signals of 0 pulse as offset values and adjust rest accordingly
            self.offset = self.meansig_charge[1] # because first value is usually garbage
            if np.mean(self.offset) > 5:
                self.log.warning("Charge offset is greater then 5 ADC! This "
                                 "may be a result of bad calibration! Offset: {}".format(np.mean(self.offset)))
            #self.meansig_charge = self.meansig_charge - offset
            #for i, pul in enumerate(self.meansig_charge):
            #    for j, val in enumerate(pul):
            #        if val < 0:
            #            self.meansig_charge[i][j] = 0


            # Calculate the mean over all channels for every pulse and then calc
            # a poly fit for the median gain curve
            # revise
            # self.mean_sig_all_ch = np.median(self.meansig_charge, axis=1)#-np.mean(self.offset)
            # self.mean_std_all_ch = np.median(self.sig_std, axis=1)#-np.mean(self.offset)
            self.mean_sig_all_ch = np.mean(self.meansig_charge, axis=1)
            self.mean_std_all_ch = np.mean(self.sig_std, axis=1)
            if self.mean_sig_all_ch[0] <= self.range[0] and self.mean_sig_all_ch[-1] >= self.range[0]:
                xminarg = np.argwhere(self.mean_sig_all_ch <= self.range[0])[-1][0]
                xmaxarg = np.argwhere(self.mean_sig_all_ch <= self.range[1])[-1][0]
            else:
                self.log.error("Range for charge cal poorly conditioned!!!")
                xmaxarg = len(self.mean_sig_all_ch) - 1
                xminarg = 0

            # Generate a list of tuples, over signal in ADC and corresponding electrons,
            # but only in the specified range (xmin and xmax), furthermore only take these signals
            # which show a signal greater as 0
            fit_params = [(sig, pul) for sig, pul in zip(self.mean_sig_all_ch[xminarg:xmaxarg],
                                                         self.pulses[xminarg:xmaxarg]) if sig > 0]

            # Generate poly fit a cut of the offset and append a 0 instead
            self.meancoeff = np.polyfit([tup[0] for tup in fit_params],
                                        [tup[1] for tup in fit_params],
                                        deg=self.degpoly, full=False)
            self.log.info("Mean fit coefficients over all channels are: %s", self.meancoeff)

            # Calculate the gain curve for EVERY channel-------------------------------------------
            self.channel_coeff = np.zeros([self.numChan, self.degpoly+1])
            for i in range(self.numChan):
                if i not in self.noisy_channels:
                    #self.log.debug("Fitting channel: {}".format(i))
                    try:
                        # Taking the correct channel from the means, this has the length of pulses, and the correct
                        # polarity is already accored to. Warning first value will always be cutted away,
                        # to ensure better convergence while fitting!!!
                        mean_sig = self.meansig_charge[1:,i]
                        sig_std = self.sig_std[1:, i]
                        # Find the range for the fit
                        if mean_sig[0] <= self.range[0] and mean_sig[-1] >= self.range[0]:
                            xminarg = np.argwhere(mean_sig <= self.range[0])[-1][0]
                            xmaxarg = np.argwhere(mean_sig <= self.range[1])[-1][0]
                        else:
                            self.log.error("Range for charge cal for channel {} may be poorly conditioned!!!".format(i))
                            xminarg = 0
                            xmaxarg = len(mean_sig)

                        # In the beginning of the pulses the error can be huge. Therefore, check if std is small enough
                        # Otherwise search for point, which has a low enough std
                        std_ok = False
                        while not std_ok:
                            if xminarg == xmaxarg:
                                # Todo: make it possible to run nontheless
                                self.log.error("Could not find satisfying std value for charge cal in channel {}. This may happen"
                                               " with bad calibration. Further calculations may fail! This channel"
                                               " will be added to noisy channels!".format(i))
                                self.noisy_channels = np.append(self.noisy_channels, [i])
                            if mean_sig[xminarg]*0.4 <= sig_std[xminarg]:
                                xminarg += 1
                            else:
                                std_ok = True
                                break

                        self.channel_coeff[i] = np.polyfit(mean_sig[xminarg:xmaxarg],
                                                            self.pulses[xminarg:xmaxarg],
                                                            deg=self.degpoly, full=False)
                    except Exception as err:
                        if "SVD did not converge" in str(err):
                            self.log.error("SVD did not converge in Linear Least Squares for channel {}"
                                           " this channel will be added to noisy channels!".format(i))
                            self.noisy_channels = np.append(self.noisy_channels, i)