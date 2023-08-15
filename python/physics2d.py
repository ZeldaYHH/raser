#!/usr/bin/env python3
# -*- encoding: utf-8 -*-



#基础函数库
#Node.py文件

import devsim
import math
debug = False


def SetMaterialParameters(device, region):
    q=1.6e-19
    k=1.3806503e-23
    eps=8.85e-14
    T=300
    
    for name, value in (
        ("Permittivity", 11.1*eps),
      ("ElectronCharge", q),
      ("kT", eps * T),
      ("V_t", k*T/q),
      ("mu_n", 1100),
      ("mu_p", 114),
      ("n_i",3.8e-9),
      ("n_a",21000000),
      ("n_b",17000000),
      ("p_a",29600000),
      ("p_b",16000000)
    ):
        devsim.set_parameter(device=device, region=region, name=name, value=value)








'''
建立方程求解变量
'''
def CreateSolution(device, region, name):
    '''
      Creates solution variables
      As well as their entries on each edge
    '''
    devsim.node_solution(name=name, device=device, region=region)
    devsim.edge_from_node_model(node_model=name, device=device, region=region)
#建立求解模型（主体部分）
def CreateNodeModel(device, region, model, expression):
    '''
      Creates a node model
    '''
    result=devsim.node_model(device=device, region=region, name=model, equation=expression)
    if debug:
        print(("NODEMODEL {d} {r} {m} \"{re}\"".format(d=device, r=region, m=model, re=result)))


def CreateEdgeModel (device, region, model, expression):
    '''
      Creates an edge model
    '''
    result=devsim.edge_model(device=device, region=region, name=model, equation=expression)
    if debug:
        print("EDGEMODEL {d} {r} {m} \"{re}\"".format(d=device, r=region, m=model, re=result))

#建立电极处的方程
def CreateContactNodeModel(device, contact, model, expression):
    '''
      Creates a contact node model
    '''
    result=devsim.contact_node_model(device=device, contact=contact, name=model, equation=expression)
    if debug:
        print(("CONTACTNODEMODEL {d} {c} {m} \"{re}\"".format(d=device, c=contact, m=model, re=result)))

def CreateContactEdgeModel(device, contact, model, expression):
    '''
      Creates a contact edge model
    '''
    result=devsim.contact_edge_model(device=device, contact=contact, name=model, equation=expression)
    if debug:
        print(("CONTACTEDGEMODEL {d} {c} {m} \"{re}\"".format(d=device, c=contact, m=model, re=result)))

#对电极处的模型求微分

def CreateNodeModelDerivative(device, region, model, expression, *vars):
    '''
      Create a node model derivative
    '''
    for v in vars:
        CreateNodeModel(device, region,
                        "{m}:{v}".format(m=model, v=v),
                        "simplify(diff({e},{v}))".format(e=expression, v=v))


def CreateContactNodeModelDerivative(device, contact, model, expression, variable):
    '''
      Creates a contact node model derivative
    '''
    CreateContactNodeModel(device, contact,
                           "{m}:{v}".format(m=model, v=variable),
                           "simplify(diff({e}, {v}))".format(e=expression, v=variable))


def CreateEdgeModelDerivatives(device, region, model, expression, variable):
    '''
      Creates edge model derivatives
    '''
    CreateEdgeModel(device, region,
                    "{m}:{v}@n0".format(m=model, v=variable),
                    "simplify(diff({e}, {v}@n0))".format(e=expression, v=variable))
    CreateEdgeModel(device, region,
                    "{m}:{v}@n1".format(m=model, v=variable),
                    "simplify(diff({e}, {v}@n1))".format(e=expression, v=variable))


def CreateContactEdgeModelDerivative(device, contact, model, expression, variable):
    '''
      Creates contact edge model derivatives with respect to variable on node
    '''
    CreateContactEdgeModel(device, contact, "{m}:{v}".format(m=model, v=variable), "simplify(diff({e}, {v}))".format(e=expression, v=variable))






#检查是否在模型里
def InEdgeModelList(device, region, model):
    '''
      Checks to see if this edge model is available on device and region
    '''
    return model in devsim.get_edge_model_list(device=device, region=region)

