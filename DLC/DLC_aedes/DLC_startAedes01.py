# import deeplabcut
import os
from pathlib import Path

os.environ["DLClight"]="True"

import deeplabcut

# video_path = ['/Users/felix/biteOscope/DLC_aedes/videos/mockVideo01.mp4']
# config_path = deeplabcut.create_new_project('aedes01','felix', video_path, copy_videos=False, videotype='.mp4')

config_path = '/home/felix/biteOscope/DLC_aedes/aedes01-felix-2020-01-10/config.yaml'


# deeplabcut.label_frames(config_path)

# deeplabcut.create_training_dataset(config_path, num_shuffles=2)

# deeplabcut.train_network(config_path, shuffle=2)

deeplabcut.evaluate_network(config_path, Shuffles=[2], plotting=True, gputouse=0)
