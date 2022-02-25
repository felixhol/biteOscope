'''
author: Felix Hol
date: 2022  Feb
content: process biteOscope videos using DeepLabCut
'''
import os
from pathlib import Path
import glob

os.environ["DLClight"]="True"

import deeplabcut
import pandas as pd
from pathlib import Path
import numpy as np



config_path = '/PATH_TO_CONFIG/config.yaml'

videos = glob.glob('/PATH_TO_VIDEOS/*.mp4')

print('analyzing ' + str(len(videos)) + ' videos:')
print(*videos, sep = "\n")

deeplabcut.analyze_videos(config_path, videos, shuffle=1, batchsize=8, dynamic=(True, 0.5, 100))
deeplabcut.create_video_with_all_detections(config_path, videos, 'DLC_resnet50_aedesNov16shuffle1_80000')
deeplabcut.convert_detections2tracklets(config_path, videos, shuffle=1, videotype='mp4', trainingsetindex=0, track_method='box')

trackletPickles = glob.glob('/PATH_TO_VIDEOS/*_bx.pickle')

print('Converting ' + str(len(trackletPickles)) + ' tracklets:')
print(*trackletPickles, sep = "\n")

for tracklet in trackletPickles:
    deeplabcut.convert_raw_tracks_to_h5(config_path, tracklet)