def InNodeModelList(device, region, model):
    '''
      Checks to see if this node model is available on device and region
    '''
    return model in devsim.get_node_model_list(device=device, region=region)

#### Make sure that the model exists, as well as it's node model
def EnsureEdgeFromNodeModelExists(device, region, nodemodel):
    '''
      Checks if the edge models exists
    '''
    if not InNodeModelList(device, region, nodemodel):
        raise "{} must exist"

    emlist = devsim.get_edge_model_list(device=device, region=region)
    emtest = ("{0}@n0".format(nodemodel) and "{0}@n1".format(nodemodel))
    if not emtest:
        if debug:
            print("INFO: Creating ${0}@n0 and ${0}@n1".format(nodemodel))
        devsim.edge_from_node_model(device=device, region=region, node_model=nodemodel)

#漂流迁移模型


def CreateBernoulli (device, region):
    
    #### test for requisite models here
    EnsureEdgeFromNodeModelExists(device, region, "Potential")
    vdiffstr="(Potential@n0 - Potential@n1)/V_t"
    CreateEdgeModel(device, region, "vdiff", vdiffstr)
    CreateEdgeModel(device, region, "vdiff:Potential@n0",  "V_t^(-1)")
    CreateEdgeModel(device, region, "vdiff:Potential@n1",  "-vdiff:Potential@n0")
    CreateEdgeModel(device, region, "Bern01",              "B(vdiff)")
    CreateEdgeModel(device, region, "Bern01:Potential@n0", "dBdx(vdiff) * vdiff:Potential@n0")
    CreateEdgeModel(device, region, "Bern01:Potential@n1", "-Bern01:Potential@n0")

'''
定义产出电流
'''

def CreateElectronCurrent(device, region, mu_n):
    '''
    Electron current
    '''
    EnsureEdgeFromNodeModelExists(device, region, "Potential")
    EnsureEdgeFromNodeModelExists(device, region, "Electrons")
    EnsureEdgeFromNodeModelExists(device, region, "Holes")
    # Make sure the bernoulli functions exist
    if not InEdgeModelList(device, region, "Bern01"):
        CreateBernoulli(device, region)

    Jn = "q*{0}*EdgeInverseLength*V_t*kahan3(Electrons@n1*Bern01,  Electrons@n1*vdiff,  -Electrons@n0*Bern01)".format(mu_n)
    #Jn = "q*ElectronMobility*EdgeInverseLength*V_T0*kahan3(Electrons@n1*Bern01,  Electrons@n1*vdiff,  -Electrons@n0*Bern01)"

    CreateEdgeModel(device, region, "ElectronCurrent", Jn)
    for i in ("Electrons", "Potential", "Holes"):
        CreateEdgeModelDerivatives(device, region, "ElectronCurrent", Jn, i)

def CreateHoleCurrent(device, region, mu_p):
    '''
    Hole current
    '''
    EnsureEdgeFromNodeModelExists(device, region, "Potential")
    EnsureEdgeFromNodeModelExists(device, region, "Holes")
    # Make sure the bernoulli functions exist
    if not InEdgeModelList(device, region, "Bern01"):
        CreateBernoulli(device, region)

    Jp ="-q*{0}*EdgeInverseLength*V_t*kahan3(Holes@n1*Bern01, -Holes@n0*Bern01, -Holes@n0*vdiff)".format(mu_p)
    #Jp ="-q*HoleMobility*EdgeInverseLength*V_T0*kahan3(Holes@n1*Bern01, -Holes@n0*Bern01, -Holes@n0*vdiff)"

    CreateEdgeModel(device, region, "HoleCurrent", Jp)
    for i in ("Holes", "Potential", "Electrons"):
        CreateEdgeModelDerivatives(device, region, "HoleCurrent", Jp, i)














