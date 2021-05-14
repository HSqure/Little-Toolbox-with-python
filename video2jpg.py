import os
import cv2

# video set list
VIDEO_NAME_SET=['wildfire1.mp4',
                'carfire1.mp4',
                'carfire2.mp4',
                'carfire3.mp4',
                'forestfire1.mp4',
                'forestfire2.mp4',
                'forestfire3.mp4',
                'housefire2.mp4',
                'housefire3.mp4',
                'housefire4.mp4']
              
SKIP_FRAME = 4

def creat_pic_group_folder(video_name):
    # take the part before '.' as folder name, which is video name
    folder_name = video_name.split('.')[0]
    is_exist = os.path.exists(folder_name)
    if not is_exist:
        os.makedirs(folder_name)
        print('--- Creating new folder{}... ---'.format(folder_name))
    else:
        print('--- Using existed folder ---')
    return folder_name


def video2jpg(video_name):
    vid = cv2.VideoCapture(video_name)
    if not vid.isOpened():
        raise IOError("Couldn't open video")
    folder_name = creat_pic_group_folder(video_name) 
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
            cv2.imwrite(folder_name + '/' + image_name, frame)
            print('Picture {} is gennerated !'.format(image_name))

if __name__ == "__main__":

    for video_name in VIDEO_NAME_SET:
        video2jpg(video_name)


