# -*- coding: utf-8 -*-
"""
Created on Sat Apr  3 14:55:46 2021

@author: Vincent Reurslag
"""
import pandas as pd
from pyomo.environ import *

def flatten_dict(d):
    def items():
        for key, value in d.items():
            if isinstance(value, dict):
                for subkey, subvalue in flatten_dict(value).items():
                    if type(key) == int:
                        yield (key,) + (subkey,), subvalue
                    else:
                        yield key + (subkey,), subvalue
            else:
                yield key, value

    return dict(items())

class Superstructure:
    def __init__(self, xlsx_file,a,j,k):
        """Initializes the superstructure by getting the indices j,k,i,u and corresponding names
        NOTE: Leave the excel tabs empty besides the corresponding tables"""

        df = pd.read_excel(xlsx_file,'Superstructure a,j,k')
        equipment_names = df.iloc[1:, 2:]
        
        
        equipment_names.index = k
        equipment_names.columns = pd.MultiIndex.from_product([a,j])
        equipment_names.index.name = 'k'
        equipment_names.columns.names = ['a','j']
        
        df = pd.read_excel(xlsx_file,'Components i')
        i = list(df.iloc[1:,0])
        component_names = df.iloc[1:,1]
        component_names.index = i
        component_names.index.name = 'i'
        
        df = pd.read_excel(xlsx_file,'Utilities u')
        u = list(df.iloc[1:,0])
        utilities_names = df.iloc[1:,1]
        utilities_names.index = u
        utilities_names.index.name = 'u'
        
        self.a = a
        self.j = j
        self.k = k
        self.i = i
        self.u = u
        self.equipment_names = equipment_names
        self.component_names = component_names
        self.utilities_names = utilities_names
        
    def get_4index(self,xlsx_file,sheets):
        for sheet in sheets:
            df = pd.read_excel(xlsx_file, sheet)
            df = df.iloc[2:,2:]
            columns = pd.MultiIndex.from_product([self.a,self.j,self.k])
            df.columns = columns
            df.columns.names = ['a','j','k']
            
            if sheet in sheets[0:2]: 
                df.index = self.i
                df.index.name = 'i'
            elif sheet in sheets[2:]:
                df.index = self.u
                df.index.name = 'u'
            
            df = df.to_dict()
            df = flatten_dict(df)
            
            if sheet == 'SF a,j,k,i':
                self.SF_data = df
            elif sheet == 'Q a,j,k,i':
                self.Q_data = df
            elif sheet == 'Tau a,j,k,u':
                self.Tau_data = df
    
    
    def get_3index(self,xlsx_file,sheets):
        for sheet in sheets:
            df = pd.read_excel(xlsx_file, sheet)
            df = df.iloc[1:,2:]
            df.columns = pd.MultiIndex.from_product([self.a,self.j])
            df.index = self.k
            df.columns.names = ['a','j']
            df.index.name = 'k'
            df = df.to_dict()
            df = flatten_dict(df)
            
            if sheet == 'EC a,j,k':
                self.EC_data = df
            elif sheet == 'Temperature a,j,k':
                self.Temp_data = df
            elif sheet == 'ReferenceCost a,j,k':
                self.RefCost_data = df
            elif sheet == 'ReferenceSize a,j,k':
                self.RefSize_data = df
            elif sheet == 'ReferenceIndex a,j,k':
                self.RefIndex_data = df
            elif sheet == 'SizingFactor a,j,k':
                self.Sizing_data = df
        
    def get_1index(self,xlsx_file,sheets):
        for sheet in sheets:
            df = pd.read_excel(xlsx_file, sheet)
            df = df.iloc[1:,2]
            if sheet in sheets[0:3]:
                df.index = self.i
                df.index.name = 'i'
            elif sheet in sheets[3:]:
                df.index = self.u
                df.index.name = 'u'
    
            df = df.to_dict()
            if sheet == 'Flow0 i':
                self.F0_data = df
            elif sheet == 'CP i':
                self.CP_data = df
            elif sheet == 'CompCost i':
                self.CCost_data = df
            elif sheet == 'SpecificCostU u':
                self.uCost_data = df
    
        
    def get_results(self,model):
        """Get results from the pyomo model (Logic and flow data)"""
        from pyomo.core import ConcreteModel, Set, NonNegativeReals, Var, value
        Flow_in = {(a, j, k, i): value(flow) for (a, j, k, i), flow in model.flow_in.items()}
        Flow_in = pd.DataFrame.from_dict(Flow_in, orient="index", columns=["variable value"])
        Flow_in = Flow_in.values.reshape(len(self.a)*len(self.j)*len(self.k),len(self.i)).transpose()
        Flow_in = pd.DataFrame(Flow_in)
        Flow_in.index = self.i
        Flow_in.index.name = 'i'
        columns = pd.MultiIndex.from_product([self.a,self.j,self.k])
        Flow_in.columns = columns
        Flow_in.columns.names = ['a','j','k']
        
        
        Flow_intot = {(a, j, k): value(flow) for (a, j, k), flow in model.flow_intot.items()}
        Flow_intot = pd.DataFrame.from_dict(Flow_intot, orient="index", columns=["variable value"])
        Flow_intot = Flow_intot.values.reshape(len(self.a)*len(self.j)*len(self.k),1).transpose()
        Flow_intot = pd.DataFrame(Flow_intot)
        columns = pd.MultiIndex.from_product([self.a,self.j,self.k])
        Flow_intot.columns = columns
        Flow_intot.columns.names = ['a','j','k']
        
        
        y = {(a, j, k): value(flow) for (a, j, k), flow in model.y.items()}
        y = pd.DataFrame.from_dict(y, orient="index", columns=["variable value"])
        y = y.values.reshape(len(self.a)*len(self.j)*len(self.k),1).transpose()
        y = pd.DataFrame(y)
        columns = pd.MultiIndex.from_product([self.a,self.j,self.k])
        y.columns = columns
        y.columns.names = ['a','j','k']
        
        
        CostCorr = {(a, j, k): value(flow) for (a, j, k), flow in model.CostCorr.items()}
        CostCorr = pd.DataFrame.from_dict(CostCorr, orient="index", columns=["variable value"])
        CostCorr = CostCorr.values.reshape(len(self.a)*len(self.j)*len(self.k),1).transpose()
        CostCorr = pd.DataFrame(CostCorr)
        columns = pd.MultiIndex.from_product([self.a,self.j,self.k])
        CostCorr.columns = columns
        CostCorr.columns.names = ['a','j','k']
        
        self.Flow_in = Flow_in
        self.Flow_intot = Flow_intot
        self.y = y
        self.CostCorr = CostCorr
        self.IR_LF = value(model.IRCalc)
        self.AIC = value(model.AIC)
        self.TUC = value(model.TUC)
        self.RMC = value(model.RMC)
        self.OMC = value(model.OMC)
        self.WC = value(model.WashingOC)
        self.BDP = value(model.BDP)
        self.MTAC = value(model.MTAC)
        
        self.GlycAIC = value(model.GlycAIC)
        self.GlycTUC = value(model.GlycTUC)
        self.GlycRMC = value(model.GlycRMC)
        self.GlycOMC = value(model.GlycOMC)
        self.GlycWC = value(model.GlycWashingOC)
        self.GlycTAR = value(model.GlycCost)
        self.GlycMTAC = value(model.GlycMTAC)
        
        self.FeedCost = value(model.F0Cost)
        self.HotU = value(model.HotU)
        self.ColdU = value(model.ColdU)
        self.HotUCost = value(model.HotUCost)
        self.ColdUCost = value(model.ColdUCost)
        self.MembraneReactorCost = value(model.MembraneReactorCost)

        self.ElectricityAmount = value(model.ElectricityAmount)
        self.HeatingAmount = value(model.HeatingAmount)
        self.CoolingAmount = value(model.CoolingAmount)