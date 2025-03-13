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

    This function identifies the players in the current dataset, and the dataset containing the new
    position.
        -If any players are present in both, we append the new position to their POS column.
        -If they are present in only the new dataset, we append the record and change nothing.
        -If they are present in only the old dataset, we simply leave them alone.
        -Duplicate records are dropped.
    
    Parameters:

    Returns:

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

def blownSavesEstimates(data, estimator):
    """
    This function estimates the number of blown saves for all relievers. The
    definition of a reliever is any player with 5+ relief appears, as estimated by
    total games - games started.

    Parameters:
        data (dataframe): dataframe with all pitcher data. Already concatenated to
            include all relievers and starters, but not subset to the fantasy relevant
            fields
        estimator (sklearn estimator): estimator from a user-chosen model. Anyone can use
            any model they chose here as long as estimator.predict() returns predicted values
    Returns:
        output (dataframe): dataframe containing all input data with estimates for blown saves 
    """
    ## if BS isn't already dropped, then drop it. If it is dropped,
    ## then ignore the error
    data.drop('BS', axis = 1, inplace = True, errors = 'ignore')
    
    ## Set Index for Joins
    data.set_index('PlayerId')
    
    ## create two necessary features
    data['ERA'] = data['ER']/(data['IP']/9)
    data['ReliefApps'] = data['G'] - data['GS']
    
    ### only predict for players with 5+ estimated relief appearances
    modelData = data[data['ReliefApps'] >= 5]
    modelData = modelData[['ERA', 'SV', 'HLD', 'IP', 'HR', 'BB', 'SO', 'ReliefApps']]

    # use estimator to make predictions
    modelData['BS'] = np.round(estimator.predict(modelData))

    ## join to data, making the output dataset
    output = data.merge(modelData[['BS']], how = 'left',
                             left_index = True, right_index = True)
    
    ## fillna with 0 for the 4 or fewer relief apps
    output['BS'].fillna(0, inplace = True)

    return output

def cleanBatters(dataDir, fileName):
    """
    
    """
    battersAll = pd.DataFrame()

    ## List all batter positions
    batterTypes = ['C' ,'1B','2B','3B','SS','OF','DH']

    ### this is lovely but it needs to become a function as we repeat for pitchers
    for pos in batterTypes:
        ## load in the position-specific csv
        battersTemp = pd.read_csv(dataDir + fileName.format(pos=pos))
        
        ## set the POS to the corresponding position
        battersTemp['POS'] = pos
        ## make the PlayerID a string to prevent any strange integer operations
        battersTemp['PlayerId'] = battersTemp['PlayerId'].astype(str)
        
        ## if there are multiple rows, update the dataframe with our previous defined function
        if (battersAll.shape[0] != 0):
            battersAll = updateDataFrame(battersTemp, battersAll, pos)
        
        ## if there are zero rows, then concat the data to the df
        else:
            battersAll = pd.concat([battersAll, battersTemp])


    return battersAll[['Name', 'Team', 'POS', 'PlayerId', '1B',
                       '2B', '3B', 'HR', 'R', 'RBI', 'SO', 'SB', 'CS', 'HBP']]

def cleanPitchers(dataDir, fileName, estimator):
    pitcherTypes = ['SP' ,'RP']

    pitchersAll = cleanAddPOS(pitcherTypes, dataDir, fileName)
    pitchersClean = blownSavesEstimates(pitchersAll, estimator)
    
    return pitchersClean[['Name', 'Team', 'POS', 'PlayerId', 'W', 'IP', 'HLD', 'SV',
                          'SO', 'ER','BS']]


def main():
    ## load in the chosen estimator
    estimator = readPickle(vars['data_clean'],'bestRandomForest.pkl')
    
    ## produce the cleaned batters dataset with blown saves estimates
    pitchersClean = cleanPitchers(vars['data_raw'], vars['filename'], estimator)
    
    ## produce the cleaned batters dataset
    battersClean = cleanBatters(vars['data_raw'], vars['filename'])

    allClean = battersClean.merge(pitchersClean, how = 'outer', on = ['Name', 'Team', 'POS', 'PlayerId'], suffixes = ('_bat', '_pit'))
    allClean.fillna(0, inplace = True)

    pitchersClean.to_csv(vars['data_clean'] + 'pitchersClean.csv')
    battersClean.to_csv(vars['data_clean'] + 'battersClean.csv')
    allClean.to_csv(vars['data_clean'] + 'allClean.csv')

    writePickle(vars['data_clean'], 'pitchersClean.pkl', pitchersClean)
    writePickle(vars['data_clean'], 'battersClean.pkl', battersClean)
    writePickle(vars['data_clean'], 'allClean.pkl', allClean)

if __name__ == '__main__':
    main()