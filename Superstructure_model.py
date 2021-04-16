# -*- coding: utf-8 -*-
"""
Created on Sun Mar 28 16:32:52 2021

@author: Vincent Reurslag
"""

from pyomo.environ import *



def Superstructure_model(Superstructure):
    model = ConcreteModel()
    
    #initialize sets, want to add utilities u later to this
    model.a = Set(initialize = Superstructure.a, doc = 'Process step')
    model.j = Set(initialize = Superstructure.j, doc = 'Processing stage')
    model.k = Set(initialize = Superstructure.k, doc = 'Technology options')
    model.i = Set(initialize = Superstructure.i, doc = 'Species in reaction mixture')
    model.u = Set(initialize = Superstructure.u, doc = 'Utilities considered')
    
    #initialize parameters. The data comes from the created Superstructure class
    #M parameter is for the big M notation later in the model
    model.SF = Param(model.a, model.j, model.k, model.i, initialize = Superstructure.SF_data, doc = 'Split factor data for equipment types')
    model.EC = Param(model.a, model.j, model.k, initialize = Superstructure.EC_data, doc = 'Cost data for equipment types')
    model.flow_in0 = Param(model.i, initialize = Superstructure.F0_data, doc = 'Flow coming out of membrane reactor')
    model.N = Param(model.a, model.j, model.k, initialize = Superstructure.Sizing_data)
    model.RefSize = Param(model.a, model.j, model.k, initialize = Superstructure.RefSize_data)
    model.Q = Param(model.a, model.j, model.k, model.i, initialize = Superstructure.Q_data)
    
    model.Tau = Param(model.a , model.j, model.k, model.i, initialize = Superstructure.Tau_data)
    model.Temp = Param(model.a, model.j, model.k, initialize = Superstructure.Temp_data)
    
    
    
    model.M = Param(initialize = 1e5)
    model.lb = Param(initialize = 500)
    model.ub = Param(initialize = 1000)
    model.T0 = Param(initialize = 80)
    
    ##initialize variables
    model.flow_in = Var(model.a, model.j, model.k, model.i, bounds = (0,None), initialize = 0, doc = 'Flow at every equipment for every component')
    model.y = Var(model.a, model.j, model.k, domain = Binary, doc = 'Logic variable')
    model.TEC = Var(bounds = (0, None), initialize = 0, doc = 'Total equipment cost')
    model.BDP = Var(bounds = (0, None), initialize = 0, doc = 'Biodiesel production')
    model.flow_intot = Var(model.a, model.j, model.k, bounds = (0, None), initialize = 0)
    model.flow_instage = Var(model.a, model.i, bounds = (0, None), initialize = 0)
    model.flow_inout = Var(model.a, model.j, model.k, model.i, bounds = (0, None), initialize = 0)
    
    model.EC1 = Var(model.a,model.i,model.k, bounds = (0, None), initialize = 0)
    model.Utility = Var(model.a, model.j, model.k, model.u, bounds = (0 , None), initialize = 0)
    model.HX = Var(model.a, model.j, model.k, bounds = (0 , None), initialize = 0)
    model.TOT_Utility = Var(model.a, model.j, model.k, model.u, bounds = (0 , None), initialize = 0)
    model.prevtemp = Var(model.a, model.j, model.k, bounds = (0, None), initialize = 0)
    
    def utilities_rule(model, a, j, k, u):
        return model.Utility[a,j,k,u] == model.flow_intot[a,j,k] * model.Tau[a,j,k,u]

    def HX_rule(model, a, j, k):
        return model.HX[a,j,k] == (model.Temp[a,j,k] - model.prevtemp[a]) * model.flow_intot[a,j,k]
    
    
    
  
    def prevtemp_rule1(model,a,j,k):
        if a >= 2:
            return model.prevtemp[a,j,k] <= model.Temp[a-1,j,k] + model.M * (1-model.y[a-1,j,k])
        elif j == 1 and k == 1:
            return model.prevtemp[a,j,k] == model.T0
        else:
            return model.prevtemp[a,j,k] == 0
    
    def prevtemp_rule2(model,a,j,k):
        if a >= 2:
            return model.prevtemp[a,j,k] >= model.Temp[a-1,j,k] - model.M * (1-model.y[a-1,j,k])
        else:
            return Constraint.Skip
    
    def prevtemp_rule3(model,a,j,k):
        if a >= 2:
            return model.prevtemp[a,j,k] <= model.M * model.y[a-1,j,k]
        else:
            return Constraint.Skip
    
    model.utilities_rule = Constraint(model.a, model.j, model.k, model.u, rule = utilities_rule)
    #model.HX_rule = Constraint(model.a, model.j, model.k, rule = HX_rule)

    model.prevtemp_rule1 = Constraint(model.a, model.j, model.k, rule = prevtemp_rule1)
    model.prevtemp_rule2 = Constraint(model.a, model.j, model.k, rule = prevtemp_rule2)
    model.prevtemp_rule3 = Constraint(model.a, model.j, model.k, rule = prevtemp_rule3)
    
    
    def massbalance_rule1(model,a, j, k, i):
        """3 massbalance rules for big M implementation:
            It calculates flow[j,k,i] = flow at previous stage * Separation factor * logic_variable
            This equation is an MINLP so it is converted using the big M notation for performance"""
        if a >= 2:
            return model.flow_in[a,j,k,i] <= (model.flow_instage[a-1,i] + model.Q[a,j,k,i]) + model.M * (1-model.y[a,j,k])
        else:
            return model.flow_in[a,j,k,i] == (model.flow_in0[i] + model.Q[a,j,k,i]) * model.y[a,j,k]
        
    def massbalance_rule2(model, a, j, k, i):
        if a >= 2:
            return model.flow_in[a,j,k,i] >= (model.flow_instage[a-1,i] + model.Q[a,j,k,i]) - model.M * (1-model.y[a,j,k])
        else:
            return Constraint.Skip
    
    def massbalance_rule3(model, a, j, k, i):
        if a >= 2:
            return model.flow_in[a,j,k,i] <= model.M * model.y[a,j,k]
        else:
            return Constraint.Skip
    
    model.massrule1 = Constraint(model.a, model.j, model.k, model.i, rule = massbalance_rule1)
    model.massrule2= Constraint(model.a, model.j, model.k, model.i, rule = massbalance_rule2)
    model.massrule3 = Constraint(model.a, model.j, model.k, model.i, rule = massbalance_rule3)
    
    def flowout_rule(model, a, j, k, i):
        return model.flow_inout[a,j,k,i] == model.flow_in[a,j,k,i] * model.SF[a,j,k,i]
    
    model.flow_inout_rule = Constraint(model.a, model.j, model.k, model.i, rule = flowout_rule)
    
    
    
    def flowstage_rule(model, a, i):
        """Simply calculating the total flow at a stage by summing for every equipment at that stage"""
        return model.flow_instage[a,i] == sum(model.flow_inout[a,j,k,i] for j in model.j for k in model.k)
    
    model.flow_instage_rule = Constraint(model.a, model.i, rule = flowstage_rule)
    
    def logic_rule(model, a):
        """Only 1 equipment can be chosen at a stage"""
        return sum(model.y[a,j,k] for j in model.j for k in model.k) == 1
    
    model.logic = Constraint(model.a, rule = logic_rule, doc = 'One option per stage')
    
    
    """ Logic for which paths are allowed through the superstructure"""
    def logic_rule1(model):
        return sum(model.y[1,1,k] for k in model.k) - sum(model.y[2,1,k] for k in model.k) - sum(model.y[2,2,k] for k in model.k) == 0
    
    def logic_rule2(model):
        return sum(model.y[1,2,k] for k in model.k) - sum(model.y[2,3,k] for k in model.k) - sum(model.y[2,4,k] for k in model.k) == 0
    
    def logic_rule3(model):
        return sum(model.y[2,1,k] for k in model.k) - sum(model.y[3,1,k] for k in model.k) == 0
    
    def logic_rule4(model):
        return sum(model.y[2,2,k] for k in model.k) + sum(model.y[2,3,k] for k in model.k) - sum(model.y[3,2,k] for k in model.k) == 0
    

    def logic_rule6(model):
        return sum(model.y[2,4,k] for k in model.k) - sum(model.y[3,3,k] for k in model.k) == 0
    
    def logic_rule7(model):
        return sum(model.y[3,1,k] for k in model.k) - sum(model.y[4,1,k] for k in model.k) == 0
    
    def logic_rule8(model):
        return sum(model.y[3,2,k] for k in model.k) - sum(model.y[4,2,k] for k in model.k) == 0
    
    def logic_rule9(model):
        return sum(model.y[3,3,k] for k in model.k) - sum(model.y[4,3,k] for k in model.k) == 0
    
    def logic_rule10(model):
        return sum(model.y[4,2,k] for k in model.k) + sum(model.y[4,3,k] for k in model.k) - model.y[5,1,1] == 0
    
    def logic_rule11(model):
        return sum(model.y[4,1,k] for k in model.k) - model.y[5,1,2] == 0
    

    model.logic1 = Constraint(rule = logic_rule1)
    model.logic2 = Constraint(rule = logic_rule2)
    model.logic3 = Constraint(rule = logic_rule3)
    model.logic4 = Constraint(rule = logic_rule4)
    model.logic6 = Constraint(rule = logic_rule6)
    model.logic7 = Constraint(rule = logic_rule7)
    model.logic8 = Constraint(rule = logic_rule8)
    model.logic9 = Constraint(rule = logic_rule9)
    model.logic10 = Constraint(rule = logic_rule10)
    model.logic11 = Constraint(rule = logic_rule11)

    
    def BDP_rule(model):
        """Determine how much  biodiesel is produced at the final stage"""
        return model.BDP == model.flow_inout[5,1,1,1]
    
    model.BDP_rule = Constraint(rule = BDP_rule, doc = 'Biodiesel produced')
    
    def flowtot_rule(model, a, j, k):
        """Sum up the total flow for every component for economy of scale calculation"""
        return model.flow_intot[a,j,k] == sum(model.flow_in[a,j,k,i] for i in model.i)

    
    model.flow_intot_rule = Constraint(model.a, model.j, model.k, rule = flowtot_rule)
    
    
    
    def EC_rule1(model,a, j, k):
        """This part of the code deals with economy of scale. The exponential
            function is linearized over a certain domain to approximate and keep the model
            as an MILP problem"""
         
        slope = (model.ub**model.N[a,j,k] - model.lb**model.N[a,j,k])/(model.ub - model.lb)
        b = model.lb**model.N[a,j,k] - slope * model.lb 
        
        # Using economy of scale equation: Cost = (Flow^N/FlowRef^N) * (index2020/indexRef)
        return model.EC1[a,j,k] <= (model.flow_intot[a,j,k] * slope + b) / (model.RefSize[a,j,k]**model.N[a,j,k]) + model.M * (1-model.y[a,j,k])
    
        
    def EC_rule2(model, a, j, k):
        """Simply determining the y = ax + b of the approximation"""
        slope = (model.ub**model.N[a,j,k] - model.lb**model.N[a,j,k])/(model.ub - model.lb)
        b = model.lb**model.N[a,j,k] - slope * model.lb 
        
        # Using economy of scale equation: Cost = (Flow^N/FlowRef^N) * (index2020/indexRef)
        return model.EC1[a,j,k] >= (model.flow_intot[a,j,k] * slope + b) / (model.RefSize[a,j,k]**model.N[a,j,k]) - model.M * (1-model.y[a,j,k])
                        
                        
    def EC_rule3(model, a, j, k):
        return model.EC1[a,j,k] <= model.M * model.y[a,j,k]

    
    model.EC_rule1 = Constraint(model.a, model.j, model.k, rule = EC_rule1)
    model.EC_rule2 = Constraint(model.a, model.j, model.k, rule = EC_rule2)
    model.EC_rule3 = Constraint(model.a, model.j, model.k, rule = EC_rule3)
    
    
    def TEC_rule(model):
        """For every k and every j multiply the equipment cost with the total flow and sum it up to determine TEC"""
        return model.TEC == sum(model.EC[a,j,k] * model.EC1[a,j,k] for a in model.a for j in model.j for k in model.k)
    
    model.TEC_rule = Constraint(rule = TEC_rule)
    
    
    def objective_rule(model):
        """Objective is to minimize cost (TEC)"""
        return model.TEC
    
    #Minimize the TEC
    model.objective = Objective(rule = objective_rule, sense = minimize)
    
    
    def pyomo_postprocess(options=None, instance=None, results=None):
      model.flow_intot.display()
    
    
    # This emulates what the pyomo command-line tools does
    from pyomo.opt import SolverFactory
    import pyomo.environ
    opt = SolverFactory("glpk")
    results = opt.solve(model, tee = True)
    #sends results to stdout
    results.write()
    print("\nDisplaying Solution\n" + '-'*60)
    pyomo_postprocess(None, model, results)
    
    return model






