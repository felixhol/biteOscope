'''
author: Felix Hol
date: 2020 04 24
content: runs DeepLabCut inference on timelapse images of mosquitoes using model trained on aegypti and ablopictus
Takes cropped frames as input
Output is:
1) body part coordinates per DeepLabCut standards
2) an .avi of the images (this is only used for make the labelled video and/or quick viewing, not for inference)
3) labelled video
'''


import os
os.environ["DLClight"]="True"

import deeplabcut
# from pathlib import Path

import cv2
import numpy as np
import glob
from PIL import Image

print('deeplabcut version: ' + str(deeplabcut.__version__))


import tensorflow as tf
print('tensorflow version: ' + str(tf.__version__))


# tf.test.gpu_device_name()

config = '/Users/felix/biteOscope_repo/biteOscope/DLC_aedes/aedes01-felix-2020-01-10/config.yaml'


dataDir = '/Users/felix/biteOscope_clean/test/dump/testcrops_p1.0/'
files = sorted(glob.glob(dataDir +'*.png'))
# saveDirMovie = '/home/felix/biteData/FFDEET/test/'

img_array = []

for filename in files:
    img = cv2.imread(filename)
    height, width, layers = img.shape
    size = (width,height)
    img_array.append(img)


videoBaseName = os.path.basename(os.path.normpath(dataDir))

if '.' in videoBaseName:
    videoBaseName = videoBaseName[:-2]

videoName = dataDir + videoBaseName + '.avi'
out = cv2.VideoWriter(videoName, cv2.VideoWriter_fourcc(*'DIVX'), 25, size)
 
for i in range(len(img_array)):
    out.write(img_array[i])
out.release()

videoPath = videoName
imageDir = dataDir

deeplabcut.analyze_time_lapse_frames(config, imageDir, save_as_csv=True, rgb=False)

deeplabcut.create_labeled_video(config, [videoPath], filtered=False)