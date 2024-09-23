import requests
import logging
import json
import select
import sys
import signal

logging.basicConfig(level=logging.INFO)


class Commands:
    def __init__(self, port: int) -> None:
        self.port = port

    def _display_dict(self, dictionary: dict, command: str) -> None:
        if not dictionary:
            return
        if (command == "status"):
            for key, value in dictionary.items():
                print(f"{key:<20}{value[0]:<20}{value[1]:>7}")
        elif (command == "attach_cmd"):
            print(dictionary['return'][0])
        elif (command == "debug"):
            print(dictionary)
        else:
            print(f"{command} executed successfully.")

    def _send(self, command: str, process: str) -> None:
        try:
            response = requests.post(f"http://localhost:{self.port}/",
                                     data={command: process},
                                     headers={
                                         "Content-Type":
                                         "application/x-www-form-urlencoded"})
            if response.status_code == 200:
                logging.debug("POST request successful!")
                logging.debug(f"Response from server: {response.text}")
                self._display_dict(dict(json.loads(response.text)), command)
            else:
                logging.debug(f"POST request failed with \
status code {response.status_code}")

        except requests.exceptions.ConnectionError:
            logging.info("The server cannot be reached.")

        except Exception as e:
            logging.error(f"An error occurred: {e}")

    def exit(self, args):
        return True

    def quit(self, args):
        return True

    def restart(self, args):
        if (args == ""):
            print("Error: restart requires a process name")
            return False

        for process in args.split():
            self._send("restart", process)
        return True

    def start(self, args):
        if (args == ""):
            print("Error: start requires a process name")
            return False

        for process in args.split():
            self._send("start", process)
        return True

    def stop(self, args):
        if (args == ""):
            print("Error: stop requires a process name")
            return False

        for process in args.split():
            self._send("stop", process)
        return True

    def update(self, args):
        if (len(args) > 0):
            print("Error: update accepts no arguments")
            return False

        confirmation = input("Are you sure you want to update \
the remote taskmaster? y/N? ")
        if confirmation.lower() == "y":
            self._send("update", "all")
        return True

    def status(self, args):
        if (args == ""):
            self._send("status", "all")
        else:
            for process in args.split():
                self._send("status", process)
        return True

    def set_sigint(self, num, _):
        self.running = False

    def attach(self, args):
        self._send("attach", args.split()[0])
        cmd = ""
        signal.signal(signal.SIGINT, self.set_sigint)
        self.running = True
        while self.running:
            fd_r, _, _ = select.select([sys.stdin], [], [], 1)
            if len(fd_r) > 0:
                _line = sys.stdin.readline()
                cmd += _line
                if "\n" in cmd:
                    self._send("attach_cmd", cmd)
                    cmd = ""
            else:
                self._send("ping", "yo")
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    def debug(self, args):
        if (args == ""):
            self._send("debug", "all")
        else:
            for process in args.split():
                self._send("debug", process)
        return True
