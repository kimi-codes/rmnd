from pygame import mixer
from gtts import gTTS
import pandas as pd
import threading
import requests
import time
import sys
import os

SERVER_HOST = '0.0.0.0'
SERVER_PORT = '8085'

RECORDING_PATH = './rec'

TIME_FORMAT = '%Y%m%dt%H%M%S'
data_template = pd.DataFrame(columns=['id', 'reminder_time', 'message', 'x_sec_repeat'])


def set_host_config():
    global SERVER_HOST
    global SERVER_PORT
    global BASE_URL
    global LS_URL
    global DATA_VER_URL

    if len(sys.argv) >= 2:
        SERVER_HOST = sys.argv[1]
        if len(sys.argv) >= 3:
            SERVER_PORT = sys.argv[2]
            if len(sys.argv) > 3:
                print('WARNING: Too many args received and were ignored. (Correct syntax: [PROGRAM] [SERVER HOST] [SERVER PORT])')
        
    BASE_URL = f'http://{SERVER_HOST}:{SERVER_PORT}'
    LS_URL = f'{BASE_URL}/list'
    DATA_VER_URL = f'{BASE_URL}/data-version'

# loads only upcoming reminders
def load_data():
    global data
    params = {'from': time.strftime(TIME_FORMAT, time.localtime(time.time()))}
    r = requests.get(url=LS_URL, params=params)

    data = pd.read_json(r.content, orient="records",  convert_dates=False)
    if data.empty:
        data = data_template.copy()
    data = data.sort_values(by=['reminder_time'])


# creates a tts recording file and saves locally
def create_recording(id, msg):
    filename = f'{id}.mp3'
    path = f'{RECORDING_PATH}/{filename}'
    language = 'en'

    rec = gTTS(msg, lang=language)
    rec.save(path)


# plays the recording
def play_rec(id):
    filename = f'{id}.mp3'
    path = f'{RECORDING_PATH}/{filename}'
    
    mixer.init()

    with open(path, 'rb') as file_object:
        mixer.music.load(file_object)
        mixer.music.play(0)
        while mixer.music.get_busy():
            time.sleep(0.1)
        mixer.quit()

    #removes file after playing 
    os.remove(path)


# get the data version from the api
def get_data_version():
    r = requests.get(url=DATA_VER_URL)
    return int(r.text)


# check if the data has updated in the server, and update the reminders with the changed data
def check_for_updates():
    global data_version

    while True:
        current_data_ver = get_data_version()
        if current_data_ver != data_version:
            load_data()
            data_version = current_data_ver
        time.sleep(0.5)


# plays reminders
def play_reminder():
    global data
    x_sec_to_rem = 30 #number of second before the reminder is due to create the recording file.
    rec_created = False

    while True:
        if not data.empty:
            # create recording
            if not rec_created:
                if int(data.iloc[0]["reminder_time"]-x_sec_to_rem) <= int(time.time()):
                    create_recording(data.iloc[0]["id"], data.iloc[0]["message"])
                    rec_created = True
            # play recording
            if int(data.iloc[0]["reminder_time"]) <= int(time.time()):
                #create_recording(data.iloc[0]["id"], data.iloc[0]["message"])
                print(data.iloc[0]["message"])
                play_rec(data.iloc[0]["id"])
                data = data.drop(data.index[0])
                rec_created = False


if __name__ == '__main__':
    data = None
    data_version = 0
    data_updated = False

    set_host_config()
    load_data()
    # create recordings folder
    if not os.path.exists(RECORDING_PATH):
        os.makedirs(RECORDING_PATH)

    socket_thread = threading.Thread(target=check_for_updates, args=())
    socket_thread.start()
    play_reminder()

