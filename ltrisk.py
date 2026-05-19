
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
import os

rfs = pd.read_csv('rfs.csv')
tps = pd.read_csv('tps.csv')

rfs['age'] = rfs['age'].round(1)
tps['age'] = tps['age'].round(1)

sex = 1
age = 20
ldl = 2
sbp = 110
lpa = None
dia = None
sma = None
smo = None
cig = None


df = pd.DataFrame({
    'sex': sex,
    'age': np.arange(1000) / 10
})
df = pd.merge(df, rfs, on=['sex', 'age'], how='inner')
df = pd.merge(df, tps, on=['sex', 'age'], how='inner')



def calculate_ldl(df, ldl_input, age_input):
    if ldl_input is None or np.isnan(ldl_input):
        df['ldl'] = df['rf_ldl']
    else:
        df['ldlnollt'] = df['rf_ldl']
        val_at_age_40 = df.loc[df['age'] == 40.0, 'rf_ldl'].item()
        df.loc[df['age'] > 40, 'ldlnollt'] = val_at_age_40
        val_at_age = df.loc[df['age'] == age_input, 'ldlnollt'].item()
        ratio = ldl_input/val_at_age
        df['ldl'] = np.nan
        df.loc[df['age'] <= 40, 'ldl'] = ratio * df['ldlnollt']
        ldl_at_age_40 = df.loc[df['age'] == 40.0, 'ldl'].item()
        df.loc[df['age'] > 40, 'ldl'] = ldl_at_age_40
    return df

def calculate_sbp(df, sbp_input, age_input):
    if sbp_input is None or np.isnan(sbp_input):
        df['sbp'] = df['rf_sbp']
    else:
        val_at_age = df.loc[df['age'] == age_input, 'rf_sbp'].item()
        ratio = sbp_input/val_at_age
        df['sbp'] = ratio * df['rf_sbp']
    return df

def calculate_lpa(df, lpa_input):
    if lpa_input is None or np.isnan(lpa_input):
        df['lpa'] = df['rf_lpa']
    else:
        df['lpa'] = lpa_input
    return df

def calculate_lsi(df, sma_input, smo_input, cig_input):
    if sma_input is None or np.isnan(sma_input):
        df['lsi'] = 0
    else:
        df['dursmk'] = np.nan
        df['tsc'] = np.nan
        df.loc[df['age'] < sma_input, 'dursmk'] = 0
        if smo_input is None or np.isnan(smo_input):
            df.loc[df['age'] >= sma_input, 'dursmk'] = df['age'] - sma_input
            df['tsc'] = 0
        else:
            df.loc[(df['age'] >= sma_input) & (df['age'] < smo_input), 'dursmk'] = df['age'] - sma_input
            df.loc[df['age'] >= smo_input, 'dursmk'] = smo_input - sma_input
            df.loc[df['age'] < smo_input, 'tsc'] = 0
            df.loc[df['age'] >= smo_input, 'tsc'] = df['age'] - smo_input
        if cig_input is None or np.isnan(cig_input):
            cig_input = 18
        df['lsi'] = 0.0
        df.loc[df['age'] >= sma_input, 'lsi'] = (1-(0.5**(df['dursmk']/18)))*(0.5**(df['tsc']/18))*np.log(cig_input+1)
    return df

