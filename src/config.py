import os
from flask import request

CR_DIR = os.getcwd()
VIDEO_DIR = os.path.join(CR_DIR , "raw_videos")

DATABASE_PATH = os.path.join(CR_DIR, "db.sqlite")

API_PATH = "update_call_log_media"
UPDATE_API = "update_video_description"

DATABASE_URI = 'sqlite:///db.sqlite'

# down_link = request.json['url']
# id = request.json['id']

def check_directory(path):
    if not os.path.exists(path):
        os.mkdir(path)



