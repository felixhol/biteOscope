'''
author: Felix Hol
date: 2022  Feb
content: create test videos of single DLC generated tracks (creates one video per tracklet).
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
videoIn = '/mnt/DATA/biteData/P3/210715_mp4/210715_KPPTN_ctrl1_2.mp4'
minDuration = 50        ### minimum track duration to generate video (in frames)
maxDuration = 3000      ### maximum video length (in frames)

hdfs = glob.glob(os.path.splitext(videoIn)[0] + 'DLC*bx_m*.h5')
print('processing ' + str(len(hdfs)))


def createVideo(hdf, videoIn, videoOut, minDuration, maxDuration):
    df = pd.read_hdf(hdf)
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

        fig = plt.figure(frameon=False, figsize=(w / dpi, h / dpi))
        plt.set_cmap('plasma')

        with writer.saving(fig, videoOut, dpi=dpi):
            for i in tqdm(range(start, stop)):
                cap.set(1, i)
                ret, frame = cap.read()
                plt.imshow(frame)
                j = 0
                for ind in df.columns.get_level_values(1).unique():
                    for bp in bptsToPlot:
                        plt.scatter(df[scorer, ind, bp].x[i], df[scorer, ind, bp].y[i], color=cmap(j), alpha=0.75)
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
