import os
import sys

sys.path.append('/Users/John/Documents/allProjects/genericfunctions')

import pandas as pd
import numpy as np
import xlsxwriter
from FBB_points import *
import warnings
warnings.filterwarnings("ignore") 

def query_data(local):

    ## get params to access data
    if local:
        fbb = pd.read_csv('/Users/John/Documents/allProjects/data_hidden/FBB_Points/clean/allClean.csv')
    else:
        API = st.secrets["GS_API_KEY"]
        FBB_SHEET_ID = st.secrets["FBB_SHEET_ID"]
        FBB_RANGE = st.secrets["FBB_RANGE"]

        # API Endpoint
        URL = f"https://sheets.googleapis.com/v4/spreadsheets/{FBB_SHEET_ID}/values/{FBB_RANGE}?key={API}"

        # Fetch Data
        response = requests.get(URL)
        print(response)
        data = response.json()
        # Convert to Pandas DataFrame
        if "values" in data:
            values = data["values"]
            # First row as column names
            fbb = pd.DataFrame(values[1:], columns=values[0])

    return fbb  

def calculate_points(values_array, nTeams, local):
    ## get the data
    fbb = query_data(local)
    ## hold out key columns for a return df
    output = fbb[['Name','Team','POS','ADP']]

    ## grab the values as a matrix and multiply to get point values
    projMat = fbb.drop(['Name','Team','POS','PlayerId', 'ADP'], axis = 1).to_numpy(dtype=float)
    points = np.matmul(projMat, values_array.reshape(len(values_array),1))
    output['Points'] = points

    ## sort and reset the index
    output.sort_values(by = 'Points', ascending = False, inplace = True)
    output.reset_index(drop = True, inplace = True)

    ## add in rank and round
    output['Rank'] = output.index + 1
    output['Projected Round'] = np.ceil(output['Rank']/nTeams)
    output['ADP'] = round(output['ADP'],1)


    return output[['Name', 'Team', 'POS', 'Points', 'Rank','Projected Round', 'ADP']]

pitcher_labels = ["W", "IP", "HLD", "SV", "K", "ER", "BS"]
pitcher_defaults = [8,1,2,4,1,-1,-2]
batter_labels = ["1B", "2B", "3B", "HR", "R", "RBI", "BB", "SB", "CS", "HBP"]
batter_defaults = [1,2,3,4,1,2,.5,1,-1,.5]
values_array = np.array(batter_defaults + pitcher_defaults)

allClean = readPickle(vars['data_clean'], 'allClean.pkl')

scored = calculate_points(values_array, 14, True)

def produce_scored_sheet(allClean):
    fileName = vars['data_clean'] + '/ProjectionsFinal2026.xlsx'
    with pd.ExcelWriter(fileName, engine='xlsxwriter') as writer:
        allClean.to_excel(writer, sheet_name = "All")
        for pos in ['C','1B','2B', '3B', 'SS', 'OF', 'SP', 'RP']:
            allClean[allClean['POS'].str.contains(pos)].to_excel(writer, sheet_name = pos)

produce_scored_sheet(scored)