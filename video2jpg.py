import os
import cv2

VIDEO_PATH = 'Ogdenhousefire.mp4'
SKIP_FRAME = 4

if __name__ == "__main__":

    vid = cv2.VideoCapture(VIDEO_PATH)
    if not vid.isOpened():
        raise IOError("Couldn't open video")
    
    cnt=0
    skip_key=0
    
    while True:   
    
        skip_key = skip_key + 1
        
        return_value, frame = vid.read()
        k=cv2.waitKey(1)
        if (k == 27) or (frame is None):
            break
        
        if skip_key%SKIP_FRAME==0:
            cnt = cnt + 1
            image_name = 'img{:0>5d}.jpg'.format(cnt)
        
            cv2.imwrite('converted_pic/' + image_name, frame)
            print('Picture {} is gennerated !'.format(image_name))
            


