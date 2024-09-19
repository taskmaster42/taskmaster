from config_types import AutoRestartType, ListIntegerType, SignalType
import os
from .ConfigElement import ConfigElement


class Config():
    authorized_key = {
        "cmd": (str, None),
        "numprocs": (int, 1),
        "umask": (str, "000"),
        "workingdir": (str, os.getcwd()),
        "autostart": (bool, True),
        "autorestart": (AutoRestartType, AutoRestartType('unexpected')),
        "exitcodes": (ListIntegerType, ListIntegerType([0])),
        "startretries": (int, 3),
        "startsecs": (int, 1),
        "stopwaitsecs": (int, 10),
        "stdout": (str, None),
        "stderr": (str, None),
        "env": (dict, []),
        "stopsignal": (SignalType, SignalType("SIGKILL"))
    }

    def __init__(self, config_file):
        self.config = {}

        for key, value in config_file.items():
            if key not in self.authorized_key:
                raise ValueError(f"Unknown key got {key}")
            if value is None:
                raise ValueError(f"Got None for key {key}")

            self.config[key] = ConfigElement(value,
                                             (self.authorized_key[key][0]))

        for key, value in self.authorized_key.items():
            if key not in self.config:
                self.config[key] = ConfigElement(self.authorized_key[key][1],
                                                self.authorized_key[key][0])

        if "cmd" not in self.config:
            raise AssertionError("No cmd provided")

    def get(self, key):
        return self.config[key].get_value()

    def __eq__(self, value: object) -> bool:
        for key, v in self.config.items():
            try:
                if v != value.config.get(key):
                    return False
            except Exception as e:
                    
                    return False
        return True