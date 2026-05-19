
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import time

from rfs_and_tps import construct_life_table
from life_table import lifetable
from plots import plot_ltrisk
from errorcheck import errorcheck

start = time.perf_counter()

sex = 1
age = 20
ldl = 2
sbp = 110
lpa = None
dia = None
sma = 18
smo = None
cig = None
smoke = "Yes"
ldl_lp=None
ldl_la=None
ldl_t=None
sbp_l=None
sbp_t=None
qs=None

if smoke == "Yes":
    scenarios = [
        {'ldl_lp': None, 'ldl_la': None, 'ldl_t': None, 'sbp_l': None, 'sbp_t': None, 'qs': None, 'sce': 'No intervention'},
        {'ldl_lp': None, 'ldl_la': 0.35, 'ldl_t': None, 'sbp_l': None, 'sbp_t': None, 'qs': None, 'sce': 'Small LDL-C change'},
        {'ldl_lp': 0.456, 'ldl_la': None, 'ldl_t': None, 'sbp_l': None, 'sbp_t': None, 'qs': None, 'sce': 'Large LDL-C change'},
        {'ldl_lp': None, 'ldl_la': None, 'ldl_t': 1.8, 'sbp_l': None, 'sbp_t': None, 'qs': None, 'sce': 'Achieve LDL-C target'},
        {'ldl_lp': None, 'ldl_la': None, 'ldl_t': None, 'sbp_l': 2, 'sbp_t': None, 'qs': None, 'sce': 'Small SBP change'},
        {'ldl_lp': None, 'ldl_la': None, 'ldl_t': None, 'sbp_l': 14.8, 'sbp_t': None, 'qs': None, 'sce': 'Large SBP change'},
        {'ldl_lp': None, 'ldl_la': None, 'ldl_t': None, 'sbp_l': None, 'sbp_t': 120, 'qs': None, 'sce': 'Achieve SBP target'},
        {'ldl_lp': None, 'ldl_la': None, 'ldl_t': None, 'sbp_l': None, 'sbp_t': None, 'qs': True, 'sce': 'Quit smoking'},
        {'ldl_lp': None, 'ldl_la': 0.35, 'ldl_t': None, 'sbp_l': 2, 'sbp_t': None, 'qs': True, 'sce': 'Both small changes and quit smoking'},
        {'ldl_lp': 0.456, 'ldl_la': None, 'ldl_t': None, 'sbp_l': 14.8, 'sbp_t': None, 'qs': True, 'sce': 'Both large changes and quit smoking'},
        {'ldl_lp': None, 'ldl_la': None, 'ldl_t': 1.8, 'sbp_l': None, 'sbp_t': 120, 'qs': True, 'sce': 'Achieve both targets and quit smoking'}
    ]
else:
    scenarios = [
        {'ldl_lp': None, 'ldl_la': None, 'ldl_t': None, 'sbp_l': None, 'sbp_t': None, 'qs': None, 'sce': 'No intervention'},
        {'ldl_lp': None, 'ldl_la': 0.35, 'ldl_t': None, 'sbp_l': None, 'sbp_t': None, 'qs': None, 'sce': 'Small LDL-C change'},
        {'ldl_lp': 0.456, 'ldl_la': None, 'ldl_t': None, 'sbp_l': None, 'sbp_t': None, 'qs': None, 'sce': 'Large LDL-C change'},
        {'ldl_lp': None, 'ldl_la': None, 'ldl_t': 1.8, 'sbp_l': None, 'sbp_t': None, 'qs': None, 'sce': 'Achieve LDL-C target'},
        {'ldl_lp': None, 'ldl_la': None, 'ldl_t': None, 'sbp_l': 2, 'sbp_t': None, 'qs': None, 'sce': 'Small SBP change'},
        {'ldl_lp': None, 'ldl_la': None, 'ldl_t': None, 'sbp_l': 14.8, 'sbp_t': None, 'qs': None, 'sce': 'Large SBP change'},
        {'ldl_lp': None, 'ldl_la': None, 'ldl_t': None, 'sbp_l': None, 'sbp_t': 120, 'qs': None, 'sce': 'Achieve SBP target'},
        {'ldl_lp': None, 'ldl_la': 0.35, 'ldl_t': None, 'sbp_l': 2, 'sbp_t': None, 'qs': None, 'sce': 'Both small changes'},
        {'ldl_lp': 0.456, 'ldl_la': None, 'ldl_t': None, 'sbp_l': 14.8, 'sbp_t': None, 'qs': None, 'sce': 'Both large changes'},
        {'ldl_lp': None, 'ldl_la': None, 'ldl_t': 1.8, 'sbp_l': None, 'sbp_t': 120, 'qs': None, 'sce': 'Achieve both targets'}
    ]


