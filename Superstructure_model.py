# -*- coding: utf-8 -*-
"""
Created on Sun Mar 28 16:32:52 2021

@author: Vincent Reurslag
"""

from pyomo.environ import *


def Superstructure_model(Superstructure):
    model = ConcreteModel()
    
    #initialize sets, want to add utilities u later to this
    model.j = Set(initialize = Superstructure.j, doc = 'process stages')
    model.k = Set(initialize = Superstructure.k, doc = 'Technology options')
    model.i = Set(initialize = Superstructure.i, doc = 'Species in reaction mixture')
    
    #initialize parameters. The data comes from the created Superstructure class
    #M parameter is for the big M notation later in the model
    model.SF = Param(model.j, model.k, model.i, initialize = Superstructure.SF_data, doc = 'Split factor data for equipment types')
    model.EC = Param(model.j, model.k, initialize = Superstructure.EC_data, doc = 'Cost data for equipment types')
    model.flow0 = Param(model.i, initialize = Superstructure.F0_data, doc = 'Flow coming out of membrane reactor')
    model.M = Param(initialize = 1e5)
    
    ##initialize variables
    model.flow = Var(model.j, model.k, model.i, bounds = (0.0,None), doc = 'Flow at every equipment for every component')
    model.y = Var(model.j, model.k, domain = Binary, doc = 'Logic variable')
    model.TEC = Var(bounds = (0.0, None), doc = 'Total equipment cost')
    model.BDP = Var(bounds = (0.0, None), doc = 'Biodiesel production')
    model.flowtot = Var(model.j, model.k, bounds = (0.0, None))
    model.flowstage = Var(model.j, model.i, bounds = (0.0, None))
    
    def massbalance_rule1(model, j, k, i):
        """3 massbalance rules for big M implementation:
            It calculates flow[j,k,i] = flow at previous stage * Separation factor * logic_variable
            This equation is an MINLP so it is converted using the big M notation for performance"""
        if j >= 2:
            return model.flow[j,k,i] <= model.flowstage[j-1,i] * model.SF[j,k,i] + model.M * (1-model.y[j,k])
        else:
            return model.flow[j,k,i] == model.flow0[i] * model.SF[j,k,i] * model.y[j,k]
        
    def massbalance_rule2(model, j, k, i):
        if j >= 2:
            return model.flow[j,k,i] >= model.flowstage[j-1,i] * model.SF[j,k,i] - model.M * (1-model.y[j,k])
        else:
            return Constraint.Skip
    
    def massbalance_rule3(model, j, k, i):
        if j >= 2:
            return model.flow[j,k,i] <= model.M * model.y[j,k]
        else:
            return Constraint.Skip
    
    model.massrule1 = Constraint(model.j, model.k, model.i, rule = massbalance_rule1)
    model.massrule2= Constraint(model.j, model.k, model.i, rule = massbalance_rule2)
    model.massrule3 = Constraint(model.j, model.k, model.i, rule = massbalance_rule3)
    
    def flowstage_rule(model, j, i):
        """Simply calculating the total flow at a stage by summing for every equipment at that stage"""
        return model.flowstage[j,i] == sum(model.flow[j,k,i] for k in model.k)
    
    model.flowstage_rule = Constraint(model.j, model.i, rule = flowstage_rule)
    
    def logic_rule(model, j):
        """Only 1 equipment can be chosen at a stage"""
        return sum(model.y[j,k] for k in model.k) == 1
    
    model.logic = Constraint(model.j, rule = logic_rule, doc = 'One option per stage')
    
    def BDP_rule(model):
        """Determine how much  biodiesel is produced at the final stage"""
        return model.BDP == model.flow[5,1,1]
    
    model.BDP_rule = Constraint(rule = BDP_rule, doc = 'Biodiesel produced')
    
    def flowtot_rule(model, j, k):
        """Sum up the total flow for every component for economy of scale calculation"""
        return model.flowtot[j,k] == sum(model.flow[j,k,i] for i in model.i) 
    
    model.flowtot_rule = Constraint(model.j, model.k, rule = flowtot_rule)
    
    def TEC_rule(model):
        """For every k and every j multiply the equipment cost with the total flow and sum it up to determine TEC"""
        return model.TEC == sum(model.EC[j,k] * model.flowtot[j,k] for j in model.j for k in model.k)
    
    model.TEC_rule = Constraint(rule = TEC_rule)
    
    def objective_rule(model):
        """Objective is to minimize cost (TEC)"""
        return model.TEC
    
    #Minimize the TEC
    model.objective = Objective(rule = objective_rule, sense = minimize)
    
    
    def pyomo_postprocess(options=None, instance=None, results=None):
      model.flow.display()
      model.y.display()
      model.flowtot.display()
    
    
    # This emulates what the pyomo command-line tools does
    from pyomo.opt import SolverFactory
    import pyomo.environ
    opt = SolverFactory("glpk")
    results = opt.solve(model)
    #sends results to stdout
    results.write()
    print("\nDisplaying Solution\n" + '-'*60)
    #pyomo_postprocess(None, model, results)
    
    return model