def time_weight_rfs(df):
    ages = df['age'].values 
    ldl = df['ldl'].values
    lpa = df['lpa'].values
    sbp = df['sbp'].values
    rf_ldl = df['rf_ldl'].values
    rf_lpa = df['rf_lpa'].values
    rf_sbp = df['rf_sbp'].values
    ii_grid, age_grid = np.meshgrid(ages, ages)
    wt_matrix_ldl = ((ii_grid - age_grid + 3.95) / 3.95)**-2
    wt_matrix_sbp = ((ii_grid - age_grid + 1.15) / 1.15)**-2
    wt_matrix_ldl = np.where(age_grid <= ii_grid, wt_matrix_ldl, 0)
    wt_matrix_sbp = np.where(age_grid <= ii_grid, wt_matrix_sbp, 0)
    cum_wt_sum_ldl = np.sum(wt_matrix_ldl, axis=0)
    cum_wt_sum_sbp = np.sum(wt_matrix_sbp, axis=0)
    ldllog_sum = np.sum(wt_matrix_ldl * ldl[:, np.newaxis], axis=0)
    lpalog_sum = np.sum(wt_matrix_ldl * lpa[:, np.newaxis], axis=0)
    sbplog_sum = np.sum(wt_matrix_sbp * sbp[:, np.newaxis], axis=0)
    rf_ldllog_sum = np.sum(wt_matrix_ldl * rf_ldl[:, np.newaxis], axis=0)
    rf_lpalog_sum = np.sum(wt_matrix_ldl * rf_lpa[:, np.newaxis], axis=0)
    rf_sbplog_sum = np.sum(wt_matrix_sbp * rf_sbp[:, np.newaxis], axis=0)
    df['mcldl'] = (ldllog_sum) / (cum_wt_sum_ldl)
    df['mclpa'] = (lpalog_sum) / (cum_wt_sum_ldl)
    df['mcsbp'] = (sbplog_sum) / (cum_wt_sum_sbp)
    df['rf_mcldl'] = (rf_ldllog_sum) / (cum_wt_sum_ldl)
    df['rf_mclpa'] = (rf_lpalog_sum) / (cum_wt_sum_ldl)
    df['rf_mcsbp'] = (rf_sbplog_sum) / (cum_wt_sum_sbp)
    return df

def apply_MR(df):
    df['tp_nfMI'] *= (1.84**(df['mcldl'] - df['rf_mcldl']))
    df['tp_nfMI'] *= (1.005**(df['mclpa'] - df['rf_mclpa']))
    df['tp_nfMI'] *= (1.032**(df['mcsbp'] - df['rf_mcsbp']))
    df['tp_nfMI'] *= (1.65**(df['lsi'] - df['rf_lsi']))
    df['tp_nfMI_dm'] = 1.32 * df['tp_nfMI'] / (1 + (0.32 * df['rf_dmp']))
    df['tp_nfMI'] /= (1 + (0.32 * df['rf_dmp']))

    df['tp_fCHD'] *= (1.84**(df['mcldl'] - df['rf_mcldl']))
    df['tp_fCHD'] *= (1.005**(df['mclpa'] - df['rf_mclpa']))
    df['tp_fCHD'] *= (1.032**(df['mcsbp'] - df['rf_mcsbp']))
    df['tp_fCHD'] *= (1.65**(df['lsi'] - df['rf_lsi']))
    df['tp_fCHD_dm'] = 1.32 * df['tp_fCHD'] / (1 + (0.32 * df['rf_dmp']))
    df['tp_fCHD'] /= (1 + (0.32 * df['rf_dmp']))

    df['tp_nfIS'] *= (1.08**(df['mcldl'] - df['rf_mcldl']))
    df['tp_nfIS'] *= (1.003**(df['mclpa'] - df['rf_mclpa']))
    df['tp_nfIS'] *= (1.033**(df['mcsbp'] - df['rf_mcsbp']))
    df['tp_nfIS'] *= (1.40**(df['lsi'] - df['rf_lsi']))
    df['tp_nfIS_dm'] = 1.73 * df['tp_nfIS'] / (1 + (0.73 * df['rf_dmp']))
    df['tp_nfIS'] /= (1 + (0.73 * df['rf_dmp']))

    df['tp_fCBD'] *= (1.08**(df['mcldl'] - df['rf_mcldl']))
    df['tp_fCBD'] *= (1.003**(df['mclpa'] - df['rf_mclpa']))
    df['tp_fCBD'] *= (1.033**(df['mcsbp'] - df['rf_mcsbp']))
    df['tp_fCBD'] *= (1.40**(df['lsi'] - df['rf_lsi']))
    df['tp_fCBD_dm'] = 1.73 * df['tp_fCBD'] / (1 + (0.73 * df['rf_dmp']))
    df['tp_fCBD'] /= (1 + (0.73 * df['rf_dmp']))

    df['tp_nfHS'] *= (1.036**(df['mcsbp'] - df['rf_mcsbp']))
    df['tp_nfHS'] *= (1.78**(df['lsi'] - df['rf_lsi']))

    df['tp_nfdm'] *= (0.80**(df['mcldl'] - df['rf_mcldl']))
    df['tp_nfdm'] *= (1.025**(df['mcsbp'] - df['rf_mcsbp']))
    df['tp_nfdm'] *= (1.20**(df['lsi'] - df['rf_lsi']))

    df['tp_fCC'] *= (1.24**(df['lsi'] - df['rf_lsi']))

    lsi_diff = df['lsi'] - df['rf_lsi']
    df['tp_fLC'] *= np.where(lsi_diff <= 1, 13.12**lsi_diff, 13.12)
    df['tp_fCOPD'] *= np.where(lsi_diff <= 1, 13.12**lsi_diff, 13.12)

    vars = ['tp_nfHS', 'tp_fLC', 'tp_fCC', 'tp_fCOPD', 'tp_fOTH', ]
    for i in vars:
        df[f"{i}_dm"] = df[i]

    df['tp_d_cvd'] = 3*(df['tp_fCHD']+df['tp_fCBD']+df['tp_fLC']+df['tp_fCC']+df['tp_fCOPD']+df['tp_fOTH'])

    return df

