import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import math as mt
from numpy import linalg
from math import floor, log10
"""
Tools used to format data of Crater Clusters and calculate the parameters needed.
All functions assume a Pandas dataframe as input for the cluster data.
It is set up to work on Mars, using its average radius in the dispersion function.
"""

#Calculating effective diameter from a pandas database:
#Must loop over single entries if done for a Multiindex of several clusters
def d_eff(ClusterData, diameter = 'Diam_m'):
    '''
    Function to calculate the effective diameter of a cluster.
    d_effective = (sum(d_crater^3))^1/3

    :param ClusterData: Dataframe containing the craters
    :type ClusterData: pandas datafram
    :param diameter: name of the column in dataframe giving the diameter in metres
    :type diameter: str
    '''
    df = ClusterData.copy() #work copy of the data to not alter the original file
    df['D_cubed'] = df[diameter].apply(lambda x: x**3)
    d_effective = round((df['D_cubed'].sum())**(1/3), 3) #calculating the effective diameter
    return d_effective

#Calculating F value. Ratio of craters of larger diameter than half the diameter of the largest crater in cluster_file
#gives d_max, number of craters larger than D/2 and F-value
def F_value(ClusterData, diameter = 'Diam_m'):
    '''
    This function will find the diameter of the largest crater in the cluster, the number of craters that are larger than half the largest and the fraction of how many those are.
    :param ClusterData: Dataframe containing the craters
    :type ClusterData: pandas datafram
    :param diameter: name of the column in dataframe giving the diameter in metres
    :type diameter: str
    '''
    #ClusterData is the pandas Database of all craters in the cluster
    #diameter is the name of the column giving the Diameter in metre
    df = ClusterData.copy() #create a work copy
    D = df[diameter].max() #diameter of largest crater in cluster
    largerDhalf = df[diameter] >=(D/2) #finding which craters are larger than D/2
    N = 0
    total = 0
    for crater in largerDhalf:
        if crater == True:
            N += 1
            total += 1
        else: total +=1 #counting amount of larger craters
    F = N/total #calculating F values
    return D, N, F

#Calculating the Dispersion of a cluster as the standard deviation of the separation of all possible crater combinations:
def dispersion(ClusterData, x = 'x_coord', y = 'y_coord'):
    '''
    This function calculates the dispersion of a cluster from a pandas dataframe giving the x and y coordinates of .
    The dispersion is defined as the standard deviation of the distance between all possible crater pairs.
    This method gives meaningul results for clusters with more than 3 craters in a cluster.
    It is using the radius of Mars to convert from lat/lon data to metres.

    :param ClusterData: Dataframe containing all craters in clusters
    :type ClusterData: pandas dataframe
    :param x: column name giving the longitude, defaults to 'x_coord'
    :type x: str
    :param y: column name giving the latitude, defaults to 'y_coord'
    :type y: str
    '''
    Rmars = 3390000 #radius of Mars in metres
    #x and y are the names of the column in ClusterData denoting the x and y coordinates respectively
    #Assumes that x and y are in degrees still!
    df = ClusterData.copy() #create work copy of database
    coord_array = np.array(df[[x, y]]) #create array of xy coordinates for craters in cluster
    sep_list = []
    for n in range(0, len(coord_array)): #iterating over all craters for separation calculation
        for m in range(1, len(coord_array)): #calculating seperation ((x2-x1)**2 + (y2 - y1)**2)**0.5 for all combinations
            dx= (coord_array[m,0] - coord_array[n,0]) *Rmars*(np.pi/180)*mt.sin(mt.radians(90 - ((coord_array[m,0]+ coord_array[n,0])/2))) #converting to metres based xy coordinates
            dy = (coord_array[m,1] - coord_array[n,1]) *Rmars*(np.pi/180)
            sep = (dx**2+ dy**2)**0.5
            sep_list.append(sep) #adding all separations to list
    dispersion = np.std(sep_list) #calculating dispersion as standard deviation
    return dispersion

