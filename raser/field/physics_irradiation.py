#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

'''
Description:  physics_irradiation.py
@Date       : 2023/10/20
@Author     : XingChen Li, Chenxi Fu, Zhan Li
@version    : 3.0
'''

import devsim
from .model_create import *

def CreateIrradiation(device, region, label="Xingchen", custom_defect = {}, flux=1e15):

    # if not InEdgeModelList(device, region, "ElectricField"):
    #     CreateEdgeModel(device, region, "ElectricField", "(Potential@n0-Potential@n1)*EdgeInverseLength")
    #     CreateEdgeModelDerivatives(device, region, "ElectricField", "(Potential@n0-Potential@n1)*EdgeInverseLength", "Potential")

    # TODO: change labels into formal names
    if label == 'XingChen':
        defects = CreateIrradiationModel_XingChen(device, region)
    elif label == 'Lizhan':
        defects = CreateIrradiationModel_Perugia(device, region)
    elif label == 'Schwandt':
        defects = CreateIrradiationModel_Schwandt(device, region)
    else:
        defects = custom_defect

    if defects == {}:
        raise KeyError(defects)

    TrappedElectrons=""
    TrappedHoles=""
    Trappingtime_n=""
    Trappingtime_p=""
    for name, E_t_ev, g_int, sigma_n_irr, sigma_p_irr in zip(names, E_ts_ev, g_ints, sigma_n_irrs, sigma_p_irrs):
        e = 1.6*1e-19
        E_t = E_t_ev * e
        N_t_irr = g_int*flux
        devsim.set_parameter(device=device, region=region, name="sigma_n_irr_"+name,   value=sigma_n_irr)
        devsim.set_parameter(device=device, region=region, name="sigma_p_irr_"+name,   value=sigma_p_irr)
        devsim.set_parameter(device=device, region=region, name="N_t_irr_"+name,   value=N_t_irr)
        devsim.set_parameter(device=device, region=region, name="E_t_"+name,   value=E_t)
        r_n = "(v_T * sigma_n_irr_{name})".format(name=name)#c_n
        n_1 = "(N_c * exp(-(E_g/2 - E_t_{name})/k_T0))".format(name=name)#e_n
        r_p = "(v_T * sigma_p_irr_{name})".format(name=name)#c_p
        p_1 = "(N_v * exp(-(E_t_{name} - (-E_g/2))/k_T0))".format(name=name)#e_p
        n_t_irr_n = "+(N_t_irr_{name}*(Electrons*{r_n}+{p_1}*{r_p})/({r_n}*(Electrons+{n_1})+{r_p}*(Holes+{p_1})))".format(name=name,r_n=r_n,n_1=n_1,r_p=r_p,p_1=p_1)
        n_t_irr_p = "+(N_t_irr_{name}*(Holes*{r_p}+{n_1}*{r_n})/({r_n}*(Electrons+{n_1})+{r_p}*(Holes+{p_1})))".format(name=name,r_n=r_n,n_1=n_1,r_p=r_p,p_1=p_1)
        trap_n = "+(v_T * sigma_n_irr_{name})*(N_t_irr_{name}*(Electrons*{r_n}+{p_1}*{r_p})/({r_n}*(Electrons+{n_1})+{r_p}*(Holes+{p_1})))".format(name=name,r_n=r_n,n_1=n_1,r_p=r_p,p_1=p_1)
        trap_p = "+(v_T * sigma_p_irr_{name})*(N_t_irr_{name}*(Holes*{r_p}+{n_1}*{r_n})/({r_n}*(Electrons+{n_1})+{r_p}*(Holes+{p_1})))".format(name=name,r_n=r_n,n_1=n_1,r_p=r_p,p_1=p_1)
        U_r="+(N_t_irr_{name}*{r_n}*{r_p}*(Electrons*Holes-n_i^2)/({r_n}*(Electrons+{n_1})+{r_p}*(Holes+{p_1})))".format(name=name,r_n=r_n,n_1=n_1,r_p=r_p,p_1=p_1)
        TrappedElectrons=TrappedElectrons+n_t_irr_n
        TrappedHoles=TrappedHoles+n_t_irr_p
        Trappingtime_n=Trappingtime_n+trap_n
        Trappingtime_p=Trappingtime_p+trap_p
    CreateNodeModel(device, region, "TrappedElectrons", TrappedElectrons)
    CreateNodeModel(device, region, "TrappedHoles", TrappedHoles)
    for i in ("Electrons", "Holes", "Potential"):
        CreateNodeModelDerivative(device, region, "TrappedElectrons", TrappedElectrons, i)
        CreateNodeModelDerivative(device, region, "TrappedHoles", TrappedHoles, i)
    
    CreateNodeModel(device, region, "U_r", U_r)
    for i in ("Electrons", "Holes"):
        CreateNodeModelDerivative(device, region, "U_r", U_r, i)

    CreateNodeModel(device, region, "Trappingtime_n", Trappingtime_n)
    CreateNodeModel(device, region, "Trappingtime_p", Trappingtime_p)