def adjust_tp(df):
    vars = ['tp_nfMI', 'tp_nfIS', 'tp_nfHS', 'tp_nfdm', 'tp_fCHD', 'tp_fCBD', 'tp_fLC', 'tp_fCC', 'tp_fCOPD', 'tp_fOTH']
    vars_dm = ['tp_nfMI_dm', 'tp_fCHD_dm', 'tp_nfIS_dm', 'tp_fCBD_dm', 'tp_nfHS_dm', 'tp_fLC_dm', 'tp_fCC_dm', 'tp_fCOPD_dm', 'tp_fOTH_dm']

    df['ratesum_he'] = df['tp_nfMI']+df['tp_nfIS']+df['tp_nfHS']+df['tp_nfdm']+df['tp_fCHD']+df['tp_fCBD']+df['tp_fLC']+df['tp_fCC']+df['tp_fCOPD']+df['tp_fOTH']
    df['ratesum_dm'] = df['tp_nfMI_dm']+df['tp_fCHD_dm']+df['tp_nfIS_dm']+df['tp_fCBD_dm']+df['tp_nfHS_dm']+df['tp_fLC_dm']+df['tp_fCC_dm']+df['tp_fCOPD_dm']+df['tp_fOTH_dm']

    df['tpsum_he'] = 1-np.exp(-df['ratesum_he']*0.1)
    df['tpsum_dm'] = 1-np.exp(-df['ratesum_dm']*0.1)

    for i in vars:
        df[i] =  df['tpsum_he']*df[i]/df['ratesum_he']
    
    for i in vars_dm:
        df[i] =  df['tpsum_dm']*df[i]/df['ratesum_dm']

    df['tp_d_cvd'] = 1-np.exp(-df['tp_d_cvd']*0.1)

    return df

