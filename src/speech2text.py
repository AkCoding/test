import io
import argparse
import os
import urllib

import speech_recognition as sr
# from google.cloud import speech
import subprocess
# from watson_developer_cloud import SpeechToTextV1
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import moviepy.editor as mp
import json
from src.nlp import clean_text
from urllib.request import urlopen

# command = 'ffmpeg -i aiml.mkv -ab 160k -ar 44100 -vn audio.wav'
# subprocess.call(command, shell=True)
from src.models import Status, Video
import pandas as pd
import time
import boto3


def aws(video):


    # if str(video.api).__contains__("https://now.tethrit.com/"):
    #     return ("", "")

    foldername = video.path.replace(os.path.basename(video.url), "")
    clip = mp.VideoFileClip(video.path)
    clip.audio.write_audiofile(f"{foldername}_theaudio.mp3")


    job_uri = 'theaudio.mp3'
    AWS_ACCESS_KEY_ID = 'AKIA6BCIF5WBSNX44D6I'
    AWS_SECRET_ACCESS_KEY = '+LdwMLI4dUy37Y/cXRm2jf1Kkz22jzDRGGVOewWP'

    job_name = (job_uri.split('.')[0]).replace(" ", "")


    transcribe = boto3.client('transcribe', aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name='us-east-1')
    transcribe.start_transcription_job(TranscriptionJobName=job_name, Media={'MediaFileUri': job_uri},
                                       MediaFormat='mp3', LanguageCode='en-US')

    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        print("Not ready yet...")
        time.sleep(2)
    print(status)

    if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
        response = urllib.urlopen(status['TranscriptionJob']['Transcript']['TranscriptFileUri'])
        data = json.loads(response.read())
        text = data['results']['transcripts'][0]['transcript']
        print(text)


def amazon_transcribe(video):


    foldername = video.path.replace(os.path.basename(video.url), "")
    clip = mp.VideoFileClip(video.path)
    clip.audio.write_audiofile(f"{foldername}_theaudio.mp3")


    AWS_ACCESS_KEY_ID = 'AKIA6BCIF5WBSNX44D6I'
    AWS_SECRET_ACCESS_KEY = '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'
    job_uri =  'https://s3.amazonaws.com/arbaazhb/theaudio.mp3'
    # Usually, I put like this to automate the process with the file name
    # "s3://bucket_name" + audio_file_name
    # Usually, file names have spaces and have the file extension like .mp3
    # we take only a file name and delete all the space to name the job
    job_name = 'theaudio'
    # file format
    file_format = '.mp3'

    transcribe = boto3.client('transcribe', aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name='us-east-1')

    # check if name is taken or not
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat=file_format,
        LanguageCode='en-US')

    while True:
        result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if result['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        time.sleep(15)
    if result['TranscriptionJob']['TranscriptionJobStatus'] == "COMPLETED":
        data = pd.read_json(result['TranscriptionJob']['Transcript']['TranscriptFileUri'])
    return data['results'][1][0]['transcript']









def google(video):

    if str(video.api).__contains__("https://now.tethrit.com/"):
        return ("", "")

    foldername = video.path.replace(os.path.basename(video.url), "")
    clip = mp.VideoFileClip(video.path)
    clip.audio.write_audiofile(f"{foldername}_theaudio.mp3")

    """Transcribe the given audio file asynchronously."""


    client = speech.SpeechClient()

    with io.open(video, "rb") as audio_file:
        content = audio_file.read()

    """
     Note that transcription is limited to a 60 seconds audio file.
     Use a GCS file for audio longer than 1 minute.
    """
    audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete...")
    response = operation.result(timeout=120)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        print(u"Transcript: {}".format(result.alternatives[0].transcript))
        print("Confidence: {}".format(result.alternatives[0].confidence))


def s2t(video):
    if str(video.api).__contains__("https://now.tethrit.com/"):
        return ("", "")

    foldername = video.path.replace(os.path.basename(video.url), "")
    clip = mp.VideoFileClip(video.path)
    clip.audio.write_audiofile(f"{foldername}_theaudio.mp3")

    apikey = 'q0xaZCelGPUu_xal2DWC1VXJ5UHMyyf9MnLQaC1uqw7i'
    url = 'https://api.us-east.speech-to-text.watson.cloud.ibm.com/instances/c6eb5eba-f1df-4c43-8e19-a1bbd3dbcefa'
    model = 'en-US_NarrowbandModel'

# Setup service
    authenticator = IAMAuthenticator(apikey)
    stt = SpeechToTextV1(authenticator=authenticator)
    stt.set_service_url(url)

    try:
        with open(f'{foldername}_theaudio.mp3', 'rb') as f:
            res = stt.recognize(audio=f, content_type='audio/mp3', model=model,
                                continuous=True,
                                inactivity_timeout=120).get_result()
            try:
                text = [result['alternatives'][0]['transcript'].rstrip() + '.\n' for result in res['results']]
                #
                # # texts = []
                # # for result in res["result"]:
                # #     for output in result:
                # #         transcripts = output["alternatives"]
                # #         for speech in transcripts:
                # #             if (speech["confidence"] > 0.70):
                # #                 texts.append(speech["transcript"])
                #
                # text = [para[0].title() + para[1:] for para in text]
                transcript = ''.join(text)

                tokens, top_keywords = clean_text(transcript)

                response = {
                    "statistics": {
                        "top_keywords": top_keywords,
                        "cateogry": "unknown"
                    },
                    "keywords": ', '.join(tokens)

                }
                return (json.dumps(res['results']), json.dumps(response))

            except Exception as err:
                print(err)
                return ("", "")


    except Exception as err:
        print("Exception in Speech to text {} ".format(err) )
        return ("", "")









