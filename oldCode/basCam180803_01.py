import pypylon
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from PIL import Image
import os
import time
import datetime
import sys
import signal


saveDir0 = sys.argv[1]
os.mkdir(saveDir0)

#saveDir0 = '/home/felix/MosquitoData/180501/data06'
#saveDir1 = '/home/felix/MosquitoData/180501/data06'
# saveDir2 = '/home/felix/test/170228test/testData/cam2'
numFrames = 20000
exposureTime = 150000


cameras = pypylon.factory.find_devices()
time.sleep(0.02)

cam1 = pypylon.factory.create_device(cameras[0])
# cam2 = pypylon.factory.create_device(cameras[1])

if not cam1.opened:
    cam1.open()

# if not cam2.opened:
#     cam2.open()

time.sleep(1)

##Set camera properties:
cam1.properties['ExposureTime'] = exposureTime
cam1.properties['DeviceLinkThroughputLimitMode'] = 'Off'
 
# cam2.properties['ExposureTime'] = 65000
# cam2.properties['DeviceLinkThroughputLimitMode'] = 'Off'

##Get current time for timestamps
T = []
startT = datetime.datetime.now()


for i in range(numFrames):
    try:
        def handler(signo, frame):
            raise RuntimeError

        signal.signal(signal.SIGALRM, handler)
        signal.alarm(10) # seconds
        
        while True:
            for im in cam1.grab_images(1):
                
                        imT1=Image.fromarray(im)
                        os.chdir(saveDir0)
                        imT1.save("imTc1_" + str(i).zfill(5) + ".png", compress_level=6)
            # for im in cam2.grab_images(1):
            #     imT2=Image.fromarray(im)
            #     os.chdir(saveDir2)
            #     imT2.save("imTc2_" + str(i).zfill(5) + ".png", compress_level=2)
            currT = datetime.datetime.now()
            dt = currT - startT
            T.append(dt.total_seconds())
            os.chdir(saveDir0)
            np.savetxt('time_03.out', T, delimiter=',')
            time.sleep(0.00001)
            break
    
    except KeyboardInterrupt:
        print("closing time")
        cam1.close()
        # cam2.close()
        sys.exit()
    
    except RuntimeError: 
        print("oh boy, an error", sys.exc_info()[0])
        time.sleep(0.5)
        cam1.close()
        # cam2.close()
        time.sleep(0.5)
        cam1.open()
        # cam2.open()
        cam1.properties['ExposureTime'] = exposureTime
        cam1.properties['DeviceLinkThroughputLimitMode'] = 'Off'
        # cam2.properties['ExposureTime'] = 25000
        # cam2.properties['DeviceLinkThroughputLimitMode'] = 'Off'

cam1.close()
# cam2.close()

time.sleep(1)

##np.savetxt('time.out', T, delimiter=',')