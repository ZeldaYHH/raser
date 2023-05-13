'''
Description:  Physics.py
@Date       : 2022/10/25 16:40:46
@Author     : Tao Yang
@version    : 1.0
'''

import devsim
from raser.Node import *
from raser.DriftDiffusion import *
import math


#TODO: make this a class so that paramters can be changed
contactcharge_node="contactcharge_node"
contactcharge_edge="contactcharge_edge"
ece_name="ElectronContinuityEquation"
hce_name="HoleContinuityEquation"
celec_model = "(1e-10 + 0.5*abs(NetDoping+(NetDoping^2 + 4 * n_i^2)^(0.5)))"
chole_model = "(1e-10 + 0.5*abs(-NetDoping+(NetDoping^2 + 4 * n_i^2)^(0.5)))"
#celec_model = "(0.5*abs(NetDoping+(NetDoping^2 + 4 * n_i^2)^(0.5)))"
#chole_model = "(0.5*abs(-NetDoping+(NetDoping^2 + 4 * n_i^2)^(0.5)))"


def GetContactBiasName(contact):
    return "{0}_bias".format(contact)



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
    print("{0}\t{1}\t{2}\t{3}\t{4}".format(contact, voltage, electron_current, hole_current, total_current))



def CreateSiliconPotentialOnly(device, region):
    '''
      Creates the physical models for a Silicon region
    '''
    if not InNodeModelList(device, region, "Potential"):
        print("Creating Node Solution Potential")
        CreateSolution(device, region, "Potential")
    elec_i = "n_i*exp(Potential/V_T0)"
    hole_i = "n_i*exp(-Potential/V_T0)"
    #hole_i = "n_i^2/IntrinsicElectrons"
    charge_i = "kahan3(IntrinsicHoles, -IntrinsicElectrons, NetDoping)"
    pcharge_i = "-q * IntrinsicCharge"

    # require NetDoping
    for i in (
        ("IntrinsicElectrons", elec_i),
         ("IntrinsicHoles", hole_i),
         ("IntrinsicCharge", charge_i),
         ("PotentialIntrinsicCharge", pcharge_i)
    ):
        n = i[0]
        e = i[1]
        CreateNodeModel(device, region, n, e)
        CreateNodeModelDerivative(device, region, n, e, "Potential")

    ### TODO: Edge Average Model
    for i in (
        ("ElectricField",     "(Potential@n0-Potential@n1)*EdgeInverseLength"),
        ("PotentialEdgeFlux", "eps_0* eps* ElectricField")
    ):
        n = i[0]
        e = i[1]
        CreateEdgeModel(device, region, n, e)
        CreateEdgeModelDerivatives(device, region, n, e, "Potential")

    devsim.equation(device=device, region=region, name="PotentialEquation", variable_name="Potential",
             node_model="PotentialIntrinsicCharge", edge_model="PotentialEdgeFlux", variable_update="log_damp")



def CreateSiliconPotentialOnlyContact(device, region, contact, is_circuit=False):
    '''
      Creates the potential equation at the contact
      if is_circuit is true, than use node given by GetContactBiasName
    '''
    # Means of determining contact charge
    # Same for all contacts
    if not InNodeModelList(device, region, "contactcharge_node"):
        CreateNodeModel(device, region, "contactcharge_node", "q*IntrinsicCharge")
    #### TODO: This is the same as D-Field
    if not InEdgeModelList(device, region, "contactcharge_edge"):
        CreateEdgeModel(device, region, "contactcharge_edge", "eps_0* eps* ElectricField")
        CreateEdgeModelDerivatives(device, region, "contactcharge_edge", "eps_0* eps* ElectricField", "Potential")


    contact_model = "Potential -{0} + ifelse(NetDoping > 0, \
    -V_T0*log({1}/n_i), \
    V_T0*log({2}/n_i))".format(GetContactBiasName(contact), celec_model, chole_model)

    contact_model_name = GetContactNodeModelName(contact)
    CreateContactNodeModel(device, contact, contact_model_name, contact_model)
    # Simplify it too complicated
    CreateContactNodeModel(device, contact, "{0}:{1}".format(contact_model_name,"Potential"), "1")
    
    if is_circuit:
        CreateContactNodeModel(device, contact, "{0}:{1}".format(contact_model_name,GetContactBiasName(contact)), "-1")

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




def CreateSRH(device, region):
    USRH="(Electrons*Holes - n_i^2)/(tau_p*(Electrons + n1) + tau_n*(Holes + p1))"
    CreateNodeModel(device, region, "USRH", USRH)
    for i in ("Electrons", "Holes"):
        CreateNodeModelDerivative(device, region, "USRH", USRH, i)

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
          

