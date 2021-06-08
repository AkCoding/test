import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))

import threading
import concurrent.futures
from sqlalchemy.exc import IntegrityError
import requests
from src.config import VIDEO_DIR, check_directory, API_PATH, UPDATE_API
from flask import Blueprint, jsonify, request, Flask, make_response
from src import db, app
from src.models import Video, Status
from src.speech2text import s2t
from src.util import get_video_folder, media_link, get_call_log_id_from_checkpoint, \
    get_call_log_media_id_from_checkpoint, decode_base64


# SQLALCHEMY_TRACK_MODIFICATIONS = True


@app.route('/add_checkpoint', methods=['POST'])
def add_video():
    try:
        if request.method == 'POST':

            payload = request.get_json()
            id = payload["callLogMediaId"]
            call_log_id = payload.get("callLogId")
            api_path = decode_base64(payload.get("api_path"))

            check_point_id = get_video_folder(call_log_id, id)

            video = Video.query.filter_by(checkpoint_id=check_point_id).first()
            if video:
                return make_response(
                    ({'error': False,
                      'data': {
                          "checkpoint_id": video.checkpoint_id,
                          "status": video.status
                      },
                      "message": "Checkpoint Already Created"},
                     200))

            down_link = decode_base64(payload['url'])
            filename = os.path.basename(down_link)

            try:
                # creating call report id folder
                filepath = os.path.join(VIDEO_DIR, check_point_id)
                check_directory(filepath)

                filepath = os.path.join(filepath, filename)

                video = Video(url=down_link, checkpoint_id=check_point_id, path=filepath,
                              status=Status.PENDING, api=api_path)
                db.session.add(video)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return make_response(
                    ({'error': True,
                      'data': [],
                      "message": "IntegrityError"},
                     404))

            # starting downloading this video on diffrent thread
            threading.Thread(target=media_link, args=(app, db, down_link, filepath, check_point_id)).start()
            return make_response(
                ({'error': False,
                  'data': {"id": id,
                           "status": video.status},
                  "message": "Successfully created checkpoint"},
                 201))

        else:
            return make_response(
                ({'error': True,
                  "message": 'method not supported'},
                 400))

    except Exception as err:
        return make_response(
            ({'error': True,
              "message": str(err)},
             500))


def update_media_log(video, tokens_count):
    try:

        data = {'call_log_id': str(get_call_log_id_from_checkpoint(video.checkpoint_id)),
                'call_log_media_id': str(get_call_log_media_id_from_checkpoint(video.checkpoint_id)),
                'video_description': video.transcript,
                'video_description_status': "completed",
                'video_keywords': tokens_count
                }

        # print(multipart_form_data)
        api = str(video.api.replace(API_PATH, UPDATE_API))

        print("Sending.. payload  {} to {}".format(data, api))
        response = requests.get(api, params=data)
        if (response.status_code == 200):
            responseObj = response.json()
            settings = responseObj['settings']

            print(str(response.status_code)
                  + ' and settings ' + str(settings))

        else:
            print("error while adding checkpoint {} 's transcription".format(video.checkpoint_id))


    except Exception as err:
        print('API Exception -> ' + str(err))


def process_pending(application, database):
    with application.app_context():
        videos = Video.query.filter_by(status=Status.PENDING) \
            .filter_by(download_status=Status.COMPLETED).all()

        if len(videos) > 0:

            with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
                for video, transcibe_result in zip(videos, executor.map(s2t, videos)):
                    # print(task)
                    # print(number)
                    # print(str(video.api))
                    if not str(video.api).__contains__("https://now.tethrit.com/"):

                        transcript, tokens_count = transcibe_result
                        print("Transcript for {} ".format(video.checkpoint_id))
                        print(transcript)
                        try:
                            v = Video.query.filter_by(checkpoint_id=video.checkpoint_id).first()
                            v.status = Status.COMPLETED
                            v.transcript = transcript
                            # db.session.add(video)
                            database.session.commit()
                            print("Transcript added successfully in local db for {} ".format(video.checkpoint_id))
                            print(tokens_count)
                            update_media_log(v, tokens_count)
                        except Exception as err:
                            print('Somethiong went wrong, while inserting transcript into db')
        else:
            videos = Video.query.filter_by(status=Status.PENDING) \
                .filter_by(download_status=Status.PENDING).all()

            for video in videos:
                # creating call report id folder
                filepath = os.path.join(VIDEO_DIR, video.checkpoint_id)
                check_directory(filepath)
                filename = os.path.basename(video.url)
                filepath = os.path.join(filepath, filename)
                # starting downloading this video on diffrent thread
                video.path = filepath
                db.session.add(video)
                db.session.commit()
                threading.Thread(target=media_link, args=(app, db, video.url, filepath, video.checkpoint_id)).start()




if __name__ == '__main__':
    check_directory(VIDEO_DIR)
    app.run(debug=True, port=5001)
