#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
import devsim
from util.output import output

def CreateDataBase(filename):
    devsim.create_db(filename=filename)
    print("The SICAR database is created.")


def CreateGlobalConstant():

    # define global constant

    q = 1.60217646e-19 # coul
    k = 1.3806503e-23  # J/K
    eps_0 = 8.85e-14   # F/cm^2
    T0 = 300.0         # K

    devsim.add_db_entry(material="global",   parameter="ElectronCharge",       value=q,          unit="coul",     description="Unit Charge")
    devsim.add_db_entry(material="global",   parameter="k",       value=k,          unit="J/K",      description="Boltzmann Constant")
    devsim.add_db_entry(material="global",   parameter="eps_0",   value=eps_0,      unit="F/cm^2",   description="Absolute Dielectric Constant")
    devsim.add_db_entry(material="global",   parameter="T0",      value=T0,         unit="K",        description="T0")
    devsim.add_db_entry(material="global",   parameter="k_T0",    value=k*T0,       unit="J",        description="k*T0")
    devsim.add_db_entry(material="global",   parameter="V_t",    value=k*T0/q,     unit="J/coul",   description="k*T0/q")

    T = 300.0         # K
    devsim.add_db_entry(material="global",   parameter="T",    value=T,     unit="K",   description="T")


def CreateSiliconCarbideConstant():

    # define SiliconCarbide parameters

    N_c=3.25e15
    N_v=4.8e15
    devsim.add_db_entry(material="SiliconCarbide",parameter="N_c",value=N_c, unit="/cm^3", description="effective density of states in conduction band")
    devsim.add_db_entry(material="SiliconCarbide",parameter="N_v",value=N_v, unit="/cm^3", description="effective density of states in valence band")

    E_g=3.26*1.6*1e-19
    devsim.add_db_entry(material="SiliconCarbide",   parameter="E_g",    value=E_g,       unit="J",         description="E_g")

    # material
    devsim.add_db_entry(material="SiliconCarbide",   parameter="eps",    value=9.76,      unit="1",         description="Dielectric Constant")
    eps_0 = 8.85e-14
    devsim.add_db_entry(material="SiliconCarbide",   parameter="Permittivity",    value=9.76*eps_0,      unit="F/cm^2",         description="Dielectric Constant")
    devsim.add_db_entry(material="SiliconCarbide",   parameter="n_i",    value=3.89e-9,   unit="/cm^3",     description="Intrinsic Electron Concentration")

    # mobility
    devsim.add_db_entry(material="SiliconCarbide",   parameter="mu_n",   value=1100,      unit="cm^2/Vs",   description="Constant Mobility of Electron")
    devsim.add_db_entry(material="SiliconCarbide",   parameter="mu_p",   value=114,       unit="cm^2/Vs",   description="Constant Mobility of Hole")

    # SRH
    devsim.add_db_entry(material="SiliconCarbide",   parameter="n1",     value=3.89e-9,   unit="/cm^3",     description="n1")
    devsim.add_db_entry(material="SiliconCarbide",   parameter="p1",     value=3.89e-9,   unit="/cm^3",     description="p1")
    devsim.add_db_entry(material="SiliconCarbide",   parameter="taun",  value=2.5e-6,    unit="s",         description="Constant SRH Lifetime of Electron")
    devsim.add_db_entry(material="SiliconCarbide",   parameter="taup",  value=0.5e-6,    unit="s",         description="Constant SRH Lifetime of Hole")


def CreateSiliconConstant():

    # define Silicon parameters

    N_c=2.8e19
    N_v=1.1e19
    #N_c=2.86e19
    #N_v=2.66e19
    devsim.add_db_entry(material="Silicon",parameter="N_c",value=N_c, unit="/cm^3", description="effective density of states in conduction band")
    devsim.add_db_entry(material="Silicon",parameter="N_v",value=N_v, unit="/cm^3", description="effective density of states in valence band")

    E_g=1.12*1.6*1e-19
    devsim.add_db_entry(material="Silicon",   parameter="E_g",    value=E_g,       unit="J",         description="E_g")

    # material
    devsim.add_db_entry(material="Silicon",   parameter="eps",    value=11.9,      unit="1",         description="Dielectric Constant")
    eps_0 = 8.85e-14
    devsim.add_db_entry(material="Silicon",   parameter="Permittivity",    value=11.9*eps_0,      unit="F/cm^2",         description="Dielectric Constant")
    devsim.add_db_entry(material="Silicon",   parameter="n_i",    value=1.02e10,   unit="/cm^3",     description="Intrinsic Electron Concentration")

    # mobility
    devsim.add_db_entry(material="Silicon",   parameter="mu_n",   value=1450,      unit="cm^2/Vs",   description="Constant Mobility of Electron")
    devsim.add_db_entry(material="Silicon",   parameter="mu_p",   value=500,       unit="cm^2/Vs",   description="Constant Mobility of Hole")

    # SRH
    devsim.add_db_entry(material="Silicon",   parameter="n1",     value=1.02e10,   unit="/cm^3",     description="n1")
    devsim.add_db_entry(material="Silicon",   parameter="p1",     value=1.02e10,   unit="/cm^3",     description="p1")
    devsim.add_db_entry(material="Silicon",   parameter="taun",  value=5e-6,    unit="s",         description="Constant SRH Lifetime of Electron")
    devsim.add_db_entry(material="Silicon",   parameter="taup",  value=5e-6,    unit="s",         description="Constant SRH Lifetime of Hole")


def SaveDataBase():
    devsim.save_db()
    print("The SICAR database is saved.")


def main():
    path = output(__file__, "")
    CreateDataBase(os.path.join(path, "SICARDB.db"))
    CreateGlobalConstant()
    CreateSiliconCarbideConstant()
    CreateSiliconConstant()
    SaveDataBase()

if __name__ == "__main__":
    main()