def CreateImpactGenerationSilicon(device, region):
    """
    van Ovenstraeten Model
    """
    # if not InEdgeModelList(device, region, "ElectricField"):
    #     CreateEdgeModel(device, region, "ElectricField", "(Potential@n0-Potential@n1)*EdgeInverseLength")
    #     CreateEdgeModelDerivatives(device, region, "ElectricField", "(Potential@n0-Potential@n1)*EdgeInverseLength", "Potential")


    #Ion_coeff_n  = "gamma * n_a * exp( - gamma * n_b / (ElectricField))"
    #Ion_coeff_p  = "gamma * p_a * exp( - gamma * p_b / (ElectricField))"

    Ion_coeff_n  = "ifelse(abs(ElectricField)>1.75e4, (ifelse(abs(ElectricField)>4e5, gamma * n_a_high * exp( - gamma * n_b_high / (abs(ElectricField)+1)),  gamma * n_a_low * exp( - gamma * n_b_low / (abs(ElectricField)+1)))), 1)"
    Ion_coeff_p  = "ifelse(abs(ElectricField)>1.75e4, (ifelse(abs(ElectricField)>4e5, gamma * p_a_high * exp( - gamma * p_b_high / (abs(ElectricField)+1)),  gamma * p_a_low * exp( - gamma * p_b_low / (abs(ElectricField)+1)))), 1)"

    Ion_coeff_rate = "(Ion_coeff_n*(abs(ElectronCurrent))+Ion_coeff_p*(abs(HoleCurrent)))/q"

    CreateEdgeModel(device, region, "Ion_coeff_n", Ion_coeff_n)
    CreateEdgeModelDerivatives(device, region, "Ion_coeff_n", Ion_coeff_n, "Potential")
    #CreateEdgeModelDerivatives(device, region, "Ion_coeff_n", Ion_coeff_n, "Electrons")
    #CreateEdgeModelDerivatives(device, region, "Ion_coeff_n", Ion_coeff_n, "Holes")
    CreateEdgeModel(device, region, "Ion_coeff_p", Ion_coeff_p)
    CreateEdgeModelDerivatives(device, region, "Ion_coeff_p", Ion_coeff_p, "Potential")
    #CreateEdgeModelDerivatives(device, region, "Ion_coeff_p", Ion_coeff_p, "Electrons")
    #CreateEdgeModelDerivatives(device, region, "Ion_coeff_p", Ion_coeff_p, "Holes")
    #CreateEdgeModel(device, region, "Ion_coeff_rate", Ion_coeff_rate)
    #CreateEdgeModelDerivatives(device, region, "Ion_coeff_rate", Ion_coeff_rate, "Potential")
    
    
    ImpactGen_n = "+q*%s"%(Ion_coeff_rate)
    ImpactGen_p = "-q*%s"%(Ion_coeff_rate)

    CreateEdgeModel(device, region, "ImpactGen_n", ImpactGen_n)
    CreateEdgeModelDerivatives(device, region, "ImpactGen_n", ImpactGen_n, "Potential")
    CreateEdgeModelDerivatives(device, region, "ImpactGen_n", ImpactGen_n, "Electrons")
    CreateEdgeModelDerivatives(device, region, "ImpactGen_n", ImpactGen_n, "Holes")
    
    CreateEdgeModel(device, region, "ImpactGen_p", ImpactGen_p)
    CreateEdgeModelDerivatives(device, region, "ImpactGen_p", ImpactGen_p, "Potential")
    CreateEdgeModelDerivatives(device, region, "ImpactGen_p", ImpactGen_p, "Electrons")
    CreateEdgeModelDerivatives(device, region, "ImpactGen_p", ImpactGen_p, "Holes")
    #devsim.edge_model(device=device,region=region,name="ImpactGen_p:Potential",equation="-ImpactGen_n:Potential")


