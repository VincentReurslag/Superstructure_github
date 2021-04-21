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



#xlsx_file is the input file with the data, output_file will be the result file
xlsx_file = 'SS_dataV7.xlsx'
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
#Superstructure.get_results(model)

#excel_write(Superstructure,output_file)

