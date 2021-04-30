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


model.TIN_i = Param(model.i, initialize = {1:443,2:423} )
model.TIN_j = Param(model.j, initialize = {1:293,2:353} )

model.TOUT_i = Param(model.i, initialize = {1:333,2:303} )
model.TOUT_j = Param(model.j, initialize = {1:408,2:413} )

model.F_i = Param(model.i, initialize = {1:30,2:15} )
model.F_j = Param(model.j, initialize = {1:20,2:40} )


model.U = Param(initialize = 1)
model.CCU = Param(initialize = 20)
model.CHU = Param(initialize = 80)
model.CF = Param(initialize = 1000)
model.C = Param(initialize = 1000)
model.B = Param(initialize = 0.6)
model.OMEGA = Param(initialize = 5000 )
model.TAU = Param(initialize = 300)


model.dT = Var(model.i,model.j,model.k,initialize = 0)
model.dTcu = Var(model.i,initialize = 0)
model.dThu = Var(model.j,initialize = 0)
model.Q = Var(model.i,model.j,model.k,initialize = 0)
model.Qcu = Var(model.i,initialize = 0)
model.Qhu = Var(model.j,initialize = 0)

model.Ti = Var(model.i, model.k, initialize = 0)
model.Tj = Var(model.j, model.k, initialize = 0)

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
        return (model.Ti[i,k] - model.TOUT_i[i]) * model.F_i[i] == sum(model.Q[i,j,k] for j in model.j)
    
def StageCold_rule(model,j,k):
    for k in [1,2]:
        return (model.Tj[j,k] - model.Tj[j,k+1]) * model.F_j[j] == sum(model.Q[i,j,k] for i in model.i)
    else:
        return (model.Tj[j,k] - model.TIN_j[j]) * model.F_j[j] == sum(model.Q[i,j,k] for i in model.j)

model.StageHot_rule = Constraint(model.i,model.k,rule = StageHot_rule)
model.StageCold_rule = Constraint(model.j,model.k,rule = StageCold_rule)

