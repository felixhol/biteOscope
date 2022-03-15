'''
author: Felix Hol
date: 2022 March
content: Napari-based behavioral annotator. Based on github repo of bobfromjapan.
'''

import napari
from napari_video.napari_video import VideoReaderNP
import numpy as np
import yaml
import os
import pandas as pd
import sys


VIDEO_PATH = sys.argv[1]
print(VIDEO_PATH)

# VIDEO_PATH = '/Users/felix/Documents/mosquitoes/mosquitoData/P3/210715_test/210715_KPPTN_ctrl1_2DLC_resnet50_aedesNov16shuffle1_80000_bx_m3_1616.mp4'
LABELS = ['undefined', 'rest', 'walk', 'probe', 'explore', 'groom', 'engorge']

output_name = VIDEO_PATH[:-4] + "_annotation.csv"

vr = VideoReaderNP(VIDEO_PATH)
annotations = np.array([LABELS[0]]*len(vr))

# global vars
flag_exist = False
flag_frame = 0

viewer = napari.Viewer()


@viewer.bind_key('f')
def set_start_flag(event=None):
    global flag_exist
    global flag_frame

    if flag_exist:
        print('flag already exist!!')
    else:
        flag_frame = image_layer._slice_indices[0]
        flag_exist = True
        print("start flag set to frame:", image_layer._slice_indices[0])

@viewer.bind_key('r')
def annotate_A(event=None):
    global flag_exist
    global flag_frame
    if flag_exist:
        if flag_frame > image_layer._slice_indices[0]:
            print("go to the later frame than the start flag.")
            show_globals()
        else:
            print(
                flag_frame, "to", image_layer._slice_indices[0], "are annotated to ", LABELS[1])
            annotations[flag_frame:image_layer._slice_indices[0]] = LABELS[1]
            flag_exist = False
    else:
        print("need to set the start flag.")

@viewer.bind_key('g')
def annotate_B(event=None):
    global flag_exist
    global flag_frame
    if flag_exist:
        if flag_frame > image_layer._slice_indices[0]:
            print("go to the later frame than the start flag.")
            show_globals()
        else:
            print(
                flag_frame, "to", image_layer._slice_indices[0], "are annotated to ", LABELS[2])
            annotations[flag_frame:image_layer._slice_indices[0]] = LABELS[2]
            flag_exist = False
    else:
        print("need to set the start flag.")

@viewer.bind_key('v')
def annotate_B(event=None):
    global flag_exist
    global flag_frame
    if flag_exist:
        if flag_frame > image_layer._slice_indices[0]:
            print("go to the later frame than the start flag.")
            show_globals()
        else:
            print(
                flag_frame, "to", image_layer._slice_indices[0], "are annotated to ", LABELS[3])
            annotations[flag_frame:image_layer._slice_indices[0]] = LABELS[3]
            flag_exist = False
    else:
        print("need to set the start flag.")

@viewer.bind_key('t')
def annotate_B(event=None):
    global flag_exist
    global flag_frame
    if flag_exist:
        if flag_frame > image_layer._slice_indices[0]:
            print("go to the later frame than the start flag.")
            show_globals()
        else:
            print(
                flag_frame, "to", image_layer._slice_indices[0], "are annotated to ", LABELS[4])
            annotations[flag_frame:image_layer._slice_indices[0]] = LABELS[4]
            flag_exist = False
    else:
        print("need to set the start flag.")

@viewer.bind_key('b')
def annotate_B(event=None):
    global flag_exist
    global flag_frame
    if flag_exist:
        if flag_frame > image_layer._slice_indices[0]:
            print("go to the later frame than the start flag.")
            show_globals()
        else:
            print(
                flag_frame, "to", image_layer._slice_indices[0], "are annotated to ", LABELS[5])
            annotations[flag_frame:image_layer._slice_indices[0]] = LABELS[5]
            flag_exist = False
    else:
        print("need to set the start flag.")

@viewer.bind_key('c')
def annotate_B(event=None):
    global flag_exist
    global flag_frame
    if flag_exist:
        if flag_frame > image_layer._slice_indices[0]:
            print("go to the later frame than the start flag.")
            show_globals()
        else:
            print(
                flag_frame, "to", image_layer._slice_indices[0], "are annotated to ", LABELS[6])
            annotations[flag_frame:image_layer._slice_indices[0]] = LABELS[6]
            flag_exist = False
    else:
        print("need to set the start flag.")

@viewer.bind_key('3')
def show_globals(event=None):
    global flag_frame
    global flag_exist
    print("flag:", flag_exist)
    print("pos:", flag_frame)

@viewer.bind_key('4')
def delete_flag(event=None):
    global flag_exist
    print("delete_flag")
    flag_exist = False

@viewer.bind_key('5')
def check_label(event=None):
    print(annotations)

@viewer.bind_key('0')
def save_label(event=None):
    print("save!")
    pd.DataFrame(annotations).to_csv(output_name)

image_layer = viewer.add_image(vr, rgb=True)

napari.run()
