# CraterClusterTools

## Introduction
This program is a set of tools to be used for calculating important characteristics of Crater Clusters on Mars. It was developed in a UROP research internship at Imperial College London in the Summer of 2020.

## Technologies
Python 3

## Requirements
### Modules:
Pandas 1.0.4

Numpy 1.18.5

Matplotlib 3.2.2

Jupyter

## Setup:
To install:
```
python setup.py install --user
```
Then change the file destinations 'main_list' and 'parameters_list' in parameters.py to the desired output locations.
You can test the script on the two example sheets in the repository, they are in the format that the script expects.

## Usage:
To calculate the parameters of a new cluster, run the tools.parameters.py script. It has a verbose option to show a plot of the cluster and print out the parameters, as well as a save option to write the results into a log file.

To plot the results, use the jupyter notebook. It is currently set to save all plots as .png files.

## Inspiration
The program is based on previous work by Ingrid Daubar and Eric Newland.
Some of the code is adapted from Michael Imelfort and the original can be found at https://github.com/minillinim/ellipsoid/blob/master/
