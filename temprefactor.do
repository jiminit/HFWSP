/*
cd ~/Documents/HFWSP

use ~/Documents/HF/rfs, clear
drop rf_ldl_e-rf_dmp_e
export delimited using rfs.csv, replace

use ~/Documents/HF/tps, clear
drop tp_nfMI_e-tp_fOTH_e
export delimited using tps.csv, replace
*/



local AGE = 20
local SEX = 1
local LDL = 2
local SBP = 110
local LPA = .
local DIA = .
local SMA = .
local SMO = .
local CIG = .

clear
set obs 1000
gen sex = `SEX'
gen age = (_n-1)/10
merge 1:1 sex age using ~/Documents/HF/rfs, nogen keep(3)
merge 1:1 sex age using ~/Documents/HF/tps, nogen keep(3)
drop tp_nfMI_e-tp_fOTH_e
if `LDL'==. {
gen ldl = rf_ldl
}
else {
gen ldlnollt = rf_ldl
replace ldlnollt = rf_ldl[401] if age > 40
gen ldli = `LDL'/ldlnollt if age == `AGE'
egen ldlr = min(ldli)
gen ldl = ldlr*ldlnollt if age <= 40
replace ldl = ldl[401] if age > 40
}
if `SBP'==. {
gen sbp = rf_sbp 
}
else {
gen sbpi = `SBP'/rf_sbp if age == `AGE'
egen sbpr = min(sbpi)
gen sbp = sbpr*rf_sbp
}
if `LPA'==. {
gen lpa = rf_lpa
}
else {
gen lpa = `LPA'
}



if `SMA'==. {
gen lsi = 0
}
else {
gen agess = `SMA'
gen dursmk = 0 if age < `SMA'
if `SMO'==. {
replace dursmk = age-`SMA' if age >= `SMA'
gen tsc = 0
}
else {
replace dursmk = age-`SMA' if age >= `SMA' & age < `SMO'
replace dursmk = `SMO'-`SMA' if age >= `SMO'
gen tsc = 0 if age < `SMO'
replace tsc = age-`SMO' if age >= `SMO'
}
if `CIG'==. {
gen ncig = 18
}
else {
gen ncig = `CIG'
}
gen lsi = 0 if age < `SMA'
replace lsi = (1-(0.5^(dursmk/18)))*(0.5^(tsc/18))*ln(ncig+1) if age >= `SMA'
}