#物理部分
#建立变量的类
#TODO: make this a class so that paramters can be changed
contactcharge_node="contactcharge_node"
contactcharge_edge="contactcharge_edge"
ece_name="ElectronContinuityEquation"
hce_name="HoleContinuityEquation"
celec_model = "(1e-10 + 0.5*abs(NetDoping+(NetDoping^2 + 4 * n_i^2)^(0.5)))"
chole_model = "(1e-10 + 0.5*abs(-NetDoping+(NetDoping^2 + 4 * n_i^2)^(0.5)))"
#celec_model = "(0.5*abs(NetDoping+(NetDoping^2 + 4 * n_i^2)^(0.5)))"
#chole_model = "(0.5*abs(-NetDoping+(NetDoping^2 + 4 * n_i^2)^(0.5)))"



#读取电极上的偏压设置和模型
def GetContactBiasName(contact):
    return "{0}_bias".format(contact)



def GetContactNodeModelName(contact):
    return "{0}nodemodel".format(contact)

#输出电流信息
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


'''
#求解主体部分的电流
def CreateSicPotentialOnly(device, region):
  
    if not InNodeModelList(device, region, "Potential"):
        print("Creating Node Solution Potential")
        CreateSolution(device, region, "Potential")
    elec_i = "n_i*exp(Potential/V_t)"
    hole_i = "n_i*exp(-Potential/V_t)"
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

'''

def CreateSicPotentialOnly(device, region):
  
    if not InNodeModelList(device, region, "Potential"):
        print("Creating Node Solution Potential")
        CreateSolution(device, region, "Potential")


    elec_i = "n_i*exp(Potential/V_t)"
    hole_i = "n_i*exp(-Potential/V_t)"
    #hole_i = "n_i^2/IntrinsicElectrons"
    charge_i = "kahan3(IntrinsicHoles, -IntrinsicElectrons, NetDoping)"
    pcharge_i = "-q * IntrinsicCharge"

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

    '''
    elec_i = "n_i*exp(Potential/V_t)"
    hole_i = "n_i*exp(-Potential/V_t)"
    #hole_i = "n_i^2/IntrinsicElectrons"
    charge_i = "kahan3(IntrinsicHoles, -IntrinsicElectrons, NetDoping)"
    pcharge_i = "-q * IntrinsicCharge"
    '''

    
    
    for name, equation in (
        ("EField",              "(Potential@n0-Potential@n1)*EdgeInverseLength"),
      ("EField:Potential@n0", "EdgeInverseLength"),
      ("EField:Potential@n1", "-EField:Potential@n0"),
      ("PotentialEdgeFlux", "Permittivity*EField"),
    ):
        devsim.edge_model(device=device, region=region, name=name, equation=equation)
        
    #devsim.element_model(device=device,region=region,name="PotentialEdgeFlux",equation=)

    devsim.element_from_edge_model(edge_model="EField", device=device, region=region)
    devsim.element_from_edge_model(edge_model="EField", derivative="Potential", device=device, region=region)
    devsim.element_from_edge_model(edge_model="PotentialEdgeFlux", device=device, region=region)
    foo="dot2d(EField_x, EField_y, unitx, unity)"
    for name, equation in (
        ("ElectricField", foo),
      ("ElectricField:Potential@en0", "diff(%s, Potential@en0)" % foo),
      ("ElectricField:Potential@en1", "diff(%s, Potential@en1)" % foo),
      ("ElectricField:Potential@en2", "diff(%s, Potential@en2)" % foo),
      
      #("PotentialEdgeFlux", "Permittivity*EField"),
      ("PotentialEdgeFlux:Potential@en0", "diff(Permittivity*ElectricField,Potential@en0)"),
      ("PotentialEdgeFlux:Potential@en1", "diff(Permittivity*ElectricField,Potential@en1)"),
      ("PotentialEdgeFlux:Potential@en2", "diff(Permittivity*ElectricField,Potential@en2)"),
    ):
        devsim.element_model(device=device, region=region, name=name, equation=equation)

    #devsim.equation(device=device, region=region, name="PotentialEquation", variable_name="Potential",node_model="PotentialIntrinsicCharge", element_model="PotentialEdgeFlux", variable_update="log_damp")
    devsim.equation(device=device, region=region, name="PotentialEquation", variable_name="Potential",
             node_model="PotentialIntrinsicCharge", edge_model="PotentialEdgeFlux", variable_update="log_damp")

