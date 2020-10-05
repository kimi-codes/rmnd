#!/usr/bin/python
import time
import argparse
import dateparser
import requests
import pandas as pd
import json
import os


SERVER_HOST = '0.0.0.0'
SERVER_PORT = '8085'

CONFIG_FILE = "conf.json"
TIME_FORMAT = '%Y%m%dt%H%M%S'
data_template = pd.DataFrame(columns=['id', 'reminder_time', 'message', 'x_sec_repeat'])


def set_host_config():
    global SERVER_HOST
    global SERVER_PORT
    global BASE_URL
    global ADD_URL
    global RM_URL
    global LS_URL
    global DATA_VER_URL

    # if conf file exists read current values
    try:
        with open(CONFIG_FILE) as conf_file:
            data = json.load(conf_file)
            data = json.loads(data)
            SERVER_HOST = data['host']
            SERVER_PORT = data['port']
    except: 
        pass

    BASE_URL = f'http://{SERVER_HOST}:{SERVER_PORT}'
    ADD_URL = f'{BASE_URL}/add'
    RM_URL = f'{BASE_URL}/remove'
    LS_URL = f'{BASE_URL}/list'
    DATA_VER_URL = f'{BASE_URL}/data-version'


def config_cmd(arguments):
    host = SERVER_HOST
    port = SERVER_PORT

    # no args - show current config values (from conf file if exists, or default values)
    if not arguments['host'] and not arguments['port'] and not arguments['set_default']:
        print(f'Host: {host}\nPort: {port}')

    # set-default argument - to use default host & port just delete the config file
    elif arguments['set_default']:
        os.remove(CONFIG_FILE)
        
    else:
        if arguments['host']:
            host = arguments['host'][0]
        if arguments['port']:
            port = arguments['port'][0]

        # save new values to conf file
        conf_data = {"host": host, "port": port}
        json_dump = json.dumps(conf_data)
        with open(CONFIG_FILE, 'w') as conf_file:
            json.dump(json_dump, conf_file)


def parse_args():
    parser = argparse.ArgumentParser(prog='PROG')
    subparsers = parser.add_subparsers(dest='command', help='sub-command help')

    # 'add' command parser
    parser_add = subparsers.add_parser('add', help='add reminder')
    parser_add.add_argument("text", nargs='*', default='reminder')
    parser_add.add_argument("-t", "--time", nargs='*', action='store')

    # 'rm' and 'ls' common arguments
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("id", nargs='*', action='store', default=[])
    parent_parser.add_argument("--from", nargs='*', action='store')
    parent_parser.add_argument("--to", nargs='*', action='store')

    # 'rm' and 'ls' parsers
    subparsers.add_parser('rm', parents=[parent_parser], help='remove reminder')
    subparsers.add_parser('ls', parents=[parent_parser], help='list reminders')

    # 'config' parser
    parser_config = subparsers.add_parser('config', help='edit config file')
    parser_config.add_argument("--host", nargs='*', action='store')
    parser_config.add_argument("-p", "--port", nargs='*', action='store')
    parser_config.add_argument("--set_default", action='store_true') 

    args = parser.parse_args()
    return args


def run_cmd():
    args = parse_args()
    arguments = vars(args)

    if args.command == 'add':
        add_cmd(arguments)
    elif args.command == 'ls':
        ls_cmd(arguments)
    elif args.command == 'rm':
        rm_cmd(arguments)
    elif args.command == 'config':
        config_cmd(arguments)


def add_cmd(arguments):
    dt = arguments['time']
    # reminder without time receives current time
    if dt is None:
        dt = time.strftime(TIME_FORMAT, time.localtime(time.time()))
    else:
        dt = ' '.join(dt)
        dt = dateparser.parse(dt)
        if dt is not None:
            dt = dt.strftime(TIME_FORMAT)
        else:
            print('could not parse "time"')
            exit()

    text = ' '.join(arguments['text'])
    params = {"message": text, "time": dt}
    r = requests.post(ADD_URL, params)
    print(r.text)


def ls_rm_param_parse(arguments):
    id_str = arguments['id']
    if id_str:
        id_str = ' '.join(id_str)

    from_dt = arguments['from']
    if from_dt is not None:
        t = ' '.join(from_dt)
        t = dateparser.parse(t)
        if t is not None:
            from_dt = t.strftime(TIME_FORMAT)
        else:
            print('could not parse "from" parameters')
            exit()

    to_dt = arguments['to']
    if to_dt is not None:
        t = ' '.join(to_dt)
        t = dateparser.parse(t)
        if t is not None:
            to_dt = t.strftime(TIME_FORMAT)
        else:
            print('could not parse "to" parameters')
            exit()

    params = {'from': from_dt, 'to': to_dt, 'id': id_str}
    return params


def ls_cmd(arguments):
    params = ls_rm_param_parse(arguments)

    r = requests.get(url=LS_URL, params=params)
    data = pd.read_json(r.content, orient="records", convert_dates=False)
    if data.empty:
        data = data_template.copy()
    print(data)


def rm_cmd(arguments):
    params = ls_rm_param_parse(arguments)
    r = requests.post(RM_URL, params)
    print(r.content)


set_host_config()
run_cmd()
