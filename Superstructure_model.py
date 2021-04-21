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
    model.N = Param(model.a, model.j, model.k, initialize = Superstructure.Sizing_data, doc = 'Economy of scale factor E')
    model.RefSize = Param(model.a, model.j, model.k, initialize = Superstructure.RefSize_data, doc = 'Reference size for economy of scale')
    model.Q = Param(model.a, model.j, model.k, model.i, initialize = Superstructure.Q_data, doc = 'Secondary streams added to unit operations')
    
    model.Tau = Param(model.a , model.j, model.k, model.i, initialize = Superstructure.Tau_data, doc = 'specific energy usage of a utility in a unit operation')
    model.Temp = Param(model.a, model.j, model.k, initialize = Superstructure.Temp_data, doc = 'Temperatures at which the unit operations operate')
    
    
    model.M = Param(initialize = 1e5, doc = 'M parameter to apply big M formuylation')
    model.lb = Param(initialize = 500, doc = 'Lower flow bound in main superstructure to approximate exponential function')
    model.ub = Param(initialize = 1000, doc = 'upper blow bound in main superstructure to approximate exponential function')
    model.T0 = Param(initialize = 80, doc = 'Starting temperature of incoming flow from the reactor')
    
    ##initialize variables
    model.flow_in = Var(model.a, model.j, model.k, model.i, bounds = (0,None), initialize = 0, doc = 'Ingoing flow at every equipment for every component')
    model.y = Var(model.a, model.j, model.k, domain = Binary, doc = 'Logic variable')
    model.TEC = Var(bounds = (0, None), initialize = 0, doc = 'Total equipment cost summed up for all chosen equipments')
    model.BDP = Var(bounds = (0, None), initialize = 0, doc = 'Biodiesel production')
    model.flow_intot = Var(model.a, model.j, model.k, bounds = (0, None), initialize = 0, doc = 'Total flow going into an equipment (all components summed up)')
    model.flow_instage = Var(model.a, model.i, bounds = (0, None), initialize = 0, doc = 'flow going through the different process stages (all 0 flows removed)')
    model.flow_inout = Var(model.a, model.j, model.k, model.i, bounds = (0, None), initialize = 0, doc = 'Main outgoing flow from a unit operation')
    
    model.CostCorr = Var(model.a,model.i,model.k, bounds = (0, None), initialize = 0, doc = 'Cost correction factor for economy of scale (C = RefCost * CostCorr)')
    model.Utility = Var(model.a, model.j, model.k, model.u, bounds = (0 , None), initialize = 0, doc = 'Utility usages for all equipment and all utilities')
    model.HX = Var(model.a, bounds = (None , None), initialize = 0, doc = 'Heat Exchanger cooling and heating duties')
    model.TOT_Utility = Var(model.a, model.j, model.k, model.u, bounds = (0 , None), initialize = 0, doc = 'Simply Utility + HX for total utility usage')
    model.dT = Var(model.a, bounds = (None, None), initialize = 0, doc = 'Temperature difference between stages for HX calculations')
    model.W = Var(model.a, model.j, model.k, model.i, bounds = (0, None), initialize = 0, doc = 'Waste streams from unit operations which are used for downstream processing')
    
    
    
    
    
    
    #Utility calculations
    def utilities_rule(model, a, j, k, u):
        """Simply: Specific_utility_usage = Total_flow_in * Specific_utility_usage"""
        return model.Utility[a,j,k,u] == model.flow_intot[a,j,k] * model.Tau[a,j,k,u]


    def dT_rule1(model,a):
        """Using dT = Temp_data[a] * y - Temp_[a-1] * y and taking the sum to find the temperatures"""
        if a >= 2:
            return model.dT[a] == (sum(model.Temp[a,j,k] * model.y[a,j,k] for j in model.j for k in model.k)  -  sum(model.Temp[a-1,j,k] * model.y[a-1,j,k] for j in model.j for k in model.k)) 
        else:
            return model.dT[a] == (sum(model.Temp[a,j,k] * model.y[a,j,k] for j in model.j for k in model.k) - model.T0)
        
        
    def HX_rule(model, a):
        return model.HX[a] == model.dT[a] * 700
    
  
    model.utilities_rule = Constraint(model.a, model.j, model.k, model.u, rule = utilities_rule)
    model.HX_rule = Constraint(model.a, rule = HX_rule)
    model.dT_rule1 = Constraint(model.a, rule = dT_rule1)

    
    
    
    
    
    
    
    
    #Mass balance calculations
    def massbalance_rule1(model,a, j, k, i):
        """3 massbalance rules for big M implementation:
            It calculates flow[j,k,i] = flow at previous stage * Separation factor * logic_variable
            This equation is an MINLP so it is converted using the big M notation for performance"""
        if a in [2,3,4,5]:
            return model.flow_in[a,j,k,i] <= (model.flow_instage[a-1,i] + model.Q[a,j,k,i]) + model.M * (1-model.y[a,j,k])
        elif a == 1:
            return model.flow_in[a,j,k,i] == (model.flow_in0[i] + model.Q[a,j,k,i]) * model.y[a,j,k]
        else:
            return Constraint.Skip
        
    def massbalance_rule2(model, a, j, k, i):
        if a in [2,3,4,5]:
            return model.flow_in[a,j,k,i] >= (model.flow_instage[a-1,i] + model.Q[a,j,k,i]) - model.M * (1-model.y[a,j,k])
        else:
            return Constraint.Skip
    
    def massbalance_rule3(model, a, j, k, i):
        if a in [2,3,4,5]:
            return model.flow_in[a,j,k,i] <= model.M * model.y[a,j,k]
        else:
            return Constraint.Skip
    
    model.massrule1 = Constraint(model.a, model.j, model.k, model.i, rule = massbalance_rule1)
    model.massrule2= Constraint(model.a, model.j, model.k, model.i, rule = massbalance_rule2)
    model.massrule3 = Constraint(model.a, model.j, model.k, model.i, rule = massbalance_rule3)
    
    
    
    def flowout_rule(model, a, j, k, i):
        """Calculating the flow out of a unit operation"""
        return model.flow_inout[a,j,k,i] == model.flow_in[a,j,k,i] * model.SF[a,j,k,i]
    
    def waste_rule(model, a, j, k, i):
        """Waste = Flow_in - Flow_out of a specific unit operation"""
        return model.W[a,j,k,i] == model.flow_in[a,j,k,i] - model.flow_inout[a,j,k,i]
    
    model.flow_inout_rule = Constraint(model.a, model.j, model.k, model.i, rule = flowout_rule)
    model.waste_rule = Constraint(model.a, model.j, model.k, model.i, rule = waste_rule)
    
    
    
    def flowstage_rule(model, a, i):
        """Simply calculating the total flow at a stage by summing for every equipment at that stage"""
        return model.flow_instage[a,i] == sum(model.flow_inout[a,j,k,i] for j in model.j for k in model.k)
    
    model.flow_instage_rule = Constraint(model.a, model.i, rule = flowstage_rule)
    
    
    
    def flowtot_rule(model, a, j, k):
        """Sum up the total flow for every component for economy of scale calculation"""
        return model.flow_intot[a,j,k] == sum(model.flow_in[a,j,k,i] for i in model.i)

    
    model.flow_intot_rule = Constraint(model.a, model.j, model.k, rule = flowtot_rule)
    
    
    
    
    #Glycerol processing
    def Glycerols1_rule(model, k, i):
        return model.flow_in[6,1,k,i] <= sum(model.W[1,1,k,i] for k in model.k)  + model.M * (1 - model.y[6,1,k])
    
    def Glycerols2_rule(model, k, i):
        return model.flow_in[6,1,k,i] >= sum(model.W[1,1,k,i] for k in model.k) - model.M * (1 - model.y[6,1,k])
    
    def Glycerols3_rule(model, k, i):
        return model.flow_in[6,1,k,i] <= model.M * model.y[6,1,k]
    
    model.Glycerols1_rule = Constraint(model.k, model.i, rule = Glycerols1_rule)
    model.Glycerols2_rule = Constraint(model.k, model.i, rule = Glycerols2_rule)
    model.Glycerols3_rule = Constraint(model.k, model.i, rule = Glycerols3_rule)
    
    def logic_glyc(model):
        return sum(model.y[1,1,k] for k in model.k) - sum(model.y[6,1,k] for k in model.k) == 0
    
    model.logic_glyc_rule = Constraint(rule = logic_glyc)
    
    #Logic rules
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

    
    
    
    
    
    
    
    
    #Cost calculations
    def EC_rule1(model,a, j, k):
        """This part of the code deals with economy of scale. The exponential
            function is linearized over a certain domain to approximate and keep the model
            as an MILP problem"""
         
        slope = (model.ub**model.N[a,j,k] - model.lb**model.N[a,j,k])/(model.ub - model.lb)
        b = model.lb**model.N[a,j,k] - slope * model.lb 
        
        # Using economy of scale equation: Cost = (Flow^N/FlowRef^N) * (index2020/indexRef)
        return model.CostCorr[a,j,k] <= (model.flow_intot[a,j,k] * slope + b) / (model.RefSize[a,j,k]**model.N[a,j,k]) + model.M * (1-model.y[a,j,k])
    
        
    def EC_rule2(model, a, j, k):
        """Simply determining the y = ax + b of the approximation"""
        slope = (model.ub**model.N[a,j,k] - model.lb**model.N[a,j,k])/(model.ub - model.lb)
        b = model.lb**model.N[a,j,k] - slope * model.lb 
        
        # Using economy of scale equation: Cost = (Flow^N/FlowRef^N) * (index2020/indexRef)
        return model.CostCorr[a,j,k] >= (model.flow_intot[a,j,k] * slope + b) / (model.RefSize[a,j,k]**model.N[a,j,k]) - model.M * (1-model.y[a,j,k])
                        
                        
    def EC_rule3(model, a, j, k):
        return model.CostCorr[a,j,k] <= model.M * model.y[a,j,k]

    
    model.EC_rule1 = Constraint(model.a, model.j, model.k, rule = EC_rule1)
    model.EC_rule2 = Constraint(model.a, model.j, model.k, rule = EC_rule2)
    model.EC_rule3 = Constraint(model.a, model.j, model.k, rule = EC_rule3)
    
    
    def TEC_rule(model):
        """For every k and every j multiply the equipment cost with the total flow and sum it up to determine TEC"""
        return model.TEC == sum(model.EC[a,j,k] * model.CostCorr[a,j,k] for a in model.a for j in model.j for k in model.k)
    
    model.TEC_rule = Constraint(rule = TEC_rule)
    
    
    
    
    
    
    
    
    #MISC calculations 
    def BDP_rule(model):
        """Determine how much  biodiesel is produced at the final stage"""
        return model.BDP == model.flow_inout[5,1,1,1]
    
    model.BDP_rule = Constraint(rule = BDP_rule, doc = 'Biodiesel produced')
    








    #Objective function
    def objective_rule(model):
        """Objective is to minimize cost (TEC)"""
        return model.TEC
    
    #Minimize the TEC
    model.objective = Objective(rule = objective_rule, sense = minimize)
    
    
    
    
    
    
    
    
    
    
    #Result processing and calling the solver
    def pyomo_postprocess(options=None, instance=None, results=None):
      model.flow_intot.display()
      model.dT.display()
    
    
    # This emulates what the pyomo command-line tools does
    from pyomo.opt import SolverFactory
    import pyomo.environ
    opt = SolverFactory("glpk")
    results = opt.solve(model)
    #sends results to stdout
    results.write()
    print("\nDisplaying Solution\n" + '-'*60)
    pyomo_postprocess(None, model, results)
    
    return model






