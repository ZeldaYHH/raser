#!/usr/bin/env python3
"""Wrapper for full alibava analysis via console"""
import os
import sys
from argparse import ArgumentParser
from plot_data import PlotData
from analysis_classes.utilities import create_dictionary
from analysis_classes import Calibration
from analysis_classes import NoiseAnalysis
from analysis_classes import MainAnalysis
from analysis_classes.utilities import save_all_plots, read_meas_files
import matplotlib.pyplot as plt

def main(args):
    """Start analysis"""
    if args.config:
        cfg = create_dictionary(args.config)# ./alibava/config/default_config.yml 中的内容转为参数字典
        ext = os.path.dirname(args.config)#返回 ./alibava/config
    else:
        print("AliSys needs at least the --config parameter. Type AliSys --help to see all params")
        sys.exit(0)
    plot = PlotData(os.path.join(os.getcwd(),ext,cfg.get("plot_config_file", "plot_cfg.yml")))
    results = {}

    meas_files = read_meas_files(cfg)
    it = 0
    for ped, cal, run in meas_files:
        it+=1

        ped_data = NoiseAnalysis(ped, configs=cfg)

        results["NoiseAnalysis"] = ped_data

        cal_data = Calibration(cal, Noise_calc=ped_data, configs=cfg)

        results["Calibration"] = cal_data

        cfg.update({"calibration": cal_data,
                    "noise_analysis": ped_data})

        if run:
            run_data = MainAnalysis(run, configs=cfg)
            results["MainAnalysis"] = run_data.results

        # Start plotting all results
        if it > 1:  # Closing the old files
            plt.close("all")
        plot.start_plotting(cfg, results, group="from_file")

        if cfg.get("Output_folder", "") and cfg.get("Output_name", "") and cfg.get("Save_output", False):
            fileName = cfg["Output_name"]
            dir_maker(cfg["Output_folder"], args.data)
            save_all_plots(fileName, cfg["Output_folder"] + args.data, dpi=600)

    plt.close("all")

def dir_maker(path,file_name):
    waves = os.listdir(path)
    try:
        os.mkdir(os.path.join(path,file_name))
    except Exception as e:
        pass

if __name__ == "__main__":

    PARSER = ArgumentParser()
    PARSER.add_argument("--config",
                        help="The path to the config file for the analysis run",
                        default="") 
    PARSER.add_argument("--data",
                        help="The path to the data file for the analysis run",
                        default="") 
    main(PARSER.parse_args())
