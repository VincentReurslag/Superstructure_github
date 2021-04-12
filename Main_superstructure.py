# -*- coding: utf-8 -*-
"""
Created on Sat Apr  3 15:21:03 2021

@author: Vincent Reurslag

Run this script to execute te entire program

"""


import pandas as pd
from Superstructure_class import Superstructure
from Superstructure_model import Superstructure_model
from Excel_write import excel_write



#xlsx_file is the input file with the data, output_file will be the result file
xlsx_file = 'SS_dataV5.xlsx'
output_file = 'ResultsV2.xlsx'

a = [1,2,3,4,5]
j = [1,2,3,4]
k = [1,2,3]


Superstructure = Superstructure(xlsx_file,a,j,k)
Superstructure.get_SF(xlsx_file)
Superstructure.get_EC(xlsx_file)
Superstructure.get_F0(xlsx_file)

##############################################################
model = Superstructure_model(Superstructure)
#Superstructure.get_results(model)

#excel_write(Superstructure,output_file)