def CreateImpactGenerationSiliconCarbide(device, region):
    """
    Hatakeyama Model for cutoff angle of 4°
    """

    #hbarOmega = 0.19 # eV
    #k_T0_ev = 0.0257 # eV
    # gamma = math.tanh(0.19/(2*0.0257))/math.tanh(0.19/(2*0.0257*T/T0))
    
    # if not InEdgeModelList(device, region, "ElectricField"):
    #     CreateEdgeModel(device, region, "ElectricField", "(Potential@n0-Potential@n1)*EdgeInverseLength")
    #     CreateEdgeModelDerivatives(device, region, "ElectricField", "(Potential@n0-Potential@n1)*EdgeInverseLength", "Potential")

    cutoff_angle = 4 #degree
    sin_cutoff_angle = math.sin(math.radians(cutoff_angle))
    cos_cutoff_angle = math.cos(math.radians(cutoff_angle))

    if not InEdgeModelList(device, region, "ElectricField_0001"):
        CreateEdgeModel(device, region, "ElectricField_0001", "abs(ElectricField+1)*{0}".format(cos_cutoff_angle))

    if not InEdgeModelList(device, region, "ElectricField_1120"):
        CreateEdgeModel(device, region, "ElectricField_1120", "abs(ElectricField+1)*{0}".format(sin_cutoff_angle))

    if not InEdgeModelList(device, region, "n_B"):
        CreateEdgeModel(device, region, "n_B", "abs(ElectricField+1) / pow( pow( ElectricField_1120/n_b_1120 , 2) + pow( ElectricField_0001/n_b_0001 , 2) , 0.5)")

    if not InEdgeModelList(device, region, "p_B"):
        CreateEdgeModel(device, region, "p_B", "abs(ElectricField+1) / pow( pow( ElectricField_1120/p_b_1120 , 2) + pow( ElectricField_0001/p_b_0001 , 2) , 0.5)")


    if not InEdgeModelList(device, region, "n_a_aniso"):
        CreateEdgeModel(device, region, "n_a_aniso", "pow( n_a_1120, pow( n_B*ElectricField_1120/n_b_1120/abs(ElectricField+1), 2) ) * pow( n_a_0001, pow( n_B*ElectricField_0001/n_b_0001/abs(ElectricField+1), 2) )")

    if not InEdgeModelList(device, region, "p_a_aniso"):
        CreateEdgeModel(device, region, "p_a_aniso", "pow( p_a_1120, pow( p_B*ElectricField_1120/p_b_1120/abs(ElectricField+1), 2) ) * pow( p_a_0001, pow( p_B*ElectricField_0001/p_b_0001/abs(ElectricField+1), 2) )")



    if not InEdgeModelList(device, region, "n_A"):
        CreateEdgeModel(device, region, "n_A", "log(n_a_0001/n_b_1120)")

    if not InEdgeModelList(device, region, "p_A"):
        CreateEdgeModel(device, region, "p_A", "log(p_a_0001/p_b_1120)")

    if not InEdgeModelList(device, region, "n_b_aniso"):
        CreateEdgeModel(device, region, "n_b_aniso", "n_B * pow( 1-pow(n_A,2)* pow( (n_B*ElectricField_1120*ElectricField_0001)/(abs(ElectricField+1)*n_b_1120*n_b_0001), 2), 0.5)")

    if not InEdgeModelList(device, region, "p_b_aniso"):
        CreateEdgeModel(device, region, "p_b_aniso", "p_B * pow( 1-pow(p_A,2)* pow( (p_B*ElectricField_1120*ElectricField_0001)/(abs(ElectricField+1)*p_b_1120*p_b_0001), 2), 0.5)")

    gamma_str = "tanh(0.19/(2*0.0257))/tanh(0.19/(2*0.0257*T/T0))"
    Ion_coeff_n  = "ifelse(abs(ElectricField)>1e4, {0} * n_a_aniso * exp( - {1} * n_b_aniso / (abs(ElectricField)+1)), 1)".format(gamma_str,gamma_str)
    Ion_coeff_p  = "ifelse(abs(ElectricField)>1e4, {0} * p_a_aniso * exp( - {1} * p_b_aniso / (abs(ElectricField)+1)), 1)".format(gamma_str,gamma_str)

    Ion_coeff_rate = "(Ion_coeff_n*(abs(ElectronCurrent))+Ion_coeff_p*(abs(HoleCurrent)))/q"

    CreateEdgeModel(device, region, "Ion_coeff_n", Ion_coeff_n)
    CreateEdgeModelDerivatives(device, region, "Ion_coeff_n", Ion_coeff_n, "Potential")
    #CreateEdgeModelDerivatives(device, region, "Ion_coeff_n", Ion_coeff_n, "Electrons")
    #CreateEdgeModelDerivatives(device, region, "Ion_coeff_n", Ion_coeff_n, "Holes")
    CreateEdgeModel(device, region, "Ion_coeff_p", Ion_coeff_p)
    CreateEdgeModelDerivatives(device, region, "Ion_coeff_p", Ion_coeff_p, "Potential")
    #CreateEdgeModelDerivatives(device, region, "Ion_coeff_p", Ion_coeff_p, "Electrons")
    #CreateEdgeModelDerivatives(device, region, "Ion_coeff_p", Ion_coeff_p, "Holes")
    #CreateEdgeModel(device, region, "Ion_coeff_rate", Ion_coeff_rate)
    #CreateEdgeModelDerivatives(device, region, "Ion_coeff_rate", Ion_coeff_rate, "Potential")
 
    ImpactGen_n = "+q*%s"%(Ion_coeff_rate)
    ImpactGen_p = "-q*%s"%(Ion_coeff_rate)

    CreateEdgeModel(device, region, "ImpactGen_n", ImpactGen_n)
    CreateEdgeModelDerivatives(device, region, "ImpactGen_n", ImpactGen_n, "Potential")
    CreateEdgeModelDerivatives(device, region, "ImpactGen_n", ImpactGen_n, "Electrons")
    CreateEdgeModelDerivatives(device, region, "ImpactGen_n", ImpactGen_n, "Holes")
    
    CreateEdgeModel(device, region, "ImpactGen_p", ImpactGen_p)
    CreateEdgeModelDerivatives(device, region, "ImpactGen_p", ImpactGen_p, "Potential")
    CreateEdgeModelDerivatives(device, region, "ImpactGen_p", ImpactGen_p, "Electrons")
    CreateEdgeModelDerivatives(device, region, "ImpactGen_p", ImpactGen_p, "Holes")
    #devsim.edge_model(device=device,region=region,name="ImpactGen_p:Potential",equation="-ImpactGen_n:Potential")

