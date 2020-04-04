#!/usr/bin/python
import time
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import argparse
import datetime
import requests
import pandas as pd


SERVER_HOST = ''
SERVER_PORT = '8086'
API_HOST = '0.0.0.0'
API_PORT = '8085'

BASE_URL = f'http://{API_HOST}:{API_PORT}'
ADD_URL = f'{BASE_URL}/add'
RM_URL = f'{BASE_URL}/remove'
LS_URL = f'{BASE_URL}/list'

TIME_FORMAT = '%Y%m%dt%H%M%S'

data_template = pd.DataFrame(columns=['id', 'reminder_time', 'message', 'x_sec_repeat'])

'''
(in) x [days-time] | (and/,) x [days-time] | (at) [hh:mm:ss / hh:mm / h](pm/am)
* if [hour-time] present, no 'at'

x [days-time] | (and/,) x [days-time] | ago | (at) [hh:mm:ss / hh:mm / h](pm/am)
* if [hour-time] present, no 'at'

[date] | (at) [hh:mm:ss / hh:mm / h](pm/am)

date:
[yyyy/mm/dd dd/mm/yy dd/mm]
['/' / '-' / '.'] 
[D [month] (,) yy(yy)]
[[month] D(st/nd/rd/th) (,) yy(yy)]

'''

'''
START
GOT_NUM
GOT_TYPE
GET_TIME
END


NUM (num)
DATE_PART {days, weeks, months, years}
TIME_PART {seconds, minutes, hours} 
AT "at"
AND "and"
AGO "ago"
TIME 
'''


def tp(txt):
    # time tense values:
    tense = dict(unknown=0, past=1, future=2)
    # states:
    states = dict(start=0, got_num=1, got_type=2, get_time=3, end=4, error=5)

    flags = dict(time_added=False, time_tense=tense['unknown'])
    state = states['start']

    txt = txt.split()
    for token in txt:
        if state == states['start']:
            # integer or float:
            if token.replace('.', '', 1).isdigit():
                state = states['got_num']
            # 'in' keyword
            elif token == 'in':
                flags['time_tense'] = tense['future']
            else:
                state = states['error']
                break
        elif state == states['got_num']:
            print('start')
        elif state == states['got_type']:
            # integer or float:
            if token.replace('.', '', 1).isdigit():
                state = states['got_num']
            # 'and' keyword
            elif token == 'and':
                state = states['start']
            # 'ago' keyword - only if 'in' wasnt presented
            elif token == 'ago':
                if flags['time_tense'] == tense['future']:
                    state = states['error']
                    break
                flags['time_tense'] = tense['past']

        elif state == states['get_time']:
            print('start')


def t_parse(txt):
    time_in_sec = dict(seconds=1, secs=1, s=1, minutes=60, mins=60, m=60, hours=60 * 60, h=60 * 60)
    in_flag = False
    at_flag = False
    updated_flag = False
    time_type_flag = False
    temp = 0
    dt = datetime.datetime.now()

    # try to parse using dateutil.parser
    try:
        dt = parse(txt)
        return dt
    except:
        pass

    txt = txt.split()
    for token in txt:
        if in_flag:
            if time_type_flag:
                if time_in_sec.get(token) is not None:
                    sec = temp * time_in_sec[token]
                    dt += relativedelta(seconds=sec).normalized()
                    temp = 0
                elif token == 'days' or 'd':
                    dt += relativedelta(days=temp)
                    temp = 0
                elif token == 'months':
                    dt += relativedelta(months=temp)
                    temp = 0
                else:
                    print('error')
                    return None
                updated_flag = True
                time_type_flag = False
            elif token.replace('.','',1).isdigit():
                temp = float(token)
                time_type_flag = True
            elif token == 'and':
                pass
            elif token == 'at':
                at_flag = True
                in_flag = False
            else:
                in_flag = False
        elif at_flag:
            t = parse(token)
            dt = datetime.datetime.combine(dt.date(), t.time())
            updated_flag = True
            at_flag = False
        elif token == 'in':
            in_flag = True
        else:
            print("error")
            return None
    if updated_flag:
        return dt
    return None


# add: -t, --time

# rm, ls:  --from
#          --to
#          --id


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


def add_cmd(arguments):
    dt = arguments['time']
    # reminder without time receives current time
    if dt is None:
        dt = time.strftime(TIME_FORMAT, time.localtime(time.time()))
    else:
        dt = ' '.join(dt)
        # TODO: t_parse should throw exceptions?
        dt = t_parse(dt)
        if dt is not None:
            dt = dt.strftime(TIME_FORMAT)
        else:
            print('could not parse "time"')
            exit()

    text = ' '.join(arguments['text'])
    params = {"message": text, "time": dt}
    r = requests.post(ADD_URL, params)
    print(r.content)


def ls_cmd(arguments):
    from_dt = arguments['from']
    id_str = arguments['id']
    if id_str:
        id_str = ' '.join(id_str)

    if from_dt is not None:
        t = ' '.join(from_dt)
        t = t_parse(t)
        if t is not None:
            from_dt = t.strftime(TIME_FORMAT)
        else:
            print('could not parse "from" parameters')
            exit()

    to_dt = arguments['to']
    if to_dt is not None:
        t = ' '.join(to_dt)
        t = t_parse(t)
        if t is not None:
            to_dt = t.strftime(TIME_FORMAT)
        else:
            print('could not parse "to" parameters')
            exit()

    params = {'from': from_dt, 'to': to_dt, 'id': id_str}

    r = requests.get(url=LS_URL, params=params)
    data = pd.read_json(r.content, orient="records", convert_dates=False)
    if data.empty:
        data = data_template.copy()
    print(data)


def rm_cmd(arguments):
    id_str = arguments['id']
    if id_str:
        id_str = ' '.join(id_str)

    from_dt = arguments['from']
    if from_dt is not None:
        t = ' '.join(from_dt)
        t = t_parse(t)
        if t is not None:
            from_dt = t.strftime(TIME_FORMAT)
        else:
            print('could not parse "from"')
            exit()

    to_dt = arguments['to']
    if to_dt is not None:
        t = ' '.join(from_dt)
        t = t_parse(t)
        if t is not None:
            to_dt = t.strftime(TIME_FORMAT)
        else:
            print('could not parse "to"')
            exit()

    params = {'from': from_dt, 'to': to_dt, 'id': id_str}

    r = requests.post(RM_URL, params)
    print(r.content)

run_cmd()
