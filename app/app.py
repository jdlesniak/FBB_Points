import os
import requests
import sys

import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
#import matplotlib.pyplot as plt
sys.path.append('/Users/John/Documents/allProjects/FBB_Points/app/')

from calcPoints import *

def main():
    local = False
    print(local)
    nTeams = 14
    
    st.title("Fantasy Baseball Points Projections")
    st.write("This app uses ZiPS projections to project player points based on your league's scoring settings and number of teams.")
    
    # Custom styling to change the width of number input
    st.markdown("""
        <style>
            div[data-testid="stNumberInput"] input {
                width: 100px !important;
            }
        </style>
    """, unsafe_allow_html=True)
    st.write("Enter Number of Teams")
    tcols = st.columns(10)
    nTeams = tcols[0].number_input("Number of Teams:", min_value = 1, max_value = 30, value=12, step = 1)
    st.write("Input Batter Values")
    # Creating 10 number input fields in a single row
    bcols = st.columns(10)
    batter_labels = ["1B", "2B", "3B", "HR", "R", "RBI", "BB", "SB", "CS", "HBP"]
    batter_defaults = [1,2,3,4,1,2,.5,1,-1,.5]
    batter_values = [bcols[i].number_input(f"{batter_labels[i]}:", min_value=-5.0, max_value=10.0,
                     value=float(batter_defaults[i]), step=0.5, format="%.1f") for i in range(10)]

    st.write("Input Pitcher Values")
    # Creating 8 number input fields in a single row
    pcols = st.columns(10)
    pitcher_labels = ["W", "IP", "HLD", "SV", "K", "ER", "BS"]
    pitcher_defaults = [8,1,2,4,1,-1,-2]
    pitcher_values = [pcols[i].number_input(f"{pitcher_labels[i]}:", min_value=-5.0, max_value=10.0,
                      value=float(pitcher_defaults[i]), step=0.5, format="%.1f") for i in range(7)]

    if st.button("Submit"):
        ## append the values together
        values_array = np.array(batter_values + pitcher_values)
        
        ## calcualte the points
        df = calculate_points(values_array, nTeams, local)
        
        ## log the df in the session_state
        st.session_state.df = df
        ## write the dataframe with points to the app
        st.write("### ZiPS Powered Projections:")


    if "df" in st.session_state:
        ## set session sate for df
        df = st.session_state.df

        ## define the ALL values for select boxes
        team_options = ["All"] + sorted(df['Team'].dropna().unique().tolist())
        pos_options = ['All', 'C', '1B', '2B', '3B', 'SS', 'OF', 'SP', 'RP']
        
        
        # Define filters with session state tracking
        name_filter = st.text_input("Filter by Name:", value=st.session_state.get("name_filter", ""))
        
        teampos_cols = st.columns(2)
        team_filter = teampos_cols[0].selectbox("Filter by Team:", team_options, index=team_options.index(st.session_state.get("team_filter", "All")))
        pos_filter = teampos_cols[1].selectbox("Filter by Position:", pos_options, index=pos_options.index(st.session_state.get("pos_filter", "All")))
        
        points_col = st.columns(2)
        points_operator = points_col[0].selectbox("Points Filter Operator:", [">", "<", ">=", "<="])
        points_value = points_col[1].number_input("Points:", min_value=0, step=1, format="%d")

        adp_col = st.columns(2)
        adp_operator = adp_col[0].selectbox("ADP Filter Operator:", [">", "<"])
        adp_value = adp_col[1].number_input("ADP Value:", min_value=1, step=1, format="%d")

        # Reset Filters Button
        if st.button("Reset Filters"):
            st.session_state.name_filter = ""
            st.session_state.team_filter = "All"
            st.session_state.pos_filter = "All"
            st.session_state.adp_value = 1
            st.session_state.adp_operator = '>'
            st.session_state.points_value = 0
            st.session_state.points_operator = '>'
            st.rerun()

        # Load session state or set defaults
        if "name_filter" not in st.session_state:
            st.session_state.name_filter = ""
        if "team_filter" not in st.session_state:
            st.session_state.team_filter = "All"
        if "pos_filter" not in st.session_state:
            st.session_state.pos_filter = "All"
        if "adp_value" not in st.session_state:
            st.session_state.adp_value = 1
        if "adp_operator" not in st.session_state:
            st.session_state.adp_operator = '>'
        if "points_value" not in st.session_state:
            st.session_state.points_value = 0
        if "points_operator" not in st.session_state:
            st.session_state.points_operator = '>'

        if name_filter:
            df = df[df['Name'].str.contains(name_filter, case=False, na=False)]
        if team_filter != "All":
            df = df[df['Team'] == team_filter]
        if pos_filter != "All":
            df = df[df['POS'].str.contains(pos_filter, case = False, na = False)]
        if adp_value > 1:  # Apply ADP filter if a valid number is entered
            if adp_operator == ">":
                df = df[df["ADP"] > adp_value]
            elif adp_operator == "<":
                df = df[df["ADP"] < adp_value]
        
        if points_value > 0:  # Apply Points Filter
            if points_operator == ">":
                df = df[df["Points"] > points_value]
            elif points_operator == "<":
                df = df[df["Points"] < points_value]
            elif points_operator == ">=":
                df = df[df["Points"] >= points_value]
            elif points_operator == "<=":
                df = df[df["Points"] <= points_value]
        
        ## show dataframe
        st.dataframe(df, hide_index = True)
        

if __name__ == "__main__":
    main()
