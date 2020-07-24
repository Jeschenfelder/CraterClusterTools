import ClusterTools as ct
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mp
from matplotlib.patches import Ellipse
import numpy as np
import math as mt
import sys
import argparse
'''
This program will calculate the main parameters for a Crater Cluster and add them to an excel spread sheet.
It will also add the list of craters in a cluster to a main sheet of all measured clusters.
The program takes as input the path to the cluster's data and the lat lon coordinates of the centre of the used image in degrees.
The program assumes that the cluster's data is named after the HiRise ID of the image used and will use this as a label for the data.
'''

my_parser = argparse.ArgumentParser(prog = 'ClusterParameters', description='Calculate Cluster Parameters and save data to main list and parameter sheet')
my_parser.add_argument('Path',nargs = str, help = 'Excel Sheet of raw Cluster Data, named after the HiRiseID of image')
my_parser.add_argument('latitude', nargs= float, help = 'central latitude of image')
my_parser.add_argument('longitude', nargs = float, help = 'central longitude of image')
my_parser.add_argument('-v' , '--verbose', help = 'will print the outputs and plot the cluster')
args = my_parser.parse_args()
cluster_file = args.Path
latc = args.latitude
lonc = args.longitude

#print and plot function for verbose:
def vprint(output):
    if args.verbose:
        print(output)

#checking the central lat/long:
if latc > 180 or latc < -180:
    raise ValueError('central latitude is outside allowed range')
if lonc > 180:
    lonc = lonc -360
elif lonc >360:
    raise ValueError('central longitude is outside allowed range')

ClusterData = pd.read_excel(cluster_file) #creating the dataframe for the cluster
#Finding HiRise ID of the Cluster
input_list = cluster_file.split('.')
to_split = input_list[0]
input_list = to_split.split('/')
HiRiseID = input_list[-1]


#Number of craters in cluster:
crater_no = len(ClusterData.index)
ClusterData['Diam_m'] = ClusterData['Diam_km'].apply(lambda x: round(x*1000, 2) ) #converting diameter to meters and rounding

#Calculating effective diameter:
d_effective = ct.d_eff(ClusterData)
vprint('effective diameter: ', d_effective)
#Finding largest crater, number of craters larger than D/2 and F value:
largest, N, F = ct.F_value(ClusterData)
vprint('largest crater: ', largest)
vprint('N > D/2: ', N)
vprint('F value: ', F)

#creating parameter dictionary:
new_cluster = {'HiRise_ID': HiRiseID, 'Number_Craters': crater_no, 'd_eff': d_effective, 'd_max': largest,'N>D/2': N,
 'F_value': F, 'central_latitude': latc, 'central_longitude': lonc}
#Calculating dispersion:
if crater_no >3:
    disp = ct.dispersion(ClusterData)
    vprint('dispersion: ', disp)
    new_cluster['Dispersion'] = disp #adding to dicitonary

#Converting from degrees to metres for best fit ellipse calculations and plotting:
Rmars = 3390000 #radius of Mars in metres
ClusterData_copy = ClusterData.copy() #do conversion on a copy to avoid overwriting original coordinates
ClusterData_copy['x_coord'] = ClusterData_copy['x_coord'].apply(lambda a:(a - latc)*Rmars*(np.pi/180)) #converting coordinates from degrees to metres
ClusterData_copy['y_coord'] = ClusterData_copy['y_coord'].apply(lambda a:(a - lonc)*Rmars*(np.pi/180)*mt.sin(mt.radians(90 - a)))

#Calclulating best Fit ellipse:
if crater_no > 5:
    centre , radii, rotation_matrix, rotation_angle = ct.BestFitEllipse(ClusterData_copy, latc, lonc)

if args.verbose:
    #Starting the Plot:
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, aspect = 'equal')
    ax.scatter(ClusterData_copy['x_coord'], ClusterData_copy['y_coord'],marker = '.', color = 'k') #plotting crater locations using the converted coordinates
    ax.set_title('Cluster of ' + HiRiseID)
    #Calculating bestFit ellipse and plotting the Cluster:
    if crater_no <=5:
        ax.scatter(ClusterData_copy['x_coord'], ClusterData_copy['y_coord'], color = 'k', marker = '.') #plotting crater locations
        ax.set_title('Cluster of ' + HiRiseID)

    else: #Still need to add ellipse plot!
        ellipse1 = Ellipse(centre, 2*radii[0], 2*radii[1], rotation_angle, fill = False, color = 'r')
        ellipse2 = Ellipse(centre, 2*radii[1], 2*radii[0], rotation_angle, fill = False, color = 'y') #plotting both possible ellipse orientations
        #fig, ax = ct.plotellipse(centre, radii, rotation_matrix)
        ax.add_patch(ellipse1)
        ax.add_patch(ellipse2)
        new_cluster['R1'] = radii[0] #adding to the dictionary
        new_cluster['R2'] = radii[1]
    plt.show()

#the output files:
main_list = 'C:/Users/jae4518/OneDrive - Imperial College London/HiRise_Images_Clusters/ClustersDataSheet/MainSheet.xlsx'
parameters_list = 'C:/Users/jae4518/OneDrive - Imperial College London/HiRise_Images_Clusters/ClustersDataSheet/NewClustersParameters.xlsx'

#Adding the new Cluster to existing Main sheet and data to data sheet:
df_new = ClusterData.copy() #create copy to format
#creating Multiindex and formatting to important data only
df_new.drop(['Diam_km', 'FID', 'tag', 'D_cubed'], axis = 1, inplace=True, errors= 'ignore') #dropping unnecessary data
df_new['HiRiseID'] = HiRiseID #adding HiRise ID to all craters
df_new.set_index(['HiRiseID', 'crater_no'], inplace = True) #create the Multiindex
#saving the Multiindex in the same file for further use:
df_new.to_excel(HiRiseID + 'formatted.xlsx')
df_main = pd.read_excel(main_list, index_col=[0, 1])
main = pd.concat([df_main, df_new])
main.to_excel('MainSheet.xlsx') #saving the new version


#reading in Paramaters sheet
df_parameters = pd.read_excel(parameters_list)
#adding the new values to the list:
df_parameters = df_parameters.append(new_cluster, ignore_index = True)
df_parameters.to_excel('C:/Users/jae4518/OneDrive - Imperial College London/HiRise_Images_Clusters/ClustersDataSheet/NewClustersParameters.xlsx') #saving the updated version
