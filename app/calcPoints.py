import os
import sys
import requests


import pandas as pd
import numpy as np
import streamlit as st
    
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
    print(fbb.head())
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


    return output[['Name', 'Team', 'POS', 'Points', 'Rank','Projected Round', 'ADP']]