'''
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
        ("ElectricField:Potential@n0", "EdgeInverseLength"),
      ("ElectricField:Potential@n1", "-EField:Potential@n0"),
        
        ("PotentialEdgeFlux", "eps_0* eps* ElectricField")
    ):
        n = i[0]
        e = i[1]
        CreateEdgeModel(device, region, n, e)
        CreateEdgeModelDerivatives(device, region, n, e, "Potential")





    devsim.equation(device=device, region=region, name="PotentialEquation", variable_name="Potential",
             node_model="PotentialIntrinsicCharge", edge_model="PotentialEdgeFlux", variable_update="log_damp")

'''








#求解电极部分处的电流
def CreateSicPotentialOnlyContact(device, region, contact, is_circuit=False):
    if not InNodeModelList(device, region, "contactcharge_node"):
        CreateNodeModel(device, region, "contactcharge_node", "q*IntrinsicCharge")
    #### TODO: This is the same as D-Field
    if not InEdgeModelList(device, region, "contactcharge_edge"):
        CreateEdgeModel(device, region, "contactcharge_edge", "eps_0* eps* EField")
        CreateEdgeModelDerivatives(device, region, "contactcharge_edge", "eps_0* eps* EField", "Potential")
    contact_model = "Potential -{0} + ifelse(NetDoping > 0, \
    -V_t*log({1}/n_i), \
    V_t*log({2}/n_i))".format(GetContactBiasName(contact), celec_model, chole_model)

    contact_model_name = GetContactNodeModelName(contact)
    CreateContactNodeModel(device, contact, contact_model_name, contact_model)
    # Simplify it too complicated
    CreateContactNodeModel(device, contact, "{0}:{1}".format(contact_model_name,"Potential"), "1")
              #判断是否进入电流
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


#SRH复合模型

def CreateSRH(device, region):
    USRH="(Electrons*Holes - n_i^2)/(tau_p*(Electrons + n1) + tau_n*(Holes + p1))"
    CreateNodeModel(device, region, "USRH", USRH)
    for i in ("Electrons", "Holes"):
        CreateNodeModelDerivative(device, region, "USRH", USRH, i)


def CreateImpactGeneration(device, region):
    
    
    Ion_coeff_n  = "ifelse(abs(ElectricField)>1e4, gamma * n_a * exp( - gamma * n_b / (abs(ElectricField)+1)), 1)"
    Ion_coeff_p  = "ifelse(abs(ElectricField)>1e4, gamma * p_a * exp( - gamma * p_b / (abs(ElectricField)+1)), 1)"

    Ion_coeff_rate = "(Ion_coeff_n*(abs(ElectronCurrent))+Ion_coeff_p*(abs(HoleCurrent)))/q"

    CreateEdgeModel(device, region, "Ion_coeff_n", Ion_coeff_n)
    CreateEdgeModelDerivatives(device, region, "Ion_coeff_n", Ion_coeff_n, "Potential")
    CreateEdgeModel(device, region, "Ion_coeff_p", Ion_coeff_p)
    CreateEdgeModelDerivatives(device, region, "Ion_coeff_p", Ion_coeff_p, "Potential")
    
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
    




def CreateNetGeneration(device, region):

    Gn = "-q * (USRH - 1e12)"
    Gp = "+q * (USRH - 1e12)"

    CreateNodeModel(device, region, "ElectronGeneration", Gn)
    CreateNodeModel(device, region, "HoleGeneration", Gp)

    for i in ("Electrons", "Holes"):
        CreateNodeModelDerivative(device, region, "ElectronGeneration", Gn, i)
        CreateNodeModelDerivative(device, region, "HoleGeneration", Gp, i)

#载流子退化效应
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

def CreatePE(device, region):
    pne = "-q*kahan3(Holes, -Electrons, NetDoping)"
    CreateNodeModel(device, region, "PotentialNodeCharge", pne)
    CreateNodeModelDerivative(device, region, "PotentialNodeCharge", pne, "Electrons")
    CreateNodeModelDerivative(device, region, "PotentialNodeCharge", pne, "Holes")

    devsim.equation(device=device, region=region, name="PotentialEquation", variable_name="Potential",
             node_model="PotentialNodeCharge", edge_model="PotentialEdgeFlux",
             time_node_model="", variable_update="log_damp")

 

