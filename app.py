##Run in bash
#sudo apt install python3-pip
#pip install flask
#pip install --upgrade --user stata_setup

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import time

from rfs_and_tps import construct_life_table
from life_table import lifetable
from plots import plot_ltrisk, plot_ltrisk_i, plot_ltrisk_u
from errorcheck import errorcheck

app = Flask(__name__)
app.secret_key = "157845453dbcgahytve" 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/baseline_results', methods=['POST'])
def baseline_results():
    session['user_data'] = request.form
    user_id = session.get('_id', 'guest')[:8] 
    age = int(request.form.get('age'))
    sex = int(request.form.get('sex'))
    ldl_raw = request.form.get('ldl', '')
    ldl = float(ldl_raw) if ldl_raw else None
    sbp_raw = request.form.get('sbp', '')
    sbp = float(sbp_raw) if sbp_raw else None
    lpa_raw = request.form.get('lpa', '')
    lpa = float(lpa_raw) if lpa_raw else None
    dia_raw = request.form.get('dia', '')
    dia = float(dia_raw) if dia_raw else None
    sma_raw = request.form.get('sma', '')
    sma = float(sma_raw) if sma_raw else None
    smo_raw = request.form.get('smo', '')
    smo = float(smo_raw) if smo_raw else None
    cig_raw = request.form.get('cig', '')
    cig = float(cig_raw) if cig_raw else None
    smoke = request.form.get('smoke_status')

    #Convert Lp(a) from nmol/L to mg/dL
    if lpa is not None:
        lpa = (lpa+3.83)/2.18

    session['cleaned_data'] = {
    'age': age,
    'sex': sex,
    'ldl': ldl,
    'sbp': sbp,
    'lpa': lpa,
    'dia': dia,
    'sma': sma,
    'smo': smo,
    'cig': cig,
    'smoke': smoke,
    'user_id': session.get('_id', 'guest')[:8]
    }

    ldl_lp=None
    ldl_la=None
    ldl_t=None
    sbp_l=None
    sbp_t=None
    qs=None

    error_message = errorcheck(age_input=age, 
               ldl_input=ldl, 
               sbp_input=sbp, 
               lpa_input=sbp, 
               sma_input=sma, 
               smo_input=smo, 
               cig_input=cig,
               ldl_lowering_input_p=ldl_lp,
               ldl_lowering_input_a=ldl_la,
               ldl_target_input=ldl_t,
               sbp_lowering_input=sbp_l,
               sbp_target_input=sbp_t,
               smoke_input=smoke,
               quit_smoking_input=qs)
    
    if error_message:
        return error_message

    df = construct_life_table(sex_input=sex, 
                            age_input=age, 
                            ldl_input=ldl, 
                            sbp_input=sbp, 
                            lpa_input=lpa, 
                            dia_input=dia, 
                            sma_input=sma, 
                            smo_input=smo, 
                            cig_input=cig,
                            ldl_lowering_input_p=ldl_lp,
                            ldl_lowering_input_a=ldl_la,
                            ldl_target_input=ldl_t,
                            sbp_lowering_input=sbp_l,
                            sbp_target_input=sbp_t,
                            quit_smoking_input=qs)


    df, cvd, LE = lifetable(df, age_input=age)
    LE = str(round(LE,1)) + " years"
    CV = str(round(cvd,1)) + "%"
    result_list = [LE,CV]
    fig = plot_ltrisk(df, age_input=age)
    graph_json = pio.to_json(fig)
    return render_template('baseline_results.html', result=result_list, graphJSON=graph_json)

@app.route('/interventions')
def interventions():
    data = session.get('cleaned_data')

    if not data:
        return redirect(url_for('index'))
    
    if (data['sma'] is not None) & (data['smo'] is None):
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
        error_message = errorcheck(age_input=data['age'], 
                ldl_input=data['ldl'],
                sbp_input=data['sbp'],
                lpa_input=data['sbp'],
                sma_input=data['sma'],
                smo_input=data['smo'],
                cig_input=data['cig'],
                smoke_input=data['smoke'],
                ldl_lowering_input_p=s['ldl_lp'],
                ldl_lowering_input_a=s['ldl_la'],
                ldl_target_input=s['ldl_t'],
                sbp_lowering_input=s['sbp_l'],
                sbp_target_input=s['sbp_t'],
                quit_smoking_input=s['qs'])
        
        if error_message:
            return error_message

        df = construct_life_table(sex_input=data['sex'],
                        age_input=data['age'], 
                        ldl_input=data['ldl'],
                        sbp_input=data['sbp'],
                        lpa_input=data['sbp'],
                        dia_input=data['dia'],
                        sma_input=data['sma'],
                        smo_input=data['smo'],
                        cig_input=data['cig'],
                        ldl_lowering_input_p=s['ldl_lp'],
                        ldl_lowering_input_a=s['ldl_la'],
                        ldl_target_input=s['ldl_t'],
                        sbp_lowering_input=s['sbp_l'],
                        sbp_target_input=s['sbp_t'],
                        quit_smoking_input=s['qs'])
        df, cvd, LE = lifetable(df, age_input=data['age'])
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
    result_list = cvl.values.tolist()

    final_df = pd.concat(all_df)
    fig = plot_ltrisk_i(final_df, age_input=data['age'])
    graph_json2 = pio.to_json(fig)

    return render_template('interventions.html', data = data, result=result_list, graphJSON2=graph_json2)

