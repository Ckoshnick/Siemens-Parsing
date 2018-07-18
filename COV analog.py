# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 11:39:51 2018

@author: koshnick
"""


import pandas as pd
import PI_client
import mypy


allPoints = pd.read_excel('Allpoints.xlsx', index_col=0)
trends = pd.read_excel('Parsed alltrend_04-24-18_22-48.xlsx', index_col=1)

# %%

merged = allPoints.merge(trends,right_index=True,left_index=True,how='outer')