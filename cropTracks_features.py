'''
author: Felix Hol
date: 2019 Oct 24
content: code to track mosquitoes, several filtering parameters will need tweaking depending on imaging parameters.
'''

import numpy as np
# %matplotlib inline
# import matplotlib as mpl
# import matplotlib.pyplot as plt
import os
import itertools as it
import pandas as pd
from pandas import DataFrame, Series  # for convenience
import pims
import skimage
from skimage import data, io, util
from skimage.color import rgb2gray
from skimage.measure import label, regionprops
from skimage.segmentation import active_contour
from skimage.morphology import binary_dilation, erosion, dilation, opening, binary_closing, closing, white_tophat, remove_small_objects, disk, black_tophat, skeletonize, convex_hull_image
from scipy import ndimage as ndi
import scipy
import trackpy as tp
import pylab
import math
from joblib import Parallel, delayed
import multiprocessing
from datetime import datetime
from tqdm import tnrange, tqdm
import pickle
import glob
import cv2 as cv

#### set directories where to get images and where to store output, and specifics of experiment/analysis

dataDir = '/Users/felix/Documents/mosquitoes/mosquitoData/testImages/'
saveDir = '/Users/felix/biteOscope_clean/test/dump/'
mosDataName = 'test'
frames = pims.ImageSequence(dataDir+'/*.tiff', as_grey=True)
ROIwidth = 600   #### crop frames to this width
ROIheigth = 600   #### crop frames to this heigth
tracksPickle = saveDir + mosDataName + '_tracks.pkl'
minTrackLength = 5

def mosStatsAndCrop(tFull, p, ROIwidth, ROIheigth):
    os.mkdir(saveDir + mosDataName + 'crops_p' + str(p))
    frameWidth = 2048
    frameHeigth = 2048
    # ROIwidth = 550
    # ROIheigth = 550
    halfROIwidth = ROIwidth / 2
    halfROIheigth = ROIheigth / 2
    framesPerSecond = 10
    s = np.linspace(0, 2*np.pi, 400)

    ### 42.65 culture flask is 42.65 mm (measured from inner most low rim that is continues)
    ### that is 1700 pixels in a typical field of view, adjust this number to exact number of pixels

    mmPerPix = 42.65 / 1700

    t = tFull.loc[tFull['particle'] == p].copy()

    t['distance'] = ''
    t['velocity'] = ''
    t['bellyWidth'] = ''
    t['bellyArea'] = ''
    t['mosqLength'] = ''


    indexes = t.index

    #### use below to restrict to first n frames of each track (if n time points exist in track)
    # if len(t) > 2000:
    #     t = t[:2000]

    indexCounter = 0

    for index, row in it.islice(t.iterrows(), None, len(t) - 1):
        d = math.sqrt((t.loc[indexes[indexCounter + 1]].x - row.x) ** 2 + (t.loc[indexes[indexCounter + 1]].y - row.y) ** 2)
        numFrames = t.loc[indexes[indexCounter + 1]].frame - row.frame
        indexCounter += 1
        d = d * mmPerPix
        d = d / numFrames
        velocity = d * framesPerSecond
        t.at[index, 'distance'] = d
        t.at[index, 'velocity'] = velocity
        if row['x'] < halfROIwidth:
            x_start = 0
            x_stop = ROIwidth
            newX = row.x
        elif row['x'] + halfROIwidth > frameWidth:
            x_start = frameWidth - ROIwidth
            x_stop = frameWidth
            newX = halfROIwidth + (halfROIwidth - (frameWidth - row.x))
        else:
            x_start = row['x'] - halfROIwidth
            x_stop = row['x'] + halfROIwidth
            newX = halfROIwidth
        if row['y'] < halfROIwidth:
            y_start = 0
            y_stop = ROIwidth
            newY = row.y
        elif row['y'] + halfROIwidth > frameWidth:
            y_start = frameWidth - ROIwidth
            y_stop = frameWidth
            newY = halfROIheigth + (halfROIheigth - (frameHeigth - row.y))
        else:
            y_start = row['y'] - halfROIwidth
            y_stop = row['y'] + halfROIwidth
            newY = halfROIheigth
        currFrame = frames[row['frame']]
        currROI = currFrame[int(y_start):int(y_stop), int(x_start):int(x_stop)]
        imageName = saveDir + mosDataName + 'crops_p' + str(p) +'/crop_p' + str(int(p)).zfill(3) + "_f" + str(int(row['frame'])).zfill(6) + ".png"
        skimage.io.imsave(imageName, currROI)

        x = newX + 100*np.cos(s)
        y = newY + 100*np.sin(s)
        init = np.array([x, y]).T
        imBTH = skimage.morphology.black_tophat(currROI, disk(4))
        imBT = imBTH > 7
        F = np.copy(currROI)
        F[F > np.median(currROI)] = np.median(currROI)
        F[imBT] = np.median(F)
        F[currROI>70] = np.median(F)
        F = skimage.filters.gaussian(F, 4)
        snake = active_contour(F*20, init, alpha=0.5, beta=8, gamma=0.001, w_edge=1, w_line=0)
        snakeD = np.expand_dims(snake, axis=1)
        rotRect = cv.minAreaRect(snakeD.astype(int))
        t.at[index, 'bellyWidth'] = np.min(rotRect[1]) * mmPerPix
        t.at[index, 'mosqLength'] = np.max(rotRect[1]) * mmPerPix
        t.at[index, 'bellyArea'] = cv.contourArea(snakeD.astype(int))
        t["mosqLength"] = pd.to_numeric(t["mosqLength"])
        t["distance"] = pd.to_numeric(t["distance"])
        t["velocity"] = pd.to_numeric(t["velocity"])
        t = t.replace(r'^\s*$', np.nan, regex=True)
        pickleName = saveDir + mosDataName +  'crops_p'+ str(p)+ '/' + mosDataName + '_p' + str(p) + '_tStats' + '.pkl'
        t.to_pickle(pickleName)

os.chdir(saveDir)
with open(tracksPickle, 'rb') as f:
    tFull = pickle.load(f)

tFilt = tp.filter_stubs(tFull, minTrackLength)


mosToAnalyze = tFilt.particle.unique()
# mosToAnalyze = [370]

print('found ' + str(len(mosToAnalyze)) + ' tracks to process. Total number of frames to process: ' + str(len(tFilt)))

num_cores = multiprocessing.cpu_count()
Parallel(n_jobs=num_cores)(delayed(mosStatsAndCrop)(tFull, p,  ROIwidth, ROIheigth) for p in mosToAnalyze)

