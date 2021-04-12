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
                self.Refcost_data = df
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
        Flow_data = {(j, k, i): value(flow) for (j, k, i), flow in model.flow.items()}
        Flow_data = pd.DataFrame.from_dict(Flow_data, orient="index", columns=["variable value"])
        Flow_data = Flow_data.values.reshape(len(self.j)*len(self.k),len(self.i)).transpose()
        Flow_data = pd.DataFrame(Flow_data)
        Flow_data.index = self.i
        Flow_data.index.name = 'i'
        columns = pd.MultiIndex.from_product([self.j,self.k])
        Flow_data.columns = columns
        Flow_data.columns.names = ['j','k']
        
        
        Logic_data = {(j,k) : value(y) for (j, k), y in model.y.items()}
        Logic_data = pd.DataFrame.from_dict(Logic_data, orient="index", columns=["variable value"])
        Logic_data = Logic_data.values.reshape(len(self.j),len(self.k)).transpose()
        Logic_data = pd.DataFrame(Logic_data)
        Logic_data.index = self.k
        Logic_data.index.name = 'k'
        Logic_data.columns = self.j
        Logic_data.columns.name = 'j'
        
        self.Flow_data = Flow_data
        self.Logic_data = Logic_data
        self.TEC = model.TEC.value
    
        
        
        


