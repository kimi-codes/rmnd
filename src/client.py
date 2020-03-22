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

data_template = pd.DataFrame(columns=['id', 'reminder_time', 'message', 'x_sec_repeat'])


def t_parse(txt):
    time_in_sec = dict(seconds=1, secs=1, s=1, minutes=60, mins=60, m=60, hours=60 * 60, h=60 * 60)
    in_flag = False
    at_flag = False
    updated_flag = False
    time_type_flag = False
    temp = 0
    dt = datetime.datetime.now()

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


#def parse_args():


#def run_cmd():

parser = argparse.ArgumentParser(prog='PROG')
subparsers = parser.add_subparsers(dest='command', help='sub-command help')

# 'add' command parser
parser_add = subparsers.add_parser('add', help='add reminder')
parser_add.add_argument("text", nargs='*', default='reminder')
parser_add.add_argument("-t", "--time", nargs='*', action='store')

# 'rm' command parser
parser_rm = subparsers.add_parser('rm', help='remove reminder')
parser_rm.add_argument("id", nargs='*', action='store', default=[])
parser_rm.add_argument("--from", nargs='*', action='store')
parser_rm.add_argument("--to", nargs='*', action='store')

# 'ls' command parser
parser_ls = subparsers.add_parser('ls', help='list reminders')
parser_ls.add_argument("id", nargs='*', action='store', default=[])
parser_ls.add_argument("--from", nargs='*', action='store')
parser_ls.add_argument("--to", nargs='*', action='store')

args = parser.parse_args()

print(args)
arguments = vars(args)

if args.command == 'add':
    url = f'http://{API_HOST}:{API_PORT}/add'
    t = arguments['time']
    if t is None:
        t = time.strftime("%Y%m%dt%H%M%S", time.localtime(time.time()))
    else:
        t = ' '.join(t)
        t = t_parse(t)
        print(t)
        if t is not None:
            t = t.strftime("%Y%m%dt%H%M%S")
        else:
            print('could not parse "time"')
            exit()

    text = ' '.join(arguments['text'])
    params = {"message": text, "time": t}
    r = requests.post(url, params)
    print(r.content)

elif args.command == 'ls':
    url = f'http://{API_HOST}:{API_PORT}/list'

    from_dt = None
    if arguments['from'] is not None:
        t = t_parse(arguments['from'])
        if t is not None:
            from_dt = time.strftime("%Y%m%dt%H%M%S", t)
        else:
            print('could not parse "from"')
            exit()

    to_dt = None
    if arguments['to'] is not None:
        t = t_parse(arguments['to'])
        if t is not None:
            to_dt = time.strftime("%Y%m%dt%H%M%S", t)
        else:
            print('could not parse "to"')
            exit()

    params = {'from': from_dt, 'to': to_dt, 'id': arguments['id']}
    r = requests.get(url=url, params=params)
    data = pd.read_json(r.content, orient="records", convert_dates=False)
    if data.empty:
        data = data_template.copy()
    print(data)

elif args.command == 'rm':
    print('rm')
