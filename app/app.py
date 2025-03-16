import os
import requests
import sys

import streamlit as st
st.set_page_config(layout="wide")
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
#import matplotlib.pyplot as plt
sys.path.append('/Users/John/Documents/allProjects/FBB_Points/app/')

from calcPoints import *
from renderPlots import *

def main():
    local = os.path.isfile('/Users/John/Documents/allProjects/data_hidden/FBB_Points/clean/allClean.csv')
    #print(local)
    
    st.title("Fantasy Baseball Points Projections via ZiPS DC")
    st.markdown("""This app uses ZiPS DC projections to project player points based on your league's scoring settings and number of teams. 
    ZiPS does not project blown saves, therefore I tried a few ML methods to estimate blown saves based on relief pitcher attributes.
    If a value isn't relevant to your league, then set the points to zero. The app will still function""")
    st.markdown("""""")
    st.markdown("""    Happy drafting! The spring is upon us. If you have questions, my contact information is on gitHub, as is my other work.
    [My Github](https://github.com/jdlesniak)
    """, unsafe_allow_html=True)
    st.markdown(""" """)

    st.subheader("Enter League Information")
    league_info = {}
    tcols = st.columns(10)
    league_info['nTeams'] = tcols[0].number_input("Teams:", min_value = 1, max_value = 30, value=12, step = 1)
    league_info['C'] = tcols[1].number_input("C:", min_value = 1, max_value = 3, value=1, step = 1)
    league_info['1B'] = tcols[2].number_input("1B:", min_value = 1, max_value = 3, value=1, step = 1)
    league_info['2B'] = tcols[3].number_input("2B:", min_value = 1, max_value = 3, value=1, step = 1)
    league_info['3B'] = tcols[4].number_input("3B:", min_value = 1, max_value = 3, value=1, step = 1)
    league_info['SS'] = tcols[5].number_input("SS:", min_value = 1, max_value = 3, value=1, step = 1)
    league_info['OF'] = tcols[6].number_input("OF:", min_value = 1, max_value = 7, value=4, step = 1)
    league_info['SP'] = tcols[7].number_input("SP:", min_value = 1, max_value = 10, value=5, step = 1)
    league_info['RP'] = tcols[8].number_input("RP:", min_value = 1, max_value = 5, value=2, step = 1)
    
    
    st.subheader("Input Batter Values")
    # Creating 10 number input fields in a single row
    bcols = st.columns(10)
    batter_labels = ["1B", "2B", "3B", "HR", "R", "RBI", "BB", "SB", "CS", "HBP"]
    batter_defaults = [1,2,3,4,1,2,.5,1,-1,.5]
    batter_values = [bcols[i].number_input(f"{batter_labels[i]}:", min_value=-5.0, max_value=10.0,
                     value=float(batter_defaults[i]), step=0.5, format="%.1f") for i in range(10)]

    st.subheader("Input Pitcher Values")
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
        df = calculate_points(values_array, league_info['nTeams'], local)
        
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
        
        ## get the pos plots
        pos_plots = build_POS_plots(df, league_info)
        
        ## build the static rows
        static_plots_row1 = st.columns(2)
        static_plots_row2 = st.columns(2)
        
        ## set the first static row
        static1 = points_by_round(df, league_info['nTeams'])
        static2 = render_distplot(df)
        with static_plots_row1[0]:
            st.plotly_chart(static1, use_container_width=True, key='pointsPerRound')

        with static_plots_row1[1]:
            st.plotly_chart(static2, use_container_width=True, key = 'PointsByType')

        with static_plots_row2[0]:
            st.plotly_chart(pos_plots['batters'], use_container_width=True, key='allBattersPoints')

        with static_plots_row2[1]:
            st.plotly_chart(pos_plots['pitchers'], use_container_width=True, key = 'allPitchersPoints')
        

if __name__ == "__main__":
    main()
