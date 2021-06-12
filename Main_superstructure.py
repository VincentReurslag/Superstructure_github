# -*- coding: utf-8 -*-
"""
Created on Sat Apr  3 15:21:03 2021
Run this script to execute te entire program

@author: Vincent Reurslag


"""

import pandas as pd
from Superstructure_class import Superstructure
from Superstructure_model import Superstructure_model
from Excel_write import excel_write
from pyomo.core import ConcreteModel, Set, NonNegativeReals, Var, value


#xlsx_file is the input file with the data, output_file will be the result file
xlsx_file = 'SS_dataV_AN.xlsx'
output_file = 'ResultsV2.xlsx'

a = [1,2,3,4,5,6,7,8]
j = [1,2,3,4]
k = [1,2,3]


Superstructure = Superstructure(xlsx_file,a,j,k)
Superstructure.get_4index(xlsx_file,['SF a,j,k,i', 'Q a,j,k,i','Tau a,j,k,u'])
Superstructure.get_3index(xlsx_file, ['EC a,j,k','Temperature a,j,k','ReferenceCost a,j,k','ReferenceSize a,j,k','ReferenceIndex a,j,k','SizingFactor a,j,k'])
Superstructure.get_1index(xlsx_file, ['Flow0 i', 'CP i', 'CompCost i', 'SpecificCostU u'])

##############################################################
model = Superstructure_model(Superstructure)

Flow_in = {(a, j, k, i): value(flow) for (a, j, k, i), flow in model.flow_in.items()}
Flow_in = pd.DataFrame.from_dict(Flow_in, orient="index", columns=["variable value"])
Flow_in = Flow_in.values.reshape(len(Superstructure.a)*len(Superstructure.j)*len(Superstructure.k),len(Superstructure.i)).transpose()
Flow_in = pd.DataFrame(Flow_in)
Flow_in.index = Superstructure.i
Flow_in.index.name = 'i'
columns = pd.MultiIndex.from_product([Superstructure.a,Superstructure.j,Superstructure.k])
Flow_in.columns = columns
Flow_in.columns.names = ['a','j','k']


Flow_intot = {(a, j, k): value(flow) for (a, j, k), flow in model.flow_intot.items()}
y = {(a, j, k): value(flow) for (a, j, k), flow in model.y.items()}
CostCorr = {(a, j, k): value(flow) for (a, j, k), flow in model.CostCorr.items()}



#Superstructure.get_results(model)

#excel_write(Superstructure,output_file)

