# rmnd

A command-line reminder tool, using Googles TTS to read the reminders out loud.
This program contains of a server and a client, and can be run on different computers. 


### server.py: (server)
The database of the reminders. Has a HTTP API for adding, deleting and listing reminders.  
run:  
```bash
python3 server.py
```  

### reminder.py: (client)
The TTS reminder reader. Reads the reminders from the server.

run:  
```bash
python3 reminder.py <IP> <PORT>
```  
`<IP>` - IP of the machine on which the server is running. default is localhost.  
`<PORT>` - default is 8085.

### rmnd.py: (CLI)
The command line interface for adding, listing and removing entries from the server.

On Linux move to one of the $PATH paths and give execution permissions to use as a command. 
```bash
sudo chmod +x ./rmnd.py
mv ./rmnd.py /usr/local/bin/rmnd
```  


If previous step not done, change `rmnd` with `python3 rmnd.py` or `py rmnd.py` on next examples:  

if server is running on a different host:  
```bash 
rmnd config --host <IP>
```  

For help and list of commands, run:  
```bash
rmnd --help
```  

Examples:
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