def lifetable(df, dia_input, age_input):

    df['HE_S'] = np.nan
    df['DM_S'] = np.nan
    df['CV_S'] = np.nan
    df['DT_S'] = np.nan
    df['HE_E'] = np.nan
    df['DM_E'] = np.nan
    df['CV_E'] = np.nan
    df['DT_E'] = np.nan


    if dia_input is None or np.isnan(dia_input):
        df.loc[df['age'] == age_input, 'HE_S'] = 1 - df['rf_dmp']
        df.loc[df['age'] == age_input, 'DM_S'] = df['rf_dmp']
    if dia_input == 0:
        df.loc[df['age'] == age_input, 'HE_S'] = 1.0
        df.loc[df['age'] == age_input, 'DM_S'] = 0.0
    if dia_input == 1:
        df.loc[df['age'] == age_input, 'HE_S'] = 0.0
        df.loc[df['age'] == age_input, 'DM_S'] = 1.0

    df.loc[df['age'] == age_input, 'CV_S'] = 0.0
    df.loc[df['age'] == age_input, 'DT_S'] = 0.0

    tp_nfMI = df['tp_nfMI'].values
    tp_nfIS = df['tp_nfIS'].values
    tp_nfHS = df['tp_nfHS'].values
    tp_nfdm = df['tp_nfdm'].values
    tp_fCHD = df['tp_fCHD'].values
    tp_fCBD = df['tp_fCBD'].values
    tp_fLC = df['tp_fLC'].values
    tp_fCC = df['tp_fCC'].values
    tp_fCOPD = df['tp_fCOPD'].values
    tp_fOTH = df['tp_fOTH'].values

    tp_nfMI_dm = df['tp_nfMI_dm'].values
    tp_nfIS_dm = df['tp_nfIS_dm'].values
    tp_nfHS_dm = df['tp_nfHS_dm'].values
    tp_fCHD_dm = df['tp_fCHD_dm'].values
    tp_fCBD_dm = df['tp_fCBD_dm'].values
    tp_fLC_dm = df['tp_fLC_dm'].values
    tp_fCC_dm = df['tp_fCC_dm'].values
    tp_fCOPD_dm = df['tp_fCOPD_dm'].values
    tp_fOTH_dm = df['tp_fOTH_dm'].values

    tp_d_cvd = df['tp_d_cvd'].values

    he_s = df['HE_S'].values
    dm_s = df['DM_S'].values
    cv_s = df['CV_S'].values
    dt_s = df['DT_S'].values
    
    he_e = df['HE_E'].values
    dm_e = df['DM_E'].values
    cv_e = df['CV_E'].values
    dt_e = df['DT_E'].values
    
    ages = age_input*10
    for i in range(ages, 1000):
        if i > ages:
            he_s[i] = he_e[i-1]
            dm_s[i] = dm_e[i-1]
            cv_s[i] = cv_e[i-1]
            dt_s[i] = dt_e[i-1]

        he_e[i] = he_s[i]-(he_s[i]*(tp_nfMI[i]+tp_nfIS[i]+tp_nfHS[i]+tp_nfdm[i]+tp_fCHD[i]+tp_fCBD[i]+tp_fLC[i]+tp_fCC[i]+tp_fCOPD[i]+tp_fOTH[i]))
        dm_e[i] = dm_s[i]+(he_s[i]*tp_nfdm[i])-(dm_s[i]*(tp_nfMI_dm[i]+tp_nfIS_dm[i]+tp_nfHS_dm[i]+tp_fCHD_dm[i]+tp_fCBD_dm[i]+tp_fLC_dm[i]+tp_fCC_dm[i]+tp_fCOPD_dm[i]+tp_fOTH_dm[i]))
        cv_e[i] = cv_s[i]+(he_s[i]*(tp_nfMI[i]+tp_nfIS[i]+tp_nfHS[i]))+(dm_s[i]*(tp_nfMI_dm[i]+tp_nfIS_dm[i]+tp_nfHS_dm[i]))-(cv_s[i]*tp_d_cvd[i])
        dt_e[i] = dt_s[i]+(he_s[i]*(tp_fCHD[i]+tp_fCBD[i]+tp_fLC[i]+tp_fCC[i]+tp_fCOPD[i]+tp_fOTH[i]))+(dm_s[i]*(tp_fCHD_dm[i]+tp_fCBD_dm[i]+tp_fLC_dm[i]+tp_fCC_dm[i]+tp_fCOPD_dm[i]+tp_fOTH_dm[i]))+(cv_s[i]*tp_d_cvd[i])

    cvd = ((he_s*(tp_nfMI+tp_fCHD+tp_nfIS+tp_nfHS+tp_fCBD)) + (dm_s*(tp_nfMI_dm+tp_fCHD_dm+tp_nfIS_dm+tp_nfHS_dm+tp_fCBD_dm)))
    py = 0.1*(he_e+cv_e+dm_e+(0.5*((he_s*(tp_fCHD+tp_fCBD+tp_fLC+tp_fCC+tp_fCOPD+tp_fOTH))+(dm_s*(tp_fCHD_dm+tp_fCBD_dm+tp_fLC_dm+tp_fCC_dm+tp_fCOPD_dm+tp_fOTH_dm))+(cv_s*tp_d_cvd))))


    df['HE_S'], df['DM_S'], df['CV_S'], df['DT_S'] = he_s, dm_s, cv_s, dt_s
    df['HE_E'], df['DM_E'], df['CV_E'], df['DT_E'] = he_e, dm_e, cv_e, dt_e
    df['CVD'], df['PY'] = cvd, py


    return df

