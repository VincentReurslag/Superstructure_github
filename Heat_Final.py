# -*- coding: utf-8 -*-
"""
Created on Fri May 21 13:59:23 2021

@author: Vincent Reurslag
"""

from pyomo.environ import *

model = ConcreteModel()

model.i = Set(initialize = [1,2], doc = "hot process")
model.j = Set(initialize = [1,2], doc = 'cold process')
model.HU = Set(initialize = [1], doc = 'hot utility')
model.CU = Set(initialize = [1], doc = 'cold utility')
model.k = Set(initialize = [1,2,3], doc = 'numer of temperature points')
model.ST = Set(initialize = [1,2], doc = 'number of stages')

model.TIN_i = Param(model.i, initialize = {1:443,2:423} )
model.TIN_j = Param(model.j, initialize = {1:293,2:353} )
model.TIN_HU = Param(model.HU, initialize = {1:450} )
model.TIN_CU = Param(model.CU, initialize = {1:293} )

model.TOUT_i = Param(model.i, initialize = {1:333,2:303} )
model.TOUT_j = Param(model.j, initialize = {1:408,2:413} )
model.TOUT_HU = Param(model.HU, initialize = {1:450} )
model.TOUT_CU = Param(model.CU, initialize = {1:313} )

model.F_i = Param(model.i, initialize = {1:30,2:15} )
model.F_j = Param(model.j, initialize = {1:20,2:40} )

model.U = Param(initialize = 1)
model.CCU = Param(initialize = 20)
model.CHU = Param(initialize = 80)
model.CF = Param(initialize = 1000)
model.CF_CU = Param(initialize = 1000)
model.CF_HU = Param(initialize = 1000)
model.C = Param(initialize = 1000)
model.B = Param(initialize = 0.6)
model.OMEGA = Param(initialize = 10000 )
model.TAU = Param(initialize = 1000)



model.dT = Var(model.i,model.j,model.k,bounds = (0, None), initialize = 0.1)
model.dTcu = Var(model.i,bounds = (0, None), initialize = 0.1)
model.dThu = Var(model.j, bounds = (0, None), initialize = 0.1)
model.Q = Var(model.i,model.j,model.ST, bounds = (0, None), initialize = 0.1)
model.Qcu = Var(model.i, bounds = (0, None), initialize = 0.1)
model.Qhu = Var(model.j, bounds = (0, None), initialize = 0.1)

model.Ti = Var(model.i, model.k, bounds = (0, None), initialize = 0.1)
model.Tj = Var(model.j, model.k, bounds = (0, None), initialize = 0.1)
model.AMTD = Var(model.i, model.j, model.ST, bounds = (0, None), initialize = 0.1)
model.AMTDcu = Var(model.i, model.CU, bounds = (0, None), initialize = 0.1)
model.AMTDhu = Var(model.j, model.HU, bounds = (0, None), initialize = 0.1)

model.z = Var(model.i,model.j,model.ST,domain = Binary)
model.zcu = Var(model.i, domain = Binary)
model.zhu = Var(model.j, domain = Binary)



def OverallHot_rule(model,i):
    return (model.TIN_i[i] - model.TOUT_i[i]) * model.F_i[i] == sum(model.Q[i,j,k] for j in model.j for k in model.ST) + model.Qcu[i]


def OverallCold_rule(model,j):
    return (model.TOUT_j[j] - model.TIN_j[j] ) * model.F_j[j] == sum(model.Q[i,j,k] for i in model.i for k in model.ST) +  model.Qhu[j]

model.OverallHot_rule = Constraint(model.i, rule = OverallHot_rule)
model.OverallCold_rule = Constraint(model.j, rule = OverallCold_rule)




def StageHot_rule(model,i,ST):
    return (model.Ti[i,ST] - model.Ti[i,ST+1]) * model.F_i[i] == sum(model.Q[i,j,ST] for j in model.j)

    
