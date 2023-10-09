#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import driftdiffusion_2d 
import node_in_2d
import devsim
#TODO: make this a class so that paramters can be changed
contactcharge_node="contactcharge_node"
contactcharge_edge="contactcharge_edge"
ece_name="ElectronContinuityEquation"
hce_name="HoleContinuityEquation"
celec_model = "(1e-10 + 0.5*abs(NetDoping+(NetDoping^2 + 4 * n_i^2)^(0.5)))"
chole_model = "(1e-10 + 0.5*abs(-NetDoping+(NetDoping^2 + 4 * n_i^2)^(0.5)))"
q      = 1.6e-19 # coul
k      = 1.3806503e-23 # J/K
eps_0  = 8.85e-14 # F/cm^2
#T      = 300 # K
eps_si = 9.76
eps_ox = 3.9
# TODO: make this temperature dependent
n_i    = 3.8e-9 # #/cm^3
# constant in our approximation
mu_n   = 1100
mu_p   = 114
n_a    = 2.1e7
p_a    =  2.96e7
n_b    = 1.7e7
p_b    =  1.6e7
gamma  =  1
k_T0  =4.1419509e-21

sigma_n=3e-16
sigma_p=2e-12
N_t=0
v_T=1e7


sigma_n_HS6=2e-17
sigma_p_HS6=3e-17
N_t_HS6=0

N_c=3250000000000000.0
N_v=4800000000000000.0
E_g=5.216e-19
def GetContactBiasName(contact):
    return "{0}".format(contact)

def GetContactNodeModelName(contact):
    return "{0}nodemodel".format(contact)

def PrintCurrents(device, contact):
    '''
       print out contact currents
    '''
    # TODO add charge
    contact_bias_name = GetContactBiasName(contact)
    electron_current= devsim.get_contact_current(device=device, contact=contact, equation=ece_name)
    hole_current    = devsim.get_contact_current(device=device, contact=contact, equation=hce_name)
    total_current   = electron_current + hole_current                                        
    voltage         = devsim.get_parameter(device=device, name=GetContactBiasName(contact))
    print("{0}\t{1}\t{2}\t{3}\t{4}".format(contact_bias_name, voltage, electron_current, hole_current, total_current))

#in the future, worry about workfunction
def CreateOxideContact(device, region, contact):
    conteq="Permittivity*ElectricField"
    contact_bias_name  = GetContactBiasName(contact)
    contact_model_name = GetContactNodeModelName(contact)
    eq = "Potential - {0}".format(contact_bias_name)
    devsim.CreateContactNodeModel(device, contact, contact_model_name, eq)
    devsim.CreateContactNodeModelDerivative(device, contact, contact_model_name, eq, "Potential")

    #TODO: make everyone use dfield
    if not devsim.InEdgeModelList(device, region, contactcharge_edge):
        devsim.CreateEdgeModel(device, region, contactcharge_edge, "Permittivity*ElectricField")
        devsim.CreateEdgeModelDerivatives(device, region, contactcharge_edge, "Permittivity*ElectricField", "Potential")

    devsim.contact_equation(device=device, contact=contact, name="PotentialEquation",
                     node_model=contact_model_name, edge_charge_model= contactcharge_edge)




#####
##### Constants
#####
def SetOxideParameters(device, region, T):
    '''
      Sets physical parameters
    '''
    devsim.set_parameter(device=device, region=region, name="Permittivity",   value=eps_ox * eps_0)
    devsim.set_parameter(device=device, region=region, name="ElectronCharge", value=q)

