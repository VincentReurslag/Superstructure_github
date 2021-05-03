# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 15:42:15 2021

@author: Vincent Reurslag
"""

from pyomo.environ import *

model = ConcreteModel()

model.i = Set(initialize = [1,2], doc = "hot process")
model.j = Set(initialize = [1,2], doc = 'cold process')
model.HU = Set(initialize = [1], doc = 'hot utility')
model.CU = Set(initialize = [1], doc = 'cold utility')
model.k = Set(initialize = [1,2,3], doc = 'stages')


model.TIN_i = Param(model.i, initialize = {1:100,2:100} )
model.TIN_j = Param(model.j, initialize = {1:20,2:20} )
model.TIN_HU = Param(model.HU, initialize = {1:177} )
model.TIN_CU = Param(model.CU, initialize = {1:20} )

model.TOUT_i = Param(model.i, initialize = {1:20,2:30} )
model.TOUT_j = Param(model.j, initialize = {1:200,2:60} )
model.TOUT_HU = Param(model.HU, initialize = {1:177} )
model.TOUT_CU = Param(model.CU, initialize = {1:25} )

model.F_i = Param(model.i, initialize = {1:30,2:20} )
model.F_j = Param(model.j, initialize = {1:25,2:15} )


model.U = Param(initialize = 1)
model.CCU = Param(initialize = 20)
model.CHU = Param(initialize = 80)
model.CF = Param(initialize = 1000)
model.CF_CU = Param(initialize = 1000)
model.CF_HU = Param(initialize = 1000)
model.C = Param(initialize = 1000)
model.B = Param(initialize = 0.6)
model.OMEGA = Param(initialize = 10000 )
model.TAU = Param(initialize = 300)


model.dT = Var(model.i,model.j,model.k,initialize = 0)
model.dTcu = Var(model.i,initialize = 0)
model.dThu = Var(model.j,initialize = 0)
model.Q = Var(model.i,model.j,model.k,initialize = 0)
model.Qcu = Var(model.i,initialize = 0)
model.Qhu = Var(model.j,initialize = 0)

model.Ti = Var(model.i, model.k, initialize = 0)
model.Tj = Var(model.j, model.k, initialize = 0)
model.AMTD = Var(model.i, model.j, model.k, initialize = 0)
model.AMTDcu = Var(model.i, model.CU, initialize = 0)
model.AMTDhu = Var(model.j, model.HU, initialize = 0)

model.z = Var(model.i,model.j,model.k,domain = Binary)
model.zcu = Var(model.i, domain = Binary)
model.zhu = Var(model.j, domain = Binary)





def OverallHot_rule(model,i):
    return (model.TIN_i[i] - model.TOUT_i[i]) * model.F_i[i] == sum(model.Q[i,j,k] + model.Qcu[i] for j in model.j for k in model.k)


def OverallCold_rule(model,j):
    return (model.TOUT_j[j] - model.TIN_j[j] ) * model.F_j[j] == sum(model.Q[i,j,k] + model.Qhu[j] for i in model.i for k in model.k)

model.OverallHot_rule = Constraint(model.i, rule = OverallHot_rule)
model.OverallCold_rule = Constraint(model.j, rule = OverallCold_rule)





def StageHot_rule(model,i,k):
    for k in [1,2]:
        return (model.Ti[i,k] - model.Ti[i,k+1]) * model.F_i[i] == sum(model.Q[i,j,k] for j in model.j)
    else:
        return Constraint.Skip
    
def StageCold_rule(model,j,k):
    for k in [1,2]:
        return (model.Tj[j,k] - model.Tj[j,k+1]) * model.F_j[j] == sum(model.Q[i,j,k] for i in model.i)
    else:
        return Constraint.Skip

model.StageHot_rule = Constraint(model.i,model.k,rule = StageHot_rule)
model.StageCold_rule = Constraint(model.j,model.k,rule = StageCold_rule)





def InletTempi_rule(model,i):
    return model.TIN_i[i] == model.Ti[i,1]

def InletTempj_rule(model,j):
    return model.TIN_j[j] == model.Tj[j,3]

model.InletTempi_rule = Constraint(model.i,rule = InletTempi_rule)
model.InletTempj_rule = Constraint(model.j,rule = InletTempj_rule)



def Feasibility_rule1(model,i,k):
    for k in [1,2]:
        return model.Ti[i,k] >= model.Ti[i,k+1]
    else:
        return Constraint.Skip

def Feasibility_rule2(model,j,k):
    for k in [1,2]:
        return model.Tj[j,k] >= model.Tj[j,k+1]
    else:
        return Constraint.Skip

def Feasibility_rule3(model,i):
    return model.TOUT_i[i] <= model.Ti[i,3]

def Feasibility_rule4(model,j):
    return model.TOUT_j[j] >= model.Tj[j,1] 
   
model.Feasibility_rule1 = Constraint(model.i,model.k,rule = Feasibility_rule1)
model.Feasibility_rule2 = Constraint(model.j,model.k,rule = Feasibility_rule2)
model.Feasibility_rule3 = Constraint(model.i,rule = Feasibility_rule3)
model.Feasibility_rule4 = Constraint(model.j,rule = Feasibility_rule4)



def ColdUtility_rule(model,i):
    return (model.Ti[i,3] - model.TOUT_i[i]) * model.F_i[i] == model.Qcu[i]

def HotUtility_rule(model,j):
    return (model.TOUT_j[j] - model.Tj[j,1]) * model.F_j[j] == model.Qhu[j]

model.ColdUtility_rule = Constraint(model.i,rule = ColdUtility_rule)
model.HotUtility_rule = Constraint(model.j,rule = HotUtility_rule)




def Logic_rule1(model,i,j,k):
    for k in [1,2]:
        return model.Q[i,j,k] - model.OMEGA * model.z[i,j,k] <= 0
    else:
        return Constraint.Skip
    
def Logic_rule2(model,i):
    return model.Qcu[i] - model.OMEGA * model.zcu[i] <= 0

def Logic_rule3(model,j):
    return model.Qhu[j] - model.OMEGA * model.zhu[j] <= 0

model.Logic_rule1 = Constraint(model.i,model.j,model.k,rule = Logic_rule1)
model.Logic_rule2 = Constraint(model.i,rule = Logic_rule2)
model.Logic_rule3 = Constraint(model.j,rule = Logic_rule3)



    
def ApproachT_rule1(model,i,j,k):
    for k in [1,2]:
        return model.dT[i,j,k] <= model.Ti[i,k] - model.Tj[j,k] + model.TAU * (1 - model.z[i,j,k])
    else:
        return Constraint.Skip
    
def ApproachT_rule2(model,i,j,k):
    for k in [1,2]:
        return model.dT[i,j,k+1] <= model.Ti[i,k+1] - model.Tj[j,k+1] + model.TAU * (1 - model.z[i,j,k])
    else:
        return Constraint.Skip

def ApproachT_rule3(model,i,CU):
    return model.dTcu[i] <= model.Ti[i,3] - model.TOUT_CU[CU] + model.TAU * (1 - model.zcu[i])

def ApproachT_rule4(model,j,HU):
    return model.dThu[j] <= model.TOUT_HU[HU] - model.Tj[j,1] + model.TAU * (1 - model.zhu[j])


model.ApproachT_rule1 = Constraint(model.i,model.j,model.k,rule = ApproachT_rule1)
model.ApproachT_rule2 = Constraint(model.i,model.j,model.k,rule = ApproachT_rule2)
model.ApproachT_rule3 = Constraint(model.i,model.CU,rule = ApproachT_rule3)
model.ApproachT_rule4 = Constraint(model.i,model.HU,rule = ApproachT_rule4)


def dTbound_rule(model,i,j,k):
    return model.dT[i,j,k] >= 0.1

model.dTbound_rule = Constraint(model.i,model.j,model.k,rule = dTbound_rule)



       
        

def AMTD_rule(model,i,j,k):
    for k in [1,2]:
        return model.AMTD[i,j,k] == (model.Ti[i,k] + model.Ti[i,k+1]) / 2 - (model.Tj[j,k] + model.Tj[j,k+1]) / 2
    else:
        return Constraint.Skip
    
def AMTDcu_rule(model,i,CU):
    return model.AMTDcu[i,CU] == (model.Ti[i,3] + model.TOUT_i[i]) / 2 - (model.TIN_CU[CU] + model.TOUT_CU[CU]) / 2

def AMTDhu_rule(model,j,HU):
    return model.AMTDhu[j,HU] == (model.Tj[j,1] + model.TOUT_j[j]) / 2 - (model.TIN_HU[HU] + model.TOUT_HU[HU]) / 2
    
    
model.AMTD_rule = Constraint(model.i, model.j, model.k, rule = AMTD_rule)
model.AMTDcu_rule = Constraint(model.i, model.CU, rule = AMTDcu_rule)
model.AMTDhu_rule = Constraint(model.j, model.HU, rule = AMTDhu_rule)
        
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






