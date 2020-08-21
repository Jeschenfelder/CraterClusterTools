import pandas as pd
import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt
import math as mt
import functions as ct
import sklearn.metrics as sm

#importing dataframe (test on one for now):
df1 = pd.read_excel('C:/Users/jae4518/OneDrive - Imperial College London/HiRise_Images_Clusters/ClustersDataSheet/ESP_017425_2045formatted.xlsx', index_col=[0,1])
df2 = pd.read_excel('C:/Users/jae4518/OneDrive - Imperial College London/HiRise_Images_Clusters/ClustersDataSheet/ESP_050154_1750formatted.xlsx', index_col = [0,1])
#looping to fit a gamma curve:
def gamma_fit(df,max_iter = 100, tol = 0.05):
    disp, sep_array = ct.dispersion(df) #Calculating dispersion and separations for the cluster
    a_array = np.linspace(0.1, 2, 5)
    scale_array = np.linspace(0.1, 2, 5)
    iter = 0
    x = np.linspace(0,np.max(sep_array), len(sep_array))
    while iter < max_iter:
        grid_points = {}
        for a in a_array: #looping over the arrays of possible values
            for s in scale_array:
                print('S: ',s)
                loss = sm.mean_squared_error(sep_array,st.gamma.cdf(x,a,scale=s),multioutput='uniform_average')
                if loss <= tol:
                    return a, s, loss
                grid_points[loss] = [a,s]
        smallest = sorted(grid_points)[0]
        second = sorted(grid_points)[1]
        a_array = np.linspace(grid_points[smallest][0], grid_points[second][0], 5)
        scale_array = np.linspace(grid_points[smallest][1], grid_points[second][1], 5)
        iter +=1
        print(iter)
    return a,s,loss
disp, sep_array = ct.dispersion(df1)
x = np.linspace(0,np.max(sep_array), 100)
a,s,loss = gamma_fit(df1)
print(a,s, loss)
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(st.gamma.cdf(x,a =a , scale=s), label = 'Gamma distribution')
ax.hist(sep_array, 'auto', density=True, cumulative=True)
plt.show()
