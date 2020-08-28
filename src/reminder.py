from pygame import mixer
from gtts import gTTS
import pandas as pd
import threading
import requests
import time

API_HOST = '0.0.0.0'
API_PORT = '8085'

BASE_URL = f'http://{API_HOST}:{API_PORT}'
ADD_URL = f'{BASE_URL}/add'
RM_URL = f'{BASE_URL}/remove'
LS_URL = f'{BASE_URL}/list'
DATA_VER_URL = f'{BASE_URL}/data-version'

TIME_FORMAT = '%Y%m%dt%H%M%S'
data_template = pd.DataFrame(columns=['id', 'reminder_time', 'message', 'x_sec_repeat'])


# loads only upcoming reminders
def load_data():
    global data
    params = {'from': time.strftime(TIME_FORMAT, time.localtime(time.time()))}
    r = requests.get(url=LS_URL, params=params)

    data = pd.read_json(r.content, orient="records",  convert_dates=False)
    if data.empty:
        data = data_template.copy()
    data = data.sort_values(by=['reminder_time'])


# creates and plays the recording
def play_rec(msg):
    filename = "rec" + ".mp3"
    language = 'en'

    # create a record file of the reminder and save locally
    myobj = gTTS(text=msg, lang=language, slow=False)
    myobj.save(filename)

    # play the recording
    mixer.init()
    mixer.music.load(filename)
    mixer.music.play()


# get the data version from the api
def get_data_version():
    r = requests.get(url=DATA_VER_URL)
    return int(r.text)


# check if the api has updated, and update the reminders with the changed data
def check_for_updates():
    global data_version

    while True:
        current_data_ver = get_data_version()
        if current_data_ver != data_version:
            data_version = current_data_ver
            load_data()
        time.sleep(0.5)


# plays reminders
def play_reminder():
    global data

    while True:
        if not data.empty:
            if int(data.iloc[0]["reminder_time"]) <= int(time.time()):
                msg = data.iloc[0]["message"]
                print(msg)
                play_rec(msg)
                data = data.drop(data.index[0])


if __name__ == '__main__':
    data = None
    data_version = 0
    load_data()
    socket_thread = threading.Thread(target=check_for_updates, args=())
    socket_thread.start()
    play_reminder()

