import cv2
import dlib 
import numpy as np 
from imutils import face_utils
from camera import VideoCamera
from imutils.video import WebcamVideoStream
import time
import random
import threading

cap = WebcamVideoStream(src=0).start() 


recognition = VideoCamera(cap)
a = ['right', 'left']


def main():
    status = True
    timeout = 20
    countdown = timeout

    time.sleep(2)
    while True:
        countdown -= 1

        pose = head.run()
        recog_face = recognition.get_frame()

        print(countdown)
        random_one = random.choice(a)
            
        if len(recog_face[1]) == 1 and status:
            print('HELLO {}'.format(recog_face[1][0]))
            print('look to your {}'.format(random_one))
            status = False
 
        if len(recog_face[1]) == 1 and pose == random_one:
            print('acces granted')
                      
            main()
            countdown = timeout

            status = False

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()   

if __name__ == '__main__':
    main()