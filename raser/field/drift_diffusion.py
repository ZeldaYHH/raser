'''
Description:  DriftDiffusion.py
@Date       : 2022/10/25 16:40:46
@Author     : Tao Yang
@version    : 1.0
'''

import devsim
from .node import *
import math


def CreateBernoulli (device, region):
    '''
    Creates the Bernoulli function for Scharfetter Gummel
    '''
    #### test for requisite models here
    EnsureEdgeFromNodeModelExists(device, region, "Potential")
    vdiffstr="(Potential@n0 - Potential@n1)/V_T0"
    CreateEdgeModel(device, region, "vdiff", vdiffstr)
    CreateEdgeModel(device, region, "vdiff:Potential@n0",  "V_T0^(-1)")
    CreateEdgeModel(device, region, "vdiff:Potential@n1",  "-vdiff:Potential@n0")
    CreateEdgeModel(device, region, "Bern01",              "B(vdiff)")
    CreateEdgeModel(device, region, "Bern01:Potential@n0", "dBdx(vdiff) * vdiff:Potential@n0")
    CreateEdgeModel(device, region, "Bern01:Potential@n1", "-Bern01:Potential@n0")


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
    
    Jn = "q*{0}*EdgeInverseLength*V_T0*kahan3(Electrons@n1*Bern01,  Electrons@n1*vdiff,  -Electrons@n0*Bern01)".format(mu_n)
    #Jn = "q*{0}*EdgeInverseLength*V_T0*kahan3(Electrons@n1*Bern01,  Electrons@n1*vdiff,  -Electrons@n0*Bern01)-q*{0}*ElectricField*step(-Dn_t)*(-Dn_t)".format(mu_n)
    #-1e-9*ElectricField
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
    
    '''#define electrons accumulated in the traps
    #parameter of first trap Z1/2
    Dn_t1="N_t1*r_n1*(r_n1*n_11+r_p1*Acceptors@n1)*Electrons@n1/(r_n1*(Donors@n1+n_11)+r_p1*(Acceptors@n1+p_11))^2"
    #parameter of second trap EH6/7
    Dn_t2="N_t2*r_n2*(r_n2*n_12+r_p2*Acceptors@n1)*Electrons@n1/(r_n2*(Donors@n1+n_12)+r_p2*(Acceptors@n1+p_12))^2"
    CreateEdgeModel(device,region,"Dn_t1",Dn_t1)
    CreateEdgeModel(device,region,"Dn_t2",Dn_t2)'''
    Jp ="-q*{0}*EdgeInverseLength*V_T0*kahan3(Holes@n1*Bern01, -Holes@n0*Bern01, -Holes@n0*vdiff)".format(mu_p)
    #Jp ="-q*{0}*EdgeInverseLength*V_T0*kahan3(Holes@n1*Bern01, -Holes@n0*Bern01, -Holes@n0*vdiff)+q*{0}*ElectricField*step(Dn_t)*Dn_t".format(mu_p)
    #Jp ="-q*mu_p*ElectricField*(Dn_t1+Dn_t2)-q*{0}*EdgeInverseLength*V_T0*kahan3(Holes@n1*Bern01, -Holes@n0*Bern01, -Holes@n0*vdiff)".format(mu_p)
    #Jp ="-q*HoleMobility*EdgeInverseLength*V_T0*kahan3(Holes@n1*Bern01, -Holes@n0*Bern01, -Holes@n0*vdiff)"

    CreateEdgeModel(device, region, "HoleCurrent", Jp)
    for i in ("Holes", "Potential", "Electrons"):
        CreateEdgeModelDerivatives(device, region, "HoleCurrent", Jp, i)
        
def CreateTrappingEffect(device,region):
    #calculate electrons accumulated in traps
    #coefficient of Z1/2 and EH6/7
    A_1="N_t1/(r_n1*(Donors@n1+n_11)+r_p1*(Acceptors@n1+p_11))^2"
    A_2="N_t2/(r_n2*(Donors@n1+n_12)+r_p2*(Acceptors@n1+p_12))^2"
    CreateEdgeModel(device,region,"A_1",A_1)
    CreateEdgeModel(device,region,"A_2",A_2)
    Dn_t1="A_1*(r_n1*(r_n1*n_11+r_p1*Acceptors@n1)*Electrons@n1-r_p1*(r_n1*Donors@n1+r_p1*p_11)*Holes@n1)"
    Dn_t2="A_2*(r_n2*(r_n2*n_12+r_p2*Acceptors@n1)*Electrons@n1-r_p2*(r_n2*Donors@n1+r_p2*p_12)*Holes@n1)"
    CreateEdgeModel(device,region,"Dn_t1",Dn_t1)
    CreateEdgeModel(device,region,"Dn_t2",Dn_t2)
    Dn_t="Dn_t1+Dn_t2"
    CreateEdgeModel(device,region,"Dn_t",Dn_t)
      