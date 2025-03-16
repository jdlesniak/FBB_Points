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


def get_indiv_plot_trace(df, pos, value, nTeams, ymin, ymax, bigFig):

    ymax = round(np.max(df['Points']) + 50,-1)
    ymin = 0
    p = df[df['POS'].str.contains(pos)].sort_values(by='Points', ascending = False)['Points']
    name = df[df['POS'].str.contains(pos)].sort_values(by='Points', ascending = False)['Name']
    order = np.array(range(len(p))) + 1


    fig = px.line(pd.DataFrame(dict(Points = p,Name = name,Rank = order)),    
                x =  'Rank',y = 'Points', hover_data=['Points'], hover_name = 'Name')
    fig.update_layout(title_text=f'Ordered Points for {pos}',
                        xaxis_title = 'Order',
                        yaxis_title = 'Points',
                        xaxis_range = [1,round(nTeams*value*2.5)],
                        yaxis_range = [ymin,ymax])
    fig.update_traces(line=dict(color='rgb(33, 148, 89)'))
    fig.add_vline(x=round(value*nTeams), line_width=2, line_dash="dash", line_color="black", annotation_text = 'Lowest Starter')
    fig.add_vline(x=round((value*nTeams)/2), line_width=2, line_dash="dash", line_color="blue", annotation_text= 'Midpoint Starter')
    
    ## add trace to bigFig
    bigFig.add_trace(go.Scatter( x = order,y = p, mode = 'lines', name = pos, hovertext=name))

    return fig, bigFig


def build_POS_plots(df, league_info):
    ## intialize empty figures
    pitchers = go.Figure()
    pit_x_max = 0

    batters = go.Figure()
    bat_x_max = 0
    ## initialize empty dict for DFs
    output = dict()

    ## define some useful params
    ymax = round(np.max(df['Points']) + 50,-1)
    ymin = 0
    nTeams = league_info['nTeams']

    for key, value in league_info.items():
    ## pitcher plot
        if key in ["SP", "RP"]:
            output[key], pitchers = get_indiv_plot_trace(df, key, value, nTeams, ymin, ymax, pitchers)
            pit_x_max = max(pit_x_max, value)
            
        ## batter plot
        elif key != 'nTeams':
            output[key], batters = get_indiv_plot_trace(df, key, value, nTeams, ymin, ymax, batters)
            bat_x_max = max(bat_x_max, value)
        
        ## not plot data
        else:
            nTeams
    
    
    ## update pitcher plot
    pitchers.update_layout(title = "Points by Pitcher Position",
                            yaxis_title = 'Points',
                            xaxis_title = 'Order',
                            xaxis_range = [1, round(pit_x_max*nTeams*1.2)],
                            yaxis_range = [ymin, ymax]
                            )
    
    ## update pitcher plot
    batters.update_layout(title = "Points by Batter Position",
                            yaxis_title = 'Points',
                            xaxis_title = 'Order',
                            xaxis_range = [1, round(bat_x_max*nTeams*1.2)],
                            yaxis_range = [ymin, ymax]
                            )

    output['pitchers'] = pitchers
    output['batters'] = batters
    return output