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
    devsim.add_db_entry(material="global",   parameter="sigma_n",     value=sigma_n,   unit="s/cm^2",     description="sigma_n")
    devsim.add_db_entry(material="global",   parameter="sigma_p",     value=sigma_p,   unit="s/cm^2",     description="sigma_p")
    devsim.add_db_entry(material="global",   parameter="N_t",     value=N_t,   unit="cm^(-3)",     description="N_t")
    devsim.add_db_entry(material="global",   parameter="v_T",     value=v_T,   unit="cm/s",     description="v_T")
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
    devsim.add_db_entry(material="global",   parameter="sigma_n_HS6",     value=sigma_n_HS6,   unit="s/cm^2",     description="sigma_n_HS6")
    devsim.add_db_entry(material="global",   parameter="sigma_p_HS6",     value=sigma_p_HS6,   unit="s/cm^2",     description="sigma_p_HS6")
    devsim.add_db_entry(material="global",   parameter="N_t_HS6",     value=N_t_HS6,   unit="cm^(-3)",     description="N_t_HS6")
    devsim.add_db_entry(material="global",   parameter="v_T",     value=v_T,   unit="cm/s",     description="v_T")
    R_h6="(sigma_n_HS6*sigma_p_HS6*v_T*N_t_HS6*(Electrons*Holes - n_i^2))/(sigma_n_HS6*(Electrons - n1*exp(4.8e-22/(k_T0))) + sigma_p_HS6*(Holes + p1*exp(4.8e-22/(k_T0))))"
    CreateNodeModel(device, region, "R_h6", R_h6)
    for i in ("Electrons", "Holes"):
        CreateNodeModelDerivative(device, region, "R_h6", R_h6, i)

def CreateImpactGeneration(device, region):
    
    # if not InEdgeModelList(device, region, "ElectricField"):
    #     CreateEdgeModel(device, region, "ElectricField", "(Potential@n0-Potential@n1)*EdgeInverseLength")
    #     CreateEdgeModelDerivatives(device, region, "ElectricField", "(Potential@n0-Potential@n1)*EdgeInverseLength", "Potential")


    #Ion_coeff_n  = "gamma * n_a * exp( - gamma * n_b / (ElectricField))"
    #Ion_coeff_p  = "gamma * p_a * exp( - gamma * p_b / (ElectricField))"

    Ion_coeff_n  = "ifelse(abs(ElectricField)>1e4, gamma * n_a * exp( - gamma * n_b / (abs(ElectricField)+1)), 1)"
    Ion_coeff_p  = "ifelse(abs(ElectricField)>1e4, gamma * p_a * exp( - gamma * p_b / (abs(ElectricField)+1)), 1)"

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


def CreateAnisoImpactGeneration(device, region):

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



def CreateNetGeneration(device, region):
    #Gn = "-q * ( USRH + R_z + R_h6 + R_Ti + R_EH5 )"
    #Gp = "+q * ( USRH + R_z + R_h6 + R_Ti + R_EH5 )"

    #Gn = "-q * (USRH - 1e12)"
    #Gp = "+q * (USRH - 1e12)"

    #Gn = "-q * (USRH - 1e18*x*x)"
    #Gp = "+q * (USRH - 1e18*x*x)"

    Gn = "-q * (USRH+R_z+R_h6-1e12)"
    Gp = "+q * (USRH+R_z+R_h6-1e12)"

    CreateNodeModel(device, region, "ElectronGeneration", Gn)
    CreateNodeModel(device, region, "HoleGeneration", Gp)

    for i in ("Electrons", "Holes"):
        CreateNodeModelDerivative(device, region, "ElectronGeneration", Gn, i)
        CreateNodeModelDerivative(device, region, "HoleGeneration", Gp, i)


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

    #CreateImpactGeneration(device, region)
    CreateAnisoImpactGeneration(device, region)
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
    
    #CreateImpactGeneration(device, region)
    CreateAnisoImpactGeneration(device, region)
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

 

def CreateSiliconDriftDiffusion(device, region, mu_n="mu_n", mu_p="mu_p"):
    CreatePE(device, region)
    CreateBernoulli(device, region)
    CreateSRH(device, region)
    CreateSRH1(device, region)
    CreateSRH2(device, region)
    CreateNetGeneration(device, region)
    #CreateMobility(device, region)
    CreateECE(device, region, mu_n)
    CreateHCE(device, region, mu_p)



def CreateSiliconDriftDiffusionAtContact(device, region, contact, is_circuit=False): 
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
