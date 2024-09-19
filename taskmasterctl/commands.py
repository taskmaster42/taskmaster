import requests
import logging


logging.basicConfig(level=logging.INFO)


class Commands:
    def __init__(self, port: int) -> None:
        self.port = port

    def _send(self, command: str, process: str) -> None:
        try:
            response = requests.post(f"http://localhost:{self.port}/", data={command: process})
            if response.status_code == 200:
                logging.debug("POST request successful!")
                logging.debug(f"Response from server: {response.text}")
                print(response.text)
            else:
                logging.debug(f"POST request failed with status code {response.status_code}")

        except requests.exceptions.ConnectionError:
            logging.info("The server cannot be reached.")

        except Exception as e:
            logging.error(f"An error occurred: {e}")

    def reload(self, args):
        if (len(args) > 0):
            print("Error: reload accepts no arguments")
            return False

        confirmation = input("Are you sure you want to reload the remote taskmaster? y/N? ")
        if confirmation.lower() == "y":
            self._send("reload", "")
            print("Restarted taskmaster.")
        return True

    def restart(self, args):
        if (args == ""):
            print("Error: restart requires a process name")
            return False

        for process in args.split():
            self._send("stop", process)
        for process in args.split():
            self._send("start", process)
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

# reload    YES     (no value returned)
# restart   YES     (return all the process affected)
# start
# stop
# update
# status
# exit
# quit
