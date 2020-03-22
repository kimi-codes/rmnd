from pygame import mixer
from gtts import gTTS
import pandas as pd
import threading
import requests
import socket
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


# adds or removes reminders in data df
def update(df):
    global data

    mode = df.iloc[0]['mode']
    df = df.drop(['mode'], axis=1)

    # add upcoming reminders to data df
    if mode == 'a':
        data = data.append(df, ignore_index=True)
        data = data.sort_values(by=['reminder_time'])
    # delete reminder
    elif mode == 'd':
        data = data[~data.id.isin(df['id'])]


# receives updates through socket
def server_socket():
    global data

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((SERVER_HOST, int(SERVER_PORT)))
    serversocket.listen(5)
    while True:
        conn, address = serversocket.accept()
        while True:
            received_data = conn.recv(4096)
            if not received_data:
                break
            new_data = received_data.decode('utf-8')
            new_data = pd.read_json(new_data, convert_dates=False)
            update(new_data)
        conn.close()


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
    socket_thread = threading.Thread(target=server_socket, args=())

    load_data()
    socket_thread.start()
    play_reminder()

