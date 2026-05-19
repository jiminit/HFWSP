import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio

def plot_ltrisk(df, age_input):
    df['cumcvd'] = 100*df['CVD'].cumsum()
    df['Age'], df['Cumulative_risk_of_CVD'] = df['age'], df['cumcvd']
    fig = px.line(df,
                    x="Age", 
                    y="Cumulative_risk_of_CVD", 
                    hover_data={'Age': ':,d','Cumulative_risk_of_CVD': ':.1f'},
                    )

    fig.update_layout(
                    xaxis_title="Age (years)",
                    yaxis_title="Cumulative risk of CVD (%)",
                    font=dict(family="sans-serif", size=18, color="black"),
                    plot_bgcolor='white'
                    )


    maxcvd = df['Cumulative_risk_of_CVD'].max()+10

    fig.update_xaxes(
    range=[age_input, 100],
    tickformat=',d',
    showgrid=False
    )

    fig.update_yaxes(
    range=[0, maxcvd],
    tickformat=',d',
    gridcolor='rgba(125, 125, 125, 0.2)',
    zeroline=True, 
    zerolinecolor='black', 
    zerolinewidth=0.5
    )

    return fig


def plot_ltrisk_i(df, age_input):
    df['nn'] = range(len(df))
    df = df.sort_values(['scenario', 'age'])
    df['cumcvd'] = df.groupby('scenario')['CVD'].cumsum()
    df['cumcvd'] *= 100
    df['Age'], df['Cumulative_risk_of_CVD'], df['Scenario'] = df['age'], df['cumcvd'], df['scenario']
    df = df.sort_values(['nn'])

    fig = px.line(df,
                    x="Age", 
                    y="Cumulative_risk_of_CVD", 
                    hover_data={'Age': ':,d',
                                'Cumulative_risk_of_CVD': ':.1f',
                                'Scenario': True},
                    color='Scenario',
                    color_discrete_sequence=px.colors.qualitative.Dark24
                    )

    fig.update_layout(
                    xaxis_title="Age (years)",
                    yaxis_title="Cumulative risk of CVD (%)",
                    font=dict(family="sans-serif", size=18, color="black"),
                    plot_bgcolor='white',
                    height=450,
                    margin=dict(t=50, b=50, l=50, r=50) 
                    )

    maxcvd = df['Cumulative_risk_of_CVD'].max()+10

    fig.update_xaxes(
    range=[age_input, 100],
    tickformat=',d',
    showgrid=False
    )

    fig.update_yaxes(
    range=[0, maxcvd],
    tickformat=',d',
    gridcolor='rgba(125, 125, 125, 0.2)',
    zeroline=True, 
    zerolinecolor='black', 
    zerolinewidth=0.5
    )

    return fig

def plot_ltrisk_u(df, age_input, title_input):
    df['nn'] = range(len(df))
    df = df.sort_values(['scenario', 'age'])
    df['cumcvd'] = df.groupby('scenario')['CVD'].cumsum()
    df['cumcvd'] *= 100
    df['Age'], df['Cumulative_risk_of_CVD'], df['Scenario'] = df['age'], df['cumcvd'], df['scenario']
    df = df.sort_values(['nn'])

    fig = px.line(df,
                    x="Age", 
                    y="Cumulative_risk_of_CVD", 
                    hover_data={'Age': ':,d',
                                'Cumulative_risk_of_CVD': ':.1f',
                                'Scenario': True},
                    color='Scenario',
                    color_discrete_sequence=px.colors.qualitative.Dark24,
                    title = f'{title_input}',
                    )

    fig.update_layout(
                    xaxis_title="Age (years)",
                    yaxis_title="Cumulative risk of CVD (%)",
                    font=dict(family="sans-serif", size=18, color="black"),
                    plot_bgcolor='white',
                    height=450,
                    margin=dict(t=50, b=50, l=50, r=50),
                    title_font=dict(size=18)
                    )

    maxcvd = df['Cumulative_risk_of_CVD'].max()+10

    fig.update_xaxes(
    range=[age_input, 100],
    tickformat=',d',
    showgrid=False
    )

    fig.update_yaxes(
    range=[0, maxcvd],
    tickformat=',d',
    gridcolor='rgba(125, 125, 125, 0.2)',
    zeroline=True, 
    zerolinecolor='black', 
    zerolinewidth=0.5
    )

    return fig
