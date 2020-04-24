'''
author: Felix Hol
date: 2020 04 24
content: code to pick a subset of frames from list of directories
'''


import os
import glob
from PIL import Image
import numpy as np
import pandas as pd

dirList = glob.glob('/Users/felix/Documents/mosquitoes/mosquitoData/biteData/albopictus/191022*multiple02/19*crops*/')

len(dirList)

saveDir = '/Users/felix/Documents/mosquitoes/mosquitoData/biteData/aedesTrainIm02/'

for i in dirList:
    os.chdir(i)
    fileList = glob.glob('*.png')
    if len(fileList) > 20 and len(fileList) < 40:
        step = int(np.floor(len(fileList) / 2))   
        for j in range(1, len(fileList), step):
            im = Image.open(fileList[j])
            file, ext = os.path.splitext(fileList[j])
            im.save(saveDir + file + '.png', 'PNG')
    elif len(fileList) > 40:
        step = int(np.floor(len(fileList) / 2))
        for j in range(1, len(fileList), step):
            im = Image.open(fileList[j])
            file, ext = os.path.splitext(fileList[j])
            im.save(saveDir + file + '.png', 'PNG')