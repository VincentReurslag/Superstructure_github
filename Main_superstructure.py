# -*- coding: utf-8 -*-
"""
Created on Sat Apr  3 15:21:03 2021

@author: Vincent Reurslag

"""
import pandas as pd
from Superstructure_class import Superstructure
from Superstructure_model import Superstructure_model

xlsx_file = 'SS_dataV2.xlsx'
output_file = 'ResultsV2.xlsx'


Superstructure = Superstructure(xlsx_file)
Superstructure.get_SF(xlsx_file)
Superstructure.get_EC(xlsx_file)
Superstructure.get_F0(xlsx_file)

##############################################################
model = Superstructure_model(Superstructure)
Superstructure.get_results(model)

##############################################################
from openpyxl import Workbook
import numpy as np
from openpyxl.utils import get_column_letter
from openpyxl.styles import PatternFill



filename = output_file

workbook = Workbook()
sheet = workbook.active

#Make numpy arrays for even spacing in excel sheet to write equipment data
start_col = 5
step_col = 3
col = np.arange(start_col, len(Superstructure.j)*step_col+start_col, step_col)
start_row = 5
step_row = 5
row = np.arange(start_row, len(Superstructure.k)*step_row+start_row, step_row)

#Write results to Excel
for j in range(len(Superstructure.j)):
    for k in range(len(Superstructure.k)):
        selected = Superstructure.Logic_data.iloc[k].iloc[j]
        equipment = Superstructure.equipment_names.iloc[k].iloc[j]
        
        row_cell = row[k]
        col_cell = get_column_letter(col[j])
        cell = col_cell + str(row_cell)
        
        sheet[cell] = equipment
        if selected == 1:
            sheet[cell].fill = PatternFill(start_color="ffff00", end_color="ffff00", fill_type = "solid")
        


workbook.save(filename = filename)