def CreateIrradiationModel_XingChen(device, region):
    v_T = 1e7
    E_g=1.12*1.6e-19
    N_c=2.8e19
    N_v=1.1e19
    k = 1.3806503e-23  # J/K
    T0 = 254.0         # K
    
    devsim.set_parameter(device=device, region=region, name="v_T",   value=v_T)
    devsim.set_parameter(device=device, region=region, name="k_T0",   value=k*T0)
    devsim.set_parameter(device=device, region=region, name="E_g",   value=E_g)
    devsim.set_parameter(device=device, region=region, name="N_c",   value=N_c)
    devsim.set_parameter(device=device, region=region, name="N_v",   value=N_v)

    names        = ["DA1"     , "DA2"          , "DD1"       , "DD2"    ]
    E_ts_ev      = [0.56-0.42 , 0.56-0.46      , -0.56+0.36  ,-0.56+0.48]
    g_ints       = [ 0.239*2 ,    0.09*2       ,  0.025*2     ,0.321*2  ] # cm^-1
    sigma_n_irrs = [1e-15      ,    7e-15      ,   3.23e-13  ,4.166e-15 ]
    sigma_p_irrs = [1e-14      ,     7e-14     ,   3.23e-14  ,1.965e-16 ]

    return defects

def CreateIrradiationModel_Perugia(device, region):

    # imaginary defect: perugia model
    
    sigma_e_acc1=1e-15
    sigma_h_acc1=1e-14
    sigma_e_acc2=7e-15
    sigma_h_acc2=7e-14
    eta_acc1=1.613
    eta_acc2=0.9
    sigma_e_donor=3.23e-13
    sigma_h_donor=3.23e-14
    eta_donor=0.9
    
    E_acc1=0.42*1.6e-19
    E_acc2=0.46*1.6e-19
    E_donor=0.36*1.6e-19
    
    N_t_acc1 = flux*eta_acc1
    N_t_acc2 = flux*eta_acc2
    N_t_donor = flux*eta_donor
    
    Ec=4.05*1.6e-19
    Ev=5.17*1.6e-19
    E_ts_acc1=Ec-0.42*1.6e-19
    E_ts_acc2=Ec-0.46*1.6e-19
    E_ts_donor=Ev+0.36*1.6e-19
    
    devsim.add_db_entry(material="Silicon",   parameter="sigma_e_acc1",     value=sigma_e_acc1,   unit="cm^(-2)",     description="sigma_e_acc1")
    devsim.add_db_entry(material="Silicon",   parameter="sigma_h_acc1",     value=sigma_h_acc1,   unit="cm^(-2)",     description="sigma_h_acc1")
    devsim.add_db_entry(material="Silicon",   parameter="sigma_e_acc2",     value=sigma_e_acc2,   unit="cm^(-2)",     description="sigma_e_acc2")
    devsim.add_db_entry(material="Silicon",   parameter="sigma_h_acc2",     value=sigma_h_acc2,   unit="cm^(-2)",     description="sigma_h_acc2")
    devsim.add_db_entry(material="Silicon",   parameter="sigma_e_donor",     value=sigma_e_donor,   unit="cm^(-2)",     description="sigma_e_donor")
    devsim.add_db_entry(material="Silicon",   parameter="sigma_h_donor",     value=sigma_h_donor,   unit="cm^(-2)",     description="sigma_h_donor")
    devsim.add_db_entry(material="Silicon",   parameter="eta_acc1",     value=eta_acc1,   unit="cm^(-1)",     description="eta_acc1")
    devsim.add_db_entry(material="Silicon",   parameter="eta_acc2",     value=eta_acc2,   unit="cm^(-1)",     description="eta_acc2")
    devsim.add_db_entry(material="Silicon",   parameter="eta_donor",     value=eta_donor,   unit="cm^(-1)",     description="eta_donor")

    devsim.add_db_entry(material="Silicon",   parameter="N_t_acc1",     value=N_t_acc1,   unit="cm^(-3)",     description="N_t_acc1")
    devsim.add_db_entry(material="Silicon",   parameter="N_t_acc2",     value=N_t_acc2,   unit="cm^(-3)",     description="N_t_acc2")
    devsim.add_db_entry(material="Silicon",   parameter="N_t_donor",     value=N_t_donor,   unit="cm^(-3)",     description="N_t_donor")
    devsim.add_db_entry(material="Silicon",   parameter="E_acc1",     value=E_acc1,   unit="J",     description="E_acc1")
    devsim.add_db_entry(material="Silicon",   parameter="E_acc2",     value=E_acc2,   unit="J",     description="E_acc2")
    devsim.add_db_entry(material="Silicon",   parameter="E_donor",     value=E_donor,   unit="J",     description="E_donor")
    devsim.add_db_entry(material="Silicon",   parameter="E_g",     value=1.12*1.6e-19,   unit="J",     description="E_g")
    devsim.add_db_entry(material="Silicon",   parameter="E_ts_acc1",     value=E_ts_acc1,   unit="J",     description="The real value of the defect")
    devsim.add_db_entry(material="Silicon",   parameter="E_ts_acc2",     value=E_ts_acc2,   unit="J",     description="The real value of the defect")
    devsim.add_db_entry(material="Silicon",   parameter="E_ts_donor",     value=E_ts_donor,   unit="J",     description="The real value of the defect")
    v_T=1e7
    devsim.add_db_entry(material="Silicon",   parameter="v_T",     value=v_T,   unit="cm/s",     description="v_T")
    devsim.add_db_entry(material="Silicon",   parameter="v_T_elec",     value=v_T,   unit="cm/s",     description="v_T_elec")
    devsim.add_db_entry(material="Silicon",   parameter="v_T_hole",     value=v_T,   unit="cm/s",     description="v_T_hole")
    
    r_n_donor = "(v_T * sigma_e_donor)"
    r_p_donor = "(v_T * sigma_h_donor)"
    r_n_acc1= "(v_T * sigma_e_acc1)"
    r_p_acc1= "(v_T * sigma_h_acc1)"
    r_n_acc2= "(v_T * sigma_e_acc2)"
    r_p_acc2= "(v_T * sigma_h_acc2)"
    n_1_donor = "(N_c * exp(-(E_g/2 - E_ts_donor)/k_T0))"
    p_1_donor = "(N_v * exp(-(E_ts_donor - (-E_g/2))/k_T0))"
    n_1_acc1 = "(N_c * exp(-(E_g/2 - E_ts_acc1)/k_T0))"
    p_1_acc1 = "(N_v * exp(-(E_ts_acc1 - (-E_g/2))/k_T0))"
    n_1_acc2 = "(N_c * exp(-(E_g/2 - E_ts_acc2)/k_T0))"
    p_1_acc2 = "(N_v * exp(-(E_ts_acc2- (-E_g/2))/k_T0))"

    n_t_donor_n = "+(N_t_donor*(Electrons*{r_n_donor}+{p_1_donor}*{r_p_donor})/({r_n_donor}*(Electrons+{n_1_donor})+{r_p_donor}*(Holes+{p_1_donor})))".format(r_n_donor=r_n_donor,n_1_donor=n_1_donor,r_p_donor=r_p_donor,p_1_donor=p_1_donor)
    n_t_donor_p = "+(N_t_donor - {n_t_donor_n})".format(n_t_donor_n=n_t_donor_n)
    
    n_t_acc1_n = "+(N_t_acc1*(Electrons*{r_n_acc1}+{p_1_acc1}*{r_p_acc1})/({r_n_acc1}*(Electrons+{n_1_acc1})+{r_p_acc1}*(Holes+{p_1_acc1})))".format(r_n_acc1=r_n_acc1,n_1_acc1=n_1_acc1,r_p_acc1=r_p_acc1,p_1_acc1=p_1_acc1)
    n_t_acc1_p = "+(N_t_acc1 - {n_t_acc1_n})".format(n_t_acc1_n=n_t_acc1_n)
    
    n_t_acc2_n = "+(N_t_acc2*(Electrons*{r_n_acc2}+{p_1_acc2}*{r_p_acc2})/({r_n_acc2}*(Electrons+{n_1_acc2})+{r_p_acc2}*(Holes+{p_1_acc2})))".format(r_n_acc2=r_n_acc2,n_1_acc2=n_1_acc2,r_p_acc2=r_p_acc2,p_1_acc2=p_1_acc2)
    n_t_acc2_p = "+(N_t_acc2 - {n_t_acc2_n})".format(n_t_acc2_n=n_t_acc2_n)
    
    n_t_irr_n = n_t_donor_n + n_t_acc1_n + n_t_acc2_n
    n_t_irr_p = n_t_donor_p + n_t_acc1_p + n_t_acc2_p
    # #R_t_irr += "+(N_t_irr_{name} * ({c_n} * Electrons * {c_p} * Holes - {e_n} * {e_p})/({c_n} * Electrons + {e_n} + {c_p} * Holes + {e_p}))".format(name=name,c_n=c_n,e_n=e_n,c_p=c_p,e_p=e_p)
    # R_t_irr += "+(sigma_n_irr_{name}*sigma_p_irr_{name}*v_T*N_t_irr_{name}*(Electrons*Holes - n_i^2))/(sigma_n_irr_{name}*(Electrons - n1*exp(-(E_g/2 - E_t_{name})/k_T0)) + sigma_p_irr_{name}*(Holes + p1*exp(-(E_t_{name} - (-E_g/2))/k_T0)))".format(name=name)


    CreateNodeModel(device, region, "TrappedElectrons", n_t_irr_n)
    CreateNodeModel(device, region, "TrappedHoles", n_t_irr_p)
    #CreateNodeModel(device, region, "R_t_irr", R_t_irr)
    for i in ("Electrons", "Holes", "Potential"):
        CreateNodeModelDerivative(device, region, "TrappedElectrons", n_t_irr_n, i)
        CreateNodeModelDerivative(device, region, "TrappedHoles", n_t_irr_p, i)
        #CreateNodeModelDerivative(device, region, "R_t_irr", R_t_irr, i)
    
    k = 1.3806503e-23  # J/K
    T0 = 300.0         # K    
    devsim.add_db_entry(material="Silicon",   parameter="kT0",    value=k*T0,       unit="J",        description="k*T0")
    
    e_acc1_posi= "(exp(E_acc1 / V_T0))"  #T0 = 300K
    e_acc1_nega= "(exp(-(E_acc1 / V_T0)))" 
    e_acc2_posi= "(exp(E_acc2 / V_T0))"  
    e_acc2_nega= "(exp(-(E_acc2 / V_T0)))" 
    e_donor_posi= "(exp(E_donor / V_T0))"  
    e_donor_nega= "(exp(-(E_donor / V_T0)))"  
    
    R_acc1_up = "(v_T_hole *v_T_elec * sigma_e_acc1 * sigma_h_acc1 * N_t_acc1 * (Electrons*Holes - n_i * n_i))"
    R_acc1_down1 = "(v_T_elec * sigma_e_acc1 *(Electrons + n_i *{e_acc1_posi}))".format(e_acc1_posi=e_acc1_posi)
    R_acc1_down2 = "(v_T_hole * sigma_h_acc1 *(Holes + n_i *{e_acc1_nega}))".format(e_acc1_nega=e_acc1_nega)
    R_acc1 = "{R_acc1_up}/({R_acc1_down1}+{R_acc1_down2})".format(R_acc1_up=R_acc1_up,R_acc1_down1=R_acc1_down1,R_acc1_down2=R_acc1_down2)
    
    R_acc2_up = "(v_T_hole *v_T_elec * sigma_e_acc2 * sigma_h_acc2 * N_t_acc2 * (Electrons*Holes - n_i * n_i))"
    R_acc2_down1 = "(v_T_elec * sigma_e_acc2 *(Electrons + n_i *{e_acc2_posi}))".format(e_acc2_posi=e_acc2_posi)
    R_acc2_down2 = "(v_T_hole * sigma_h_acc2 *(Holes + n_i *{e_acc2_nega}))".format(e_acc2_nega=e_acc2_nega)
    R_acc2 = "{R_acc2_up}/({R_acc2_down1}+{R_acc2_down2})".format(R_acc2_up=R_acc2_up,R_acc2_down1=R_acc2_down1,R_acc2_down2=R_acc2_down2)
    
    R_donor_up = "(v_T_hole *v_T_elec * sigma_e_donor * sigma_h_donor * N_t_donor * (Electrons*Holes - n_i * n_i))"
    R_donor_down1 = "(v_T_elec * sigma_e_donor *(Electrons + n_i *{e_donor_posi}))".format(e_donor_posi=e_donor_posi)
    R_donor_down2 = "(v_T_hole * sigma_h_donor *(Holes + n_i *{e_donor_nega}))".format(e_donor_nega=e_donor_nega)
    R_donor = "{R_donor_up}/({R_donor_down1}+{R_donor_down2})".format(R_donor_up=R_donor_up,R_donor_down1=R_donor_down1,R_donor_down2=R_donor_down2)
    #print("\n\n\n\n"+R_donor+"\n\n\n\n")
    
    R_irr="{R_donor}+{R_acc1}+{R_acc2}".format(R_donor=R_donor,R_acc1=R_acc1,R_acc2=R_acc2)

    CreateNodeModel(device, region, "R_irr", R_irr)
    for i in ("Electrons", "Holes", "Potential"):
        CreateNodeModelDerivative(device, region, "R_irr", R_irr, i)
    
    #Gd = "-q * (USRH+{R_donor})".format(R_donor=R_donor)  #Gd -q
    #Ga = "+q * (USRH+{R_acc1}+{R_acc2})".format(R_acc1=R_acc1,R_acc2=R_acc2)
    if Rirr==None:
        R_irr="0"
    else:
        R_irr=Rirr
    Gd = "-q * (USRH+{R_irr})".format(R_irr=R_irr)  #donor -q
    Ga = "+q * (USRH+{R_irr})".format(R_irr=R_irr)

    return defects