gen cumldl=.
gen mcldl=.
gen rf_cumldl=.
gen rf_mcldl=.
gen cumlpa=.
gen mclpa=.
gen rf_cumlpa=.
gen rf_mclpa=.
gen cumsbp=.
gen mcsbp=.
gen rf_cumsbp=.
gen rf_mcsbp=.
replace age = age*10
forval ii = 0/999 {
gen wt = ((`ii'-age+39.5)/39.5)^(-2) if age <= `ii'
gen ldllog = ldl*wt
gen rf_ldllog = rf_ldl*wt
gen cumldllog = sum(ldllog)/10
gen rf_cumldllog = sum(rf_ldllog)/10
gen cumlog = sum(wt)/10
replace cumldl = cumldllog if age == `ii'
replace mcldl = cumldllog/cumlog if age == `ii'
replace rf_cumldl = rf_cumldllog if age == `ii'
replace rf_mcldl = rf_cumldllog/cumlog if age == `ii'
drop wt ldllog cumldllog cumlog rf_ldllog rf_cumldllog
}
forval ii = 0/999 {
gen wt = ((`ii'-age+39.5)/39.5)^(-2) if age <= `ii'
gen lpalog = lpa*wt
gen rf_lpalog = rf_lpa*wt
gen cumlpalog = sum(lpalog)/10
gen rf_cumlpalog = sum(rf_lpalog)/10
gen cumlog = sum(wt)/10
replace cumlpa = cumlpalog if age == `ii'
replace mclpa = cumlpalog/cumlog if age == `ii'
replace rf_cumlpa = rf_cumlpalog if age == `ii'
replace rf_mclpa = rf_cumlpalog/cumlog if age == `ii'
drop wt lpalog cumlpalog cumlog rf_lpalog rf_cumlpalog
}
forval ii = 0/999 {
gen wt = ((`ii'-age+11.5)/11.5)^(-2) if age <= `ii'
gen sbplog = sbp*wt
gen rf_sbplog = rf_sbp*wt
gen cumsbplog = sum(sbplog)/10
gen rf_cumsbplog = sum(rf_sbplog)/10
gen cumlog = sum(wt)/10
replace cumsbp = cumsbplog if age == `ii'
replace mcsbp = cumsbplog/cumlog if age == `ii'
replace rf_cumsbp = rf_cumsbplog if age == `ii'
replace rf_mcsbp = rf_cumsbplog/cumlog if age == `ii'
drop wt sbplog cumsbplog cumlog rf_sbplog rf_cumsbplog
}
replace age = age*0.1
replace tp_nfMI = tp_nfMI*(1.84^(mcldl-rf_mcldl))
replace tp_nfMI = tp_nfMI*(1.005^(mclpa-rf_mclpa))
replace tp_nfMI = tp_nfMI*(1.032^(mcsbp-rf_mcsbp))
replace tp_nfMI = tp_nfMI*(1.65^(lsi-rf_lsi))
gen tp_nfMI_dm = 1.32*tp_nfMI/(1+(0.32*rf_dmp))
replace tp_nfMI = tp_nfMI/(1+(0.32*rf_dmp))
replace tp_fCHD = tp_fCHD*(1.84^(mcldl-rf_mcldl))
replace tp_fCHD = tp_fCHD*(1.005^(mclpa-rf_mclpa))
replace tp_fCHD = tp_fCHD*(1.032^(mcsbp-rf_mcsbp))
replace tp_fCHD = tp_fCHD*(1.65^(lsi-rf_lsi))
gen tp_fCHD_dm = 1.32*tp_fCHD/(1+(0.32*rf_dmp))
replace tp_fCHD = tp_fCHD/(1+(0.32*rf_dmp))
replace tp_nfIS = tp_nfIS*(1.08^(mcldl-rf_mcldl))
replace tp_nfIS = tp_nfIS*(1.003^(mclpa-rf_mclpa))
replace tp_nfIS = tp_nfIS*(1.033^(mcsbp-rf_mcsbp))
replace tp_nfIS = tp_nfIS*(1.40^(lsi-rf_lsi))
gen tp_nfIS_dm = 1.73*tp_nfIS/(1+(0.73*rf_dmp))
replace tp_nfIS = tp_nfIS/(1+(0.73*rf_dmp))
replace tp_fCBD = tp_fCBD*(1.08^(mcldl-rf_mcldl))
replace tp_fCBD = tp_fCBD*(1.003^(mclpa-rf_mclpa))
replace tp_fCBD = tp_fCBD*(1.033^(mcsbp-rf_mcsbp))
replace tp_fCBD = tp_fCBD*(1.40^(lsi-rf_lsi))
gen tp_fCBD_dm = 1.73*tp_fCBD/(1+(0.73*rf_dmp))
replace tp_fCBD = tp_fCBD/(1+(0.73*rf_dmp))
replace tp_nfHS = tp_nfHS*(1.036^(mcsbp-rf_mcsbp))
replace tp_nfHS = tp_nfHS*(1.78^(lsi-rf_lsi))
replace tp_nfdm = tp_nfdm*(0.80^(mcldl-rf_mcldl))
replace tp_nfdm = tp_nfdm*(1.025^(mcsbp-rf_mcsbp))
replace tp_nfdm = tp_nfdm*(1.20^(lsi-rf_lsi))
replace tp_fLC = tp_fLC*(13.12^(lsi-rf_lsi))
replace tp_fCC = tp_fCC*(1.24^(lsi-rf_lsi))
replace tp_fCOPD = tp_fCOPD*(13.12^(lsi-rf_lsi))
foreach var of varlist tp_nfHS tp_fLC-tp_fOTH {
gen `var'_dm=`var'
}
replace tp_d_cvd = 3*(tp_fCHD+tp_fCBD+tp_fLC+tp_fCC+tp_fCOPD+tp_fOTH)
gen ratesum_he = 0
foreach var of varlist tp_nfMI-tp_fOTH {
replace ratesum_he = ratesum_he+`var'
}
gen tpsum_he = 1-exp(-ratesum_he*0.1)
foreach var of varlist tp_nfMI-tp_fOTH {
replace `var' = tpsum_he*`var'/ratesum_he
}
gen ratesum_dm = 0
foreach var of varlist tp_nfMI_dm-tp_fOTH_dm {
replace ratesum_dm = ratesum_dm+`var'
}
gen tpsum_dm = 1-exp(-ratesum_dm*0.1)
foreach var of varlist tp_nfMI_dm-tp_fOTH_dm {
replace `var' = tpsum_dm*`var'/ratesum_dm
}
replace tp_d_cvd = 1-exp(-tp_d_cvd*0.1)
if `DIA'==. {
gen double HE_S = 1-rf_dmp if age == `AGE'
gen double DM_S = rf_dmp if age == `AGE'
}
if `DIA'==0 {
gen double HE_S = 1 if age == `AGE'
gen double DM_S = 0 if age == `AGE'
}
if `DIA'==1 {
gen double HE_S = 0 if age == `AGE'
gen double DM_S = 1 if age == `AGE'
}
gen double CV_S = 0 if age == `AGE'
gen double DT_S = 0 if age == `AGE'
gen double MICHD = .
gen double STCBD = .
gen double HE_E = .
gen double DM_E = .
gen double CV_E = .
gen double DT_E = .
replace MICHD = (HE_S*(tp_nfMI+tp_fCHD)) + (DM_S*(tp_nfMI_dm+tp_fCHD_dm)) if age == `AGE'
replace STCBD = (HE_S*(tp_nfIS+tp_nfHS+tp_fCBD)) + (DM_S*(tp_nfIS_dm+tp_nfHS_dm+tp_fCBD_dm)) if age == `AGE'
replace HE_E = HE_S-(HE_S*(tp_nfMI+tp_nfIS+tp_nfHS+tp_nfdm+tp_fCHD+tp_fCBD+tp_fLC+tp_fCC+tp_fCOPD+tp_fOTH)) if age == `AGE'
replace DM_E = DM_S+(HE_S*tp_nfdm)-(DM_S*(tp_nfMI_dm+tp_nfIS_dm+tp_nfHS_dm+tp_fCHD_dm+tp_fCBD_dm+tp_fLC_dm+tp_fCC_dm+tp_fCOPD_dm+tp_fOTH_dm)) if age == `AGE'
replace CV_E = CV_S+(HE_S*(tp_nfMI+tp_nfIS+tp_nfHS))+(DM_S*(tp_nfMI_dm+tp_nfIS_dm+tp_nfHS_dm))-(CV_S*tp_d_cvd) if age == `AGE'
replace DT_E = DT_S+(HE_S*(tp_fCHD+tp_fCBD+tp_fLC+tp_fCC+tp_fCOPD+tp_fOTH))+(DM_S*(tp_fCHD_dm+tp_fCBD_dm+tp_fLC_dm+tp_fCC_dm+tp_fCOPD_dm+tp_fOTH_dm))+(CV_S*tp_d_cvd) if age == `AGE'
local a = (`AGE'*10)+2
forval i = `a'/1000 {
replace HE_S = HE_E[_n-1] if _n == `i'
replace DM_S = DM_E[_n-1] if _n == `i'
replace CV_S = CV_E[_n-1] if _n == `i'
replace DT_S = DT_E[_n-1] if _n == `i'
replace MICHD = (HE_S*(tp_nfMI+tp_fCHD)) + (DM_S*(tp_nfMI_dm+tp_fCHD_dm)) if _n == `i'
replace STCBD = (HE_S*(tp_nfIS+tp_nfHS+tp_fCBD)) + (DM_S*(tp_nfIS_dm+tp_nfHS_dm+tp_fCBD_dm)) if _n == `i'
replace HE_E = HE_S-(HE_S*(tp_nfMI+tp_nfIS+tp_nfHS+tp_nfdm+tp_fCHD+tp_fCBD+tp_fLC+tp_fCC+tp_fCOPD+tp_fOTH)) if _n == `i'
replace DM_E = DM_S+(HE_S*tp_nfdm)-(DM_S*(tp_nfMI_dm+tp_nfIS_dm+tp_nfHS_dm+tp_fCHD_dm+tp_fCBD_dm+tp_fLC_dm+tp_fCC_dm+tp_fCOPD_dm+tp_fOTH_dm)) if _n == `i'
replace CV_E = CV_S+(HE_S*(tp_nfMI+tp_nfIS+tp_nfHS))+(DM_S*(tp_nfMI_dm+tp_nfIS_dm+tp_nfHS_dm))-(CV_S*tp_d_cvd) if _n == `i'
replace DT_E = DT_S+(HE_S*(tp_fCHD+tp_fCBD+tp_fLC+tp_fCC+tp_fCOPD+tp_fOTH))+(DM_S*(tp_fCHD_dm+tp_fCBD_dm+tp_fLC_dm+tp_fCC_dm+tp_fCOPD_dm+tp_fOTH_dm))+(CV_S*tp_d_cvd) if _n == `i'
}
gen PY = 0.1*(HE_E+CV_E+DM_E+(0.5*((HE_S*(tp_fCHD+tp_fCBD+tp_fLC+tp_fCC+tp_fCOPD+tp_fOTH))+(DM_S*(tp_fCHD_dm+tp_fCBD_dm+tp_fLC_dm+tp_fCC_dm+tp_fCOPD_dm+tp_fOTH_dm))+(CV_S*tp_d_cvd))))
gen TPY =.
forval i = 1/1000 {
su PY if _n>=`i'
replace TPY = r(sum) if _n==`i'
}
gen LE = `AGE'+TPY/(HE_S+DM_S+CV_S)
gen LTriskCHD = sum(MICHD)+sum(STCBD)
keep if _n == `a' | _n==_N

br LE LTriskCHD
stop
gen LTriskCHD = sum(MICHD)
gen LTriskCBD = sum(STCBD)
local b = (`AGE'*10)+1
mat A = (LE[`b']+`AGE',100*LTriskCHD[1000],100*LTriskCBD[1000],100*(LTriskCHD[1000]+LTriskCBD[1000]))
mat colnames A = LE LTRCHD LTRCBD LTRCVD
return matrix ltrisk_mat = A
return local LE = LE[`b']+`AGE'
return local LTRCVD = 100*(LTriskCHD[1000]+LTriskCBD[1000])
}
end
}

gen A = LTriskCHD+LTriskCBD


quietly {

*copy /home/jimb0w/Documents/HF/rfs.dta /home/jimb0w/Documents/HFWS/stata_files/rfs.dta
*copy /home/jimb0w/Documents/HF/tps.dta /home/jimb0w/Documents/HFWS/stata_files/tps.dta

program drop _all

program ltrisk, rclass
args AGE SEX LDL SBP LPA DIA SMA SMO CIG
if `AGE' < 10 | `AGE' > 90 {
di "Age must be between 10 and 90 years"
exit
}
if `AGE'!=int(`AGE') {
di "Age must be an integer"
exit
}
if `SEX'!= 0 & `SEX'!= 1 {
di "Invalid sex"
exit
}
if `LDL' < 0.1 | (`LDL' > 10 & `LDL'!=.) {
di "LDL-C must be between 0.1 and 10 mmol/L"
exit
}
if `SBP' < 80 | (`SBP' > 250 & `SBP'!=.) {
di "Systolic blood pressure must be between 80 and 250 mmHg"
exit
}
if `LPA' < 0.1 | (`LPA' > 1000 & `LPA'!=.) {
di "Lp(a) must be between 0.1 and 1000 mg/dL"
exit
}
if `DIA'!= 0 & `DIA'!= 1 & `DIA'!=. {
di "Invalid Diabetes status"
exit
}
if `SMA' < 5 | (`SMA' > 90 & `SMA'!=.) {
di "Age of starting smoking must be between 5 and 90 years"
exit
}
if `SMA'!=int(`SMA') {
di "Age of starting smoking must be an integer"
exit
}
if `SMO' < 5 | (`SMO' > 90 & `SMO'!=.) {
di "Age of quitting smoking must be between 5 and 90 years"
exit
}
if `SMO'!=int(`SMO') {
di "Age of quitting smoking must be an integer"
exit
}
if (`SMO' <= `SMA') & `SMO'!=. & `SMA'!=. {
di "The age of quitting smoking must be greater than the age of starting smoking"
exit
}
if (`SMO'!=. | `CIG'!=.) & `SMA'==. {
di "Please enter a smoking starting age"
exit
}
if `CIG' < 0.1 | (`CIG' > 200 & `CIG'!=.) {
di "Number of cigarettes smoked daily must be a number between 0.1 and 200"
exit
}
if `SMA' > `AGE' & `SMA'!=. {
di "Age of starting smoking must be less than or equal to current age"
exit
}
if `SMO' > `AGE' & `SMO'!=. {
di "Age of quitting smoking must be less than or equal to current age"
exit
}
quietly {
clear
set obs 1000
gen sex = `SEX'
gen age = (_n-1)/10
merge 1:1 sex age using stata_files/rfs, nogen keep(3)
merge 1:1 sex age using stata_files/tps, nogen keep(3)
drop tp_nfMI_e-tp_fOTH_e
if `LDL'==. {
gen ldl = rf_ldl
}
else {
gen ldlnollt = rf_ldl
replace ldlnollt = rf_ldl[401] if age > 40
gen ldli = `LDL'/ldlnollt if age == `AGE'
egen ldlr = min(ldli)
gen ldl = ldlr*ldlnollt if age <= 40
replace ldl = ldl[401] if age > 40
}
if `SBP'==. {
gen sbp = rf_sbp 
}
else {
gen sbpi = `SBP'/rf_sbp if age == `AGE'
egen sbpr = min(sbpi)
gen sbp = sbpr*rf_sbp
}
if `LPA'==. {
gen lpa = rf_lpa
}
else {
gen lpa = `LPA'
}
if `SMA'==. {
gen lsi = 0
}
else {
gen agess = `SMA'
gen dursmk = 0 if age < `SMA'
if `SMO'==. {
replace dursmk = age-`SMA' if age >= `SMA'
gen tsc = 0
}
else {
replace dursmk = age-`SMA' if age >= `SMA' & age < `SMO'
replace dursmk = `SMO'-`SMA' if age >= `SMO'
gen tsc = 0 if age < `SMO'
replace tsc = age-`SMO' if age >= `SMO'
}
if `CIG'==. {
gen ncig = 18
}
else {
gen ncig = `CIG'
}
gen lsi = 0 if age < `SMA'
replace lsi = (1-(0.5^(dursmk/18)))*(0.5^(tsc/18))*ln(ncig+1) if age >= `SMA'
}
gen cumldl=.
gen mcldl=.
gen rf_cumldl=.
gen rf_mcldl=.
gen cumlpa=.
gen mclpa=.
gen rf_cumlpa=.
gen rf_mclpa=.
gen cumsbp=.
gen mcsbp=.
gen rf_cumsbp=.
gen rf_mcsbp=.
replace age = age*10
forval ii = 0/999 {
gen wt = ((`ii'-age+39.5)/39.5)^(-2) if age <= `ii'
gen ldllog = ldl*wt
gen rf_ldllog = rf_ldl*wt
gen cumldllog = sum(ldllog)/10
gen rf_cumldllog = sum(rf_ldllog)/10
gen cumlog = sum(wt)/10
replace cumldl = cumldllog if age == `ii'
replace mcldl = cumldllog/cumlog if age == `ii'
replace rf_cumldl = rf_cumldllog if age == `ii'
replace rf_mcldl = rf_cumldllog/cumlog if age == `ii'
drop wt ldllog cumldllog cumlog rf_ldllog rf_cumldllog
}
forval ii = 0/999 {
gen wt = ((`ii'-age+39.5)/39.5)^(-2) if age <= `ii'
gen lpalog = lpa*wt
gen rf_lpalog = rf_lpa*wt
gen cumlpalog = sum(lpalog)/10
gen rf_cumlpalog = sum(rf_lpalog)/10
gen cumlog = sum(wt)/10
replace cumlpa = cumlpalog if age == `ii'
replace mclpa = cumlpalog/cumlog if age == `ii'
replace rf_cumlpa = rf_cumlpalog if age == `ii'
replace rf_mclpa = rf_cumlpalog/cumlog if age == `ii'
drop wt lpalog cumlpalog cumlog rf_lpalog rf_cumlpalog
}
forval ii = 0/999 {
gen wt = ((`ii'-age+11.5)/11.5)^(-2) if age <= `ii'
gen sbplog = sbp*wt
gen rf_sbplog = rf_sbp*wt
gen cumsbplog = sum(sbplog)/10
gen rf_cumsbplog = sum(rf_sbplog)/10
gen cumlog = sum(wt)/10
replace cumsbp = cumsbplog if age == `ii'
replace mcsbp = cumsbplog/cumlog if age == `ii'
replace rf_cumsbp = rf_cumsbplog if age == `ii'
replace rf_mcsbp = rf_cumsbplog/cumlog if age == `ii'
drop wt sbplog cumsbplog cumlog rf_sbplog rf_cumsbplog
}
replace age = age*0.1
replace tp_nfMI = tp_nfMI*(1.84^(mcldl-rf_mcldl))
replace tp_nfMI = tp_nfMI*(1.005^(mclpa-rf_mclpa))
replace tp_nfMI = tp_nfMI*(1.032^(mcsbp-rf_mcsbp))
replace tp_nfMI = tp_nfMI*(1.65^(lsi-rf_lsi))
gen tp_nfMI_dm = 1.32*tp_nfMI/(1+(0.32*rf_dmp))
replace tp_nfMI = tp_nfMI/(1+(0.32*rf_dmp))
replace tp_fCHD = tp_fCHD*(1.84^(mcldl-rf_mcldl))
replace tp_fCHD = tp_fCHD*(1.005^(mclpa-rf_mclpa))
replace tp_fCHD = tp_fCHD*(1.032^(mcsbp-rf_mcsbp))
replace tp_fCHD = tp_fCHD*(1.65^(lsi-rf_lsi))
gen tp_fCHD_dm = 1.32*tp_fCHD/(1+(0.32*rf_dmp))
replace tp_fCHD = tp_fCHD/(1+(0.32*rf_dmp))
replace tp_nfIS = tp_nfIS*(1.08^(mcldl-rf_mcldl))
replace tp_nfIS = tp_nfIS*(1.003^(mclpa-rf_mclpa))
replace tp_nfIS = tp_nfIS*(1.033^(mcsbp-rf_mcsbp))
replace tp_nfIS = tp_nfIS*(1.40^(lsi-rf_lsi))
gen tp_nfIS_dm = 1.73*tp_nfIS/(1+(0.73*rf_dmp))
replace tp_nfIS = tp_nfIS/(1+(0.73*rf_dmp))
replace tp_fCBD = tp_fCBD*(1.08^(mcldl-rf_mcldl))
replace tp_fCBD = tp_fCBD*(1.003^(mclpa-rf_mclpa))
replace tp_fCBD = tp_fCBD*(1.033^(mcsbp-rf_mcsbp))
replace tp_fCBD = tp_fCBD*(1.40^(lsi-rf_lsi))
gen tp_fCBD_dm = 1.73*tp_fCBD/(1+(0.73*rf_dmp))
replace tp_fCBD = tp_fCBD/(1+(0.73*rf_dmp))
replace tp_nfHS = tp_nfHS*(1.036^(mcsbp-rf_mcsbp))
replace tp_nfHS = tp_nfHS*(1.78^(lsi-rf_lsi))
replace tp_nfdm = tp_nfdm*(0.80^(mcldl-rf_mcldl))
replace tp_nfdm = tp_nfdm*(1.025^(mcsbp-rf_mcsbp))
replace tp_nfdm = tp_nfdm*(1.20^(lsi-rf_lsi))
replace tp_fLC = tp_fLC*(13.12^(lsi-rf_lsi))
replace tp_fCC = tp_fCC*(1.24^(lsi-rf_lsi))
replace tp_fCOPD = tp_fCOPD*(13.12^(lsi-rf_lsi))
foreach var of varlist tp_nfHS tp_fLC-tp_fOTH {
gen `var'_dm=`var'
}
replace tp_d_cvd = 3*(tp_fCHD+tp_fCBD+tp_fLC+tp_fCC+tp_fCOPD+tp_fOTH)
gen ratesum_he = 0
foreach var of varlist tp_nfMI-tp_fOTH {
replace ratesum_he = ratesum_he+`var'
}
gen tpsum_he = 1-exp(-ratesum_he*0.1)
foreach var of varlist tp_nfMI-tp_fOTH {
replace `var' = tpsum_he*`var'/ratesum_he
}
gen ratesum_dm = 0
foreach var of varlist tp_nfMI_dm-tp_fOTH_dm {
replace ratesum_dm = ratesum_dm+`var'
}
gen tpsum_dm = 1-exp(-ratesum_dm*0.1)
foreach var of varlist tp_nfMI_dm-tp_fOTH_dm {
replace `var' = tpsum_dm*`var'/ratesum_dm
}
replace tp_d_cvd = 1-exp(-tp_d_cvd*0.1)
if `DIA'==. {
gen double HE_S = 1-rf_dmp if age == `AGE'
gen double DM_S = rf_dmp if age == `AGE'
}
if `DIA'==0 {
gen double HE_S = 1 if age == `AGE'
gen double DM_S = 0 if age == `AGE'
}
if `DIA'==1 {
gen double HE_S = 0 if age == `AGE'
gen double DM_S = 1 if age == `AGE'
}
gen double CV_S = 0 if age == `AGE'
gen double DT_S = 0 if age == `AGE'
gen double MICHD = .
gen double STCBD = .
gen double HE_E = .
gen double DM_E = .
gen double CV_E = .
gen double DT_E = .
replace MICHD = (HE_S*(tp_nfMI+tp_fCHD)) + (DM_S*(tp_nfMI_dm+tp_fCHD_dm)) if age == `AGE'
replace STCBD = (HE_S*(tp_nfIS+tp_nfHS+tp_fCBD)) + (DM_S*(tp_nfIS_dm+tp_nfHS_dm+tp_fCBD_dm)) if age == `AGE'
replace HE_E = HE_S-(HE_S*(tp_nfMI+tp_nfIS+tp_nfHS+tp_nfdm+tp_fCHD+tp_fCBD+tp_fLC+tp_fCC+tp_fCOPD+tp_fOTH)) if age == `AGE'
replace DM_E = DM_S+(HE_S*tp_nfdm)-(DM_S*(tp_nfMI_dm+tp_nfIS_dm+tp_nfHS_dm+tp_fCHD_dm+tp_fCBD_dm+tp_fLC_dm+tp_fCC_dm+tp_fCOPD_dm+tp_fOTH_dm)) if age == `AGE'
replace CV_E = CV_S+(HE_S*(tp_nfMI+tp_nfIS+tp_nfHS))+(DM_S*(tp_nfMI_dm+tp_nfIS_dm+tp_nfHS_dm))-(CV_S*tp_d_cvd) if age == `AGE'
replace DT_E = DT_S+(HE_S*(tp_fCHD+tp_fCBD+tp_fLC+tp_fCC+tp_fCOPD+tp_fOTH))+(DM_S*(tp_fCHD_dm+tp_fCBD_dm+tp_fLC_dm+tp_fCC_dm+tp_fCOPD_dm+tp_fOTH_dm))+(CV_S*tp_d_cvd) if age == `AGE'
local a = (`AGE'*10)+2
forval i = `a'/1000 {
replace HE_S = HE_E[_n-1] if _n == `i'
replace DM_S = DM_E[_n-1] if _n == `i'
replace CV_S = CV_E[_n-1] if _n == `i'
replace DT_S = DT_E[_n-1] if _n == `i'
replace MICHD = (HE_S*(tp_nfMI+tp_fCHD)) + (DM_S*(tp_nfMI_dm+tp_fCHD_dm)) if _n == `i'
replace STCBD = (HE_S*(tp_nfIS+tp_nfHS+tp_fCBD)) + (DM_S*(tp_nfIS_dm+tp_nfHS_dm+tp_fCBD_dm)) if _n == `i'
replace HE_E = HE_S-(HE_S*(tp_nfMI+tp_nfIS+tp_nfHS+tp_nfdm+tp_fCHD+tp_fCBD+tp_fLC+tp_fCC+tp_fCOPD+tp_fOTH)) if _n == `i'
replace DM_E = DM_S+(HE_S*tp_nfdm)-(DM_S*(tp_nfMI_dm+tp_nfIS_dm+tp_nfHS_dm+tp_fCHD_dm+tp_fCBD_dm+tp_fLC_dm+tp_fCC_dm+tp_fCOPD_dm+tp_fOTH_dm)) if _n == `i'
replace CV_E = CV_S+(HE_S*(tp_nfMI+tp_nfIS+tp_nfHS))+(DM_S*(tp_nfMI_dm+tp_nfIS_dm+tp_nfHS_dm))-(CV_S*tp_d_cvd) if _n == `i'
replace DT_E = DT_S+(HE_S*(tp_fCHD+tp_fCBD+tp_fLC+tp_fCC+tp_fCOPD+tp_fOTH))+(DM_S*(tp_fCHD_dm+tp_fCBD_dm+tp_fLC_dm+tp_fCC_dm+tp_fCOPD_dm+tp_fOTH_dm))+(CV_S*tp_d_cvd) if _n == `i'
}
gen PY = 0.1*(HE_E+CV_E+DM_E+(0.5*((HE_S*(tp_fCHD+tp_fCBD+tp_fLC+tp_fCC+tp_fCOPD+tp_fOTH))+(DM_S*(tp_fCHD_dm+tp_fCBD_dm+tp_fLC_dm+tp_fCC_dm+tp_fCOPD_dm+tp_fOTH_dm))+(CV_S*tp_d_cvd))))
gen TPY =.
forval i = 1/1000 {
su PY if _n>=`i'
replace TPY = r(sum) if _n==`i'
}
gen LE = TPY/(HE_S+DM_S+CV_S)
gen LTriskCHD = sum(MICHD)
gen LTriskCBD = sum(STCBD)
local b = (`AGE'*10)+1
mat A = (LE[`b']+`AGE',100*LTriskCHD[1000],100*LTriskCBD[1000],100*(LTriskCHD[1000]+LTriskCBD[1000]))
mat colnames A = LE LTRCHD LTRCBD LTRCVD
return matrix ltrisk_mat = A
return local LE = LE[`b']+`AGE'
return local LTRCVD = 100*(LTriskCHD[1000]+LTriskCBD[1000])
}
end
}