def SetSiliconParameters(device, region, T):
    '''
      Sets physical parameters assuming constants
    '''
    #### TODO: make T a free parameter and T dependent parameters as models
    devsim.set_parameter(device=device, region=region, name="Permittivity",   value=eps_si * eps_0)
    devsim.set_parameter(device=device, region=region, name="ElectronCharge", value=q)
    devsim.set_parameter(device=device, region=region, name="n_i",            value=n_i)
    devsim.set_parameter(device=device, region=region, name="T",              value=T)
    devsim.set_parameter(device=device, region=region, name="kT",             value=k * T)
    devsim.set_parameter(device=device, region=region, name="V_t",            value=k*T/q)
    devsim.set_parameter(device=device, region=region, name="mu_n",           value=mu_n)
    devsim.set_parameter(device=device, region=region, name="mu_p",           value=mu_p)
    devsim.set_parameter(device=device, region=region, name="q",           value=q)
    devsim.set_parameter(device=device, region=region, name="gamma",           value=gamma)
    devsim.set_parameter(device=device, region=region, name="k_T0",           value=k_T0)
    #default SRH parameters
    devsim.set_parameter(device=device, region=region, name="n1", value=n_i)
    devsim.set_parameter(device=device, region=region, name="p1", value=n_i)
    devsim.set_parameter(device=device, region=region, name="taun", value=2.5e-6)
    devsim.set_parameter(device=device, region=region, name="taup", value=5e-7)
    devsim.set_parameter(device=device, region=region, name="n_a", value=n_a)
    devsim.set_parameter(device=device, region=region, name="p_a", value=p_a)
    devsim.set_parameter(device=device, region=region, name="n_b", value=n_b)
    devsim.set_parameter(device=device, region=region, name="p_b", value=p_b)

    
    #default SRH1 parameters
    devsim.set_parameter(device=device, region=region, name="sigma_n", value=sigma_n)
    devsim.set_parameter(device=device, region=region, name="sigma_p", value=sigma_p)
    devsim.set_parameter(device=device, region=region, name="N_t", value=N_t)
    devsim.set_parameter(device=device, region=region, name="v_T", value=v_T)


    #default SRH2 parameters
    devsim.set_parameter(device=device, region=region, name="sigma_n_HS6", value=sigma_n_HS6)
    devsim.set_parameter(device=device, region=region, name="sigma_p_HS6", value=sigma_p_HS6)
    devsim.set_parameter(device=device, region=region, name="N_t_HS6", value=N_t_HS6)



    devsim.set_parameter(device=device, region=region, name="N_v", value=N_v)
    devsim.set_parameter(device=device, region=region, name="E_g", value=E_g)
    devsim.set_parameter(device=device, region=region, name="N_c", value=N_c)





def CreateSiliconPotentialOnly(device, region):
    '''
      Creates the physical models for a Silicon region
    '''
    if not node_in_2d.InNodeModelList(device, region, "Potential"):
        print("Creating Node Solution Potential")
        node_in_2d.CreateSolution(device, region, "Potential")
    elec_i = "n_i*exp(Potential/V_t)"
    hole_i = "n_i*exp(-Potential/V_t)"
    #hole_i = "n_i^2/IntrinsicElectrons"
    charge_i = "kahan3(IntrinsicHoles, -IntrinsicElectrons, NetDoping)"
    pcharge_i = "-ElectronCharge * IntrinsicCharge"

    # require NetDoping
    for i in (
        ("IntrinsicElectrons", elec_i),
         ("IntrinsicHoles", hole_i),
         ("IntrinsicCharge", charge_i),
         ("PotentialIntrinsicCharge", pcharge_i)
    ):
        n = i[0]
        e = i[1]
        node_in_2d.CreateNodeModel(device, region, n, e)
        node_in_2d.CreateNodeModelDerivative(device, region, n, e, "Potential")

    ### TODO: Edge Average Model
    for i in (
        ("ElectricField",     "(Potential@n0-Potential@n1)*EdgeInverseLength"),
      ("PotentialEdgeFlux", "Permittivity * ElectricField")
    ):
        n = i[0]
        e = i[1]
        node_in_2d.CreateEdgeModel(device, region, n, e)
        node_in_2d.CreateEdgeModelDerivatives(device, region, n, e, "Potential")

    devsim.equation(device=device, region=region, name="PotentialEquation", variable_name="Potential",
             node_model="PotentialIntrinsicCharge", edge_model="PotentialEdgeFlux", variable_update="log_damp")

def CreateSiliconPotentialOnlyContact(device, region, contact, is_circuit=False):
    '''
      Creates the potential equation at the contact
      if is_circuit is true, than use node given by GetContactBiasName
    '''
    # Means of determining contact charge
    # Same for all contacts
    if not node_in_2d.InNodeModelList(device, region, "contactcharge_node"):
        node_in_2d.CreateNodeModel(device, region, "contactcharge_node", "ElectronCharge*IntrinsicCharge")
    #### TODO: This is the same as D-Field
    if not node_in_2d.InEdgeModelList(device, region, "contactcharge_edge"):
        node_in_2d.CreateEdgeModel(device, region, "contactcharge_edge", "Permittivity*ElectricField")
        node_in_2d.CreateEdgeModelDerivatives(device, region, "contactcharge_edge", "Permittivity*ElectricField", "Potential")