#
def CreateSicDriftDiffusion(device, region, mu_n="mu_n", mu_p="mu_p"):
    CreatePE(device, region)
    CreateBernoulli(device, region)
    CreateSRH(device, region)
    CreateNetGeneration(device, region)
    #CreateMobility(device, region)
    CreateECE(device, region, mu_n)
    CreateHCE(device, region, mu_p)



def CreateSicDriftDiffusionAtContact(device, region, contact, is_circuit=False): 
   
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


#初始化




def InitialSolution(device, region, circuit_contacts=None):
    # Create Potential, Potential@n0, Potential@n1
    CreateSolution(device, region, "Potential")
    
    CreateNodeModel(device, region, "InitialElectron", "n_i*exp(Potential/V_t)")
    CreateNodeModel(device, region, "InitialHole", "n_i*exp(-Potential/V_t)")
    
    # Create potential only physical models
    CreateSicPotentialOnly(device, region)


    # Set up the contacts applying a bias
    for i in devsim.get_contact_list(device=device):
        if circuit_contacts and i in circuit_contacts:
            CreateSicPotentialOnlyContact(device, region, i, True)
        else:
            ###print "FIX THIS"
            ### it is more correct for the bias to be 0, and it looks like there is side effects
            devsim.set_parameter(device=device, name=GetContactBiasName(i), value=0.0)
            CreateSicPotentialOnlyContact(device, region, i)


def DriftDiffusionInitialSolution(device, region, circuit_contacts=None):
    ####
    #### drift diffusion solution variables
    ####
    CreateSolution(device, region, "Electrons")
    CreateSolution(device, region, "Holes")

    ####
    #### create initial guess from dc only solution
    ####
    devsim.set_node_values(device=device, region=region, name="Electrons", init_from="IntrinsicElectrons")
    devsim.set_node_values(device=device, region=region, name="Holes",     init_from="IntrinsicHoles")
    #devsim.set_node_values(device=device, region=region, name="Electrons", init_from="InitialElectron")
    #devsim.set_node_values(device=device, region=region, name="Holes",     init_from="InitialHole")

    ###
    ### Set up equations
    ###
    CreateSicDriftDiffusion(device, region)
    for i in devsim.get_contact_list(device=device):
        if circuit_contacts and i in circuit_contacts:
            CreateSicDriftDiffusionAtContact(device, region, i, True)
        else:
            CreateSicDriftDiffusionAtContact(device, region, i)



# Copyright 2019 DEVSIM LLC
#
# SPDX-License-Identifier: Apache-2.0

import devsim

def print_ac_circuit_solution():
    print('Circuit AC Solution')
    nodes = devsim.get_circuit_node_list()
    for node in devsim.get_circuit_node_list():
        r = devsim.get_circuit_node_value(solution='ssac_real', node=node)
        i = devsim.get_circuit_node_value(solution='ssac_imag', node=node)
        print("%s\t%1.15e\t%1.15e" % (node, r , i))

def print_circuit_solution():
    print('Circuit Solution')
    nodes = devsim.get_circuit_node_list()
    for node in devsim.get_circuit_node_list():
        r = devsim.get_circuit_node_value(solution='dcop', node=node)
        print("%s\t%1.15e" % (node, r))


def printResistorCurrent(device, contact):
    ecurr=devsim.get_contact_current(device=device, contact=contact, equation="ElectronContinuityEquation")
    hcurr=0.0
    tcurr=ecurr + hcurr
    print("Contact: %s\nElectron %g\nHole %g\nTotal %g" % (contact, ecurr, hcurr, tcurr))

####
#### Meshing
####
def CreateSimpleMesh(device, region, material='Si'):
    '''
      Commonly used for the regressions
      device length: 1
      spacing:       0.1
      contacts:      top (x=0), bot (x=1)
    '''
    devsim.create_1d_mesh  (mesh='dog')
    devsim.add_1d_mesh_line(mesh='dog', pos=0, ps=0.1, tag='top')
    devsim.add_1d_mesh_line(mesh='dog', pos=1, ps=0.1, tag='bot')
    devsim.add_1d_contact  (mesh='dog', name='top', tag='top', material='metal')
    devsim.add_1d_contact  (mesh='dog', name='bot', tag='bot', material='metal')
    devsim.add_1d_region   (mesh='dog', material=material, region=region, tag1='top', tag2='bot')
    devsim.finalize_mesh   (mesh='dog')
    devsim.create_device   (mesh='dog', device=device)