def lifetable_outputs(df, age_input):
    cvd = 100*df['CVD'].sum()
    LE = df['PY'].sum() + age_input
    return cvd, LE

def plot_ltrisk(df, age_input):
    df['cumcvd'] = 100*df['CVD'].cumsum()
    df['Age'], df['Cumulative_risk_of_CVD'] = df['age'], df['cumcvd']
    fig = px.line(df,
                    x="Age", 
                    y="Cumulative_risk_of_CVD", 
                    hover_data={'Age': ':,d','Cumulative_risk_of_CVD': ':.1f'},
                    title="Cumulative risk of CVD",
                    )

    fig.update_layout(
                    xaxis_title="Age (years)",
                    yaxis_title="Cumulative risk of CVD (%)",
                    font=dict(family="Courier New, monospace", size=18)
    )


    maxcvd = df['Cumulative_risk_of_CVD'].max()+10

    fig.update_xaxes(
    range=[age_input, 100],
    tickformat=',d',
    zeroline=True, 
    zerolinecolor='black', 
    zerolinewidth=2
    )
    fig.update_yaxes(
    range=[0, maxcvd],
    tickformat=',d',
    zeroline=True, 
    zerolinecolor='black',
    zerolinewidth=2
    )

    return fig


df = calculate_ldl(df, ldl_input=ldl, age_input=age)
df = calculate_sbp(df, sbp_input=sbp, age_input=age)
df = calculate_lpa(df, lpa_input=lpa)
df = calculate_lsi(df, sma_input=sma, smo_input=smo, cig_input=cig)
df = time_weight_rfs(df)
df = apply_MR(df)
df = adjust_tp(df)
df = lifetable(df, dia_input=dia, age_input=age)
cvd, LE = lifetable_outputs(df, age_input=age)
fig = plot_ltrisk(df, age_input=age)
graph_json = pio.to_json(fig)

print(round(cvd, 1))
print(round(LE, 2))


#df2 = pd.DataFrame({
#    'sex': df['sex'],
#    'age': df['CVD']
#})

#print(df.tail())

#print(df2.tail())

# Then interventions
# Then into the website

#print(df[['PY']].head())

#print(df.tail())


#print(df.loc[(df['age'] >= 39) & (df['age'] <= 41), ['age', 'ldl', 'rf_ldl']])




#print(df[['age', 'ldl']].head())

#print(df.loc[(df['age'] >= 39) & (df['age'] <= 41), ['age', 'sbp', 'rf_sbp']])


#print(df[['age', 'ldl']].head())


#df.loc[mask, 'col'] = val      replace col = val if ...
#df['col'].replace(old, new)    recode col (old=new)
#df['col'] = new_values         replace col = ... (no if)
#df['col'].fillna(0)            replace col = 0 if col == .
