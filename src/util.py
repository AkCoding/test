import os
import urllib.request
from src.config import VIDEO_DIR
from src.models import Video, Status
import base64

def get_video_folder(callreport_id, call_video_id):
    return "{}_{}".format(callreport_id, call_video_id)

def get_call_log_id_from_checkpoint(checkpoint):
    return checkpoint.split("_")[0]

def get_call_log_media_id_from_checkpoint(checkpoint):
    return checkpoint.split("_")[1]

def media_link(app, db, dwn_link, path, checkpoint_id):
    if not os.path.exists(VIDEO_DIR):
        os.mkdir(VIDEO_DIR)
    result = urllib.request.urlretrieve(dwn_link, path)

    with app.app_context():
        video = Video.query.filter_by(checkpoint_id=checkpoint_id).first()
        video.download_status = Status.COMPLETED
        db.session.commit()
        print("{} 's download complete".format(checkpoint_id))

# tokens = ["hi", "hellpo", "yasia"]
# print(', '.join(tokens))

def get_base64(data):
    # Standard Base64 Encoding
    encodedBytes = base64.b64encode(data.encode("utf-8"))
    encodedStr = str(encodedBytes, "utf-8")
    return encodedStr


def decode_base64(data):
    # Standard Base64 Encoding
    encodedBytes = base64.b64decode(data.encode("utf-8"))
    encodedStr = str(encodedBytes, "utf-8")
    return encodedStr
