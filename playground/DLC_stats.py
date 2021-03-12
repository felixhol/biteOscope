'''
author: Felix Hol
date: 2021 Mar 12
content: summary stats of DeepLabCut data
'''

# import matplotlib as mpl
# import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import numpy as np
import os
from tqdm import tnrange, tqdm
import glob
import math

dataFiles = glob.glob('/home/felix/biteData/P3/reID2/*reID.h5')
saveDir = '/home/felix/biteData/P3/indData/'

print('processing: ' + str(len(dataFiles)) + ' files.')
print(dataFiles)

minEngInc = 1.5
minEngW = 37
minEngTime = 200
maxMinW = 35
bellyWindow = 50

for dataFile in dataFiles:
    D = pd.read_hdf(dataFile)
    scorer=D.columns.get_level_values(0)[0]
    expt = os.path.splitext(os.path.basename(dataFile))[0]
    #### add individual level metrics to DCL dataframe:
    for ind in tqdm(D.columns.get_level_values(1).unique()):
        D[scorer, ind, 'metrics', 'distance'] = np.linalg.norm(
            [D[scorer][ind]['thorax'].x.diff(), D[scorer][ind]['thorax'].y.diff()], axis=0)
        D[scorer, ind, 'metrics', 'bellyW'] = np.linalg.norm(
            [D[scorer][ind]['abdomenL'].x - D[scorer][ind]['abdomenR'].x,
             D[scorer][ind]['abdomenL'].y - D[scorer][ind]['abdomenR'].y], axis=0)
    ####make new dataframe with summary stats per individual
    indData = pd.DataFrame(columns=['experiment', 'infected', 'ID', 'totDist', 'totTime', 'meanSpeed',
                                'activeTime', 'bellyInc', 'bellyMax09', 'bellyMin01', 'engorged'])
    for ind in tqdm(D.columns.get_level_values(1).unique()):
        D[scorer, ind, 'metrics', 'bellyWr'] = D[scorer][ind]['metrics']['bellyW'].rolling(bellyWindow).mean()
        indData.loc[ind, 'experiment'] = expt
        indData.loc[ind, 'ID'] = ind
        indData.loc[ind, 'totDist'] = D[scorer][ind]['metrics'].distance.sum()
        indData.loc[ind, 'totTime'] = len(D.loc[D[scorer][ind]['thorax'].x > 0])
        if len(D.loc[D[scorer][ind]['thorax'].x > 0]) > minEngTime + 1:
            startI = D[scorer][ind]['metrics'].bellyWr.first_valid_index()
            indData.loc[ind, 'bellyInc'] = D[scorer][ind]['metrics'].bellyWr.quantile(.8) / D[scorer][ind]['metrics'].bellyWr[startI : startI + minEngTime].quantile(.1)
            indData.loc[ind, 'bellyMax09'] = D[scorer][ind]['metrics'].bellyWr.quantile(.9)
            indData.loc[ind, 'bellyMin01'] = D[scorer][ind]['metrics'].bellyWr[startI : startI + minEngTime].quantile(.1)
        else:
            indData.loc[ind, 'bellyInc'] = D[scorer][ind]['metrics'].bellyW.quantile(.8) / D[scorer][ind]['metrics'].bellyW.quantile(.1)
            indData.loc[ind, 'bellyMax09'] = D[scorer][ind]['metrics'].bellyW.quantile(.9)
            indData.loc[ind, 'bellyMin01'] = D[scorer][ind]['metrics'].bellyW.quantile(.1)
        if 'denv' in expt:
            indData.loc[ind, 'infected'] = 1
        elif 'ctrl' in expt:
            indData.loc[ind, 'infected'] = 0

    indData['meanSpeed'] = indData.totDist / indData.totTime
    indData['engorged'] = 0
    indData.loc[(indData['bellyInc'] > minEngInc) & (indData['bellyMax09'] > minEngW)
                & (indData['bellyMin01'] < maxMinW) & (indData['totTime'] > minEngTime), 'engorged'] = 1
    newNameDLC = dataFile[:-3] + '_metrics.h5'
    D.to_hdf(newNameDLC, key="df_with_missing", mode="w")
    newNameInd = saveDir + expt[:20] + '_indData.pkl'
    indData.to_pickle(newNameInd)