def CreateSimpleMeshWithInterface(device, region0, region1, interface, material1='Si', material2='Si'):
    '''
      Commonly used for the regressions
      device length: 1
      spacing:       0.1
      contacts:      top (x=0), bot (x=1)
      interface:     mid (x=0.5)
    '''
    devsim.create_1d_mesh  (mesh='dog')
    devsim.add_1d_mesh_line(mesh='dog', pos=0, ps=0.1, tag='top')
    devsim.add_1d_mesh_line(mesh='dog', pos=0.5, ps=0.1, tag='mid')
    devsim.add_1d_mesh_line(mesh='dog', pos=1, ps=0.1, tag='bot')
    devsim.add_1d_contact  (mesh='dog', name='top', tag='top', material='metal')
    devsim.add_1d_contact  (mesh='dog', name='bot', tag='bot', material='metal')
    devsim.add_1d_interface(mesh='dog', name=interface, tag='mid')
    devsim.add_1d_region(mesh='dog', material=material1, region=region0, tag1='top', tag2='mid')
    devsim.add_1d_region(mesh='dog', material=material2, region=region1, tag1='mid', tag2='bot')
    devsim.finalize_mesh   (mesh='dog')
    devsim.create_device   (mesh='dog', device=device)

def CreateNoiseMesh(device, region, material='Si'):
    '''
      Commonly used for the regressions
      device length: 1
      spacing:       0.1
      contacts:      top (x=0), bot (x=1)
    '''
    devsim.create_1d_mesh  (mesh='dog')
    devsim.add_1d_mesh_line(mesh='dog', pos=0, ps=5e-7, tag='top')
    devsim.add_1d_mesh_line(mesh='dog', pos=1e-5, ps=5e-7, tag='bot')
    devsim.add_1d_contact  (mesh='dog', name='top', tag='top', material='metal')
    devsim.add_1d_contact  (mesh='dog', name='bot', tag='bot', material='metal')
    devsim.add_1d_region   (mesh='dog', material=material, region=region, tag1='top', tag2='bot')
    devsim.finalize_mesh   (mesh='dog')
    devsim.create_device   (mesh='dog', device=device)

####
#### Constants
####
def SetupResistorConstants(device, region):
    for name, value in (
        ("Permittivity",     11.1*8.85e-14),
      ("ElectronCharge",   1.6e-19),
      ("IntrinsicDensity", 1.0e10),
      ("ThermalVoltage",   0.0259),
      ("mu_n", 400),
      ("mu_p", 200),
    ):
        devsim.set_parameter(device=device, region=region, name=name, value=value)

def SetupInitialResistorSystem(device, region, net_doping=1e16):
    '''
      resistor physics
    '''
    devsim.set_parameter(device=device, region=region, name='net_doping', value=net_doping)
    devsim.node_solution(device=device, region=region, name='Potential')
    devsim.edge_from_node_model(device=device, region=region, node_model='Potential')

    # node models
    for name, equation in (
        ("NetDoping",                 "net_doping"),
      ("IntrinsicElectrons",        "NetDoping"),
      ("IntrinsicCharge",           "-IntrinsicElectrons + NetDoping"),
      ("IntrinsicCharge:Potential", "-IntrinsicElectrons:Potential"),
    ):
        devsim.node_model(device=device, region=region, name=name, equation=equation)

    # edge models
    for name, equation in (
        ("ElectricField",              "(Potential@n0 - Potential@n1)*EdgeInverseLength"),
      ("ElectricField:Potential@n0", "EdgeInverseLength"),
      ("ElectricField:Potential@n1", "-EdgeInverseLength"),
      ("PotentialEdgeFlux",              "Permittivity*ElectricField"),
      ("PotentialEdgeFlux:Potential@n0", "diff(Permittivity*ElectricField, Potential@n0)"),
      ("PotentialEdgeFlux:Potential@n1", "-PotentialEdgeFlux:Potential@n0"),
    ):
        devsim.edge_model(device=device, region=region, name=name, equation=equation)

    ####
    #### PotentialEquation
    ####
    devsim.equation(device=device, region=region, name="PotentialEquation", variable_name="Potential", edge_model="PotentialEdgeFlux", variable_update="log_damp")