#  devsim.set_parameter(device=device, region=region, name=GetContactBiasName(contact), value=0.0)

    contact_model = "Potential -{0} + ifelse(NetDoping > 0, \
    -V_t*log({1}/n_i), \
    V_t*log({2}/n_i))".format(GetContactBiasName(contact), celec_model, chole_model)

    contact_model_name = GetContactNodeModelName(contact)
    node_in_2d.CreateContactNodeModel(device, contact, contact_model_name, contact_model)
    # Simplify it too complicated
    node_in_2d.CreateContactNodeModel(device, contact, "{0}:{1}".format(contact_model_name,"Potential"), "1")
    if is_circuit:
        node_in_2d.CreateContactNodeModel(device, contact, "{0}:{1}".format(contact_model_name,GetContactBiasName(contact)), "-1")

    if is_circuit:
        devsim.contact_equation(device=device, contact=contact, name="PotentialEquation",
                         node_model=contact_model_name, edge_model="",
                         node_charge_model="", edge_charge_model="contactcharge_edge",
                         #node_charge_model="contactcharge_node", edge_charge_model="contactcharge_edge",
                         node_current_model="", edge_current_model="", circuit_node=GetContactBiasName(contact))
    else:
        devsim.contact_equation(device=device, contact=contact, name="PotentialEquation",
                         node_model=contact_model_name, edge_model="",
                         node_charge_model="", edge_charge_model="contactcharge_edge",
                         #node_charge_model="contactcharge_node", edge_charge_model="contactcharge_edge",
                         node_current_model="", edge_current_model="")

#add srh1&2
def CreateSRH1(device, region):
    '''
    Add defect Z 1 / 2
    '''
    R_z="(sigma_n*sigma_p*v_T*N_t*(Electrons*Holes - n_i^2))/(sigma_n*(Electrons - n1*exp(1.6e-19/(k_T0))) + sigma_p*(Holes + p1*exp(1.6e-19/(k_T0))))"
    node_in_2d.CreateNodeModel(device, region, "R_z", R_z)
    for i in ("Electrons", "Holes"):
        node_in_2d.CreateNodeModelDerivative(device, region, "R_z", R_z, i)

def CreateSRH2(device, region):
    '''
    Add defect EH 6 / 7
    '''
   
    R_h6="(sigma_n_HS6*sigma_p_HS6*v_T*N_t_HS6*(Electrons*Holes - n_i^2))/(sigma_n_HS6*(Electrons - n1*exp(4.8e-22/(k_T0))) + sigma_p_HS6*(Holes + p1*exp(4.8e-22/(k_T0))))"
    node_in_2d.CreateNodeModel(device, region, "R_h6", R_h6)
    for i in ("Electrons", "Holes"):
        node_in_2d.CreateNodeModelDerivative(device, region, "R_h6", R_h6, i)
          





def CreateSRH(device, region):
    #CreateSRH1(device,region)
    #CreateSRH2(device,region)
    USRH="-q*(Electrons*Holes - n_i^2)/(taup*(Electrons + n1) + taun*(Holes + p1))"
    #半导体器件仿真内的shr模型是n乘n，p乘p
    #USRH="-q*(Electrons*Holes - n_i^2)/(taun*(Electrons + n1) + taup*(Holes + p1))"
    #Gn = "-ElectronCharge * USRH"
    #Gp = "+ElectronCharge * USRH"
    Gn = "-q * (USRH -1e16) "
    Gp = "+q * (USRH -1e16)"
    node_in_2d.CreateNodeModel(device, region, "USRH", USRH)
    node_in_2d.CreateNodeModel(device, region, "ElectronGeneration", Gn)
    node_in_2d.CreateNodeModel(device, region, "HoleGeneration", Gp)
    for i in ("Electrons", "Holes"):
        node_in_2d.CreateNodeModelDerivative(device, region, "USRH", USRH, i)
        node_in_2d.CreateNodeModelDerivative(device, region, "ElectronGeneration", Gn, i)
        node_in_2d.CreateNodeModelDerivative(device, region, "HoleGeneration", Gp, i)



