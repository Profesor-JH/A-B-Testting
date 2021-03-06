import os
os.chdir("C:/Users/hp/Documents")

import numpy as np 
import pandas as pd

import warnings
warnings.filterwarnings('ignore')
pd.set_option('max_column', None)


data1= pd.read_csv("AdSmart.csv", na_values=['?', None])



Data Cleaning
session_counts = data1['auction_id'].value_counts(ascending=False)
session_counts
multi_users = session_counts[session_counts > 1].count()

print(f'There are {multi_users} users that appear multiple times in the dataset')



users_to_drop = session_counts[session_counts > 1].index

data1 = data1[~data1['auction_id'].isin(users_to_drop)]
print(f'The updated dataset now has {data1.shape[0]} entries')



def missing_values_table(df):
    # Total missing values
    mis_val = df.isnull().sum()

    # Percentage of missing values
    mis_val_percent = 100 * df.isnull().sum() / len(df)

    # dtype of missing values
    mis_val_dtype = df.dtypes

    # Make a table with the results
    mis_val_table = pd.concat([mis_val, mis_val_percent, mis_val_dtype], axis=1)

    # Rename the columns
    mis_val_table_ren_columns = mis_val_table.rename(
    columns = {0 : 'Missing Values', 1 : '% of Total Values', 2: 'Dtype'})

    # Sort the table by percentage of missing descending
    mis_val_table_ren_columns = mis_val_table_ren_columns[
        mis_val_table_ren_columns.iloc[:,1] != 0].sort_values(
    '% of Total Values', ascending=False).round(1)

    # Print some summary information
    print ("Your selected dataframe has " + str(df.shape[1]) + " columns.\n"      
        "There are " + str(mis_val_table_ren_columns.shape[0]) +
          " columns that have missing values.")

    # Return the dataframe with missing information
    return mis_val_table_ren_columns





data1["yes"].value_counts()
data1["no"].value_counts()




# To make sure all the control group are seeing Questionnaire 

pd.crosstab(data1['experiment'], data1['yes'])



Let's compute the dataframe which contains only those who said yes and those who said no, we are not interested about those who didn't take a part of the questionnaire.


sample1 = data1[data1['yes'] == 1]

sample2 = data1[data1['no'] == 1]

compl_1 = pd.concat([sample1, sample2], axis=0)
#compl_1.reset_index(drop=True, inplace=True)


sample2['brand_Lux'] = np.where(sample2['no'] == 1, 2, 0)
sample2.head()

sample1['brand_Lux'] = np.where(sample1['yes'] == 1, 1, 0)
sample1.head()



result = sample1.append(sample2)



##Graphical analysis
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns


plt.figure(figsize=(8,6))

sns.barplot(x=result['experiment'], y=result['brand_Lux'], ci=False)

plt.ylim(0,1)
plt.title('brand_Lux rate by group', pad=20)
plt.xlabel('experiment', labelpad=15)
plt.ylabel('brand_Lux (proportion)', labelpad=15);



def plot_count(df:pd.DataFrame, column:str) -> None:
    plt.figure(figsize=(12, 7))
    sns.countplot(data=df, x=column)
    plt.title(f'Distribution of {column}', size=20, fontweight='bold')
    plt.show()



def plot_hist(df:pd.DataFrame, column:str, color:str)->None:
    plt.figure(figsize=(9, 7))
    sns.displot(data=df, x=column, color=color, kde=True, height=7, aspect=2)
    plt.title(f'Distribution of {column}', size=20, fontweight='bold')
    plt.show()
    
    
    
    
#histogramme
data1_clean1 = result.drop(['auction_id','experiment', 'date', 'device_make','browser','yes','no','brand_Lux'], axis=1)



data_scal = (data1_clean1-data1_clean1.min())/(data1_clean1.max()-data1_clean1.min())
# apply normalization techniques
for column in data_scal.columns:
    data_scal[column] = (data_scal[column] -
                           data_scal[column].mean()) / data_scal[column].std()
                           
                           
 plot_hist(df, 'column', 'color') 
 
 
 
 
 def plot_box_multi(df:pd.DataFrame, x_col:str, y_col:str, title:str) -> None:
    plt.figure(figsize=(12, 7))
    sns.boxplot(data = df, x=x_col, y=y_col)
    plt.title(title, size=20)
    plt.xticks(rotation=75, fontsize=14)
    plt.yticks( fontsize=14)
    plt.show()
                           
                           

####Sampling

import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.stats.api as sms
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
from math import ceil
import scipy.stats as stats
from math import ceil



### Sample Size


effect_size = sms.proportion_effectsize(0.13, 0.15)    # Calculating effect size based on our expected rates

required_n = sms.NormalIndPower().solve_power(
    effect_size, 
    power=0.15, 
    alpha=0.05, 
    ratio=1
    )                                                  # Calculating sample size needed

required_n = ceil(required_n)                          # Rounding up to next whole number                          

print(required_n)





##Compute now
control_sample = result[result['experiment'] == 'control'].sample(n=required_n, random_state=22)
treatment_sample = result[result['experiment'] == 'exposed'].sample(n=required_n, random_state=22)

ab_test = pd.concat([control_sample, treatment_sample], axis=0)
ab_test.reset_index(drop=True, inplace=True)




#Sequential Agorithm testing

from statsmodels.stats.proportion import proportions_ztest, proportion_confint

control_results = ab_test[ab_test['experiment'] == 'control']['brand_Lux']
treatment_results = ab_test[ab_test['experiment'] == 'exposed']['brand_Lux']


## A/B Testing

n_con = control_results.count()
n_treat = treatment_results.count()
successes = [control_results.sum(), treatment_results.sum()]
nobs = [n_con, n_treat]

z_stat, pval = proportions_ztest(successes, nobs=nobs)
(lower_con, lower_treat), (upper_con, upper_treat) = proportion_confint(successes, nobs=nobs, alpha=0.05)

print(f'z statistic: {z_stat:.2f}')
print(f'p-value: {pval:.3f}')
print(f'ci 95% for control group: [{lower_con:.3f}, {upper_con:.3f}]')
print(f'ci 95% for treatment group: [{lower_treat:.3f}, {upper_treat:.3f}]')

