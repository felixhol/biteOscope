'''
author: Felix Hol
date: 2021 Nov
content: cut individual DLC tracks into individual dataframes (including disconnected tracks labeled as same individual)
'''

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import numpy as np
import os
from tqdm import tnrange, tqdm
import glob
import math
#
# os.environ["DLClight"]="True"
# import deeplabcut
import warnings
warnings.filterwarnings("ignore")


hdfs = glob.glob('/Users/felix/Documents/mosquitoes/mosquitoData/P3/boxH5/*bx.h5')

minLen = 4
smoothLenXY = 2
smoothLenDist = 5
smoothLenBelly = 50
minEngInc = 1.5
minEngW = 37
minEngTime = 200
maxMinW = 35
extraLenEngorge = 250
movingThres = 2.5

### dt is a new dataframe with added column 'group' for each individual in which continuous stretches of a
### trajectory are assigned a number g which can be used to extract the trajectory

def addGroup(dt):
    for ind in dt.columns.get_level_values(1).unique():
        dt[scorer, ind, 'group', 'g'] = (dt[scorer][ind]['abdomenC'].x.isnull().cumsum()  + 1) * ~dt[scorer][ind]['abdomenC'].x.isnull()


def processTracks(dt, hdfName):
    print('processing: ' + hdfName)
    experiment = os.path.splitext(os.path.basename(hdfName))[0][0:20]
    trackData = pd.DataFrame(columns=['experiment', 'infected', 'ID', 'totDist', 'totDistSm', 'totTime', 'meanSpeed',
                                    'movingTime', 'movingFrac', 'bellyInc', 'bellyMax09', 'bellyMin01', 'engorged', 'timeToEngorge'])
    originalInd = dt.columns.get_level_values(1).unique().tolist()
    plt.figure(figsize=(30,10))

    for ind in tqdm(originalInd):
        plt.figure(figsize=(10,7))
        dm = dt.copy()
        individuals = originalInd.copy()
        individuals.remove(ind)
        dm.drop(individuals, axis=1, level=1, inplace = True)
        for gID in dm[scorer, ind].group.g.unique():
            if gID != 0 :
                ID = experiment + '_' + ind + '_' + str(gID)
                Dg = dm.loc[dm[scorer, ind, 'group'].g == gID]
                if len(Dg) > minLen:
                    Dg.drop('group', axis=1, level=2, inplace = True)
                    for bp in Dg.columns.get_level_values(2).unique():
                        Dg[scorer, ind, bp, 'xSm'] = Dg[scorer, ind, bp, 'x'].interpolate(limit = 2)
                        Dg[scorer, ind, bp, 'xSm'] = Dg[scorer, ind, bp, 'xSm'].rolling(smoothLenXY, min_periods=1).mean()
                        Dg[scorer, ind, bp, 'ySm'] = Dg[scorer, ind, bp, 'y'].interpolate(limit = 2)
                        Dg[scorer, ind, bp, 'ySm'] = Dg[scorer, ind, bp, 'ySm'].rolling(smoothLenXY, min_periods=1).mean()
                        Dg[scorer, ind, bp, 'distance'] = \
                        np.linalg.norm([Dg[scorer][ind][bp].xSm.diff(),
                                        Dg[scorer][ind][bp].ySm.diff()], axis=0)
                        Dg.replace([np.inf, -np.inf], np.nan, inplace=True)
                        Dg[scorer, ind, bp, 'distance'].interpolate(inplace = True)
                        if len(Dg) > smoothLenDist:
                            Dg[scorer, ind, bp, 'distanceSm'] = Dg[scorer, ind, bp, 'distance'].rolling(smoothLenDist, min_periods=1).mean()
                        else:
                            Dg[scorer, ind, bp, 'distanceSm'] = Dg[scorer, ind, bp, 'distance']
                    Dg[scorer, ind, 'abdomenC', 'bellyW'] = \
                    np.linalg.norm([Dg[scorer][ind]['abdomenL'].x - Dg[scorer][ind]['abdomenR'].x,
                                    Dg[scorer][ind]['abdomenL'].y - Dg[scorer][ind]['abdomenR'].y], axis=0)
                    if len(Dg) > smoothLenBelly:
                        Dg[scorer, ind, 'abdomenC', 'bellyWSm'] = \
                        np.linalg.norm([Dg[scorer][ind]['abdomenL'].x.rolling(smoothLenBelly, min_periods=1).mean() -
                                        Dg[scorer][ind]['abdomenR'].x.rolling(smoothLenBelly, min_periods=1).mean(),
                                        Dg[scorer][ind]['abdomenL'].y.rolling(smoothLenBelly, min_periods=1).mean() -
                                        Dg[scorer][ind]['abdomenR'].y.rolling(smoothLenBelly, min_periods=1).mean()],
                                       axis=0)
                        Dg[scorer, ind, 'abdomenC', 'bellyWSm'] = Dg[scorer, ind, 'abdomenC', 'bellyWSm'].rolling(smoothLenBelly, min_periods=1).mean()
                    else:
                        Dg[scorer, ind, 'abdomenC', 'bellyWSm'] = Dg[scorer, ind, 'abdomenC', 'bellyW']

                    Dg[scorer, ind, 'abdomenC', 'engorged'] = 0

                    if len(Dg.loc[Dg[scorer][ind]['abdomenC'].bellyW > 0]) > minEngTime:
                                startI = Dg[scorer][ind]['abdomenC'].bellyWSm.first_valid_index()
                                if ~np.isnan(startI):
                                    bellyMax08 = Dg[scorer][ind]['abdomenC'].bellyWSm.quantile(.8)
                                    bellyMax09 = Dg[scorer][ind]['abdomenC'].bellyWSm.quantile(.9)
                                    bellyMin01 = Dg[scorer][ind]['abdomenC'].bellyWSm.loc[startI : startI + minEngTime].quantile(.1)
                                    if bellyMax08 > minEngW and bellyMin01 < maxMinW:
                                        Dg[scorer, ind, 'abdomenC', 'engorged'] = Dg[scorer][ind]['abdomenC'].bellyWSm.where(Dg[scorer][ind]['abdomenC'].bellyWSm > bellyMax08) > 0
                                        Dg[scorer, ind, 'abdomenC', 'engorged'] = Dg[scorer, ind, 'abdomenC', 'engorged'].astype(int)
                                        timeToEngorge = Dg[scorer][ind]['abdomenC'].bellyWSm.where(Dg[scorer][ind]['abdomenC'].bellyWSm > bellyMax09).first_valid_index() - startI
                                        engorgeFrameNo = Dg[scorer][ind]['abdomenC'].bellyWSm.where(Dg[scorer][ind]['abdomenC'].bellyWSm > bellyMax09).first_valid_index()
                                        Dg = Dg.truncate(after = engorgeFrameNo + extraLenEngorge)
                                        plt.plot(Dg[scorer, ind, 'abdomenC', 'bellyWSm'].values, '-m')
                                    elif bellyMax08 > minEngW and bellyMin01 > maxMinW:
                                        Dg[scorer, ind, 'abdomenC', 'engorged'] = 2
                                        timeToEngorge = np.nan
                                        plt.plot(Dg[scorer, ind, 'abdomenC', 'bellyWSm'].values, '.-c')
                                    else:
                                        timeToEngorge = np.nan
                                        plt.plot(Dg[scorer, ind, 'abdomenC', 'bellyWSm'].values, '-k', alpha=0.75)
                    else:
                        bellyMax08 = Dg[scorer][ind]['abdomenC'].bellyWSm.quantile(.8)
                        bellyMax09 = Dg[scorer][ind]['abdomenC'].bellyWSm.quantile(.9)
                        bellyMin01 = Dg[scorer][ind]['abdomenC'].bellyWSm.quantile(.1)
                        timeToEngorge = np.nan


                    h5Name = hdfName[:-3] + '_' + ind + '_' + str(gID) + '.h5'
                    Dg.to_hdf(h5Name, key="df_with_missing", mode="w")
                    movingTime = len(Dg[scorer, ind, 'thorax'].loc[Dg[scorer, ind, 'thorax', 'distanceSm'] > movingThres])
                    trackData = trackData.append({'experiment': experiment,
                                                 'ID': ID,
                                                 'totDist': Dg[scorer, ind, 'thorax', 'distance'].sum(),
                                                 'totDistSm': Dg[scorer, ind, 'thorax', 'distanceSm'].sum(),
                                                 'totTime': len(Dg),
                                                  'bellyMax09': bellyMax09,
                                                  'bellyMin01': bellyMin01,
                                                  'engorged': Dg[scorer, ind, 'abdomenC', 'engorged'].max(),
                                                  'timeToEngorge': timeToEngorge,
                                                  'movingTime': movingTime,
                                                  'movingFrac': movingTime / len(Dg),
                                                 }, ignore_index=True)
        if ~dm[scorer, ind, 'abdomenC', 'x'].isnull().all():
            figName = hdfName[:-3] + '_' + ind + '_' + 'bellyPlot.pdf'
            plt.savefig(figName)

    if 'denv' in experiment:
        trackData['infected'] = 1
    elif 'ctrl' in experiment:
        trackData['infected'] = 0

    trackData.loc[trackData.bellyMin01 < 15].bellyMin01 = np.nan
    trackData['meanSpeed'] = trackData['totDist'] / trackData['totTime']
    trackData['bellyInc'] = trackData['bellyMax09'] / trackData['bellyMin01']
    trackData.to_hdf(hdfName[:-3] + '_trackData.h5', key="df_with_missing", mode="w")



for hdfFile in hdfs:
    print('processing: ' + hdfFile)
    dt = pd.read_hdf(hdfFile)
    scorer = dt.columns.get_level_values(0)[0]
    originalInd = dt.columns.get_level_values(1).unique().tolist()
    addGroup(dt)
    processTracks(dt, hdfFile)
