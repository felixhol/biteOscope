# import deeplabcut
import os
from pathlib import Path
import glob

# os.environ["DLClight"]="True"

import deeplabcut

config_path = '/home/felix/biteOscope/aedes-bbb-2020-11-16_05/config.yaml'

videos = glob.glob('/home/felix/test/WT*cropTrim.mp4')

# # #
print('analyzing ' + str(len(videos)) + ' videos:')
print(*videos, sep = "\n")
# # #
# # #
deeplabcut.analyze_videos(config_path, videos, shuffle=1, batchsize=8, dynamic=(True, 0.5, 100))
# # # # #
deeplabcut.create_video_with_all_detections(config_path, videos, 'DLC_resnet50_aedesNov16shuffle1_80000')
# # #
# deeplabcut.convert_detections2tracklets(config_path, videos, shuffle=1, videotype='mp4', trainingsetindex=0, track_method='box')
# # #
# # # #
# trackletPickles = glob.glob('/home/felix/Dropbox/lisaBaik/*_bx.pickle')
# #
# print('Converting ' + str(len(trackletPickles)) + ' tracklets:')
# print(trackletPickles)
# #
# for tracklet in trackletPickles:
#     deeplabcut.convert_raw_tracks_to_h5(config_path, tracklet)
#
# deeplabcut.create_labeled_video(config_path, videos, videotype='.mp4', track_method='box', filtered=False, color_by='individual')
