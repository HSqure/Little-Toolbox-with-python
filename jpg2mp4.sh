#!/bin/bash

VIDEO_NAME1='bus-stop'
VIDEO_NAME2='busy-street'
VIDEO_NAME3='construction-workers'
VIDEO_NAME4='night'
VIDEO_NAME5='night2'
VIDEO_NAME6='night3'
VIDEO_NAME7='no-helmet-workers'

ffmpeg -r 25 -pattern_type glob -i $VIDEO_NAME1'/*.jpg' -c:v libx264 -r 25 $VIDEO_NAME1.mp4
ffmpeg -r 30 -pattern_type glob -i $VIDEO_NAME2'/*.jpg' -c:v libx264 -r 30 $VIDEO_NAME2.mp4
ffmpeg -r 25 -pattern_type glob -i $VIDEO_NAME3'/*.jpg' -c:v libx264 -r 25 $VIDEO_NAME3.mp4
ffmpeg -r 25 -pattern_type glob -i $VIDEO_NAME4'/*.jpg' -c:v libx264 -r 25 $VIDEO_NAME4.mp4
ffmpeg -r 25 -pattern_type glob -i $VIDEO_NAME5'/*.jpg' -c:v libx264 -r 25 $VIDEO_NAME5.mp4
ffmpeg -r 25 -pattern_type glob -i $VIDEO_NAME6'/*.jpg' -c:v libx264 -r 25 $VIDEO_NAME6.mp4
ffmpeg -r 25 -pattern_type glob -i $VIDEO_NAME7'/*.jpg' -c:v libx264 -r 25 $VIDEO_NAME7.mp4
