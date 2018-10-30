import sys
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import patsy as pt
import pymc3 as pm
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from patsy import dmatrices
import statsmodels.discrete.discrete_model as sm


# Setup
plt.rcParams['figure.figsize'] = 14, 6
np.random.seed(0)
print('Running on PyMC3 v{}'.format(pm.__version__))

seed=314159

# Data
full_df = pd \
    .read_csv('datasets/processed_fitbit_df_r.csv') \
    .dropna()

X = full_df[['steps', 'mean_rate', 'sd_rate', 'dsp_lag', 
             'deep_sleep_prop']]

# patsy lets you use R-style formulas in models
fml = 'deep_sleep_prop ~ mean_rate + sd_rate + dsp_lag'

with pm.Model() as model_robust:
    family = pm.glm.families.StudentT()
    pm.GLM.from_formula(fml, X, family=family)
    trace_robust = pm.sample(20000, tune=5000, njobs=4, chains=4, 
                             step=pm.Metropolis())

print(pm.summary(trace_robust, 
                 varnames=model_robust.unobserved_RVs)[stats])


with pm.Model() as mdl2:
    pm.glm.GLM.from_formula(fml, X, 
      family=pm.glm.families.Normal())

# NUTS doesn't work with my currently version of joblib
with mdl2:
    trc2 = pm.sample(10000, tune=5000, njobs=4, chains=4, 
                    step=pm.Metropolis())

# Analysis
print(pm.summary(trc2, varnames=mdl2.unobserved_RVs)[stats])


plt.show()

stats = ['mean','hpd_2.5','hpd_97.5']
percentiles = [2.5, 50, 97.5]
print(pm.summary(trc2,  varnames=mdl2.unobserved_RVs)[stats])
print('mean_rate: ', np.percentile(trc2['mean_rate'], percentiles))
print('sd_rate: ', np.percentile(trc2['sd_rate'], percentiles))
print('dsp_lag: ', np.percentile(trc2['dsp_lag'], percentiles))

# read in the data & create matrices
sm_y, sm_X = dmatrices(fml, X, return_type = 'dataframe')
# sm
ols = sm.lm.OLS(sm_y, sm_X).fit()
print(ols.summary())
"""
                            OLS Regression Results                            
==============================================================================
Dep. Variable:        deep_sleep_prop   R-squared:                       0.101
Model:                            OLS   Adj. R-squared:                  0.087
Method:                 Least Squares   F-statistic:                     7.319
Date:                Sun, 21 Oct 2018   Prob (F-statistic):           0.000113
Time:                        22:27:32   Log-Likelihood:                 181.30
No. Observations:                 199   AIC:                            -354.6
Df Residuals:                     195   BIC:                            -341.4
Df Model:                           3                                         
Covariance Type:            nonrobust                                         
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
Intercept     -0.1176      0.108     -1.093      0.276      -0.330       0.095
mean_rate      0.0048      0.001      3.220      0.002       0.002       0.008
sd_rate       -0.0029      0.001     -2.000      0.047      -0.006   -4.07e-05
dsp_lag        0.2040      0.069      2.968      0.003       0.068       0.339
==============================================================================
Omnibus:                        1.957   Durbin-Watson:                   1.965
Prob(Omnibus):                  0.376   Jarque-Bera (JB):                2.034
Skew:                           0.223   Prob(JB):                        0.362
Kurtosis:                       2.786   Cond. No.                     1.25e+03
==============================================================================

Warnings:
[1] Standard Errors assume that the covariance matrix of 
the errors is correctly specified.
[2] The condition number is large, 1.25e+03. This might indicate that there are
strong multicollinearity or other numerical problems.
"""