def SetupCarrierResistorSystem(device, region):
    '''
      This adds electron continuity
    '''
    devsim.node_solution(device=device, region=region, name='Electrons')
    devsim.edge_from_node_model(device=device, region=region, node_model='Electrons')
    devsim.set_node_values(device=device, region=region, name='Electrons', init_from='IntrinsicElectrons')

    ####
    #### PotentialNodeCharge
    ####
    for name, equation in (
        ("PotentialNodeCharge",           "-ElectronCharge*(-Electrons + NetDoping)"),
      ("PotentialNodeCharge:Electrons", "+ElectronCharge"),
    ):
        devsim.node_model(device=device, region=region, name=name, equation=equation)

    ####
    #### PotentialEquation modified for carriers present
    ####
    devsim.equation(device=device, region=region, name='PotentialEquation', variable_name='Potential', node_model='PotentialNodeCharge',
                    edge_model="PotentialEdgeFlux", variable_update="default")


    ####
    #### vdiff, Bern01, Bern10
    ####
    for name, equation in (
        ("vdiff",               "(Potential@n0 - Potential@n1)/ThermalVoltage"),
      ("vdiff:Potential@n0",  "ThermalVoltage^(-1)"),
      ("vdiff:Potential@n1",  "-ThermalVoltage^(-1)"),
      ("Bern01",              "B(vdiff)"),
      ("Bern01:Potential@n0", "dBdx(vdiff)*vdiff:Potential@n0"),
      ("Bern01:Potential@n1", "dBdx(vdiff)*vdiff:Potential@n1"),
      ("Bern10",              "Bern01 + vdiff"),
      ("Bern10:Potential@n0", "Bern01:Potential@n0 + vdiff:Potential@n0"),
      ("Bern10:Potential@n1", "Bern01:Potential@n1 + vdiff:Potential@n1"),
    ):
        devsim.edge_model(device=device, region=region, name=name, equation=equation)

    ####
    #### Electron Current
    ####
    current_equation="ElectronCharge*mu_n*EdgeInverseLength*ThermalVoltage*(Electrons@n1*Bern10 - Electrons@n0*Bern01)"
    for name, equation in (
        ("ElectronCurrent", current_equation),
      ("ElectronCurrent:Electrons@n0", "simplify(diff(%s, Electrons@n0))" % current_equation),
      ("ElectronCurrent:Electrons@n1", "simplify(diff(%s, Electrons@n1))" % current_equation),
      ("ElectronCurrent:Potential@n0", "simplify(diff(%s, Potential@n0))" % current_equation),
      ("ElectronCurrent:Potential@n1", "simplify(diff(%s, Potential@n1))" % current_equation),
    ):
        devsim.edge_model(device=device, region=region, name=name, equation=equation)

    ####
    #### Time derivative term
    ####
    for name, equation in (
        ("NCharge", "-ElectronCharge * Electrons"),
      ("NCharge:Electrons", "-ElectronCharge"),
    ):
        devsim.node_model(device=device, region=region, name=name, equation=equation)

    ####
    #### Electron Continuity Equation
    ####
    devsim.equation(device=device, region=region, name="ElectronContinuityEquation", variable_name="Electrons",
                    edge_model="ElectronCurrent", time_node_model="NCharge", variable_update="positive")


