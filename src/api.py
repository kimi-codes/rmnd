from flask import Flask, request, jsonify
import pandas as pd
import ciso8601
import json
import time

SERVER_HOST = ''
SERVER_PORT = '8086'
API_HOST = '0.0.0.0'
API_PORT = '8085'

data_template = pd.DataFrame(columns=['id', 'reminder_time', 'message', 'x_sec_repeat'])
data_file = f"data.csv"
data_version_file = f"data_ver.txt"

app = Flask(__name__)


# creates missing file
def create_files():
    # data file
    try:
        f = open(data_file, "r")
        f.close()
    except FileNotFoundError:
        df = data_template.copy()
        df.to_csv(data_file, index=False)
    # data-version file
    try:
        f = open(data_version_file, "r")
        f.close()
    except FileNotFoundError:
        f = open(data_version_file, "w+")
        f.write("0")
        f.close()


# returns the ID of the last created reminder, or 0 if empty
def get_last_id():
    data = pd.read_csv(data_file)
    last_id = 0
    if not data.empty:
        last_id = data['id'].max()

    return last_id


def update_data_version():
    global data_ver

    data_ver += 1
    f = open(data_version_file, "w+")
    f.write(str(data_ver))
    f.close()


# parses time to epoch format
def parse_time(dt):
    ts = ciso8601.parse_datetime(dt)
    ts = int(time.mktime(ts.timetuple()))
    return ts


# returns a dataframe containing all or part of the reminders
def get_reminder(from_date, to_date, id_list):
    data = pd.read_csv(data_file)

    from_date = None if from_date == '' else from_date
    to_date = None if to_date == '' else to_date

    if id_list is not None:
        id_list = id_list.split(" ")
        data = data[data.id.isin(id_list)]

    if from_date is not None:
        dt = parse_time(from_date)
        data = data.loc[data['reminder_time'] > dt]

    if to_date is not None:
        dt = parse_time(to_date)
        data = data.loc[data['reminder_time'] < dt]

    return data


@app.route('/')
def hello():
    return "Hello World!"


@app.route('/add', methods=['POST'])
def add_reminder():
    global next_id
    msg = request.form.get('message')
    dt = request.form.get('time')
    dt = parse_time(dt)

    new_rem_df = data_template.copy()
    new_row = {'id': next_id, 'reminder_time': dt, 'message': msg, 'x_sec_repeat': 0}
    new_rem_df = new_rem_df.append(new_row, ignore_index=True)

    # save to the data file
    new_rem_df.to_csv(data_file, mode='a', header=False, index=False)
    next_id += 1
    update_data_version()

    jdata = json.loads(new_rem_df.to_json(orient='records'))
    return jsonify(jdata)
    # TODO: return status code


@app.route('/remove', methods=['POST'])
def remove_rem():
    from_date = request.form.get('from')
    to_date = request.form.get('to')
    id_list = request.form.get('id')

    # create a df of IDs to delete
    rm_id = get_reminder(from_date, to_date, id_list)
    rm_id = rm_id['id']

    # update data file
    data = pd.read_csv(data_file)
    data = data[~data.id.isin(rm_id)]
    data.to_csv(data_file, header=True, index=False)

    update_data_version()

    return rm_id.to_string(index=False)


@app.route('/list', methods=['GET'])
def get_rem():
    from_date = request.args.get('from')
    to_date = request.args.get('to')
    id_list = request.args.get('id')

    data = get_reminder(from_date, to_date, id_list)
    jdata = json.loads(data.to_json(orient='records'))
    return jsonify(jdata)


@app.route('/data-version', methods=['GET'])
def get_data_version():
    f = open(data_version_file, "r")
    ver = f.read()
    f.close()

    return ver


if __name__ == '__main__':
    create_files()
    next_id = get_last_id() + 1
    data_ver = int(get_data_version())

    app.run(debug=True, host=API_HOST, port=API_PORT)
