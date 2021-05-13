#!/bin/bash

ffmpeg -r 20 -pattern_type glob -i 'output_result/a/*.jpg' -c:v libx264 -r 20 axu2cga-yolov3-vehicle_vol.1.mp4

#ffmpeg -r 20 -pattern_type glob -i 'output_result/b/*.jpg' -c:v libx264 -r 20 axu2cga-yolov3-vehicle_vol.2.mp4

#ffmpeg -r 20 -pattern_type glob -i 'output_result/c/*.jpg' -c:v libx264 -r 20 axu2cga-yolov3-vehicle_vol.3.mp4

#ffmpeg -r 20 -pattern_type glob -i 'output_result/d/*.jpg' -c:v libx264 -r 20 axu2cga-yolov3-vehicle_vol.4.mp4

#ffmpeg -r 20 -pattern_type glob -i 'output_result/img/*.jpg' -c:v libx264 -r 20 axu2cga-yolov3-vehicle_vol.5.mp4

