import CraterTools as ct
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mp
from matplotlib.patches import Ellipse
import numpy as np
import math as mt
#Input: Raw data from ArcGIS as an Excel file with HiRiseID as name
#Input: lat and lon from HiRise webpage as centre latitude and longitude

cluster_file = input('Cluster excel file:') #Input of excel file
ClusterData = pd.read_excel(cluster_file) #creating the dataframe for the cluster
latc = float(input('central latitude:'))
lonc = float(input('central longitude:'))
#Finding HiRise ID of the Cluster
input_list = cluster_file.split('.')
to_split = input_list[0]
input_list = to_split.split('/')
HiRiseID = input_list[-1]

#Number of craters in cluster:
crater_no = ClusterData['crater_no'].max()
ClusterData['Diam_m'] = ClusterData['Diam_km'].apply(lambda x: ct.round_sig(x*1000, sig=3) ) #converting diaeter to meters and rounding

#Calculating effective diameter:
d_effective = ct.d_eff(ClusterData)
print('effective diameter: ', d_effective)
#Finding largest crater, number of craters larger than D/2 and F value:
largest, N, F = ct.F_value(ClusterData)
print('largest crater: ', largest)
print('N > D/2: ', N)
print('F value: ', F)


#Calculating dispersion:
if crater_no >3:
    disp = ct.dispersion(ClusterData)
    print('dispersion: ', disp)

#Converting from degrees to metres for best fit ellipse calculations and plotting:
Rmars = 3390000 #radius of Mars in metres
ClusterData_copy = ClusterData.copy() #do conversion on a copy to avoid overwriting original coordinates
ClusterData_copy['x_coord'] = ClusterData_copy['x_coord'].apply(lambda a:(a - latc)*Rmars*(np.pi/180)) #converting coordinates from degrees to metres
ClusterData_copy['y_coord'] = ClusterData_copy['y_coord'].apply(lambda a:(a - lonc)*Rmars*(np.pi/180)*mt.sin(mt.radians(90 - a)))

#Calculating bestFit ellipse and plotting the Cluster:
if crater_no <=5:
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111)
    ax.scatter(ClusterData_copy['x_coord'], ClusterData_copy['y_coord'], color = 'k', marker = '.') #plotting crater locations
    ax.set_title('Cluster of ' + HiRiseID)
    plt.show()
else: #Still need to add ellipse plot!
    centre , radii, rotation_matrix, rotation_angle = ct.BestFitEllipse(ClusterData_copy, latc, lonc)
    ellipse = Ellipse(centre, 2*radii[0], 2*radii[1], rotation_angle, fill = False, color = 'r')
    #fig, ax = ct.plotellipse(centre, radii, rotation_matrix)
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111)
    ax.scatter(ClusterData_copy['x_coord'], ClusterData_copy['y_coord'],marker = '.', color = 'k') #plotting crater locations using the converted coordinates
    ax.add_patch(ellipse)
    ax.set_title('Cluster of ' + HiRiseID)
    plt.show()

#Adding the new Cluster to existing Main sheet and data to data sheet:
df_new = ClusterData.copy() #create copy to format
#creating Multiindex and formatting to important data only
df_new.drop(['Diam_km', 'FID', 'tag', 'D_cubed'], axis = 1, inplace=True, errors= 'ignore') #dropping unnecessary data
df_new['HiRiseID'] = HiRiseID #adding HiRise ID to all craters
df_new.set_index(['HiRiseID', 'crater_no'], inplace = True) #create the Multiindex
#saving the Multiindex in the same file for further use:
df_new.to_excel(HiRiseID + 'formatted.xlsx')
df_main = pd.read_excel('C:/Users/jae4518/OneDrive - Imperial College London/HiRise_Images_Clusters/ClustersDataSheet/MainSheet.xlsx', index_col=[0, 1])
main = pd.concat([df_main, df_new])
main.to_excel('MainSheet.xlsx') #saving the new version

#creating parameter dictionary:
new_cluster = {'HiRise_ID': HiRiseID, 'Number_Craters': crater_no, 'd_eff': d_effective, 'd_max': largest,
'Number>D/2': N, 'F_value': F, 'Dispersion': disp,
'central_latitude': latc, 'central_longitude': lonc, 'R1': radii[0], 'R2': radii[1]}
#reading in Paramaters sheet
df_parameters = pd.read_excel('C:/Users/jae4518/OneDrive - Imperial College London/HiRise_Images_Clusters/ClustersDataSheet/NewClustersParameters.xlsx')
#adding the new values to the list:
df_parameters = df_parameters.append(new_cluster)
df_parameters.to_excel('C:/Users/jae4518/OneDrive - Imperial College London/HiRise_Images_Clusters/ClustersDataSheet/NewClustersParameters.xlsx') #saving the updated version