def CreateImpactGeneration(device, region):
   
  
    #Ion_coeff_p  = "gamma * p_a * exp( - gamma * p_b / (ElectricField))"

    Ion_coeff_n  = "ifelse(abs(ElectricField)>1e4, gamma * n_a * exp( - gamma * n_b / (abs(ElectricField)+1)), 1)"
    Ion_coeff_p  = "ifelse(abs(ElectricField)>1e4, gamma * p_a * exp( - gamma * p_b / (abs(ElectricField)+1)), 1)"

    Ion_coeff_rate = "(Ion_coeff_n*(abs(ElectronCurrent))+Ion_coeff_p*(abs(HoleCurrent)))/q"

    node_in_2d.CreateEdgeModel(device, region, "Ion_coeff_n", Ion_coeff_n)
    node_in_2d.CreateEdgeModelDerivatives(device, region, "Ion_coeff_n", Ion_coeff_n, "Potential")
    node_in_2d.CreateEdgeModel(device, region, "Ion_coeff_p", Ion_coeff_p)
    node_in_2d.CreateEdgeModelDerivatives(device, region, "Ion_coeff_p", Ion_coeff_p, "Potential")
 
    ImpactGen_n = "+q*%s"%(Ion_coeff_rate)
    ImpactGen_p = "-q*%s"%(Ion_coeff_rate)

    node_in_2d.CreateEdgeModel(device, region, "ImpactGen_n", ImpactGen_n)
    node_in_2d.CreateEdgeModelDerivatives(device, region, "ImpactGen_n", ImpactGen_n, "Potential")
    node_in_2d.CreateEdgeModelDerivatives(device, region, "ImpactGen_n", ImpactGen_n, "Electrons")
    node_in_2d.CreateEdgeModelDerivatives(device, region, "ImpactGen_n", ImpactGen_n, "Holes")
    
    node_in_2d.CreateEdgeModel(device, region, "ImpactGen_p", ImpactGen_p)
    node_in_2d.CreateEdgeModelDerivatives(device, region, "ImpactGen_p", ImpactGen_p, "Potential")
    node_in_2d.CreateEdgeModelDerivatives(device, region, "ImpactGen_p", ImpactGen_p, "Electrons")
    node_in_2d.CreateEdgeModelDerivatives(device, region, "ImpactGen_p", ImpactGen_p, "Holes")
    #devsim.edge_model(device=device,region=region,name="ImpactGen_p:Potential",equation="-ImpactGen_n:Potential")
'''
#Netgeneration
def CreateNetGeneration(device, region):

    Gn = "-q * (USRH - 1e12)"
    Gp = "+q * (USRH - 1e12)"

    #Gn = "-q * (USRH - 1e18*x*x)"
    #Gp = "+q * (USRH - 1e18*x*x)"

    #Gn = "-q * (USRH)"
    #Gp = "+q * (USRH)"

    node_in_2d.CreateNodeModel(device, region, "ElectronGeneration", Gn)
    node_in_2d.CreateNodeModel(device, region, "HoleGeneration", Gp)

    for i in ("Electrons", "Holes"):
        node_in_2d.CreateNodeModelDerivative(device, region, "ElectronGeneration", Gn, i)
        node_in_2d.CreateNodeModelDerivative(device, region, "HoleGeneration", Gp, i)

'''


def CreateECE(device, region, mu_n):
    driftdiffusion_2d.CreateElectronCurrent(device, region, mu_n)

    NCharge = "-ElectronCharge * Electrons"
    node_in_2d.CreateNodeModel(device, region, "NCharge", NCharge)
    node_in_2d.CreateNodeModelDerivative(device, region, "NCharge", NCharge, "Electrons")
    #addimpact
    CreateImpactGeneration(device, region)
    '''
    devsim.equation(device=device, region=region, name="ElectronContinuityEquation", variable_name="Electrons",
             time_node_model = "NCharge",
             edge_model="ElectronCurrent", variable_update="positive", node_model="ElectronGeneration")
    '''
    devsim.equation(device=device, region=region, name="ElectronContinuityEquation", variable_name="Electrons",
             time_node_model = "NCharge",
             edge_model="ElectronCurrent", variable_update="positive", 
             node_model="ElectronGeneration", 
             edge_volume_model="ImpactGen_n"
             )