def CreateImpactGeneration(device, region):
    if devsim.get_material(device=device, region=region) == "Silicon":
        CreateImpactGenerationSilicon(device, region)
    elif devsim.get_material(device=device, region=region) == "SiliconCarbide":
        CreateImpactGenerationSiliconCarbide(device, region)

def CreateTunnelingAndAvalanche(device,region):
    cutoff_angle = 4 #degree
    sin_cutoff_angle = math.sin(math.radians(cutoff_angle))
    cos_cutoff_angle = math.cos(math.radians(cutoff_angle))
    if not InEdgeModelList(device, region, "ElectricField_0001"):
        CreateEdgeModel(device, region, "ElectricField_0001", "abs(ElectricField+1)*{0}".format(cos_cutoff_angle))
    if not InEdgeModelList(device, region, "ElectricField_1120"):
        CreateEdgeModel(device, region, "ElectricField_1120", "abs(ElectricField+1)*{0}".format(sin_cutoff_angle))
    if not InEdgeModelList(device, region, "n_B"):
        CreateEdgeModel(device, region, "n_B", "abs(ElectricField+1) / pow( pow( ElectricField_1120/n_b_1120 , 2) + pow( ElectricField_0001/n_b_0001 , 2) , 0.5)")
    if not InEdgeModelList(device, region, "p_B"):
        CreateEdgeModel(device, region, "p_B", "abs(ElectricField+1) / pow( pow( ElectricField_1120/p_b_1120 , 2) + pow( ElectricField_0001/p_b_0001 , 2) , 0.5)")
    if not InEdgeModelList(device, region, "n_a_aniso"):
        CreateEdgeModel(device, region, "n_a_aniso", "pow( n_a_1120, pow( n_B*ElectricField_1120/n_b_1120/abs(ElectricField+1), 2) ) * pow( n_a_0001, pow( n_B*ElectricField_0001/n_b_0001/abs(ElectricField+1), 2) )")
    if not InEdgeModelList(device, region, "p_a_aniso"):
        CreateEdgeModel(device, region, "p_a_aniso", "pow( p_a_1120, pow( p_B*ElectricField_1120/p_b_1120/abs(ElectricField+1), 2) ) * pow( p_a_0001, pow( p_B*ElectricField_0001/p_b_0001/abs(ElectricField+1), 2) )")
    if not InEdgeModelList(device, region, "n_A"):
        CreateEdgeModel(device, region, "n_A", "log(n_a_0001/n_b_1120)")
    if not InEdgeModelList(device, region, "p_A"):
        CreateEdgeModel(device, region, "p_A", "log(p_a_0001/p_b_1120)")
    if not InEdgeModelList(device, region, "n_b_aniso"):
        CreateEdgeModel(device, region, "n_b_aniso", "n_B * pow( 1-pow(n_A,2)* pow( (n_B*ElectricField_1120*ElectricField_0001)/(abs(ElectricField+1)*n_b_1120*n_b_0001), 2), 0.5)")
    if not InEdgeModelList(device, region, "p_b_aniso"):
        CreateEdgeModel(device, region, "p_b_aniso", "p_B * pow( 1-pow(p_A,2)* pow( (p_B*ElectricField_1120*ElectricField_0001)/(abs(ElectricField+1)*p_b_1120*p_b_0001), 2), 0.5)")
    gamma_str = "tanh(0.19/(2*0.0257))/tanh(0.19/(2*0.0257*T/T0))"
    Ion_coeff_n  = "ifelse(abs(ElectricField)>1e4, {0} * n_a_aniso * exp( - {1} * n_b_aniso / (abs(ElectricField)+1)), 1)".format(gamma_str,gamma_str)
    Ion_coeff_p  = "ifelse(abs(ElectricField)>1e4, {0} * p_a_aniso * exp( - {1} * p_b_aniso / (abs(ElectricField)+1)), 1)".format(gamma_str,gamma_str)
    Ion_coeff_rate = "(Ion_coeff_n*(abs(ElectronCurrent))+Ion_coeff_p*(abs(HoleCurrent)))/q"
    CreateEdgeModel(device, region, "Ion_coeff_n", Ion_coeff_n)
    CreateEdgeModelDerivatives(device, region, "Ion_coeff_n", Ion_coeff_n, "Potential")
    CreateEdgeModel(device, region, "Ion_coeff_p", Ion_coeff_p)
    CreateEdgeModelDerivatives(device, region, "Ion_coeff_p", Ion_coeff_p, "Potential")
    
    R_BTBT="3.11*abs(ElectricField)^2.5*exp(abs(ElectricField)/3e4)"
    CreateEdgeModel(device,region,"R_BTBT",R_BTBT)
    CreateEdgeModelDerivatives(device,region,"R_BTBT",R_BTBT,"Potential")
    ImpactGen_n = "+q*(%s+R_BTBT)"%(Ion_coeff_rate)
    ImpactGen_p = "-q*(%s+R_BTBT)"%(Ion_coeff_rate)

    CreateEdgeModel(device, region, "ImpactGen_n", ImpactGen_n)
    CreateEdgeModelDerivatives(device, region, "ImpactGen_n", ImpactGen_n, "Potential")
    CreateEdgeModelDerivatives(device, region, "ImpactGen_n", ImpactGen_n, "Electrons")
    CreateEdgeModelDerivatives(device, region, "ImpactGen_n", ImpactGen_n, "Holes")
    
    CreateEdgeModel(device, region, "ImpactGen_p", ImpactGen_p)
    CreateEdgeModelDerivatives(device, region, "ImpactGen_p", ImpactGen_p, "Potential")
    CreateEdgeModelDerivatives(device, region, "ImpactGen_p", ImpactGen_p, "Electrons")
    CreateEdgeModelDerivatives(device, region, "ImpactGen_p", ImpactGen_p, "Holes")