def CreateIrradiationModel_Schwandt(device, region):
    names        = ["E30K"   , "V3"      , "Ip"      , "H220"    , "CiOi"    ]
    E_ts_ev      = [0.56-0.1 , 0.56-0.458, 0.56-0.545, -0.56+0.48, -0.56+0.36]
    g_ints       = [0.0497   , 0.6447    , 0.4335    , 0.5978    , 0.3780    ] # cm^-1
    sigma_n_irrs = [2.300e-14, 2.551e-14 , 4.478e-15 , 4.166e-15 , 3.230e-17 ]
    sigma_p_irrs = [2.920e-16, 1.551e-13 , 6.709e-15 , 1.965e-16 , 2.036e-14 ]

    return defects


def CreateSRH1(device, region):
    '''
    Add defect Z 1 / 2
    '''
    sigma_n=3e-16
    sigma_p=2e-12
    N_t=0
    v_T=1e7
    devsim.add_db_entry(material="SiliconCarbide",   parameter="sigma_n",     value=sigma_n,   unit="s/cm^2",     description="sigma_n")
    devsim.add_db_entry(material="SiliconCarbide",   parameter="sigma_p",     value=sigma_p,   unit="s/cm^2",     description="sigma_p")
    devsim.add_db_entry(material="SiliconCarbide",   parameter="N_t",     value=N_t,   unit="cm^(-3)",     description="N_t")
    devsim.add_db_entry(material="SiliconCarbide",   parameter="v_T",     value=v_T,   unit="cm/s",     description="v_T")
    R_z="(sigma_n*sigma_p*v_T*N_t*(Electrons*Holes - n_i^2))/(sigma_n*(Electrons - n1*exp(1.6e-19/(k_T0))) + sigma_p*(Holes + p1*exp(1.6e-19/(k_T0))))"
    CreateNodeModel(device, region, "R_z", R_z)
    for i in ("Electrons", "Holes"):
        CreateNodeModelDerivative(device, region, "R_z", R_z, i)