def BestFitEllipse(ClusterData, tolerance=0.1, lat = 'x_coord', lon = 'y_coord'):
    '''
    adapted from Michael Imelfort at https://github.com/minillinim/ellipsoid/blob/master/ellipsoid.py
    This function will calculate the radii, centre point and rotation of the best fitting Ellipse around the cluster from a pandas dataframe.
    It is using a Bootstrap of 300 iterations to minimise the impact outliers have on the final Ellipse and the Kachiyan algorithm to find the minimum volume Ellipse for each sample.
    This method works for clusters larger than 5 craters.

    :param ClusterData: Dataframe containing all craters in clusters
    :type ClusterData: pandas dataframe
    :param tolerance: gives the tolerance for the Kachiyan algorithm, defaults to 0.1
    :type tolerance: float
    :param x: column name giving the longitude, defaults to 'x_coord'
    :type x: str
    :param y: column name giving the latitude, defaults to 'y_coord'
    :type y: str
    '''
#Output:radii, rotation and centre of ellipse
    df = ClusterData.copy() #creating a workable copy of the data
    coord_array = np.array(df[[lat, lon]]) #create array of coordinates
    #iterating over the coordinates to find best fitting ellipse
    #using a Bootstrap (300 iterations) to minimise impact of outliers
    counter = 0 #counter for the Bootstrap Samples
    #setting up lists for results of samples for average ellipse later:
    Rminor = []
    Rmajor = []
    rotation = []
    centrex = []
    centrey = []
    rot1 = []
    rot2 = []
    rot3 = []
    rot4 = []
    while counter <= 300:
            P = np.array(random.choices(coord_array, k = len(coord_array))) #choosing the sample for current iteration
            counter +=1
            #running the Kachiyan Algorithm over the sample:
            (N, d) = np.shape(P)
            d = float(d)

            # Creating a working array
            Q = np.vstack([np.copy(P.T), np.ones(N)])
            QT = Q.T

            # initializations
            err = 1.0 + tolerance
            u = (1.0 / N) * np.ones(N)

            # Khachiyan Algorithm
            while err > tolerance:
                V = np.dot(Q, np.dot(np.diag(u), QT))
                M = np.diag(np.dot(QT , np.dot(linalg.inv(V), Q)))    # M the diagonal vector of an NxN matrix
                j = np.argmax(M)
                maximum = M[j]
                step_size = (maximum - d - 1.0) / ((d + 1.0) * (maximum - 1.0))
                new_u = (1.0 - step_size) * u
                new_u[j] += step_size
                err = np.linalg.norm(new_u - u)
                u = new_u

            # center of the ellipse
            center = np.dot(P.T, u)
            centrex.append(center[0])
            centrey.append(center[1])
            # the A matrix for the ellipse
            A = linalg.inv(
                           np.dot(P.T, np.dot(np.diag(u), P)) -
                           np.array([[a * b for b in center] for a in center])
                           ) / d

            # Get radii and rotation matrix
            U, s, rotation = linalg.svd(A)
            radii = 1.0/np.sqrt(s)
            Rminor.append(radii[0])
            Rmajor.append(radii[1])
            rot1.append(rotation[0,0]) #mapping the rotation output to the right place to create a standard rotation matrix [0,1] [1,1] [0,0] [1,0]
            rot2.append(rotation[0,1])
            rot3.append(rotation[1,1])
            rot4.append(rotation[1,0])
            av_rot1 = np.mean(rot1)
            av_rot2 = np.mean(rot2)
            av_rot3 = np.mean(rot3)
            av_rot4 = np.mean(rot4)
    #calculate mean of parameters to find average best fit ellipse:
    av_center = np.array([np.mean(centrex), np.mean(centrey)])
    av_radii = np.array([np.mean(Rminor), np.mean(Rmajor)])
    av_rotation = np.array([[av_rot1, av_rot2], [av_rot3, av_rot4]])
    print(av_rotation)
    #converting the rotation matrix to angle:
    if av_rotation[1,0] > 0:
        alpha = mt.acos(av_rotation[0,0]) *(180/np.pi)
    else:
        alpha = - mt.acos(av_rotation[0,0]) *(180/np.pi)
    return (av_center, av_radii, av_rotation, alpha) #return both rotation matrix and angle
