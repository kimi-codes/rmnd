# rmnd

A command-line reminder tool, using Googles TTS to read the reminders out loud.
This program contains of a server and a client, and can be run on different computers. 

## Table of Contents
* General Info
* How It Works
* Instalation
* Setup
* CLI Usage
* Servers API usage

## General Info
This app was built for learning porpuses of Python programming, creating an HTTP API using Flask, creating a server-client app, and creating a CLI.
The idea for the app came from my need for a TTS reminder app, and my love for the terminal and CLI apps.


## How It Works

#### server.py: (server)
The database of the reminders. Has a HTTP API using Flask, for adding, deleting, listing reminders and checking for updates.
keeps a data version file, with the value updated on every change made to the remminders. 

#### reminder.py: (client)
The TTS reminder reader. Using the servers API, it pulls all upcomming reminders on startup, and keeps checking the server for updates (using a comparisson of the data version). 
Few seconds before a reminder is due (currently 30), a TTS audio file is created to be ready to play on time.

#### rmnd.py: (CLI)
The command line interface for adding, listing and removing entries from the server. It uses the servers API.  

All parts can run on different machines.


## Instalation

### Requirements
This project requires Python3 and several Python packages to run.

#### Python 3.X
You should have Python 3.X installed on your machine.
To check if Python3 installed run the following in terminal:
```
python3 --version
```
###### To get Pyhton3:
For Debian-based Linux distributions (Mint, Ubuntu, Kali):
```
$ sudo apt-get install python3 python3-pip
```

For Windows, MacOS and other Linux distros you can get it on:   
https://www.python.org/getit/

#### Python packages
to install required Python packages run:  
```
pip3 install -r requirements.txt
```  


## Setup

#### Running the server
The server must first run for the rmnd app to work:  
```bash
python3 server.py
```  

#### Running the rmnd client 
This is the TTS reminder reader. It Reads the reminders from the server.

```bash
python3 reminder.py <IP> <PORT>
```    
`<IP>` - IP of the machine on which the server is running. default is localhost.  
`<PORT>` - default is 8085.  
If the clients runs in same machine as the server and no changes been made to the servers port, `<IP>` and `<PORT>`can be ommited.

#### Setting the CLI
##### Optional:
To avoid using `Python3` command everytime running a rmnd CLI command: 

On Linux move the rmnd.py file to one of the $PATH paths and give execution permissions to use as a command. 
```bash
sudo chmod +x ./rmnd.py
mv ./rmnd.py /usr/local/bin/rmnd
```  

##### Configuring Server Host and Port
If the server is running on a different host or changes been made to the default port:  
```bash 
rmnd config --host <IP> --port <PORT>
```  
`--host <IP>` or `--port <PORT>` can be ommited if they`re default values.
** If previous step not done. use `python3 rmnd.py` instead of `rmnd`.



## CLI Usage

For help and list of commands, run:  
```bash
rmnd --help
```  

##### Examples:
```bash
# add reminder
rmnd add Hello world -t in 1 minute

# list all reminders
rmnd ls

# remove reminders from 1 hour ago to 30 minutes ago
rmnd rm --from 1 hour ago --to 30 minutes ago

# remove reminder by id
rmnd rm 1 2 4
```  

## Servers API usage

Comming Soon