def CreateInitialNetGeneration(device, region):

    Gn = "-q * USRH"
    Gp = "+q * USRH"

    CreateNodeModel(device, region, "ElectronGeneration", Gn)
    CreateNodeModel(device, region, "HoleGeneration", Gp)

    for i in ("Electrons", "Holes"):
        CreateNodeModelDerivative(device, region, "ElectronGeneration", Gn, i)
        CreateNodeModelDerivative(device, region, "HoleGeneration", Gp, i)

def CreateNetGeneration(device, region):

    #Gn = "-q * ( USRH + R_z + R_h6 + R_Ti + R_EH5 )"
    #Gp = "+q * ( USRH + R_z + R_h6 + R_Ti + R_EH5 )"

    #Gn = "-q * (USRH - 1e12)"
    #Gp = "+q * (USRH - 1e12)"

    #Gn = "-q * (USRH - 1e18*x*x)"
    #Gp = "+q * (USRH - 1e18*x*x)"

    if devsim.get_material(device=device, region=region) == "SiliconCarbide":
        Gn = "-q * (USRH+R_z+R_h6-1e12)"
        Gp = "+q * (USRH+R_z+R_h6-1e12)"
    if devsim.get_material(device=device, region=region) == "Silicon":
        Gn = "-q * (USRH)"
        Gp = "+q * (USRH)"
    else:
        Gn = "-q * (USRH-1e12)"
        Gp = "+q * (USRH-1e12)"

    CreateNodeModel(device, region, "ElectronGeneration", Gn)
    CreateNodeModel(device, region, "HoleGeneration", Gp)

    for i in ("Electrons", "Holes"):
        CreateNodeModelDerivative(device, region, "ElectronGeneration", Gn, i)
        CreateNodeModelDerivative(device, region, "HoleGeneration", Gp, i)
        

