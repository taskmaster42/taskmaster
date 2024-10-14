# taskmaster
A simple job manager inspired by taskmasterd written in python3 for linux.


## Installation
```
git clone git@github.com:taskmaster42/taskmaster.git
cd taskmaster
pip install -r requirements.txt
```

## Usage
taskmaster uses a client/server architecture. The server will manage the jobs and the client is the command line interface to interact with the server. The server loads a configuration file and starts the jobs defined in it.

```
python main.py [options] <port>
```
Options:
- `--config`: path to the configuration file (default: ./config.yaml)
- `--log`: path to the log file (default: ./taskmaster.log)
- `--silent`: no output in the console

The client can interact with the server to start, stop, restart, reload, status, attach to a process.
```
python taskmasterctl/main.py [options] <port>
```
Actions:
- `start`: Start a programme
- `restart`: stop and restart a programm
- `stop`: stop a programm
- `reload`: reload the configuration file, restart only the modified jobs
- `status`: get the status of the jobs
- `attach`: attach to a process by giving a shell

## Configuration file
The configuration file is a yaml file. The root element is a list of jobs. Each job is a dictionary with the following keys: (see config_sample.yaml for example)

| key | description | value | default | trigger job restart in case of reload |
| --- | :-----------: | :---: | :-------: | :------------------------------: |
| `cmd`| command to execute | string | required | true
| `numprocs`| number of processes to start| int | 1 | true if number goes down
| `autostart`| start the job at the server start| bool | true | false
| `autorestart`| restart the job if it exits | true, false, unexpected | true | false
| `exitcodes`| exit codes that will define expected/unexpected | list of int | [0] | false 
| `startretries`| the number of retries before giving up | int | 3 | false
| `startsecs`| the time to wait before restarting the job | int | 1 | false
| `stopsignal`| the signal to send to stop the job | string | SIGTERM | false
| `stopwaitsecs`| the time to wait after sendint stop signal before kiling with SIKKILL | int | 10 | false
| `stdout`| the path to the stdout file | string | None | false
| `stderr`| the path to the stderr file | string | None | false
| `env`| a dictionary of environment variables | dict | {} | true
| `umask`| the umask of the process | octal | 000 | true
| `workingdir`| the working directory of the process | string | current working dir | true
| `user`| the user to run the process (only if server started as root) | string | current user | true
