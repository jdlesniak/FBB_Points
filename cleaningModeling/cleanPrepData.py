import os
import sys

import pandas as pd
import numpy as np

sys.path.append('/Users/John/Documents/allProjects/genericfunctions')

from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV, train_test_split
from sklearn.ensemble import RandomForestRegressor

from scipy.stats import randint

from FBB_points import *
import warnings
warnings.filterwarnings("ignore")

seedA = 73

def updateDataFrame(new, total, pos):
   """
    This function is called in cleanAddPOS.

   This function identifies the players in the current dataset, and the dataset containing the new position.
      -If any players are present in both, we append the new position to their POS column.
      -If they are present in only the new dataset, we append the record and change nothing.
      -If they are present in only the old dataset, we simply leave them alone.
      -Duplicate records are dropped.
   """
   # Identify the players in both records via inner join
   overlap = pd.merge(total,new, how = 'inner', on= ['Name','Team'], suffixes=('', '_New'))
   ids = overlap['PlayerId'].tolist()
    
   # Identify players from large DF in new dataframe - update required
   ## These are IN BOTH new and total and must be dropped from BOTH to prevent duplicates
   update = total[total['PlayerId'].isin(ids)]
    
   # Identify the players not in new dataframe - no update required
   noUpdate = total[~(total['PlayerId'].isin(ids))]
   
   # drop updated records from new dataframe
   dropRecords = new[~(new['PlayerId'].isin(ids))]
    
   # Update the POS column for additional Positions
   update['POS'] = update['POS'] + f", {pos}".format(pos = pos)
    
   # Concatenate all three dfs
   finalProduct = pd.concat([update, noUpdate, dropRecords]).reset_index(drop = True)
    
   return(finalProduct)   


def cleanAddPOS(positions, filepath, filename):
    outputAll = pd.DataFrame()

    for pos in positions:
        ## load in the position-specific csv
        posTemp = pd.read_csv(vars['data_raw'] + vars['filename'].format(pos=pos))
        
        ## set the POS to the corresponding position
        posTemp['POS'] = pos
        ## make the PlayerID a string to prevent any strange integer operations
        posTemp['PlayerId'] = posTemp['PlayerId'].astype(str)
        
        ## if there are multiple rows, update the dataframe with our previous defined function
        if (outputAll.shape[0] != 0):
            outputAll = updateDataFrame(posTemp, outputAll, pos)
        
        ## if there are zero rows, then concat the data to the df
        else:
            outputAll = pd.concat([outputAll, posTemp])
    return outputAll