def CreateSRH2(device, region):
    '''
    Add defect EH 6 / 7
    '''
    sigma_n_HS6=2e-17
    sigma_p_HS6=3e-17
    N_t_HS6=0
    v_T=1e7
    devsim.add_db_entry(material="SiliconCarbide",   parameter="sigma_n_HS6",     value=sigma_n_HS6,   unit="s/cm^2",     description="sigma_n_HS6")
    devsim.add_db_entry(material="SiliconCarbide",   parameter="sigma_p_HS6",     value=sigma_p_HS6,   unit="s/cm^2",     description="sigma_p_HS6")
    devsim.add_db_entry(material="SiliconCarbide",   parameter="N_t_HS6",     value=N_t_HS6,   unit="cm^(-3)",     description="N_t_HS6")
    devsim.add_db_entry(material="SiliconCarbide",   parameter="v_T",     value=v_T,   unit="cm/s",     description="v_T")
    R_h6="(sigma_n_HS6*sigma_p_HS6*v_T*N_t_HS6*(Electrons*Holes - n_i^2))/(sigma_n_HS6*(Electrons - n1*exp(4.8e-22/(k_T0))) + sigma_p_HS6*(Holes + p1*exp(4.8e-22/(k_T0))))"
    CreateNodeModel(device, region, "R_h6", R_h6)
    for i in ("Electrons", "Holes"):
        CreateNodeModelDerivative(device, region, "R_h6", R_h6, i)