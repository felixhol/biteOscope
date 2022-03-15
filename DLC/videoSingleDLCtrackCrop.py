'''
author: Felix Hol
date: 2022  March
content: create test videos of single DLC generated tracks (creates one video per tracklet). Crop to trajectory
'''

import cv2
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
import glob
import pandas as pd
import warnings
from tqdm import tqdm
import os
warnings.filterwarnings("ignore")

### video to be processed
videoIn = '/mnt/DATA/biteData/P3/210715_mp4/210715_KPPTN_denv5_6.mp4'

minDuration = 100      ### minimum track duration to generate video (in frames)
maxDuration = 2000      ### maximum video length (in frames)
cropExtra = 25          ### the full frame is cropped to the extreme values of the body parts + cropExtra
pCutOff = 0.9          ### only plot detected key points having a likelihood > pCutOff

hdfs = glob.glob(os.path.splitext(videoIn)[0] + 'DLC*bx_m*.h5')
print('processing ' + str(len(hdfs)))


def createVideo(hdf, videoIn, videoOut, minDuration, maxDuration):
    df = pd.read_hdf(hdf)
    scorer = df.columns.get_level_values(0)[0]
    for ind in df.columns.get_level_values(1).unique():
        for bp in df.columns.get_level_values(2).unique():
            df[scorer, ind, bp, 'x'].mask(df[scorer, ind, bp, 'likelihood'] < pCutOff,inplace=True)
            df[scorer, ind, bp, 'y'].mask(df[scorer, ind, bp, 'likelihood'] < pCutOff,inplace=True)
    if len(df) > minDuration - 1:
        scorer = df.columns.get_level_values(0)[0]
        bptsToPlot = ['proboscis1', 'proboscis2', 'head', 'thorax', 'abdomenC', 'abdomenR', 'abdomenL', 'bottom',
               'rightForeLeg1', 'rightForeLeg2', 'rightForeLeg3',
               'leftForeLeg1', 'leftForeLeg2', 'leftForeLeg3',
               'rightMidleg1', 'rightMidleg2', 'rightMidleg3',
               'leftMidleg1', 'leftMidleg2', 'leftMidleg3',
               'rightHindleg1', 'rightHindleg2', 'rightHindleg3',
               'leftHindleg1', 'leftHindleg2', 'leftHindleg3']
        cmap = mpl.cm.get_cmap('plasma', len(bptsToPlot) + 2)
        start = df.first_valid_index()
        stop = df.last_valid_index()
        if stop - start > maxDuration:
            stop = start + maxDuration

        cap = cv2.VideoCapture(videoIn)
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.set(1, start)
        ret, frame = cap.read()
        (h, w) = frame.shape[:2]
        dpi = 100
        writer = FFMpegWriter(fps=fps, codec='h264')

        ind = df.columns.get_level_values(1).unique()[0]
        x_min = int(df[scorer, ind].loc[:,(slice(None),'x')].min().min())
        x_max = int(df[scorer, ind].loc[:,(slice(None),'x')].max().max())
        y_min = int(df[scorer, ind].loc[:,(slice(None),'y')].min().min())
        y_max = int(df[scorer, ind].loc[:,(slice(None),'y')].max().max())

        if x_min < cropExtra + 1:
            x_min = 0
        else:
            x_min = x_min - cropExtra
        if y_min < cropExtra + 1:
            y_min = 0
        else:
            y_min = y_min - cropExtra
        if x_max < w - cropExtra + 1:
            x_max = x_max + cropExtra
        else:
            x_max = w
        if y_max < h - cropExtra + 1:
            y_max = y_max + cropExtra
        else:
            y_max = h

        fig = plt.figure(frameon=False, figsize=((x_max - x_min) / dpi, (y_max - y_min) / dpi))
        plt.set_cmap('plasma')

        with writer.saving(fig, videoOut, dpi=dpi):
            for i in tqdm(range(start, stop)):
                cap.set(1, i)
                ret, frame = cap.read()
                plt.imshow(frame[y_min:y_max, x_min:x_max])
                j = 0
                for ind in df.columns.get_level_values(1).unique():
                    for bp in bptsToPlot:
                        plt.scatter(df[scorer, ind, bp].x[i] - x_min, df[scorer, ind, bp].y[i] - y_min, color=cmap(j), alpha=0.75)
                        j += 1
                plt.axis('off')
                plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
                writer.grab_frame()
                plt.clf()

        plt.close(fig)

for hdf in hdfs:
    videoOut = hdf.replace('h5', 'mp4')
    print('creating video: ' + videoOut)
    createVideo(hdf, videoIn, videoOut, minDuration, maxDuration)
