import os
import sys

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.express as px

batters_list = ['C','1B','2B','3B','SS','OF']
pitchers_list = ['SP','RP']

def points_by_round(df, nTeams):
    rounds = 27
    outByRound = df.groupby('Projected Round',as_index=False)['Points'].mean()
    pltData = outByRound[outByRound['Projected Round'] <= rounds]

    fig = px.bar(pltData, x = 'Projected Round', y = 'Points', 
            hover_data = ['Points'], title = f'Average Points per Round for {rounds} Rounds')
    fig.update_traces(marker_color='rgb(33, 148, 89)')

    return fig

def render_distplot(df):
    bat = df[~(df['POS'].str.contains('RP') | df['POS'].str.contains('SP'))]['Points'].to_list()
    pit = df[(df['POS'].str.contains('RP') | df['POS'].str.contains('SP'))]['Points'].to_list()
    colors = ['rgb(33, 148, 89)', 'rgb(36, 137, 204)']
    fig = ff.create_distplot([bat,pit], group_labels=["Batters", "Pitchers"], colors=colors,
                            show_rug=False, show_hist=False)
    fig.update_layout(title_text='Distribution of Points by Pitchers vs Batters',
                      xaxis_title = 'Points',
                      yaxis_title = 'Density of Players')
    return fig
