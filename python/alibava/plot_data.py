"""PlotData Class"""
# pylint: disable=R0201,C0103,E0401,R0913
import numpy as np
import logging
from scipy.stats import norm, rv_continuous
import matplotlib.pyplot as plt
import logging
import matplotlib.mlab as mlab
from scipy import optimize
# import pylandau
from analysis_classes.utilities import handle_sub_plots
from analysis_classes.utilities import create_dictionary
import csv

class PlotData:# used
    """Plots for ALiBaVa Analysis"""
    def __init__(self, config_path, logger=None):
        self.log = logger or logging.getLogger(__class__.__name__)
        # canvas for plotting the data [width, height (inches)]

        self.log = logging.getLogger(__name__)
        self.cfg = create_dictionary(config_path)
        #self.groups["Brace yourself! plots are comming"] = np.concatenate([x for x in self.groups.items()])

    def start_plotting(self, mcfg, obj, group=None, fig_name=None):# used
        """Plots the data calculated by the framework. Suppress drawing and
        showing the canvas by setting "show" to False.
        Returns matplotlib.pyplot.figure object.
        """

        if group=="all" or group=="from_file":
            for grp in self.cfg["Render"]:
                fig_name = grp
                self.log.info("Plotting group: {}".format(grp))
                fig = plt.figure(fig_name, figsize=[10, 8])
                for funcname, cfg in zip(self.cfg["Render"][grp]["Plots"], self.cfg["Render"][grp]["arrangement"]):
                    try:
                        plot_func = getattr(self, str(funcname))
                        plot_func(cfg, obj, fig)
                    except Exception as err:
                        self.log.error("Plotting function {} raised an error. Error: {}".format(funcname, err))
                fig.subplots_adjust(hspace = 0.4) # Adjusts the padding so nothing is overlapping
                fig.subplots_adjust(wspace = 0.3) # Adjusts the padding so nothing is overlapping

    def plot_rawnoise_ch(self, cfg, obj, fig=None):
        """plot noise per channel with commom mode correction"""
        data = obj["NoiseAnalysis"]

        noise_plot = handle_sub_plots(fig, cfg)
        noise_plot.bar(np.arange(data.numchan), data.noise_raw, 1.,
                       alpha=0.4, color="b", label="Noise level per strip (CMC)")
        # plot line idicating masked and unmasked channels
        valid_strips = np.zeros(data.numchan)
        valid_strips[data.noisy_strips] = 1
        noise_plot.plot(np.arange(data.numchan), valid_strips, color="r",
                        label="Masked strips")

        # Plot the threshold for deciding a good channel
        xval = [0, data.numchan]
        yval = [data.median_noise + data.noise_cut,
                data.median_noise + data.noise_cut]
        noise_plot.plot(xval, yval, "r--", color="g",
                        label="Threshold for noisy strips")

        noise_plot.set_xlabel('Channel [#]')
        noise_plot.set_ylabel('Noise [ADC]')
        noise_plot.set_title('Raw Noise levels per Channel (CMC)')
        noise_plot.legend(loc='upper right')
        noise_plot.set_ylim(0,10)
        return noise_plot
