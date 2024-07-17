import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
import HandTrackingModule as htm
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
devices = AudioUtilities.GetSpeakers()

video_capture = cv2.VideoCapture(0)
wcam, hcam = 640, 480
video_capture.set(3, wcam)
video_capture.set(4, hcam)
ptime = 0 
detector = htm.handDetector()


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volrange= volume.GetVolumeRange()
minvol = volrange[0]
maxvol = volrange[1]
vol =0
volbar = 400
volper = 0


while True:
    ret, img = video_capture.read()
    img = detector.findhands(img)
    lmlist = detector.findPosition(img, draw=False)
    if len(lmlist) != 0:
        #print(lmlist[4], lmlist[8])
        x1, y1 = lmlist[4][1], lmlist[4][2]
        x2, y2 = lmlist[8][1], lmlist[8][2]
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
        length = math.hypot(x2 - x1, y2 - y1)
        #print(length)
        # Hand range 20 - 200
        # Volume Range -65 - 0
        vol = np.interp(length, [20, 200], [minvol, maxvol])
        volbar = np.interp(length, [20, 200], [400, 150])
        volper = np.interp(length, [20, 200], [0, 100])
        #print(vol)
        volume.SetMasterVolumeLevel(vol, None)

        if length < 20:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
    
    cv2.rectangle(img, (50, 150), (85, 400), (0, 0,0), 3)
    cv2.rectangle(img, (50, int(volbar)), (85, 400), (0, 0,255), cv2.FILLED)
    
    frame=cv2.flip(img,1)
    cv2.putText(frame , f'{int(volper)}%', (540, 450), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 2)
    
    ctime = time.time()
    fps = 1/(ctime - ptime)
    ptime = ctime
    cv2.putText(frame, f'FPS: {int(fps)}', (10, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 2)
    cv2.imshow('Video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
video_capture.release()
cv2.destroyAllWindows()