all_df = []
all_CV = []
all_LE = []
all_sce = []

for s in scenarios:
    error_message = errorcheck(age_input=age, 
            ldl_input=ldl, 
            sbp_input=sbp, 
            lpa_input=sbp, 
            sma_input=sma, 
            smo_input=smo, 
            cig_input=cig,
            smoke_input=smoke,
            ldl_lowering_input_p=s['ldl_lp'],
            ldl_lowering_input_a=s['ldl_la'],
            ldl_target_input=s['ldl_t'],
            sbp_lowering_input=s['sbp_l'],
            sbp_target_input=s['sbp_t'],
            quit_smoking_input=s['qs'])
    
#    if error_message:
#        return error_message

    df = construct_life_table(sex_input=sex, 
                    age_input=age, 
                    ldl_input=ldl, 
                    sbp_input=sbp, 
                    lpa_input=lpa, 
                    dia_input=dia, 
                    sma_input=sma, 
                    smo_input=smo, 
                    cig_input=cig,
                    ldl_lowering_input_p=s['ldl_lp'],
                    ldl_lowering_input_a=s['ldl_la'],
                    ldl_target_input=s['ldl_t'],
                    sbp_lowering_input=s['sbp_l'],
                    sbp_target_input=s['sbp_t'],
                    quit_smoking_input=s['qs'])
    df, cvd, LE = lifetable(df, age_input=age)
    df['scenario'] = s['sce']
    all_df.append(df)
    all_CV.append(cvd)
    all_LE.append(LE)
    all_sce.append(s['sce'])


cvl = pd.DataFrame({
        'sce': all_sce,
        'LE': all_LE,
        'CV': all_CV
    })

BaseLE = cvl.loc[cvl['sce'] == 'No intervention', 'LE'].values[0]
BaseCV = cvl.loc[cvl['sce'] == 'No intervention', 'CV'].values[0]

cvl['LEG'] = cvl['LE']-BaseLE
cvl['ARR'] = cvl['CV']-BaseCV

cvl = cvl[['sce', 'LE', 'LEG', 'CV', 'ARR']]

cvl['LE'] = cvl['LE'].round(2)
cvl['LEG'] = cvl['LEG'].round(2)
cvl['CV'] = cvl['CV'].round(1)
cvl['ARR'] = cvl['ARR'].round(1)

cvl.loc[cvl['sce'] == 'No intervention', 'LEG'] = None
cvl.loc[cvl['sce'] == 'No intervention', 'ARR'] = None

print(cvl)

#PICKUP: See if you can get this to work on the website in results, then come back and make the figure

final_df = pd.concat(all_df)
#print(final_df)

#df, cvd, LE = lifetable(df, age_input=age)
#LE = str(round(LE,1)) + " years"
#CV = str(round(cvd,1)) + "%"
#result_list = [LE,CV]
#fig = plot_ltrisk(df, age_input=age)
#graph_json = pio.to_json(fig)

print(final_df)

final_df = final_df.sort_values(['scenario', 'age'])

final_df = final_df.sort_values(['scenario', 'age'])

final_df['cumcvd'] = final_df.groupby('scenario')['CVD'].cumsum()

final_df['cumcvd'] *= 100

final_df['Age'], final_df['Cumulative_risk_of_CVD'], final_df['Scenario'] = final_df['age'], final_df['cumcvd'], final_df['scenario']


fig = px.line(final_df,
                x="Age", 
                y="Cumulative_risk_of_CVD", 
                hover_data={'Age': ':,d',
                            'Cumulative_risk_of_CVD': ':.1f',
                            'Scenario': True},
                title="Cumulative risk of CVD",
                color='Scenario',
                color_discrete_sequence=px.colors.qualitative.Dark24
                )

fig.update_layout(
                xaxis_title="Age (years)",
                yaxis_title="Cumulative risk of CVD (%)",
                font=dict(family="sans-serif", size=18, color="black"),
                plot_bgcolor='white'
                )

maxcvd = final_df['Cumulative_risk_of_CVD'].max()+10

fig.update_xaxes(
range=[age, 100],
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

# In your Python console or script
print(final_df.info(memory_usage='deep'))



# High-speed logic
# 

end = time.perf_counter()
print(f"Elapsed: {end - start:.6f} seconds")
