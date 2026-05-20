import pandas as pd
import numpy as np

def lifetable(df, age_input):

    tp_nfMI = df['tp_nfMI'].values.copy()
    tp_nfIS = df['tp_nfIS'].values.copy()
    tp_nfHS = df['tp_nfHS'].values.copy()
    tp_nfdm = df['tp_nfdm'].values.copy()
    tp_fCHD = df['tp_fCHD'].values.copy()
    tp_fCBD = df['tp_fCBD'].values.copy()
    tp_fLC = df['tp_fLC'].values.copy()
    tp_fCC = df['tp_fCC'].values.copy()
    tp_fCOPD = df['tp_fCOPD'].values.copy()
    tp_fOTH = df['tp_fOTH'].values.copy()

    tp_nfMI_dm = df['tp_nfMI_dm'].values.copy()
    tp_nfIS_dm = df['tp_nfIS_dm'].values.copy()
    tp_nfHS_dm = df['tp_nfHS_dm'].values.copy()
    tp_fCHD_dm = df['tp_fCHD_dm'].values.copy()
    tp_fCBD_dm = df['tp_fCBD_dm'].values.copy()
    tp_fLC_dm = df['tp_fLC_dm'].values.copy()
    tp_fCC_dm = df['tp_fCC_dm'].values.copy()
    tp_fCOPD_dm = df['tp_fCOPD_dm'].values.copy()
    tp_fOTH_dm = df['tp_fOTH_dm'].values.copy()

    tp_d_cvd = df['tp_d_cvd'].values.copy()

    he_s = df['HE_S'].values.copy()
    dm_s = df['DM_S'].values.copy()
    cv_s = df['CV_S'].values.copy()
    dt_s = df['DT_S'].values.copy()
    
    he_e = df['HE_E'].values.copy()
    dm_e = df['DM_E'].values.copy()
    cv_e = df['CV_E'].values.copy()
    dt_e = df['DT_E'].values.copy()
    
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

    cvd = 100*df['CVD'].sum()
    LE = df['PY'].sum() + age_input
    
    return df, cvd, LE
