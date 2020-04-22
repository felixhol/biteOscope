import picamera 
import os
import time
import datetime
import numpy as np
from PIL import Image
from fractions import Fraction

c = picamera.PiCamera()

numFrames = 50000
expTime = 0.06 
saveDir = '/home/pi/Documents/wellPlateBites/180815_wellGel/data01/'

expTimeM = int(expTime * 1000000) #in seconds
frameRate = Fraction(1/expTime)
c.framerate = frameRate

time.sleep(1)

c.resolution = (1296,972)
g = c.awb_gains
c.awb_mode = 'off'
c.awb_gains = g
c.exposure_mode = 'off'
c.shutter_speed = expTimeM


T = []
startT = datetime.datetime.now()

os.chdir(saveDir)

# c.start_preview()
# time.sleep(2)
# c.stop_preview()

#print(c.shutter_speed)

for i in range(numFrames):
	currT = datetime.datetime.now()
	dt = currT - startT
	T.append(dt.total_seconds())
	np.savetxt('time.out', T, delimiter=',')
	time.sleep(0.003)
	c.capture("imT" + str(i).zfill(5) + ".jpg")
	#imT=Image.fromarray(im)


#np.savetxt('time.out', T, delimiter=',')