def StageCold_rule(model,j,ST):
    return (model.Tj[j,ST] - model.Tj[j,ST+1]) * model.F_j[j] == sum(model.Q[i,j,ST] for i in model.i)

model.StageHot_rule = Constraint(model.i,model.ST,rule = StageHot_rule)
model.StageCold_rule = Constraint(model.j,model.ST,rule = StageCold_rule)



def InletTempi_rule(model,i):
    return model.TIN_i[i] == model.Ti[i,1]

def InletTempj_rule(model,j):
    return model.TIN_j[j] == model.Tj[j,3]

model.InletTempi_rule = Constraint(model.i,rule = InletTempi_rule)
model.InletTempj_rule = Constraint(model.j,rule = InletTempj_rule)




def Feasibility_rule1(model,i,ST):
    return model.Ti[i,ST] >= model.Ti[i,ST+1]


def Feasibility_rule2(model,j,ST):
    return model.Tj[j,ST] >= model.Tj[j,ST+1]


def Feasibility_rule3(model,i):
    return model.TOUT_i[i] <= model.Ti[i,3]

def Feasibility_rule4(model,j):
    return model.TOUT_j[j] >= model.Tj[j,1] 
   
model.Feasibility_rule1 = Constraint(model.i,model.ST,rule = Feasibility_rule1)
model.Feasibility_rule2 = Constraint(model.j,model.ST,rule = Feasibility_rule2)
model.Feasibility_rule3 = Constraint(model.i,rule = Feasibility_rule3)
model.Feasibility_rule4 = Constraint(model.j,rule = Feasibility_rule4)


def ColdUtility_rule(model,i):
    return (model.Ti[i,3] - model.TOUT_i[i]) * model.F_i[i] == model.Qcu[i]

def HotUtility_rule(model,j):
    return (model.TOUT_j[j] - model.Tj[j,1]) * model.F_j[j] == model.Qhu[j]

model.ColdUtility_rule = Constraint(model.i,rule = ColdUtility_rule)
model.HotUtility_rule = Constraint(model.j,rule = HotUtility_rule)




def Logic_rule1(model,i,j,ST):
    return model.Q[i,j,ST] - model.OMEGA * model.z[i,j,ST] <= 0
    
def Logic_rule2(model,i):
    return model.Qcu[i] - model.OMEGA * model.zcu[i] <= 0

def Logic_rule3(model,j):
    return model.Qhu[j] - model.OMEGA * model.zhu[j] <= 0

model.Logic_rule1 = Constraint(model.i,model.j,model.ST,rule = Logic_rule1)
model.Logic_rule2 = Constraint(model.i,rule = Logic_rule2)
model.Logic_rule3 = Constraint(model.j,rule = Logic_rule3)



#Maybe one constraint?
def ApproachT_rule1(model,i,j,ST):
    return model.dT[i,j,ST] <= model.Ti[i,ST] - model.Tj[j,ST] + model.TAU * (1 - model.z[i,j,ST])

    
def ApproachT_rule2(model,i,j,ST):
    return model.dT[i,j,ST+1] <= model.Ti[i,ST+1] - model.Tj[j,ST+1] + model.TAU * (1 - model.z[i,j,ST])


def ApproachT_rule3(model,i,CU):
    return model.dTcu[i] <= model.Ti[i,3] - model.TOUT_CU[CU] + model.TAU * (1 - model.zcu[i])

def ApproachT_rule4(model,j,HU):
    return model.dThu[j] <= model.TOUT_HU[HU] - model.Tj[j,1] + model.TAU * (1 - model.zhu[j])


#model.ApproachT_rule1 = Constraint(model.i,model.j,model.ST,rule = ApproachT_rule1)
#model.ApproachT_rule2 = Constraint(model.i,model.j,model.ST,rule = ApproachT_rule2)
#model.ApproachT_rule3 = Constraint(model.i,model.CU,rule = ApproachT_rule3)
#model.ApproachT_rule4 = Constraint(model.i,model.HU,rule = ApproachT_rule4)