@app.route('/select_intervention')
def select_intervention():

    data = session.get('cleaned_data')
    if not data:
        return redirect(url_for('index'))
    
    print(data['ldl'])
    print(session.get('cleaned_data'))
    return render_template('select_intervention.html', data=data)

@app.route('/intervention', methods=['POST'])
def intervention():
    data = session.get('cleaned_data')
    if not data:
        return redirect(url_for('index'))
    
    ldl_lp_raw = request.form.get('ldl_lp', '')
    ldl_lp = float(ldl_lp_raw) if ldl_lp_raw else None
    if ldl_lp:
        ldl_lp = ldl_lp/100
    ldl_la_raw = request.form.get('ldl_la', '')
    ldl_la = float(ldl_la_raw) if ldl_la_raw else None
    ldl_t_raw = request.form.get('ldl_t', '')
    ldl_t = float(ldl_t_raw) if ldl_t_raw else None
    sbp_l_raw = request.form.get('sbp_l', '')
    sbp_l = float(sbp_l_raw) if sbp_l_raw else None
    sbp_t_raw = request.form.get('sbp_t', '')
    sbp_t = float(sbp_t_raw) if sbp_t_raw else None
    qs_raw = request.form.get('qs', '')
    qs_r = int(qs_raw) if qs_raw else None
    qs = True if qs_r==1 else None
    
    error_message = errorcheck(age_input=data['age'], 
                ldl_input=data['ldl'],
                sbp_input=data['sbp'],
                lpa_input=data['sbp'],
                sma_input=data['sma'],
                smo_input=data['smo'],
                cig_input=data['cig'],
                smoke_input=data['smoke'],
                ldl_lowering_input_p=ldl_lp,
                ldl_lowering_input_a=ldl_la,
                ldl_target_input=ldl_t,
                sbp_lowering_input=sbp_l,
                sbp_target_input=sbp_t,
                quit_smoking_input=qs)
        
    if error_message:
        return error_message
    
    if ldl_lp is not None:
        ldl100 = ldl_lp*100
        ldl_int = f'lower LDL-C {ldl100}%'
    elif ldl_la is not None:
        ldl_int = f'lower LDL-C {ldl_la} mmol/L'
    elif ldl_t is not None:
        ldl_int = f'lower LDL-C to {ldl_t} mmol/L'
    else:
        ldl_int = None

    if sbp_l is not None:
        sbp_int = f'lower systolic blood pressure {sbp_l} mmHg'
    elif sbp_t is not None:
        sbp_int = f'lower systolic blood pressure to {sbp_t} mmHg'
    else:
        sbp_int = None

    if qs == 1:
        if (ldl_int is not None) & (sbp_int is not None):
            inter = f'Intervention: {ldl_int}, {sbp_int}, and quit smoking'
        if (ldl_int is not None) & (sbp_int is None):
            inter = f'Intervention: {ldl_int} and quit smoking'
        if (ldl_int is None) & (sbp_int is not None):
            inter = f'Intervention: {sbp_int} and quit smoking'
        if (ldl_int is None) & (sbp_int is None):
            inter = f'Intervention: quit smoking'
    else:
        if (ldl_int is not None) & (sbp_int is not None):
            inter = f'Intervention: {ldl_int} and {sbp_int}'
        if (ldl_int is not None) & (sbp_int is None):
            inter = f'Intervention: {ldl_int}'
        if (ldl_int is None) & (sbp_int is not None):
            inter = f'Intervention: {sbp_int}'
        if (ldl_int is None) & (sbp_int is None):
            inter = f'No intervention'
    
    scenarios = [
            {'ldl_lp': None, 'ldl_la': None, 'ldl_t': None, 'sbp_l': None, 'sbp_t': None, 'qs': None, 'sce': 'No intervention'},
            {'ldl_lp': ldl_lp, 'ldl_la': ldl_la, 'ldl_t': ldl_t, 'sbp_l': sbp_l, 'sbp_t': sbp_t, 'qs': qs, 'sce': 'Intervention'},
        ]

    all_df = []
    all_CV = []
    all_LE = []
    all_sce = []

    for s in scenarios:
        
        df = construct_life_table(sex_input=data['sex'],
                        age_input=data['age'], 
                        ldl_input=data['ldl'],
                        sbp_input=data['sbp'],
                        lpa_input=data['sbp'],
                        dia_input=data['dia'],
                        sma_input=data['sma'],
                        smo_input=data['smo'],
                        cig_input=data['cig'],
                        ldl_lowering_input_p=s['ldl_lp'],
                        ldl_lowering_input_a=s['ldl_la'],
                        ldl_target_input=s['ldl_t'],
                        sbp_lowering_input=s['sbp_l'],
                        sbp_target_input=s['sbp_t'],
                        quit_smoking_input=s['qs'])
        df, cvd, LE = lifetable(df, age_input=data['age'])
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
    cvl.loc[cvl['sce'] == 'Intervention', 'sce'] = f'{inter}'
    result_list = cvl.values.tolist()
    print(cvl)
    print(result_list)

    final_df = pd.concat(all_df)
    fig = plot_ltrisk_u(final_df, age_input=data['age'], title_input=inter)
    graph_json2 = pio.to_json(fig)

    return render_template('intervention.html', data = data, result=result_list, graphJSON2=graph_json2)


@app.route('/restart')
def restart():
    session.clear() 
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)