def CreateIrradiatedCharge(device, region,Neutron_eq=1e16):
    '''
    Add Deep Levels from Irradiated Defect 
    able to Catch Carriers Directly and Keep Them Trapped
    '''
    e = 1.6*1e-19
    v_T = 1e7
    devsim.add_db_entry(material="global",   parameter="v_T",     value=v_T,   unit="cm/s",     description="v_T")
    
    names        = ["E30K"   , "V3"      , "Ip"      , "H220"    , "CiOi"    ]
    E_ts_ev      = [0.56-0.1 , 0.56-0.458, 0.56-0.545, -0.56+0.48, -0.56+0.36]
    g_ints       = [0.0497   , 0.6447    , 0.4335    , 0.5978    , 0.3780    ] # cm^-1
    sigma_n_irrs = [2.300e-14, 2.551e-14 , 4.478e-15 , 4.166e-15 , 3.230e-17 ]
    sigma_p_irrs = [2.920e-16, 1.551e-13 , 6.709e-15 , 1.965e-16 , 2.036e-14 ]

    n_t_irr_n = "0"
    n_t_irr_p = "0"
    
    for name, E_t_ev, g_int, sigma_n_irr, sigma_p_irr in zip(names, E_ts_ev, g_ints, sigma_n_irrs, sigma_p_irrs):
        E_t = E_t_ev * e
        N_t_irr = g_int*Neutron_eq
        
        devsim.add_db_entry(material="global",   parameter="sigma_n_irr_"+name,     value=sigma_n_irr,   unit="s/cm^2",     description="sigma_n_"+name)
        devsim.add_db_entry(material="global",   parameter="sigma_p_irr_"+name,     value=sigma_p_irr,   unit="s/cm^2",     description="sigma_p_"+name)
        devsim.add_db_entry(material="global",   parameter="N_t_irr_"+name,     value=N_t_irr,   unit="cm^(-3)",     description="N_t_"+name)
        devsim.add_db_entry(material="global",   parameter="E_t_"+name,     value=E_t,   unit="J",     description="E_t_"+name)

        c_n = "(v_T * sigma_n_irr_{name})".format(name=name)
        e_n = "(N_c * exp(-(E_g/2 - E_t_{name})/k_T0))".format(name=name)
        c_p = "(v_T * sigma_p_irr_{name})".format(name=name)
        e_p = "(N_v * exp(-(E_t_{name} - (-E_g/2))/k_T0))".format(name=name)

        n_t_irr_n += "+(N_t_irr_{name} * {c_n} * Electrons /({c_n} * Electrons + {e_n}))".format(name=name,c_n=c_n,e_n=e_n)
        n_t_irr_p += "+(N_t_irr_{name} * {c_p} * Holes /({c_p} * Holes + {e_p}))".format(name=name,c_p=c_p,e_p=e_p)

    CreateNodeModel(device, region, "TrappedElectrons", n_t_irr_n)
    CreateNodeModel(device, region, "TrappedHoles", n_t_irr_p)
    for i in ("Electrons", "Holes", "Potential"):
        CreateNodeModelDerivative(device, region, "TrappedElectrons", n_t_irr_n, i)
        CreateNodeModelDerivative(device, region, "TrappedHoles", n_t_irr_p, i)

def CreateIrradiatedGeneration(device, region):
    c_n = "(v_T * sigma_n_irr)"
    e_n = "(N_c * exp(-(E_g/2 - E_t)/k_T0))"
    c_p = "(v_T * sigma_p_irr)"
    e_p = "(N_v * exp(-(E_t - (-E_g/2))/k_T0))"

    R_n_irr = "(N_t_irr-TrappedElectrons)*{c_n}*Electrons-TrappedElectrons*{e_n}".format(c_n=c_n,e_n=e_n)
    R_p_irr = "(N_t_irr-TrappedHoles)*{c_p}*Holes-TrappedHoles*{e_p}".format(c_p=c_p,e_p=e_p)

    Gn = "-q * (USRH+R_z+R_h6+{R_n_irr})".format(R_n_irr=R_n_irr)
    Gp = "+q * (USRH+R_z+R_h6+{R_p_irr})".format(R_p_irr=R_p_irr)

    CreateNodeModel(device, region, "ElectronGeneration", Gn)
    CreateNodeModel(device, region, "HoleGeneration", Gp)
    
    
def CreateSiIrradiatedCharge(device, region):

    # imaginary defect: perugia model
    flux = 1.12e15
    sigma_e_acc1=1e-15
    sigma_h_acc1=1e-14
    sigma_e_acc2=7e-15
    sigma_h_acc2=7e-14
    eta_acc1=1.613
    eta_acc2=0.9
    sigma_e_donor=3.23e-13
    sigma_h_donor=3.23e-14
    eta_donor=0.9
    
    E_acc1=0.42
    E_acc2=0.46
    E_donor=0.36
    
    N_t_acc1 = flux*eta_acc1
    N_t_acc2 = flux*eta_acc2
    N_t_donor = flux*eta_donor
    
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

    v_T=1e7
    devsim.add_db_entry(material="Silicon",   parameter="v_T_elec",     value=v_T,   unit="cm/s",     description="N_t_acc1")
    devsim.add_db_entry(material="Silicon",   parameter="v_T_hole",     value=v_T,   unit="cm/s",     description="N_t_acc2")