def dTbound_rule(model,i,j,k):
    return model.dT[i,j,k] >= 0.1

#model.dTbound_rule = Constraint(model.i,model.j,model.k,rule = dTbound_rule)



def AMTD_rule(model,i,j,ST):
    return model.AMTD[i,j,ST] == (model.Ti[i,ST] + model.Ti[i,ST+1]) / 2 - (model.Tj[j,ST] + model.Tj[j,ST+1]) / 2

    
def AMTDcu_rule(model,i,CU):
    return model.AMTDcu[i,CU] == (model.Ti[i,3] + model.TOUT_i[i]) / 2 - (model.TIN_CU[CU] + model.TOUT_CU[CU]) / 2

def AMTDhu_rule(model,j,HU):
    return model.AMTDhu[j,HU] == (model.Tj[j,1] + model.TOUT_j[j]) / 2 - (model.TIN_HU[HU] + model.TOUT_HU[HU]) / 2
    
    
model.AMTD_rule = Constraint(model.i, model.j, model.ST, rule = AMTD_rule)
model.AMTDcu_rule = Constraint(model.i, model.CU, rule = AMTDcu_rule)
model.AMTDhu_rule = Constraint(model.j, model.HU, rule = AMTDhu_rule)




def Objective_rule(model):
    return sum(model.CCU * model.Qcu[i] for i in model.i) + sum(model.CHU * model.Qhu[j] for j in model.j) \
           + sum(model.CF * model.z[i,j,k] for i in model.i for j in model.j for k in [1,2]) + sum(model.CF_CU * model.zcu[i] for i in model.i) \
           + sum(model.CF_HU * model.zhu[j] for j in model.j) \
           + sum(model.C * (model.Q[i,j,k] / (model.U * ( (model.dT[i,j,k]) * (model.dT[i,j,k+1]) * (model.dT[i,j,k] + model.dT[i,j,k+1]) / 2) ** 0.33) ) \
           for i in model.i for j in model.j for k in [1,2] ) ** model.B \
           + sum(model.C (model.Qcu[i] / (model.U * (model.dTcu[i] * (model.TOUT_i[i] - model.TIN_CU[CU]) 
           * (model.dTcu[i] + (model.TOUT_i[i] - model.TIN_CU[CU]) ) / 2) ** 0.33) ) for i in model.i for CU in model.CU) ** model.B \
           + sum(model.C * (model.Qhu[j] / (model.U * (model.dThu[j] * (model.TIN_HU[HU] - model.TOUT_j[j]) 
           * (model.dThu[j] + (model.TIN_HU[HU] - model.TOUT_j[j]) ) / 2 ) ** 0.33 ) ) for j in model.j for HU in model.HU) ** model.B 
           
def Objective_rule1(model):

    return sum(model.CCU * model.Qcu[i] for i in model.i) + sum(model.CHU * model.Qhu[j] for j in model.j) \
           + sum(model.CF * model.z[i,j,k] for i in model.i for j in model.j for k in [1,2]) + sum(model.CF_CU * model.zcu[i] for i in model.i)  \
           + sum(model.CF_HU * model.zhu[j] for j in model.j)  
           
model.Objective = Objective(rule = Objective_rule1, sense = minimize)


def pyomo_postprocess(options=None, instance=None, results=None):
    model.Q.display()
    model.Ti.display()
    model.Tj.display()
    model.Qcu.display()
    model.Qhu.display()
    model.AMTD.display()
    model.AMTDcu.display()
    model.AMTDhu.display()



from pyomo.opt import SolverFactory
import pyomo.environ
opt = SolverFactory("gurobi",solver_io="python")
opt.options['NonConvex'] = 2   
results = opt.solve(model)
#sends results to stdout
results.write()
print("\nDisplaying Solution\n" + '-'*60)
pyomo_postprocess(None, model, results)




