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
    model.k = Set(initialize = Superstructure.k, doc = 'AIChnology options')
    model.i = Set(initialize = Superstructure.i, doc = 'Species in reaction mixture')
    model.u = Set(initialize = Superstructure.u, doc = 'Utilities considered')
    model.hi = Set(initialize = [1,2,3,4,5])
    
    
    #initialize parameters. The data comes from the created Superstructure class
    #M parameter is for the big M notation later in the model
    model.SF = Param(model.a, model.j, model.k, model.i, initialize = Superstructure.SF_data, doc = 'Split factor data for equipment types')
    model.EC = Param(model.a, model.j, model.k, initialize = Superstructure.RefCost_data, doc = 'Cost data for equipment types')
    model.RefIndex = Param(model.a, model.j, model.k, initialize = Superstructure.RefIndex_data, doc = 'Index data for economy of scale calculation')
    model.flow_in0 = Param(model.i, initialize = Superstructure.F0_data, doc = 'Flow coming out of membrane reactor')
    model.N = Param(model.a, model.j, model.k, initialize = Superstructure.Sizing_data, doc = 'Economy of scale factor E')
    model.RefSize = Param(model.a, model.j, model.k, initialize = Superstructure.RefSize_data, doc = 'Reference size for economy of scale')
    model.Q = Param(model.a, model.j, model.k, model.i, initialize = Superstructure.Q_data, doc = 'Secondary streams added to unit operations')
    
    model.Tau = Param(model.a , model.j, model.k, model.i, initialize = Superstructure.Tau_data, doc = 'specific energy usage of a utility in a unit operation')
    model.Temp = Param(model.a, model.j, model.k, initialize = Superstructure.Temp_data, doc = 'Temperatures at which the unit operations operate')
    
    
    model.M = Param(initialize = 1e5, doc = 'M parameter to apply big M formuylation')
    model.lb = Param(initialize = 500, doc = 'Lower flow bound in main superstructure to approximate exponential function')
    model.ub = Param(initialize = 1000, doc = 'upper blow bound in main superstructure to approximate exponential function')
    model.lbGlyc = Param(initialize = 50, doc = 'Lower flow bound in Glycerol superstructure')
    model.ubGlyc = Param(initialize = 150, doc = 'Upper flow bound in glycerol superstrucuture')
    model.T0 = Param(initialize = 60, doc = 'Starting temperature of incoming flow from the reactor')
    
    model.K_eng = Param(initialize = 3.3, doc = 'Coefficient for engineering and planning')
    model.IR = Param(initialize = 0.1, doc = 'Interest Rate on investment')
    model.LT = Param(initialize = 20, doc = 'Estimated lifetime of plant')
    model.H = Param(initialize = 8000, doc = 'Number of operating hours of a plant yearly')
    model.CostIndex = Param(initialize = 607.5, doc = 'Index cost for 2019')
    
    model.CCost = Param(model.i, initialize = Superstructure.CCost_data, doc = 'Cost per kg for components used')
    model.UCost = Param(model.u, initialize = Superstructure.uCost_data, doc = 'Costs for utility usage')
    
    model.FameSell = Param(initialize = 1.5, doc = 'biodiesel selling price')
    model.GlycWaste = Param(initialize = -0.015, doc = 'Cost for glycerol waste')
    model.GlycSell1 = Param(initialize = 0.17, doc = 'Selling upgraded glycerol 80%')
    model.GlycSell2 = Param(initialize = 0.895, doc = 'Selling upgraded glycerol 99%')
    model.GlycSell3 = Param(initialize = 1.275, doc = 'Selling upgraded glycerol 99.9%')
    
    
    model.WaterWashingOC = Param(initialize = 0.024, doc = 'Water washing cost in $/kg including waste disposal')
    model.MagnesolWashOC = Param(initialize = 0.036, doc = 'Magnesol washing cost in $/kg including filtering')
    model.IonExchangeOC = Param(initialize = 0.030, doc = 'Ion exchange washing cost in $/kg for resins')
    model.FameDensity = Param(initialize = 0.8747, doc = 'Biodiesel density in kg/l')
    model.GlycDensity = Param(initialize = 1.26, doc = 'Glycerol density in kg/l')
    
    ##initialize variables
    model.flow_in = Var(model.a, model.j, model.k, model.i, bounds = (0,None), initialize = 0, doc = 'Ingoing flow at every equipment for every component')
    model.y = Var(model.a, model.j, model.k, domain = Binary, doc = 'Logic variable')
    model.BDP = Var(bounds = (0, None), initialize = 0, doc = 'Biodiesel production')
    model.flow_intot = Var(model.a, model.j, model.k, bounds = (0, None), initialize = 0, doc = 'Total flow going into an equipment (all components summed up)')
    model.flow_instage = Var(model.a, model.i, bounds = (0, None), initialize = 0, doc = 'flow going through the different process stages (all 0 flows removed)')
    model.flow_inout = Var(model.a, model.j, model.k, model.i, bounds = (0, None), initialize = 0, doc = 'Main out flow from a unit operation')
    model.flow_outtot = Var(model.a, model.j, model.k, bounds = (0, None), initialize = 0, doc = 'Summed up for components outgoing flow from a unit operation')
    
    model.CostCorr = Var(model.a,model.j,model.k, bounds = (0, None), initialize = 0, doc = 'Cost correction factor for economy of scale (C = RefCost * CostCorr)')
    model.Utility = Var(model.a, model.j, model.k, model.u, bounds = (0 , None), initialize = 0, doc = 'Utility usages for all equipment and all utilities')
    model.HX = Var(model.a, bounds = (None , None), initialize = 0, doc = 'Heat Exchanger cooling and heating duties')
    model.TOT_Utility = Var(model.a, model.j, model.k, model.u, bounds = (0 , None), initialize = 0, doc = 'Simply Utility + HX for total utility usage')
    model.dT = Var(model.a, bounds = (None, None), initialize = 0, doc = 'Temperature difference between stages for HX calculations')
    model.dT1 = Var(model.a, bounds = (None, None), initialize = 0, doc = 'Temperature difference between stages for HX calculations')
    model.W = Var(model.a, model.j, model.k, model.i, bounds = (0, None), initialize = 0, doc = 'Waste streams from unit operations which are used for downstream processing')
    
    
    model.AIC = Var(bounds = (0, None), initialize = 0, doc = 'Total equipment cost summed up for all chosen equipments')
    model.TUC = Var(bounds = (0, None), initialize = 0, doc = 'Total utility costs')
    model.RMC = Var(bounds = (0, None), initialize = 0, doc = 'Material costs for make up flows')
    model.OMC = Var(bounds = (0, None), initialize= 0, doc = 'Operating and managment cost')
    model.MTAC = Var(bounds = (None, None), initialize = 0, doc = 'Annual profit or not')
    
    model.GlycAIC = Var(bounds = (0, None), initialize = 0, doc = 'Total equipment cost summed up for all chosen equipments')
    model.GlycTUC = Var(bounds = (0, None), initialize = 0, doc = 'Total utility costs')
    model.GlycRMC = Var(bounds = (0, None), initialize = 0, doc = 'Material costs for make up flows')
    model.GlycOMC = Var(bounds = (0, None), initialize= 0, doc = 'Operating and managment cost')
    model.GlycMTAC = Var(bounds = (None, None), initialize = 0, doc = 'Annual profit or not')
    model.GlycCost = Var(initialize = 0, doc = 'Profit or loss made from glyceol waste or byproduct')
    model.NeutPrice = Var()

    
    model.IRCalc = Var(initialize = 0)
    model.WashingOC = Var(initialize = 0)
    model.GlycWashingOC = Var(initialize = 0)
    
    model.HotU = Var()
    model.ColdU = Var()
    model.CP = Param(model.i, initialize = Superstructure.CP_data)
    model.CPtot = Var(model.a, model.j)
    model.CP0 = Var()
    model.S = Param(model.hi, initialize = {1:10, 2:60, 3:10, 4:25, 5:10})
    model.dH = Var(model.hi)
 
    model.F0Cost = Var(doc = 'Cost of ingoing feed')
    model.OilPrice = Param(initialize = 1.1, doc = 'price per kg of oil')
    model.MeOHPrice = Param(initialize = 0.214, doc = 'price per kg of MeOH')
    model.NaOHPrice = Param(initialize = 0.24, doc = 'price per kg of NaOH')
    model.OilAmount = Param(initialize = 1050, doc = 'amount of oil feed to membrane system')
    model.MeOHAmount= Param(initialize = 314, doc = 'amount of methanol to membrane system')
    model.NaOHAmount = Param(initialize = 5.25, doc = 'amount of NaOH to membrane system')
    

    
    model.HotUPrice = Param(initialize = 35, doc = 'price of HP in $/MWh from paper of phillip')
    model.ColdUPrice = Param(initialize = 0.27, doc = 'Price of CW in $/MWh from paper of phillip')
    model.HotUCost = Var()
    model.ColdUCost = Var()
    
    model.ECmemreactor = Param(initialize = 350000, doc =  'cost of membrane reactor in $')
    model.MembraneReactorCost = Var()
    
    model.ElectricityAmount = Var()
    model.HeatingAmount = Var()
    model.CoolingAmount = Var()
    model.GlycNeutPrice = Var()

    
    
    
    #Utility calculations
    def utilities_rule(model, a, j, k, u):
        """Simply: Specific_utility_usage = Total_flow_in * Specific_utility_usage"""
        return model.Utility[a,j,k,u] == model.flow_intot[a,j,k] * model.Tau[a,j,k,u]
    

    def ElectricityAmount_rule(model):
        return model.ElectricityAmount == sum(model.Utility[a,j,k,1] * model.H * (1/1000) * model.UCost[1] for a in model.a for j in model.j for k in model.k)
    
    model.ElectricityAmount_rule = Constraint(rule = ElectricityAmount_rule)
    
    def HeatingAmount_rule(model):
        return model.HeatingAmount == sum(model.Utility[a,j,k,2] * model.H * (1/1000) * model.UCost[2] for a in model.a for j in model.j for k in model.k)
    
    model.HeatingAmount_rule = Constraint(rule = HeatingAmount_rule)
    
    def CoolingAmount_rule(model):
        return model.CoolingAmount == sum(model.Utility[a,j,k,3] * model.H * (1/1000) * model.UCost[3] for a in model.a for j in model.j for k in model.k)
    
    model.CoolingAmount_rule = Constraint(rule = CoolingAmount_rule)
    

    def dT_rule1(model,a):
        """Using dT = Temp_data[a] * y - Temp_[a-1] * y and taking the sum to find the temperatures"""
        if a in [2,3,4,5,7,8]:
            return model.dT[a] == (sum(model.Temp[a,j,k] * model.y[a,j,k] for j in model.j for k in model.k)  -  sum(model.Temp[a-1,j,k] * model.y[a-1,j,k] for j in model.j for k in model.k)) 
        elif a in [1,6]:
            return model.dT[a] == (sum(model.Temp[a,j,k] * model.y[a,j,k] for j in model.j for k in model.k) - model.T0)



     
        
    def HX_rule(model, a):
        return model.HX[a] == model.dT[a] * sum(model.flow_instage[a,i] for i in model.i)
    
  
    model.utilities_rule = Constraint(model.a, model.j, model.k, model.u, rule = utilities_rule)
    model.HX_rule = Constraint(model.a, rule = HX_rule)
    model.dT_rule1 = Constraint(model.a, rule = dT_rule1)

    
    
    
    
    #Mass balance calculations
    def massbalance_rule1(model,a, j, k, i):
        """3 massbalance rules for big M implementation:
            It calculates flow[j,k,i] = flow at previous stage * Separation factor * logic_variable
            This equation is an MINLP so it is converted using the big M notation for performance"""
        if a in [2,3,4,5,7,8]:
            return model.flow_in[a,j,k,i] <= (model.flow_instage[a-1,i] + model.Q[a,j,k,i]) + model.M * (1-model.y[a,j,k])
        elif a == 1:
            return model.flow_in[a,j,k,i] == (model.flow_in0[i] + model.Q[a,j,k,i]) * model.y[a,j,k]
        else:
            return Constraint.Skip
        
    def massbalance_rule2(model, a, j, k, i):
        if a in [2,3,4,5,7,8]:
            return model.flow_in[a,j,k,i] >= (model.flow_instage[a-1,i] + model.Q[a,j,k,i]) - model.M * (1-model.y[a,j,k])
        else:
            return Constraint.Skip
    
    def massbalance_rule3(model, a, j, k, i):
        if a in [2,3,4,5,7,8]:
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
    
    def flowouttot_rule(model, a, j, k):
        return model.flow_outtot[a,j,k] == sum(model.flow_inout[a,j,k,i] for i in model.i)
    
    model.flow_outtot_rule = Constraint(model.a, model.j, model.k, rule = flowouttot_rule)
    
    
    
    
    
    
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
    
    
    
    def Glycerols1_rule1(model, k, i):
        return model.flow_in[6,2,k,i] <= sum(model.W[2,3,k,i] for k in model.k)  + model.M * (1 - model.y[6,2,k])
    
    def Glycerols2_rule1(model, k, i):
        return model.flow_in[6,2,k,i] >= sum(model.W[2,3,k,i] for k in model.k) - model.M * (1 - model.y[6,2,k])
    
    def Glycerols3_rule1(model, k, i):
        return model.flow_in[6,2,k,i] <= model.M * model.y[6,2,k]
    
    model.Glycerols1_rule1 = Constraint(model.k, model.i, rule = Glycerols1_rule1)
    model.Glycerols2_rule1 = Constraint(model.k, model.i, rule = Glycerols2_rule1)
    model.Glycerols3_rule1 = Constraint(model.k, model.i, rule = Glycerols3_rule1)
    
    
    
    def Glycerols1_rule2(model, k, i):
        return model.flow_in[6,3,k,i] <= sum(model.W[4,3,k,i] for k in model.k)  + model.M * (1 - model.y[6,3,k])
    
    def Glycerols2_rule2(model, k, i):
        return model.flow_in[6,3,k,i] >= sum(model.W[4,3,k,i] for k in model.k) - model.M * (1 - model.y[6,3,k])
    
    def Glycerols3_rule2(model, k, i):
        return model.flow_in[6,3,k,i] <= model.M * model.y[6,3,k]
    
    model.Glycerols1_rule2 = Constraint(model.k, model.i, rule = Glycerols1_rule2)
    model.Glycerols2_rule2 = Constraint(model.k, model.i, rule = Glycerols2_rule2)
    model.Glycerols3_rule2 = Constraint(model.k, model.i, rule = Glycerols3_rule2)
    
    
    
    
    def Glycerols1_rule3(model, k, i):
        return model.flow_in[6,4,k,i] <= sum(model.W[4,3,k,i] for k in model.k)  + model.M * (1 - model.y[6,4,k])
    
    def Glycerols2_rule3(model, k, i):
        return model.flow_in[6,4,k,i] >= sum(model.W[4,3,k,i] for k in model.k) - model.M * (1 - model.y[6,4,k])
    
    def Glycerols3_rule3(model, k, i):
        return model.flow_in[6,4,k,i] <= model.M * model.y[6,4,k]
    
    model.Glycerols1_rule3 = Constraint(model.k, model.i, rule = Glycerols1_rule3)
    model.Glycerols2_rule3 = Constraint(model.k, model.i, rule = Glycerols2_rule3)
    model.Glycerols3_rule3 = Constraint(model.k, model.i, rule = Glycerols3_rule3)
    
    
    def logic_glyc(model):
        return sum(model.y[1,1,k] for k in model.k) - sum(model.y[6,1,k] for k in model.k) == 0
    
    def logic_glyc1(model):
        return sum(model.y[2,3,k] for k in model.k) - sum(model.y[6,2,k] for k in model.k) == 0
    
    def logic_glyc2(model):
        return sum(model.y[4,3,k] for k in model.k) - sum(model.y[6,3,k] for k in model.k) == 0
    
    model.logic_glyc_rule  = Constraint(rule = logic_glyc)
    model.logic_glyc_rule1 = Constraint(rule = logic_glyc1)
    model.logic_glyc_rule2 = Constraint(rule = logic_glyc2)
    
    
    
    def logic_glyc3(model):
        """If waste is selected all other options will be ruled out"""
        return 2 * model.y[6,1,1] - model.y[7,1,1] - model.y[8,1,1] == 0
    
    def logic_glyc4(model):
        """If processing is selected either selling or further processing becomes avialable"""
        return model.y[6,1,2] - model.y[7,1,2] - model.y[7,1,3] == 0 
    
    def logic_glyc5(model):
        """If sell is selected all options will be ruled out """
        return model.y[7,1,2] - model.y[8,1,2] == 0
    
    def logic_glyc6(model):
        """If again procesing is selected premium selling must be slected as well"""
        return model.y[7,1,3] - model.y[8,1,3] == 0
    
    
    
    def logic_glyc7(model):
        """If sell is selected all other options will be ruled out"""
        return 2 * model.y[6,2,1] - model.y[7,2,1] - model.y[8,2,1] == 0
    
    def logic_glyc8(model):
        """If processing is selected either selling or further processing becomes avialable"""
        return model.y[6,2,2] - model.y[7,2,2] == 0
    
    def logic_glyc9(model):
        """If sell is selected all other options will be ruled out"""
        return model.y[7,2,2] - model.y[8,2,2] - model.y[8,2,3] == 0
    

    
    
    
    def logic_glyc11(model):
        return 2 * model.y[6,3,1] - model.y[7,3,1] - model.y[8,3,1] == 0
    
    def logic_glyc12(model):
        return 2 * model.y[6,3,2] - model.y[7,3,2] - model.y[8,3,2] == 0
    
    model.logic_glyc_rule3 = Constraint(rule = logic_glyc3)
    model.logic_glyc_rule4 = Constraint(rule = logic_glyc4)
    model.logic_glyc_rule5 = Constraint(rule = logic_glyc5)
    model.logic_glyc_rule6 = Constraint(rule = logic_glyc6)
    model.logic_glyc_rule7 = Constraint(rule = logic_glyc7)
    model.logic_glyc_rule8 = Constraint(rule = logic_glyc8)
    model.logic_glyc_rule9 = Constraint(rule = logic_glyc9)

    model.logic_glyc_rule11 = Constraint(rule = logic_glyc11)
    model.logic_glyc_rule12 = Constraint(rule = logic_glyc12)

    
    def GlycCost_rule(model):
        return model.GlycCost ==  (model.flow_inout[8,1,1,3] * model.GlycWaste + (model.flow_inout[8,1,2,3] + model.flow_inout[8,2,1,3]) * model.GlycSell1 + \
               (model.flow_inout[8,1,3,3] + model.flow_inout[8,2,2,3] + model.flow_inout[8,3,1,3]) * model.GlycSell2 + \
               (model.flow_inout[8,2,3,3] + model.flow_inout[8,3,2,3]) * model.GlycSell3) * model.H
        
    model.GlycCost_rule = Constraint(rule = GlycCost_rule)
    
    
    def GlycAIC_rule(model):
        """Annualized equipment costs using liftime and interest rates"""
        return model.GlycAIC == sum(model.EC[a,j,k] * model.CostCorr[a,j,k] for a in [6,7,8] for j in model.j for k in model.k) * model.IRCalc
    
    model.GlycAIC_rule = Constraint(rule = GlycAIC_rule)
    
    def GlycTUC_rule(model):
        """Calculating total utility costs by multiplying usage with the price and summing everything up"""
        return model.GlycTUC == sum(model.Utility[a,j,k,u] * model.H * (1/1000) * model.UCost[u] for a in [6,7,8] for j in model.j for k in model.k for u in model.u)
    
    model.GlycTUC_rule = Constraint(rule = GlycTUC_rule)
    
    def GlycRMC_rule(model):
        """Cost calculation for make up flows Q"""
        return model.GlycRMC == sum(model.Q[a,j,k,i] * model.CCost[i] for a in [6,7,8] for j in model.j for k in model.k for i in model.i) + model.GlycNeutPrice
    
    model.GlycRMC_rule = Constraint(rule = GlycRMC_rule)
    
    def GlycOMC_rule(model):
        """Calculation for management and operating costs"""
        return model.GlycOMC == 0.02 * model.GlycAIC
    
    def GlycWashing_rule(model):
        return model.GlycWashingOC == (model.flow_intot[8,1,3] + model.flow_intot[7,2,2]) * model.H * model.IonExchangeOC * model.GlycDensity
    
    model.GlycWashing_rule = Constraint(rule = GlycWashing_rule)
    
    model.GlycOMC_rule = Constraint(rule = GlycOMC_rule)
    
    def GlycMTAC_rule(model):
        return model.GlycMTAC == model.GlycAIC + model.GlycOMC + model.GlycWashingOC
    
    model.GlycMTAC_rule = Constraint(rule = GlycMTAC_rule)
    
    
    
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
        return sum(model.y[4,2,k] for k in model.k) + sum(model.y[4,3,k] for k in model.k) - sum(model.y[5,1,k] for k in model.k) == 0
    
    def logic_rule11(model):
        return sum(model.y[4,1,k] for k in model.k) - model.y[5,2,1] == 0
    

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
        
        if a in [1,2,3,4,5]:
            slope = (model.ub**model.N[a,j,k] - model.lb**model.N[a,j,k])/(model.ub - model.lb)
            b = model.lb**model.N[a,j,k] - slope * model.lb 
        elif a in [6,7,8]:
            slope = (model.ubGlyc**model.N[a,j,k] - model.lbGlyc**model.N[a,j,k])/(model.ubGlyc - model.lbGlyc)
            b = model.lbGlyc**model.N[a,j,k] - slope * model.lbGlyc       
        
        # Using economy of scale equation: Cost = (Flow^N/FlowRef^N) * (index2020/indexRef)
        return model.CostCorr[a,j,k] <= (model.flow_intot[a,j,k] * slope + b) / (model.RefSize[a,j,k]**model.N[a,j,k]) * (model.CostIndex / model.RefIndex[a,j,k]) + model.M * (1-model.y[a,j,k])
    
        
    def EC_rule2(model, a, j, k):
        """Simply determining the y = ax + b of the approximation"""
        
        if a in [1,2,3,4,5]:
            slope = (model.ub**model.N[a,j,k] - model.lb**model.N[a,j,k])/(model.ub - model.lb)
            b = model.lb**model.N[a,j,k] - slope * model.lb 
        elif a in [6,7,8]:
            slope = (model.ubGlyc**model.N[a,j,k] - model.lbGlyc**model.N[a,j,k])/(model.ubGlyc - model.lbGlyc)
            b = model.lbGlyc**model.N[a,j,k] - slope * model.lbGlyc 
        
        # Using economy of scale equation: Cost = (Flow^N/FlowRef^N) * (index2020/indexRef)
        return model.CostCorr[a,j,k] >= (model.flow_intot[a,j,k] * slope + b) / (model.RefSize[a,j,k]**model.N[a,j,k]) * (model.CostIndex / model.RefIndex[a,j,k]) - model.M * (1-model.y[a,j,k])
                        
                        
    def EC_rule3(model, a, j, k):
        return model.CostCorr[a,j,k] <= model.M * model.y[a,j,k]

    
    model.EC_rule1 = Constraint(model.a, model.j, model.k, rule = EC_rule1)
    model.EC_rule2 = Constraint(model.a, model.j, model.k, rule = EC_rule2)
    model.EC_rule3 = Constraint(model.a, model.j, model.k, rule = EC_rule3)
    
    def IRCalc_rule(model):
        return model.IRCalc == (model.IR * (model.IR + 1)**model.LT)/((model.IR + 1)**model.LT - 1) * 1.05 * 5.93
    
    model.IRCalc_rule = Constraint(rule = IRCalc_rule)
    
    def AIC_rule(model):
        """Annualized equipment costs using liftime and interest rates"""
        return model.AIC == sum(model.EC[a,j,k] * model.CostCorr[a,j,k] for a in [1,2,3,4,5] for j in model.j for k in model.k) * model.IRCalc + model.MembraneReactorCost
    
    model.AIC_rule = Constraint(rule = AIC_rule)
    
    def TUC_rule(model):
        """Calculating total utility costs by multiplying usage with the price and summing everything up"""
        return model.TUC == sum(model.Utility[a,j,k,u]  * model.H * (1/1000) * model.UCost[u] for a in [1,2,3,4,5] for j in model.j for k in model.k for u in model.u)
    
    model.TUC_rule = Constraint(rule = TUC_rule)
    
    def RMC_rule(model):
        """Cost calculation for make up flows Q"""
        return model.RMC == sum(model.Q[a,j,k,i] * model.CCost[i] for a in [1,2,3,4,5] for j in model.j for k in model.k for i in model.i)  + model.NeutPrice 
    
    model.RMC_rule = Constraint(rule = RMC_rule)
    
    def OMC_rule(model):
        """Calculation for management and operating costs"""
        return model.OMC == 0.02 * model.AIC
    
    model.OMC_rule = Constraint(rule = OMC_rule)
    
    def WashingOC_rule(model):
        return model.WashingOC == ( (model.flow_intot[3,1,1] + model.flow_intot[4,3,1] + model.flow_intot[4,2,1] + model.flow_intot[4,3,1]) * model.WaterWashingOC + \
           (model.flow_intot[3,1,2] + model.flow_intot[4,2,2]) * model.MagnesolWashOC + \
           (model.flow_intot[3,1,3] + model.flow_intot[4,2,3]) * model.IonExchangeOC) * model.H
               
    model.WahsingOC_rule = Constraint(rule = WashingOC_rule)
    
    
    def MembraneReactorCost_rule(model):
        return model.MembraneReactorCost == model.ECmemreactor * model.IRCalc
        
    model.MembraneReactorCost_rule = Constraint(rule = MembraneReactorCost_rule)
        

    
    
    
    def MTAC_rule(model):
        """Modified total annualized cost"""
        return model.MTAC == model.AIC + model.OMC + model.WashingOC + model.RMC + model.TUC 
    
    model.MTAC_rule = Constraint(rule = MTAC_rule)
    
    
    #MISC calculations 
    def BDP_rule(model):
        """Determine how much  biodiesel is produced at the final stage"""
        return model.BDP == model.flow_inout[5,1,1,1] * model.FameSell * model.H
    
    model.BDP_rule = Constraint(rule = BDP_rule, doc = 'Biodiesel produced')



    def Flow0cost_rule(model):
        return model.F0Cost == (model.OilAmount * model.OilPrice + model.MeOHAmount * model.MeOHPrice + model.NaOHAmount * model.NaOHPrice) * model.H
    
    model.Flow0cost_rule = Constraint(rule = Flow0cost_rule)
    
    
    model.mwNaOH = Param(initialize = 0.04, doc = 'molar weight NaOH in kg/mol')
    model.mwH3PO4 = Param(initialize = 0.098, doc = 'molar weight H3PO4 in kg/mol')
    model.H3PO4Price = Param(initialize = 0.8, doc = 'price of H3PO4 in $/kg')
    
    model.mwH2SO4 = Param(initialize = 0.098, doc = 'molar weight H2SO4 in kg/mol')
    model.H2SO4Price = Param(initialize = 0.65, doc = 'price of H2SO4 in $/kg')
    
    model.mwHCl = Param(initialize = 0.036, doc = 'molar weight HCl in kg/mol')
    model.HClPrice = Param(initialize = 0.8, doc = 'price of HCl in $/kg')
    
    
    
    
    def GlycNeutralization_rule(model):
        return model.GlycNeutPrice == (model.flow_in[7,1,3,4] + model.flow_in[6,2,2,4])  * (model.mwH3PO4 * model.H3PO4Price * model.H) / (model.mwNaOH * 3)
    
    model.GlycNeutralization_rule = Constraint(rule = GlycNeutralization_rule)
    
    
    def Neutralization_rule(model):
        return model.NeutPrice ==  (model.flow_in[2,1,1,4] + model.flow_in[2,4,1,4] + model.flow_in[3,2,1,4]) * (model.mwH3PO4 * model.H3PO4Price * model.H) / (model.mwNaOH * 3) \
        + (model.flow_in[2,1,2,4] + model.flow_in[2,4,2,4] + model.flow_in[3,2,2,4]) * (model.mwH2SO4 * model.H2SO4Price * model.H) / (model.mwNaOH * 2) \
        + (model.flow_in[2,1,3,4] + model.flow_in[2,4,3,4] + model.flow_in[3,2,3,4]) * (model.mwHCl * model.HClPrice * model.H) / (model.mwNaOH * 1) 
                           
    model.Neutralization_rule = Constraint(rule = Neutralization_rule)
    
    
    
    model.CP0_2 = Var()
    model.CP0_1 = Var()

    

    model.CPin = Var(model.a, model.j)

    #Heat integration calculations
    def CPtot_rule(model,a,j):
        """Determine heat capacity of flows""" 
        return model.CPtot[a,j] == sum(model.flow_inout[a,j,k,i] * model.CP[i] for k in model.k for i in model.i)
    
    def CPtot_rule1(model,a,j):
        """Determine heat capacity of flows""" 
        return model.CPin[a,j] == sum(model.flow_in[a,j,k,i] * model.CP[i] for k in model.k for i in model.i)
    
    def CP0_rule1(model):
        """Heat capacity of incoming flow"""
        return model.CP0_1 == sum(model.flow_in0[i] * model.CP[i] for i in model.i) * sum(model.y[1,1,k] for k in model.k)
    
    def CP0_rule2(model):
        """Heat capacity of incoming flow"""
        return model.CP0_2 == sum(model.flow_in0[i] * model.CP[i] for i in model.i) * sum(model.y[1,2,k] for k in model.k)
    
    model.CPtot_rule = Constraint(model.a,model.j,rule = CPtot_rule)
    model.CPtot_rule1 = Constraint(model.a,model.j,rule = CPtot_rule1)
    model.CP0_rule1 = Constraint(rule = CP0_rule1)
    model.CP0_rule2 = Constraint(rule = CP0_rule2)


    
    def dH1_rule(model):
        """What streams belong to the first temperature inteval"""
        return model.dH[1] == model.S[1] * (-model.CP0_2 - model.CPin[2,2] - model.CPtot[3,1] - model.CPtot[4,2] - model.CPtot[4,3])
    
    def dH2_rule(model):
        """What streams belong to the second temperature inteval"""
        return model.dH[2] == model.dH[1] +  model.S[2] * (-model.CP0_2 - model.CPin[2,2] + model.CPin[2,3] + model.CPin[2,4]  + model.CPtot[2,2] - model.CPtot[3,1]  + model.CPtot[4,1] - model.CPtot[4,2] - model.CPtot[4,3] + model.CPtot[5,1])
    
    def dH3_rule(model):
        """What streams belong to the second temperature inteval"""
        return model.dH[3] == model.dH[2] +  model.S[3] * (-model.CPin[2,2] + model.CPin[2,3] + model.CPin[2,4] - model.CPtot[2,1] + model.CPtot[2,2] - model.CPtot[2,4] - model.CPtot[3,2] + model.CPtot[4,1] + model.CPtot[5,1])
    
    def dH4_rule(model):
        """What streams belong to the third temperature inteval"""
        return model.dH[4] == model.dH[3] +  model.S[4] * (model.CP0_1 - model.CPin[2,2] + model.CPin[2,3] + model.CPin[2,4] - model.CPtot[2,1] + model.CPtot[2,2] - model.CPtot[2,4] - model.CPtot[3,2] + model.CPtot[4,1] + model.CPtot[5,1])
    
    def dH5_rule(model):
        """What streams belong to the fourth temperature inteval"""
        return model.dH[5] == model.dH[4] +  model.S[5] * (model.CP0_1 + model.CPin[2,3] + model.CPin[2,4] + model.CPtot[2,2] + model.CPtot[4,1] + model.CPtot[5,1])
    
    
    model.dH1_rule = Constraint(rule = dH1_rule)
    model.dH2_rule = Constraint(rule = dH2_rule)
    model.dH3_rule = Constraint(rule = dH3_rule)
    model.dH4_rule = Constraint(rule = dH4_rule)
    model.dH5_rule = Constraint(rule = dH5_rule)

    
    def HotU_rule(model,hi):
        return model.dH[hi] + model.HotU >= 0

    def ColdU_calc(model):
        return model.ColdU == model.dH[5] + model.HotU
    
    model.HotU_rule = Constraint(model.hi, rule = HotU_rule)
    model.ColdU_calc = Constraint(rule = ColdU_calc)

    
    def HotUCost_rule(model):
        return model.HotUCost == model.HotU * (1/3600) * model.H * (1/1000) * model.HotUPrice
    
    def ColdUCost_rule(model):
        return model.ColdUCost == model.ColdU * (1/3600) * model.H * (1/1000) * model.ColdUPrice
    
    model.HotUCost_rule = Constraint(rule = HotUCost_rule)
    model.ColdUCost_rule = Constraint(rule = ColdUCost_rule)
    
    
    
    
    
    
    

    #Objective function
    def objective_rule(model):
        """Objective is to minimize cost (AIC)"""
        return (model.MTAC + model.GlycMTAC + model.HotUCost + model.ColdUCost + model.F0Cost) - model.BDP - model.GlycCost  
    
    
    #Minimize the AIC
    model.objective = Objective(rule = objective_rule, sense = minimize)
    
    
    
    
    
    
    #Result processing and calling the solver
    def pyomo_postprocess(options=None, instance=None, results=None):
      model.flow_intot.display()
      model.AIC.display()
      model.TUC.display()
      model.RMC.display()
      model.OMC.display()
      model.BDP.display()
      model.MTAC.display()
      model.GlycCost.display()
      model.GlycMTAC.display()
      model.WashingOC.display()
      model.dH.display()	
      model.CPtot.display()
      model.HotU.display()
      model.ColdU.display()
      model.HX.display()
      model.F0Cost.display()
      model.NeutPrice.display()
      model.HotUCost.display()
      model.ColdUCost.display()
      model.MembraneReactorCost.display()
      
    # This emulates what the pyomo command-line tools does
    from pyomo.opt import SolverFactory
    import pyomo.environ
    opt = SolverFactory("gurobi",solver_io="python")
    opt.options['NonConvex'] = 2   
    results = opt.solve(model)
    #sends results to stdout
    results.write()
    print("\nDisplaying Solution\n" + '-'*60)
    pyomo_postprocess(None, model, results)
    
    return model