def SetupInitialResistorContact(device, contact, use_circuit_bias=False, circuit_node=""):
    if circuit_node:
        bias_name = circuit_node
    else:
        bias_name = contact + "bias"
    bias_node_model  = contact + "node_model"

    devsim.contact_node_model(device=device, contact=contact, name=bias_node_model, equation="Potential - %s" % bias_name)
    devsim.contact_node_model(device=device, contact=contact, name="%s:Potential" % bias_node_model, equation="1")
    if use_circuit_bias:
        devsim.contact_node_model(device=device, contact=contact, name="%s:%s" % (bias_node_model, bias_name), equation="-1")
    #edge_model -device $device -region $region -name "contactcharge_edge_top"  -equation $conteq
    if use_circuit_bias:
        devsim.contact_equation(device=device, contact=contact, name="PotentialEquation",
                                node_model=bias_node_model, circuit_node=bias_name)
    else:
        devsim.contact_equation(device=device, contact=contact, name="PotentialEquation",
                                node_model=bias_node_model)

def SetupCarrierResistorContact(device, contact, use_circuit_bias=False, circuit_node=""):
    '''
      Electron continuity equation at contact
    '''
    if circuit_node:
        bias_name=circuit_node
    else:
        bias_name = contact + "bias"
    region=devsim.get_region_list(device=device, contact=contact)[0]
    if 'celec' not in devsim.get_node_model_list(device=device, region=region):
        devsim.node_model(device=device, region=region, name="celec", equation="0.5*(NetDoping+(NetDoping^2 + 4 * IntrinsicDensity^2)^(0.5))")

    for name, equation in (
        ("%snodeelectrons" % contact,           "Electrons - celec"),
      ("%snodeelectrons:Electrons" % contact, "1."),
    ):
        devsim.contact_node_model(device=device, contact=contact, name=name, equation=equation)

    if use_circuit_bias:
        devsim.contact_equation(device=device, contact=contact, name="ElectronContinuityEquation",
                                node_model="%snodeelectrons" % contact, edge_current_model="ElectronCurrent", circuit_node=bias_name)
    else:
        devsim.contact_equation(device=device, contact=contact, name="ElectronContinuityEquation",
                                node_model="%snodeelectrons" % contact, edge_current_model="ElectronCurrent")

def SetupContinuousPotentialAtInterface(device, interface):
    # type continuous means that regular equations in both regions are swapped into the primary region
    devsim.interface_model(device=device, interface=interface, name="continuousPotential", equation="Potential@r0-Potential@r1")
    devsim.interface_model(device=device, interface=interface, name="continuousPotential:Potential@r0", equation= "1")
    devsim.interface_model(device=device, interface=interface, name="continuousPotential:Potential@r1", equation="-1")
    devsim.interface_equation(device=device, interface=interface, name="PotentialEquation", interface_model="continuousPotential", type="continuous")

def SetupContinuousElectronsAtInterface(device, interface):
    # type continuous means that regular equations in both regions are swapped into the primary region
    devsim.interface_model(device=device, interface=interface, name="continuousElectrons", equation="Electrons@r0-Electrons@r1")
    devsim.interface_model(device=device, interface=interface, name="continuousElectrons:Electrons@r0", equation= "1")
    devsim.interface_model(device=device, interface=interface, name="continuousElectrons:Electrons@r1", equation="-1")
    devsim.interface_equation(device=device, interface=interface, name="ElectronContinuityEquation", interface_model="continuousElectrons", type="continuous")

def SetupElectronSRVAtInterface(device, interface):
    '''
      Surface Recombination Velocity At Interface
    '''
    devsim.set_parameter(device=device, name="alpha_n", value=1e-7)
    iexp="(alpha_n@r0)*(Electrons@r0-Electrons@r1)"
    for name, equation in (
        ("srvElectrons", iexp),
      ("srvElectrons2", "srvElectrons"),
      ("srvElectrons:Electrons@r0", "diff(%s,Electrons@r0)" % iexp),
      ("srvElectrons:Electrons@r1", "diff(%s,Electrons@r1)" % iexp),
      ("srvElectrons2:Electrons@r0", "srvElectrons:Electrons@r0"),
      ("srvElectrons2:Electrons@r1", "srvElectrons:Electrons@r1"),
    ):
        devsim.interface_model(device=device, interface=interface, name=name, equation=equation)

    devsim.interface_equation(device=device, interface=interface, name="ElectronContinuityEquation", interface_model="srvElectrons2", type="fluxterm")


