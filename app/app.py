import os
import requests

import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
#import matplotlib.pyplot as plt

from calcPoints import *

def main():
    local = False
    nTeams = 14

    fbb = query_data(local)
    
    st.title("Fantasy Baseball Points Projections")
    st.write("""This app uses ZiPS projections and a bespoke fit blown saves model to project player points based on
              your league's scoring settings.""")
    
    # Custom styling to change the width of number input
    st.markdown("""
        <style>
            div[data-testid="stNumberInput"] input {
                width: 100px !important;
            }
        </style>
    """, unsafe_allow_html=True)
    st.write("Input Batter Values.")
    # Creating 8 number input fields in a single row
    bcols = st.columns(10)
    batter_labels = ["1B", "2B", "3B", "HR", "R", "RBI", "K", "SB", "CS", "HBP"]
    batter_defaults = [1,2,3,4,1,2,5,1,-1,.5]
    batter_values = [bcols[i].number_input(f"{batter_labels[i]}:", min_value=-5.0, max_value=10.0,
                     value=float(batter_defaults[i]), step=0.5, format="%.1f") for i in range(10)]

    st.write("Input Pitcher Values.")
    # Creating 8 number input fields in a single row
    pcols = st.columns(10)
    pitcher_labels = ["W", "IP", "HLD", "SV", "K", "ER", "BS"]
    pitcher_defaults = [8,1,2,4,1,-1,-2]
    pitcher_values = [pcols[i].number_input(f"{pitcher_labels[i]}:", min_value=-5.0, max_value=10.0,
                      value=float(pitcher_defaults[i]), step=0.5, format="%.1f") for i in range(7)]

    if st.button("Submit"):
        values_array = np.array(batter_values + pitcher_values)
        calculate_points(values_array, nTeams, local)
        st.write("### Captured Values Table:")
        st.dataframe(df)

if __name__ == "__main__":
    main()