'''
#addirrdefect

def CreateIrradiatedCharge(device, region, Neutron_eq=1e9):

    #Add Deep Levels from Irradiated Defect 
    #able to Catch Carriers Directly and Keep Them Trapped
  
    
    names        = ["E30K"   , "V3"      , "Ip"      , "H220"    , "CiOi"    ]
    E_ts_ev      = [0.56-0.1 , 0.56-0.458, 0.56-0.545, -0.56+0.48, -0.56+0.36]
    g_ints       = [0.0497   , 0.6447    , 0.4335    , 0.5978    , 0.3780    ] # cm^-1
    sigma_n_irrs = [2.300e-14, 2.551e-14 , 4.478e-15 , 4.166e-15 , 3.230e-17 ]
    sigma_p_irrs = [2.920e-16, 1.551e-13 , 6.709e-15 , 1.965e-16 , 2.036e-14 ]

    n_t_irr_n = "0"
    n_t_irr_p = "0"
    R_t_irr = "0"
    
    for nametype, E_t_ev, g_int, sigma_n_irr, sigma_p_irr in zip(names, E_ts_ev, g_ints, sigma_n_irrs, sigma_p_irrs):
        E_t = E_t_ev * q
        N_t_irr = g_int*Neutron_eq
        

        devsim.set_parameter(device=device, region=region, name="sigma_n_irr_{nametype}".format(nametype=nametype), value=sigma_n_irr)
        devsim.set_parameter(device=device, region=region, name="sigma_p_irr_{nametype}".format(nametype=nametype), value=sigma_p_irr)
        devsim.set_parameter(device=device, region=region, name="N_t_irr_{nametype}".format(nametype=nametype), value=N_t_irr)
        devsim.set_parameter(device=device, region=region, name="E_t_{nametype}".format(nametype=nametype), value=E_t)
       
        r_n = "(v_T * sigma_n_irr_{name})".format(name=nametype)#c_n
        n_1 = "(N_c * exp(-(E_g/2 - E_t_{name})/k_T0))".format(name=nametype)#e_n
        r_p = "(v_T * sigma_p_irr_{name})".format(name=nametype)#c_p
        p_1 = "(N_v * exp(-(E_t_{name} - (-E_g/2))/k_T0))".format(name=nametype)#e_p

        #n_t_irr_n += "+(N_t_irr_{name}".format(name=name)
        n_t_irr_n += "+(N_t_irr_{name}*(Electrons*{r_n}+{p_1}*{r_p})/({r_n}*(Electrons+{n_1})+{r_p}*(Holes+{p_1})))".format(name=nametype,r_n=r_n,n_1=n_1,r_p=r_p,p_1=p_1)
        n_t_irr_p += "+(N_t_irr_{name} - {n_t_irr_n})".format(name=nametype,n_t_irr_n=n_t_irr_n)
        #R_t_irr += "+(N_t_irr_{name} * ({c_n} * Electrons * {c_p} * Holes - {e_n} * {e_p})/({c_n} * Electrons + {e_n} + {c_p} * Holes + {e_p}))".format(name=name,c_n=c_n,e_n=e_n,c_p=c_p,e_p=e_p)
        R_t_irr += "+(sigma_n_irr_{name}*sigma_p_irr_{name}*v_T*N_t_irr_{name}*(Electrons*Holes - n_i^2))/(sigma_n_irr_{name}*(Electrons - n1*exp(-(E_g/2 - E_t_{name})/k_T0)) + sigma_p_irr_{name}*(Holes + p1*exp(-(E_t_{name} - (-E_g/2))/k_T0)))".format(name=nametype)

    node_in_2d.CreateNodeModel(device, region, "TrappedElectrons", n_t_irr_n)
    node_in_2d.CreateNodeModel(device, region, "TrappedHoles", n_t_irr_p)
    node_in_2d.CreateNodeModel(device, region, "R_t_irr", R_t_irr)
    for i in ("Electrons", "Holes", "Potential"):
        node_in_2d.CreateNodeModelDerivative(device, region, "TrappedElectrons", n_t_irr_n, i)
        node_in_2d.CreateNodeModelDerivative(device, region, "TrappedHoles", n_t_irr_p, i)
        node_in_2d.CreateNodeModelDerivative(device, region, "R_t_irr", R_t_irr, i)


'''





