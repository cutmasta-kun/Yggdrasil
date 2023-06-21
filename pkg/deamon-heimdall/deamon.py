# deamon.py
import os
import logging
import cv2
import time
import sys

def track_iris():
    try:
        # Get the video stream URL from the environment variable
        video_stream_url = os.getenv('VIDEO_STREAM_URL', 'http://192.168.178.21:8080/video')

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.ERROR)
    track_iris()