def CreateSiIrradiatedGeneration(device, region):
    
    c_n = "(v_T * sigma_n_irr)"
    e_n = "(N_c * exp(-(E_g/2 - E_t)/k_T0))"
    c_p = "(v_T * sigma_p_irr)"
    e_p = "(N_v * exp(-(E_t - (-E_g/2))/k_T0))"
    
    k = 1.3806503e-23  # J/K
    T0 = 300.0         # K    
    devsim.add_db_entry(material="Silicon",   parameter="kT0",    value=k*T0,       unit="J",        description="k*T0")
    
    # e_acc1_posi= "(exp(E_acc1 / kT0))"  #T0 = 300K
    # e_acc1_nega= "(exp(-(E_acc1 / kT0)))" 
    # e_acc2_posi= "(exp(E_acc2 / kT0))"  
    # e_acc2_nega= "(exp(-(E_acc2 / kT0)))" 
    # e_donor_posi= "(exp(E_donor / kT0))"  
    # e_donor_nega= "(exp(-(E_donor / kT0)))"  
    
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
    print("\n\n\n\n"+R_donor+"\n\n\n\n")

    Gd = "-q * (USRH+{R_donor})".format(R_donor=R_donor)  #Gd -q
    Ga = "+q * (USRH+{R_acc1}+{R_acc2})".format(R_acc1=R_acc1,R_acc2=R_acc2)

    CreateNodeModel(device, region, "ElectronGeneration", Gd)
    CreateNodeModel(device, region, "HoleGeneration", Ga)

'''
def CreateMobility(device, region):

    if not InEdgeModelList(device, region, "ElectricField"):
        
        CreateEdgeModel(device, region, "ElectricField", "(Potential@n0-Potential@n1)*EdgeInverseLength")
        CreateEdgeModelDerivatives(device, region, "ElectricField", "(Potential@n0-Potential@n1)*EdgeInverseLength", "Potential")

    # debugE = devsim.get_edge_model_values(device, region, "Eparallel")
    # print("\n\n*********************************\n")
    # print(debugE)
    # print("\n*********************************\n\n")

    #mu_n = "{0} / (pow(1.0 + pow({1} * ElectricField /{2}, {3}), 1.0 / {4}))".format( str(n_lfm), str(n_lfm), str(n_vsatp), str(n_betap), str(n_betap))
    mu_n = "n_lfm / (pow(1.0 + pow(n_lfm * 40.0 / n_vsatp, n_betap), 1.0 / n_betap))"

    #mu_p = "{0} / (pow(1.0 + pow({1} * ElectricField /{2}, {3}), 1.0 / {4}))".format( str(p_lfm), str(p_lfm), str(p_vsatp), str(p_betap), str(p_betap))
    mu_p = "p_lfm / (pow(1.0 + pow(p_lfm * 40.0 / p_vsatp, p_betap), 1.0/p_betap))"

    CreateEdgeModel(device, region, "ElectronMobility", mu_n)
    CreateEdgeModel(device, region, "HoleMobility", mu_p)

    CreateEdgeModelDerivatives(device, region,"ElectronMobility", mu_n, "Potential")
    CreateEdgeModelDerivatives(device, region, "HoleMobility", mu_p, "Potential")
'''



def CreateECE(device, region, mu_n):
    CreateElectronCurrent(device, region, mu_n)

    NCharge = "-q * Electrons"
    CreateNodeModel(device, region, "NCharge", NCharge)
    CreateNodeModelDerivative(device, region, "NCharge", NCharge, "Electrons")

    CreateImpactGeneration(device, region)
    devsim.equation(device=device, region=region, name="ElectronContinuityEquation", variable_name="Electrons",
             time_node_model = "NCharge",
             edge_model="ElectronCurrent", variable_update="positive", 
             node_model="ElectronGeneration", 
             edge_volume_model="ImpactGen_n"
             )


def CreateHCE(device, region, mu_p):
    CreateHoleCurrent(device, region, mu_p)
    PCharge = "q * Holes"
    CreateNodeModel(device, region, "PCharge", PCharge)
    CreateNodeModelDerivative(device, region, "PCharge", PCharge, "Holes")
    
    CreateImpactGeneration(device, region)
    devsim.equation(device=device, region=region, name="HoleContinuityEquation", variable_name="Holes",
             time_node_model = "PCharge",
             edge_model="HoleCurrent", variable_update="positive", 
             node_model="HoleGeneration", 
             edge_volume_model="ImpactGen_p"
             )

def CreateECE_improved(device, region, mu_n):
    CreateElectronCurrent(device, region, mu_n)

    NCharge = "-q * Electrons"
    CreateNodeModel(device, region, "NCharge", NCharge)
    CreateNodeModelDerivative(device, region, "NCharge", NCharge, "Electrons")

    #CreateImpactGeneration(device, region)
    CreateTunnelingAndAvalanche(device, region)
    devsim.equation(device=device, region=region, name="ElectronContinuityEquation", variable_name="Electrons",
             time_node_model = "NCharge",
             edge_model="ElectronCurrent", variable_update="positive", 
             node_model="ElectronGeneration", 
             edge_volume_model="ImpactGen_n"
             )


def CreateHCE_improved(device, region, mu_p):
    CreateHoleCurrent(device, region, mu_p)
    PCharge = "q * Holes"
    CreateNodeModel(device, region, "PCharge", PCharge)
    CreateNodeModelDerivative(device, region, "PCharge", PCharge, "Holes")
    
    #CreateImpactGeneration(device, region)
    CreateTunnelingAndAvalanche(device, region)
    devsim.equation(device=device, region=region, name="HoleContinuityEquation", variable_name="Holes",
             time_node_model = "PCharge",
             edge_model="HoleCurrent", variable_update="positive", 
             node_model="HoleGeneration", 
             edge_volume_model="ImpactGen_p"
             )