def CreateHCE(device, region, mu_p):
    driftdiffusion_2d.CreateHoleCurrent(device, region, mu_p)
    PCharge = "ElectronCharge * Holes"
    node_in_2d.CreateNodeModel(device, region, "PCharge", PCharge)
    node_in_2d.CreateNodeModelDerivative(device, region, "PCharge", PCharge, "Holes")
    #addimpact
    CreateImpactGeneration(device, region)
    '''
    devsim.equation(device=device, region=region, name="HoleContinuityEquation", variable_name="Holes",
             time_node_model = "PCharge",
             edge_model="HoleCurrent", variable_update="positive", node_model="HoleGeneration")
    '''
    devsim.equation(device=device, region=region, name="HoleContinuityEquation", variable_name="Holes",
             time_node_model = "PCharge",
             edge_model="HoleCurrent", variable_update="positive", 
             node_model="HoleGeneration", 
             edge_volume_model="ImpactGen_p"
             )


def CreatePE(device, region):
    #CreateIrradiatedCharge(device,region)
    pne = "-ElectronCharge*kahan3(Holes, -Electrons, NetDoping)"
    #pne = "-q*kahan3(Holes, -Electrons, kahan3(NetDoping, TrappedHoles, -TrappedElectrons))"
    node_in_2d.CreateNodeModel(device, region, "PotentialNodeCharge", pne)
    node_in_2d.CreateNodeModelDerivative(device, region, "PotentialNodeCharge", pne, "Electrons")
    node_in_2d.CreateNodeModelDerivative(device, region, "PotentialNodeCharge", pne, "Holes")

    devsim.equation(device=device, region=region, name="PotentialEquation", variable_name="Potential",
             node_model="PotentialNodeCharge", edge_model="PotentialEdgeFlux",
             time_node_model="", variable_update="default")



def CreateSiliconDriftDiffusion(device, region, mu_n="mu_n", mu_p="mu_p"):
    #CreateIrradiatedCharge(device,region)
    CreatePE(device, region)
    driftdiffusion_2d.CreateBernoulli(device, region)
    CreateSRH(device, region)
    #CreateNetGeneration(device, region)
    CreateECE(device, region, mu_n)
    CreateHCE(device, region, mu_p)
    
    #CreateImpactGeneration(device, region)


def CreateSiliconDriftDiffusionAtContact(device, region, contact, is_circuit=False): 
    '''
      Restrict electrons and holes to their equilibrium values
      Integrates current into circuit
    '''
    contact_electrons_model = "Electrons - ifelse(NetDoping > 0, {0}, n_i^2/{1})".format(celec_model, chole_model)
    contact_holes_model = "Holes - ifelse(NetDoping < 0, +{1}, +n_i^2/{0})".format(celec_model, chole_model)
    contact_electrons_name = "{0}nodeelectrons".format(contact)
    contact_holes_name = "{0}nodeholes".format(contact)

    node_in_2d.CreateContactNodeModel(device, contact, contact_electrons_name, contact_electrons_model)
    #TODO: The simplification of the ifelse statement is time consuming
#  devsim.CreateContactNodeModelDerivative(device, contact, contact_electrons_name, contact_electrons_model, "Electrons")
    node_in_2d.CreateContactNodeModel(device, contact, "{0}:{1}".format(contact_electrons_name, "Electrons"), "1")

    node_in_2d.CreateContactNodeModel(device, contact, contact_holes_name, contact_holes_model)
    node_in_2d.CreateContactNodeModel(device, contact, "{0}:{1}".format(contact_holes_name, "Holes"), "1")

    #TODO: keyword args
    if is_circuit:
        devsim.contact_equation(device=device, contact=contact, name="ElectronContinuityEquation",
                         node_model=contact_electrons_name,
                         edge_current_model="ElectronCurrent", circuit_node=GetContactBiasName(contact))

        devsim.contact_equation(device=device, contact=contact, name="HoleContinuityEquation",
                         node_model=contact_holes_name,
                         edge_current_model="HoleCurrent", circuit_node=GetContactBiasName(contact))

    else:
        devsim.contact_equation(device=device, contact=contact, name="ElectronContinuityEquation",
                         node_model=contact_electrons_name,
                         edge_current_model="ElectronCurrent")

        devsim.contact_equation(device=device, contact=contact, name="HoleContinuityEquation",
                         node_model=contact_holes_name,
                         edge_current_model="HoleCurrent")

