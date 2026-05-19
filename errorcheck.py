def errorcheck(age_input, 
               ldl_input, 
               sbp_input, 
               lpa_input, 
               sma_input, 
               smo_input, 
               cig_input,
               ldl_lowering_input_p,
               ldl_lowering_input_a,
               ldl_target_input,
               sbp_lowering_input,
               sbp_target_input,
               smoke_input,
               quit_smoking_input):

    if (age_input < 10) | (age_input > 90):
        return "Error: Age must be between 10 and 90 years.", 400
    if ldl_input is not None:
        if (ldl_input < 0.5) | (ldl_input > 10):
            return "Error: LDL-C must be between 0.5 and 10 mmol/L.", 400
    if sbp_input is not None:
        if (sbp_input < 80) | (sbp_input > 250):
            return "Error: Systolic blood pressure must be between 80 and 250 mmHg.", 400
    if lpa_input is not None:
        if (lpa_input < 0.1) | (lpa_input > 1000):
            return "Error: Lp(a) must be between 0.1 and 2000 nmol/L.", 400
    if (smoke_input=="yes") | (quit_smoking_input is not None):
        if sma_input is None:
            return "Error: Please enter a smoking start age.", 400
    if sma_input is not None:
        if (sma_input < 10) | (sma_input > 90):
            return "Error: Age started smoking must be between 5 and 90 years.", 400
        if sma_input > age_input:
            return "Error: Age started smoking must be less than or equal to current age.", 400
    if cig_input is not None:
        if (cig_input < 0.1) | (cig_input > 200):
            return "Error: Number of cigarettes smoked daily must be a number between 0.1 and 200.", 400
    if smo_input is not None:
        if (smo_input < 10) | (smo_input > 90):
            return "Error: Age quit smoking must be between 5 and 90 years.", 400
        if smo_input > age_input:
            return "Error: Age quit smoking must be less than or equal to current age.", 400
        if sma_input > smo_input:
            return "Error: Age quit smoking must be greater than age started smoking.", 400
    if ldl_lowering_input_p is not None:
        if (ldl_lowering_input_p < 0.01) | (ldl_lowering_input_p > 0.99):
            return "Error: LDL-C lowering must be between 1 and 99%."
    if (ldl_lowering_input_a is not None) & (ldl_input is not None):
        if ldl_lowering_input_a > ldl_input:
            return "Error: LDL-C lowering cannot be greater than LDL-C.", 400
    if ldl_target_input is not None:
        if (ldl_target_input < 0.1) | (ldl_target_input > 4):
            return "Error: LDL-C target must be between 0.1 and 4 mmol/L."
    if (((ldl_lowering_input_p is not None) & (ldl_lowering_input_a is not None)) | ((ldl_lowering_input_p is not None) & (ldl_target_input is not None)) | ((ldl_lowering_input_a is not None) & (ldl_target_input is not None))):
        return "Error: Cannot have both LDL-C lowering and LDL-C target"
    if sbp_lowering_input is not None:
        if (sbp_lowering_input < 1) | (sbp_lowering_input > 60):
            return "Error: Sytolic blood pressure lowering must be between 1 and 60 mmHg."
    if sbp_target_input is not None:
        if (sbp_target_input < 120) | (sbp_target_input > 150):
            return "Error: SBP target must be between 120 and 150 mmHg."
    if (sbp_lowering_input is not None) & (sbp_target_input is not None):
        return "Error: Cannot have both Sytolic blood pressure lowering and Sytolic blood pressure target"
    
    return None
