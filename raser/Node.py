'''
Description:  Node.py
@Date       : 2022/10/25 16:40:46
@Author     : Tao Yang
@version    : 1.0
'''


import devsim

debug = False
def CreateSolution(device, region, name):
    '''
      Creates solution variables
      As well as their entries on each edge
    '''
    devsim.node_solution(name=name, device=device, region=region)
    devsim.edge_from_node_model(node_model=name, device=device, region=region)

def CreateNodeModel(device, region, model, expression):
    '''
      Creates a node model
    '''
    result=devsim.node_model(device=device, region=region, name=model, equation=expression)
    if debug:
        print(("NODEMODEL {d} {r} {m} \"{re}\"".format(d=device, r=region, m=model, re=result)))

def CreateNodeModelDerivative(device, region, model, expression, *vars):
    '''
      Create a node model derivative
    '''
    for v in vars:
        CreateNodeModel(device, region,
                        "{m}:{v}".format(m=model, v=v),
                        "simplify(diff({e},{v}))".format(e=expression, v=v))


def CreateContactNodeModel(device, contact, model, expression):
    '''
      Creates a contact node model
    '''
    result=devsim.contact_node_model(device=device, contact=contact, name=model, equation=expression)
    if debug:
        print(("CONTACTNODEMODEL {d} {c} {m} \"{re}\"".format(d=device, c=contact, m=model, re=result)))


def CreateContactNodeModelDerivative(device, contact, model, expression, variable):
    '''
      Creates a contact node model derivative
    '''
    CreateContactNodeModel(device, contact,
                           "{m}:{v}".format(m=model, v=variable),
                           "simplify(diff({e}, {v}))".format(e=expression, v=variable))

def CreateEdgeModel (device, region, model, expression):
    '''
      Creates an edge model
    '''
    result=devsim.edge_model(device=device, region=region, name=model, equation=expression)
    if debug:
        print("EDGEMODEL {d} {r} {m} \"{re}\"".format(d=device, r=region, m=model, re=result))

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

def CreateContactEdgeModel(device, contact, model, expression):
    '''
      Creates a contact edge model
    '''
    result=devsim.contact_edge_model(device=device, contact=contact, name=model, equation=expression)
    if debug:
        print(("CONTACTEDGEMODEL {d} {c} {m} \"{re}\"".format(d=device, c=contact, m=model, re=result)))

def CreateContactEdgeModelDerivative(device, contact, model, expression, variable):
    '''
      Creates contact edge model derivatives with respect to variable on node
    '''
    CreateContactEdgeModel(device, contact, "{m}:{v}".format(m=model, v=variable), "simplify(diff({e}, {v}))".format(e=expression, v=variable))


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