def CreatePE(device, region):
    pne = "-q*kahan3(Holes, -Electrons, NetDoping)"
    CreateNodeModel(device, region, "PotentialNodeCharge", pne)
    CreateNodeModelDerivative(device, region, "PotentialNodeCharge", pne, "Electrons")
    CreateNodeModelDerivative(device, region, "PotentialNodeCharge", pne, "Holes")

    devsim.equation(device=device, region=region, name="PotentialEquation", variable_name="Potential",
             node_model="PotentialNodeCharge", edge_model="PotentialEdgeFlux",
             time_node_model="", variable_update="log_damp")

def CreatePEIrradiated(device, region):
    pne = "-q*kahan3(Holes, -Electrons, kahan3(NetDoping, TrappedHoles, -TrappedElectrons))"
    CreateNodeModel(device, region, "PotentialNodeCharge", pne)
    CreateNodeModelDerivative(device, region, "PotentialNodeCharge", pne, "Electrons")
    CreateNodeModelDerivative(device, region, "PotentialNodeCharge", pne, "Holes")

    devsim.equation(device=device, region=region, name="PotentialEquation", variable_name="Potential",
             node_model="PotentialNodeCharge", edge_model="PotentialEdgeFlux",
             time_node_model="", variable_update="log_damp") 

def CreateDriftDiffusion(device, region, mu_n="mu_n", mu_p="mu_p"):
    CreatePE(device, region)
    CreateBernoulli(device, region)
    CreateSRH(device, region)
    CreateSRH1(device, region)
    CreateSRH2(device, region)
    CreateNetGeneration(device, region)
    #CreateMobility(device, region)
    CreateECE(device, region, mu_n)
    CreateHCE(device, region, mu_p)

def CreateDriftDiffusionIrradiated(device, region, mu_n="mu_n", mu_p="mu_p"):
    CreateIrradiatedCharge(device, region)
    CreatePEIrradiated(device, region)
    CreateBernoulli(device, region)
    CreateSRH(device, region)
    CreateSRH1(device, region)
    CreateSRH2(device, region)
    CreateNetGeneration(device, region)
    #CreateMobility(device, region)
    CreateECE(device, region, mu_n)
    CreateHCE(device, region, mu_p)
    

def CreateSiDriftDiffusion(device, region, mu_n="mu_n", mu_p="mu_p"):
    CreatePE(device, region)
    CreateBernoulli(device, region)
    CreateSRH(device, region)

    CreateNetGeneration(device, region)
    #CreateMobility(device, region)
    CreateECE(device, region, mu_n)
    CreateHCE(device, region, mu_p)


def CreateSiDriftDiffusionIrradiated(device, region, mu_n="mu_n", mu_p="mu_p"):
    CreateSiIrradiatedCharge(device, region)
#    CreatePEIrradiated(device, region)
    CreateBernoulli(device, region)
    CreateSRH(device, region)
    CreateSiIrradiatedGeneration(device, region)
    #CreateMobility(device, region)
    CreateECE(device, region, mu_n)
    CreateHCE(device, region, mu_p)

def CreateImprovedDriftDiffusion(device,region,mu_n="mu_n",mu_p="mu_p"):
    CreatePE(device,region)
    CreateBernoulli(device,region)
    CreateSRH(device,region)
    CreateInitialNetGeneration(device,region)
    CreateECE_improved(device,region,mu_n)
    CreateHCE_improved(device,region,mu_p)

def CreateDriftDiffusionAtContact(device, region, contact, is_circuit=False): 
    '''
      Restrict electrons and holes to their equilibrium values
      Integrates current into circuit
    '''
    contact_electrons_model = "Electrons - ifelse(NetDoping > 0, {0}, n_i^2/{1})".format(celec_model, chole_model)
    contact_holes_model = "Holes - ifelse(NetDoping < 0, +{1}, +n_i^2/{0})".format(celec_model, chole_model)
    contact_electrons_name = "{0}nodeelectrons".format(contact)
    contact_holes_name = "{0}nodeholes".format(contact)

    CreateContactNodeModel(device, contact, contact_electrons_name, contact_electrons_model)
    #TODO: The simplification of the ifelse statement is time consuming

    CreateContactNodeModel(device, contact, "{0}:{1}".format(contact_electrons_name, "Electrons"), "1")

    CreateContactNodeModel(device, contact, contact_holes_name, contact_holes_model)
    CreateContactNodeModel(device, contact, "{0}:{1}".format(contact_holes_name, "Holes"), "1")

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
