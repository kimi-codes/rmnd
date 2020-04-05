from pygame import mixer
from gtts import gTTS
import pandas as pd
import threading
import requests
import time


SERVER_HOST = ''
SERVER_PORT = '8086'
API_HOST = '0.0.0.0'
API_PORT = '8085'

data_template = pd.DataFrame(columns=['id', 'reminder_time', 'message', 'x_sec_repeat'])


# loads relevant data on app startup (only upcoming reminders)
def load_data():
    global data
    url = f'http://{API_HOST}:{API_PORT}/list'
    params = {'from': time.strftime("%Y%m%dt%H%M%S", time.localtime(time.time()))}
    r = requests.get(url=url, params=params)

    data = pd.read_json(r.content, orient="records",  convert_dates=False)
    if data.empty:
        data = data_template.copy()
    data = data.sort_values(by=['reminder_time'])


# creates and plays the recording
def play_rec(msg):
    test_t = time.time()
    filename = "rec" + ".mp3"
    language = 'en'

    # create a record file of the reminder and save locally
    myobj = gTTS(text=msg, lang=language, slow=False)
    myobj.save(filename)
    print(f'create rec: {time.time() - test_t}')
    # play the recording
    mixer.init()
    mixer.music.load(filename)
    mixer.music.play()
    while mixer.music.get_busy():
        time.sleep(0.1)

    print(f'play: {time.time() - test_t}')
    #TODO: delete rec file, maybe delete while


def get_data_version():
    url = f'http://{API_HOST}:{API_PORT}/data-version'
    r = requests.get(url=url)
    return int(r.text)

# TODO: add a hook in api
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

